#!/usr/bin/env python3
"""
Read text out of images and scanned PDFs.

    python ocr.py IN [OUT] [--which] [--engine rapidocr|tesseract]

IN may be an image (png/jpg/tif/bmp/webp) or a PDF. With no OUT, text goes to stdout.

WHY THIS SCRIPT EXISTS SEPARATELY FROM convert.py
-------------------------------------------------
The best OCR engine available is often not installed under the interpreter you are
currently running. On one machine the newest rapidocr with a wheel for Python 3.13
silently dropped isolated single digits — it read a table's multi-digit numbers
perfectly and lost every lone "3" and "2". Tesseract 5.5.3 dropped the same digits.
Only rapidocr 1.4.4, which had no 3.13 wheel and lived on an older 3.11, read them all.

On a spreadsheet that is a curiosity. On a census page, a probate record or an invoice,
a dropped digit is a wrong fact that reads as correct — the worst failure an OCR engine
can have, because nothing errors.

So this script does not assume the current interpreter. It looks at every Python on the
machine, finds which ones can run an OCR engine, prefers the highest rapidocr version it
finds anywhere, and shells out to that interpreter. Pin the capability; do not drop it
because the default interpreter cannot host it.

Override with TOOLUP_OCR_PYTHON=<full path to python> if you know which one you want.
"""
import argparse
import glob
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

WIN = platform.system() == "Windows"
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}

PROBE = (
    "import json\n"
    "out={'rapidocr':None,'tesseract':False}\n"
    "try:\n"
    "    import rapidocr_onnxruntime as r\n"
    "    v=getattr(r,'__version__',None)\n"
    "    if v is None:\n"
    "        try:\n"
    "            from importlib.metadata import version\n"
    "            v=version('rapidocr-onnxruntime')\n"
    "        except Exception: v='unknown'\n"
    "    out['rapidocr']=v\n"
    "except Exception: pass\n"
    "try:\n"
    "    import pytesseract; out['tesseract']=True\n"
    "except Exception: pass\n"
    "print(json.dumps(out))\n"
)


def candidate_interpreters():
    """Every python on this machine, not just the one running us."""
    seen, out = set(), []

    def add(p):
        if p and os.path.exists(p) and p.lower() not in seen:
            seen.add(p.lower())
            out.append(p)

    add(os.environ.get("TOOLUP_OCR_PYTHON"))
    add(sys.executable)
    for name in ("python", "python3"):
        add(shutil.which(name))
    if WIN:
        try:
            listing = subprocess.run(["py", "-0p"], capture_output=True, text=True, timeout=30)
            for line in listing.stdout.splitlines():
                for token in line.split():
                    if token.lower().endswith("python.exe"):
                        add(token.strip('"'))
        except Exception:
            pass
        local = os.environ.get("LOCALAPPDATA", "")
        for pat in (os.path.join(local, "Programs", "Python", "Python*", "python.exe"),
                    r"C:\Python*\python.exe"):
            for p in glob.glob(pat):
                add(p)
    else:
        for pat in ("/usr/bin/python3.*", "/usr/local/bin/python3.*",
                    "/opt/homebrew/bin/python3.*"):
            for p in glob.glob(pat):
                add(p)
    return out


def version_key(v):
    try:
        return tuple(int(x) for x in str(v).split(".")[:3])
    except Exception:
        return (0,)


def survey():
    """Which interpreters can do OCR, and with what."""
    found = []
    for exe in candidate_interpreters():
        try:
            r = subprocess.run([exe, "-c", PROBE], capture_output=True, text=True, timeout=120)
            info = json.loads(r.stdout.strip().splitlines()[-1])
        except Exception:
            continue
        if info.get("rapidocr") or info.get("tesseract"):
            found.append((exe, info))
    return found


def pick(found, engine=None):
    """Highest rapidocr anywhere wins; tesseract only if no rapidocr exists at all."""
    rapid = [(e, i) for e, i in found if i.get("rapidocr")]
    if engine != "tesseract" and rapid:
        rapid.sort(key=lambda t: version_key(t[1]["rapidocr"]), reverse=True)
        return rapid[0][0], "rapidocr", rapid[0][1]["rapidocr"]
    tess = [(e, i) for e, i in found if i.get("tesseract")]
    if tess:
        return tess[0][0], "tesseract", None
    return None, None, None


RUN_RAPID = r'''
import sys, json
from rapidocr_onnxruntime import RapidOCR
ocr = RapidOCR()
res, _ = ocr(sys.argv[1])
res = res or []
# sort into reading order: rows by top edge, then left to right within a row
def key(b):
    ys = [pt[1] for pt in b[0]]; xs = [pt[0] for pt in b[0]]
    return (round(min(ys) / 14), min(xs))
res.sort(key=key)
print(json.dumps([b[1] for b in res]))
'''

RUN_TESS = r'''
import sys, json, pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = sys.argv[2] or pytesseract.pytesseract.tesseract_cmd
print(json.dumps(pytesseract.image_to_string(Image.open(sys.argv[1])).splitlines()))
'''


def find_tesseract_exe():
    found = shutil.which("tesseract")
    if found:
        return found
    for c in (r"C:\Program Files\Tesseract-OCR\tesseract.exe",
              r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
              "/opt/homebrew/bin/tesseract", "/usr/local/bin/tesseract"):
        if os.path.exists(c):
            return c
    return ""


def ocr_image(exe, engine, image):
    if engine == "rapidocr":
        cmd = [exe, "-c", RUN_RAPID, str(image)]
    else:
        cmd = [exe, "-c", RUN_TESS, str(image), find_tesseract_exe()]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or "OCR failed").strip()[-400:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def pdf_pages_to_images(pdf, outdir, dpi=220):
    """Render PDF pages. Uses whichever interpreter has PyMuPDF, not necessarily ours."""
    code = ("import sys, pymupdf\n"
            "d = pymupdf.open(sys.argv[1])\n"
            "for i, pg in enumerate(d):\n"
            "    pg.get_pixmap(dpi=int(sys.argv[3])).save(sys.argv[2] + '/p%04d.png' % i)\n"
            "print(d.page_count)\n")
    for exe in candidate_interpreters():
        r = subprocess.run([exe, "-c", code, str(pdf), str(outdir), str(dpi)],
                           capture_output=True, text=True, timeout=600)
        if r.returncode == 0:
            return sorted(Path(outdir).glob("p*.png"))
    raise RuntimeError("No interpreter here has PyMuPDF, needed to render PDF pages. "
                       "Install it: python -m pip install PyMuPDF")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", nargs="?")
    ap.add_argument("dst", nargs="?")
    ap.add_argument("--which", action="store_true", help="show what OCR this machine has")
    ap.add_argument("--engine", choices=["rapidocr", "tesseract"])
    a = ap.parse_args()

    found = survey()

    if a.which or not a.src:
        if not found:
            print("No OCR engine found under any interpreter on this machine.")
            print("Install one:  python -m pip install rapidocr-onnxruntime")
            return
        for exe, info in found:
            bits = []
            if info.get("rapidocr"):
                bits.append("rapidocr " + str(info["rapidocr"]))
            if info.get("tesseract"):
                bits.append("pytesseract")
            print("%-70s %s" % (exe, ", ".join(bits)))
        exe, engine, ver = pick(found, a.engine)
        print("\nwould use: %s  (%s%s)" % (exe, engine, " " + str(ver) if ver else ""))
        return

    exe, engine, ver = pick(found, a.engine)
    if not exe:
        sys.exit("No OCR engine on this machine. Install one:\n"
                 "  python -m pip install rapidocr-onnxruntime")

    src = Path(a.src).resolve()
    if not src.exists():
        sys.exit("No such file: %s" % src)

    lines = []
    if src.suffix.lower() == ".pdf":
        with tempfile.TemporaryDirectory() as td:
            pages = pdf_pages_to_images(src, td)
            for n, page in enumerate(pages, 1):
                if len(pages) > 1:
                    lines.append("--- page %d ---" % n)
                lines.extend(ocr_image(exe, engine, page))
    elif src.suffix.lower() in IMAGE_EXT:
        lines.extend(ocr_image(exe, engine, src))
    else:
        sys.exit("Not an image or PDF: %s" % src.suffix)

    text = "\n".join(lines)
    if a.dst:
        out = Path(a.dst)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print("OK  %s  (%d chars, via %s%s on %s)"
              % (out, len(text), engine, " " + str(ver) if ver else "", exe))
    else:
        sys.stdout.write(text + "\n")


if __name__ == "__main__":
    main()
