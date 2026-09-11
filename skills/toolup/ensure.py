#!/usr/bin/env python3
"""
Install missing tools yourself. Free versions only. Disclose every account before it is needed.

    python ensure.py --plan            show what is missing and exactly what installing it involves
    python ensure.py jq ffmpeg         install specific tools
    python ensure.py --all             install everything free and account-free
    python ensure.py --python          install the missing Python packages

Rules this enforces:
  * Nothing that costs money. Every entry below is free software.
  * Nothing that needs an account gets installed silently. Those are listed, with the
    signup and login steps printed in full, and left for the human to decide.
  * The user is never handed a command they did not ask for. Run it for them.
"""
import argparse
import os
import platform
import shutil
import subprocess
import sys

WIN = platform.system() == "Windows"
MAC = platform.system() == "Darwin"

# name -> (winget id, brew formula, apt package, one-line purpose)
TOOLS = {
    "jq":        ("jqlang.jq", "jq", "jq", "JSON on the command line"),
    "fd":        ("sharkdp.fd", "fd", "fd-find", "fast file finder"),
    "rg":        ("BurntSushi.ripgrep.MSVC", "ripgrep", "ripgrep", "fast content search"),
    "sqlite3":   ("SQLite.SQLite", "sqlite", "sqlite3", "query .db files directly"),
    "pandoc":    ("JohnMacFarlane.Pandoc", "pandoc", "pandoc", "markup conversion"),
    "7z":        ("7zip.7zip", "sevenzip", "p7zip-full", "archives Windows tar cannot open"),
    "ffmpeg":    ("Gyan.FFmpeg", "ffmpeg", "ffmpeg", "audio and video, everything"),
    "magick":    ("ImageMagick.ImageMagick", "imagemagick", "imagemagick", "batch image work"),
    "tesseract": ("UB-Mannheim.TesseractOCR", "tesseract", "tesseract-ocr", "OCR for scanned pages"),
    "wget":      ("JernejSimoncic.Wget", "wget", "wget", "recursive download"),
    "make":      ("GnuWin32.Make", "make", "make", "run Makefiles"),
    "go":        ("GoLang.Go", "go", "golang", "Go toolchain"),
    "java":      ("EclipseAdoptium.Temurin.21.JDK", "temurin", "default-jdk", "JVM"),
    "cargo":     ("Rustlang.Rustup", "rustup", "rustup", "Rust toolchain"),
}

# Tools that are free to install but useless without an account.
# Nothing here is installed silently. The flow is printed instead.
ACCOUNT_TOOLS = {
    "wrangler": {
        "install": ["npm", "install", "-g", "wrangler"],
        "service": "Cloudflare",
        "cost": "Free tier is genuine: Workers, Pages, R2 and D1 all have free allowances.",
        "signup": [
            "1. Go to https://dash.cloudflare.com/sign-up",
            "2. Email + password. No card required for the free tier.",
            "3. Verify the email link.",
        ],
        "login": [
            "Run: wrangler login",
            "It opens a browser tab, you click Allow, and the token is stored locally.",
            "Nothing is charged and no card is asked for during this.",
        ],
    },
    "gh": {
        "pkg": ("GitHub.cli", "gh", "gh"),
        "service": "GitHub",
        "cost": "Free. Private repos included.",
        "signup": ["1. https://github.com/signup", "2. Username, email, password.",
                   "3. Verify email."],
        "login": [
            "Run: gh auth login",
            "Choose GitHub.com, HTTPS, then 'Login with a web browser'.",
            "It prints an 8-character code, you paste it into the browser page it opens.",
        ],
    },
    "aws": {
        "pkg": ("Amazon.AWSCLI", "awscli", "awscli"),
        "service": "Amazon Web Services",
        "cost": "A CARD IS REQUIRED AT SIGNUP even on the free tier. Charges are possible.",
        "signup": [
            "1. https://portal.aws.amazon.com/billing/signup",
            "2. Email, then a payment card, then a phone verification call or SMS.",
            "3. Pick the Basic (free) support plan.",
        ],
        "login": [
            "Create an access key under IAM, then run: aws configure",
            "It asks for the key id, secret, default region and output format.",
        ],
    },
    "gcloud": {
        "pkg": ("Google.CloudSDK", "google-cloud-sdk", "google-cloud-cli"),
        "service": "Google Cloud",
        "cost": "A CARD IS REQUIRED to enable most APIs, even inside the free credit.",
        "signup": ["1. https://console.cloud.google.com", "2. Google account, then a billing profile with a card.",
                   "3. Create a project."],
        "login": ["Run: gcloud auth login", "Browser OAuth, then: gcloud config set project <id>"],
    },
}

PY_PACKAGES = {
    "pandas": "pandas", "numpy": "numpy", "openpyxl": "openpyxl",
    "xlsxwriter": "XlsxWriter", "docx": "python-docx", "pptx": "python-pptx",
    "pypdf": "pypdf", "fitz": "PyMuPDF", "PIL": "Pillow", "bs4": "beautifulsoup4",
    "requests": "requests", "lxml": "lxml", "matplotlib": "matplotlib",
    "yaml": "PyYAML", "markdown": "Markdown", "chardet": "chardet",
    "dateutil": "python-dateutil", "ebooklib": "EbookLib",
    "pytesseract": "pytesseract", "rapidfuzz": "rapidfuzz",
}


# Programs that install correctly but never join PATH. Checking PATH alone reports these as
# missing, which is how a working Tesseract got called absent and nearly reinstalled.
OFF_PATH = {
    "tesseract": [r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                  r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                  "/opt/homebrew/bin/tesseract", "/usr/local/bin/tesseract"],
    "magick":    [r"C:\Program Files\ImageMagick-7.Q16-HDRI\magick.exe",
                  "/opt/homebrew/bin/magick", "/usr/local/bin/magick"],
    "ffmpeg":    [r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
                  "/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"],
    "sqlite3":   [r"C:\Program Files\SQLite\sqlite3.exe", "/opt/homebrew/bin/sqlite3"],
    "7z":        [r"C:\Program Files\7-Zip\7z.exe", r"C:\Program Files (x86)\7-Zip\7z.exe",
                  "/opt/homebrew/bin/7z", "/usr/bin/7z", "/usr/local/bin/7z"],
    "pandoc":    [r"C:\Program Files\Pandoc\pandoc.exe", "/opt/homebrew/bin/pandoc"],
    "make":      [r"C:\Program Files (x86)\GnuWin32\bin\make.exe", "/usr/bin/make"],
    "java":      [r"C:\Program Files\Eclipse Adoptium\jdk-21\bin\java.exe",
                  "/usr/bin/java", "/opt/homebrew/bin/java"],
    "go":        [r"C:\Program Files\Go\bin\go.exe", "/usr/local/go/bin/go",
                  "/opt/homebrew/bin/go"],
    "wget":      [r"C:\Program Files (x86)\GnuWin32\bin\wget.exe", "/opt/homebrew/bin/wget"],
}


def resolve(tool):
    """Full path to the tool, or None. Checks PATH, then winget's link and package
    directories, then known install locations. Never concludes 'missing' from PATH alone."""
    found = shutil.which(tool)
    if found:
        return found
    if WIN:
        local = os.environ.get("LOCALAPPDATA", "")
        link = os.path.join(local, "Microsoft", "WinGet", "Links", tool + ".exe")
        if os.path.exists(link):
            return link
        pkgs = os.path.join(local, "Microsoft", "WinGet", "Packages")
        if os.path.isdir(pkgs):
            for entry in os.listdir(pkgs):
                cand = os.path.join(pkgs, entry, tool + ".exe")
                if os.path.exists(cand):
                    return cand
    for cand in OFF_PATH.get(tool, []):
        if os.path.exists(cand):
            return cand
    return None


def have(tool):
    return resolve(tool) is not None


def missing_tools():
    return [t for t in TOOLS if not have(t)]


def missing_python():
    """Actually import each module. find_spec() lies about packages installed into the
    user site-packages directory, which is visible from some shells and not others."""
    gone = []
    for mod in PY_PACKAGES:
        try:
            __import__(mod)
        except Exception:
            gone.append(mod)
    return gone


def install_cmd(tool):
    """Build the install command for whatever package manager this OS actually has."""
    if tool in TOOLS:
        winget_id, brew, apt, _ = TOOLS[tool]
    else:
        entry = ACCOUNT_TOOLS[tool]
        if "install" in entry:          # already a literal command, e.g. npm -g
            return entry["install"]
        winget_id, brew, apt = entry["pkg"]
    if WIN:
        return ["winget", "install", "--id", winget_id, "-e", "--silent",
                "--accept-package-agreements", "--accept-source-agreements"]
    if MAC:
        return ["brew", "install", brew]
    for mgr, args in (("apt-get", ["sudo", "apt-get", "install", "-y", apt]),
                      ("dnf", ["sudo", "dnf", "install", "-y", apt]),
                      ("pacman", ["sudo", "pacman", "-S", "--noconfirm", apt])):
        if shutil.which(mgr):
            return args
    return None


def banner(text):
    print("\n" + text)
    print("-" * len(text))


def show_plan():
    banner("INTERPRETER THIS ANSWER IS ABOUT")
    print("  " + sys.executable)
    print("  version {}".format(platform.python_version()))
    import site
    user_site = site.getusersitepackages()
    print("  user site-packages: {}".format(
        "on sys.path" if user_site in sys.path else "NOT on sys.path — " + user_site))
    print("  A different shell may launch a different interpreter and give a different answer.")

    gone = missing_tools()
    banner("FREE, NO ACCOUNT, NO SIGNUP — safe to install without asking")
    if gone:
        for t in gone:
            print("  {:<10} {}".format(t, TOOLS[t][3]))
        print("\n  Install all of them:  python ensure.py --all")
    else:
        print("  nothing missing")

    pygone = missing_python()
    banner("PYTHON PACKAGES — free, pip, no account")
    if pygone:
        print("  " + " ".join(PY_PACKAGES[m] for m in pygone))
        print("\n  Install:  python ensure.py --python")
    else:
        print("  nothing missing")

    banner("NEEDS AN ACCOUNT — read this before anything is installed")
    for name, info in ACCOUNT_TOOLS.items():
        if have(name):
            print("\n  {}  ALREADY SET UP".format(name))
            continue
        print("\n  {}  ({})".format(name, info["service"]))
        print("    cost:   {}".format(info["cost"]))
        print("    signing up means:")
        for line in info["signup"]:
            print("      " + line)
        print("    logging in means:")
        for line in info["login"]:
            print("      " + line)
    print("\n  None of these are installed automatically. Say which you want.")


def run(cmd):
    # flush before handing the console to a subprocess, or the log prints out of order
    print("  $ " + " ".join(cmd), flush=True)
    result = subprocess.run(cmd, check=False)
    return result.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tools", nargs="*")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--python", action="store_true")
    a = ap.parse_args()

    if a.plan or (not a.tools and not a.all and not a.python):
        show_plan()
        return

    if a.python:
        gone = missing_python()
        if gone:
            run([sys.executable, "-m", "pip", "install"] + [PY_PACKAGES[m] for m in gone])
        else:
            print("python packages already complete")

    targets = list(a.tools) or (missing_tools() if a.all else [])
    for t in targets:
        if t in ACCOUNT_TOOLS:
            info = ACCOUNT_TOOLS[t]
            banner("{} needs a {} account — not installing silently".format(t, info["service"]))
            print("  " + info["cost"])
            for line in info["signup"] + info["login"]:
                print("  " + line)
            continue
        if t not in TOOLS:
            print("unknown tool: {}".format(t))
            continue
        if have(t):
            print("{} already present".format(t))
            continue
        cmd = install_cmd(t)
        if not cmd:
            print("no package manager for {}".format(t))
            continue
        print("installing {} — {}".format(t, TOOLS[t][3]), flush=True)
        run(cmd)
        if WIN:
            print("  PATH updated; new shells see it. This session may not.", flush=True)


if __name__ == "__main__":
    main()
