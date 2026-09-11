#!/usr/bin/env python3
"""
Convert documents using whatever is on the machine; acquire a free converter if nothing is.

    python convert.py IN OUT [--no-install]

Order of preference:
  1. Microsoft Office via COM      (Windows, best fidelity, already on most work machines)
  2. LibreOffice `soffice`         (any OS, free)
  3. A Chromium browser            (html -> pdf only, no office suite needed)
  4. Install LibreOffice, then go  (winget / brew / apt / dnf / pacman)

Never asks the user to open an application, click Save As, or install anything by hand.
"""
import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from html import unescape
from pathlib import Path

WIN = platform.system() == "Windows"
MAC = platform.system() == "Darwin"

OFFICE_IN = {".docx", ".doc", ".rtf", ".odt", ".txt", ".md",
             ".xlsx", ".xls", ".csv", ".ods", ".pptx", ".ppt", ".odp"}
BROWSER_IN = {".html", ".htm"}


def real_format(path):
    """What the file ACTUALLY is, by content. Extensions lie, and the common liars are
    exports: Confluence and Outlook both save MHTML as .doc, and 'not a valid Word
    document' is the wrong answer to a file that is perfectly readable HTML."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(4096)
    except OSError:
        return None
    if head[:4] == b"PK\x03\x04":
        return "zip"                      # docx/xlsx/pptx/odt are all zip containers
    if head[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        return "ole"                      # genuine legacy .doc/.xls
    if head[:5] == b"%PDF-":
        return "pdf"
    try:
        text = head.decode("utf-8", errors="replace").lower()
    except Exception:
        return None
    if "mime-version:" in text and "multipart/related" in text:
        return "mhtml"
    if "content-type: text/html" in text and "mime-version:" in text:
        return "mhtml"
    if text.lstrip().startswith(("<!doctype html", "<html")):
        return "html"
    return None


def log(msg):
    print(msg, file=sys.stderr)


# ---------- backend discovery ----------

def find_soffice():
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if exe:
        return exe
    guesses = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/bin/soffice", "/usr/local/bin/soffice", "/snap/bin/libreoffice",
    ]
    return next((g for g in guesses if os.path.exists(g)), None)


def find_browser():
    for name in ("msedge", "chrome", "chromium", "chromium-browser", "brave"):
        found = shutil.which(name)
        if found:
            return found
    guesses = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome", "/usr/bin/chromium",
    ]
    return next((g for g in guesses if os.path.exists(g)), None)


def has_office_com():
    """True only if Word automation actually starts, not merely if Office is installed."""
    if not WIN:
        return False
    ps = "try { $w = New-Object -ComObject Word.Application; $w.Quit(); 'yes' } catch { 'no' }"
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                             capture_output=True, text=True, timeout=90)
        return "yes" in out.stdout
    except Exception:
        return False


# ---------- acquisition ----------

def install_libreoffice():
    """Fetch the free converter. Silent, non-interactive, no user involvement."""
    if WIN and shutil.which("winget"):
        cmd = ["winget", "install", "--id", "TheDocumentFoundation.LibreOffice",
               "-e", "--silent", "--accept-package-agreements", "--accept-source-agreements"]
    elif MAC and shutil.which("brew"):
        cmd = ["brew", "install", "--cask", "libreoffice"]
    elif shutil.which("apt-get"):
        cmd = ["sudo", "apt-get", "install", "-y", "libreoffice"]
    elif shutil.which("dnf"):
        cmd = ["sudo", "dnf", "install", "-y", "libreoffice"]
    elif shutil.which("pacman"):
        cmd = ["sudo", "pacman", "-S", "--noconfirm", "libreoffice-fresh"]
    else:
        log("No package manager found. Get it from https://www.libreoffice.org/download/")
        return None
    log("No converter present. Installing LibreOffice: " + " ".join(cmd))
    subprocess.run(cmd, check=False)
    return find_soffice()


# ---------- conversion routes ----------

PS_CONVERT = r"""
param($In, $Out)
$si = [IO.Path]::GetExtension($In).ToLower()
function Fin($a){ try { $a.Quit() } catch {}; [Runtime.InteropServices.Marshal]::ReleaseComObject($a) | Out-Null }
if ($si -eq '.pdf') {
  $w = New-Object -ComObject Word.Application; $w.Visible=$false; $w.DisplayAlerts=0
  $d = $w.Documents.Open($In,[ref]$false,[ref]$false,[ref]$false,[ref]"",[ref]"",[ref]$false)
  $d.SaveAs2($Out, 16); $d.Close([ref]0); Fin $w
} elseif ($si -in '.xlsx','.xls','.csv') {
  $x = New-Object -ComObject Excel.Application; $x.Visible=$false; $x.DisplayAlerts=$false
  $b = $x.Workbooks.Open($In); $b.ExportAsFixedFormat(0,$Out); $b.Close($false); Fin $x
} elseif ($si -in '.pptx','.ppt') {
  $p = New-Object -ComObject PowerPoint.Application
  $d = $p.Presentations.Open($In,$true,$false,$false); $d.SaveAs($Out,32); $d.Close(); Fin $p
} else {
  $w = New-Object -ComObject Word.Application; $w.Visible=$false; $w.DisplayAlerts=0
  $d = $w.Documents.Open($In,[ref]$false,[ref]$true); $d.ExportAsFixedFormat($Out,17); $d.Close([ref]0); Fin $w
}
"""


def via_office(src: Path, dst: Path) -> bool:
    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8") as f:
        f.write(PS_CONVERT)
        script = f.name
    try:
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                        "-File", script, str(src), str(dst)],
                       capture_output=True, text=True, timeout=300)
    finally:
        os.unlink(script)
    return dst.exists()


def via_soffice(exe: str, src: Path, dst: Path) -> bool:
    target = dst.suffix.lstrip(".")
    with tempfile.TemporaryDirectory() as td:
        subprocess.run([exe, "--headless", "--norestore", "--convert-to", target,
                        "--outdir", td, str(src)],
                       capture_output=True, text=True, timeout=300)
        produced = Path(td) / (src.stem + dst.suffix)
        if produced.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(produced), str(dst))
            return True
    return False


def mhtml_to_html(src: Path) -> str:
    """Pull the HTML part out of a MIME/MHTML container."""
    import email
    with open(src, encoding="utf-8", errors="replace") as fh:
        msg = email.message_from_file(fh)
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            payload = part.get_payload(decode=True)
            if payload is None:
                continue
            return payload.decode(part.get_content_charset() or "utf-8", errors="replace")
    raise ValueError("no text/html part in %s" % src)


def html_to_text(html: str) -> str:
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        text = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
        text = re.sub(r"(?s)<[^>]+>", "\n", text)
        return re.sub(r"\n{3,}", "\n\n", unescape(text)).strip()
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return re.sub(r"\n{3,}", "\n\n", soup.get_text("\n")).strip()


def via_mhtml(src: Path, dst: Path) -> bool:
    """MHTML in, html/txt/md/pdf out. PDF goes via a temp .html and the browser route."""
    html = mhtml_to_html(src)
    so = dst.suffix.lower()
    dst.parent.mkdir(parents=True, exist_ok=True)
    if so in (".html", ".htm"):
        dst.write_text(html, encoding="utf-8")
    elif so in (".txt", ".md"):
        dst.write_text(html_to_text(html), encoding="utf-8")
    elif so == ".pdf":
        exe = find_browser()
        if not exe:
            return False
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "page.html"
            tmp.write_text(html, encoding="utf-8")
            return via_browser(exe, tmp, dst)
    else:
        return False
    return dst.exists()


def via_browser(exe: str, src: Path, dst: Path) -> bool:
    subprocess.run([exe, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    "--print-to-pdf=" + str(dst), src.resolve().as_uri()],
                   capture_output=True, text=True, timeout=180)
    # The browser finishes writing after the process returns, and a page with remote
    # assets can take seconds. Checking immediately reports a working conversion as a
    # failure — wait for the file to appear and stop growing.
    last, stable = -1, 0
    for _ in range(60):
        if dst.exists():
            size = dst.stat().st_size
            if size > 0 and size == last:
                stable += 1
                if stable >= 2:
                    return True
            else:
                stable = 0
            last = size
        time.sleep(0.25)
    return dst.exists() and dst.stat().st_size > 0


# ---------- driver ----------

def done(dst: Path, how: str):
    print("OK  {}  ({} bytes, via {})".format(dst, dst.stat().st_size, how))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--no-install", action="store_true",
                    help="fail rather than installing LibreOffice")
    a = ap.parse_args()

    src, dst = Path(a.src).resolve(), Path(a.dst)
    if not src.exists():
        sys.exit("No such file: {}".format(src))
    dst.parent.mkdir(parents=True, exist_ok=True)
    si = src.suffix.lower()

    # Sniff before trusting the extension. A Confluence or Outlook export named .doc is
    # MHTML, and handing it to Word gets you "not a valid document" for a readable file.
    actual = real_format(src)
    if actual == "mhtml":
        if via_mhtml(src, dst):
            return done(dst, "MHTML extraction")
        sys.exit("%s is MHTML. Supported targets are .html, .txt, .md and .pdf; "
                 "%s failed%s." % (src.name, dst.suffix,
                                   " (no browser found for PDF)" if dst.suffix.lower() == ".pdf"
                                   and not find_browser() else ""))
    if actual == "html" and si not in BROWSER_IN:
        si = ".html"

    if si in BROWSER_IN:
        browser = find_browser()
        if browser and via_browser(browser, src, dst):
            return done(dst, "browser")

    # Office only truly serves two targets. Asked for anything else it silently exports a PDF
    # under the requested name, so the route must be gated on the destination, not the source.
    so = dst.suffix.lower()
    office_route = ((si in OFFICE_IN and so == ".pdf")
                    or (si == ".pdf" and so in (".docx", ".doc")))
    if office_route and has_office_com() and via_office(src, dst):
        return done(dst, "Microsoft Office")

    exe = find_soffice()
    if not exe and not a.no_install:
        exe = install_libreoffice()
    if exe and via_soffice(exe, src, dst):
        return done(dst, "LibreOffice")

    sys.exit("Could not convert {} -> {}. No usable converter.".format(si, dst.suffix))


if __name__ == "__main__":
    main()
