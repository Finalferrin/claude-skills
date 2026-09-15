# agent-skills

Portable agent skills for Claude Code and Codex. Claude Code can install this repository as a
plugin marketplace; Codex uses the same `SKILL.md` and scripts as a native local skill.

## Install

### Claude Code

**Two commands:**

```
/plugin marketplace add Finalferrin/claude-skills
/plugin install toolup@claude-skills
/plugin install no-legal-waiver-wallpaper@claude-skills
```

That's it. Same mechanism as any other plugin — it stays up to date and uninstalls cleanly.

### Codex

Clone the repository, then run the installer for Codex:

```powershell
git clone https://github.com/Finalferrin/claude-skills
Set-Location claude-skills
.\install.ps1 -Target Codex
```

That copies each skill to `%USERPROFILE%\.codex\skills\`. Start a new Codex task after
installation so its skill catalog refreshes. Codex installations managed by an organization may
use a different configured skill directory; use that directory when one is provided.

<details>
<summary>Other ways, if the marketplace isn't an option</summary>

**Clone and run the installer**

```bash
git clone https://github.com/Finalferrin/claude-skills
cd claude-skills
./install.sh --target both          # Windows: .\install.ps1 -Target Both
```

**Or by hand** — drop `plugins/toolup/skills/toolup` into either:

| Agent | Windows | macOS/Linux |
|---|---|---|
| Claude Code | `%USERPROFILE%\.claude\skills\toolup` | `~/.claude/skills/toolup` |
| Codex | `%USERPROFILE%\.codex\skills\toolup` | `~/.codex/skills/toolup` |

Start a new session or task after manual installation.
</details>

Requires Python 3.9+. Everything else the skill installs for itself. Windows, macOS, Linux.

---

## `toolup`

**Stops an agent handing you homework.**

You ask for a document as a PDF. It tells you to install LibreOffice. Or to open it in Word and
save it yourself. Or that some tool isn't available, followed by a clunky workaround.

You asked for a file. You got a to-do list.

### What changes

**Documents just convert.** docx, xlsx, pptx, odt, rtf, md and html → PDF, and PDF → docx.
Drives Office headlessly if present, LibreOffice if not, a browser for HTML — and installs
LibreOffice itself if none exist. No window opens, no dialog appears, nothing lands in your
recent files.

**"Not installed" gets checked before it's claimed.** Plenty of programs install somewhere PATH
never learns about, and that's where most false "you don't have X" reports come from. On the
machine this was built on, three programs — Tesseract, 7-Zip and Make — were installed, working,
and being reported as missing.

**Free tools get installed, not requested.** jq, ripgrep, fd, ffmpeg, ImageMagick, Tesseract,
pandoc, sqlite3, 7-Zip, wget, make, Go, Java, Rust, plus the usual Python stack — silently, via
winget, brew, apt, dnf or pacman.

**Scans get read, not described.** `ocr.py` turns images and scanned PDFs into text — and it
doesn't use whichever Python you happen to be running. It surveys every interpreter on the
machine and picks the one with the best OCR engine, because on the machine this was built on the
newest engine available for the default interpreter **silently dropped isolated single digits**.
It read multi-digit numbers perfectly and lost every lone `3` and `2` in a table. So did
Tesseract. Only an older engine on an older interpreter read them all. On an invoice or a census
page that's a wrong figure that reads as correct, and nothing errors.

**File extensions get checked, not believed.** Confluence and Outlook both export MHTML with a
`.doc` extension. Handed to Word that's "not a valid Word document" — for a file that is
perfectly readable HTML. `convert.py` sniffs the bytes and routes it properly.

**Anything with a signup stops and tells you the truth first.** `wrangler`, `gh`, `aws` and
`gcloud` are never installed quietly. You get the real signup steps, including — stated plainly —
whether a payment card is required. **AWS and Google Cloud both want one even on their free
tiers.** Cloudflare and GitHub don't.

### Rules it holds an agent to

- Never "you'll need to install X" — install it, or use what's already there
- Never ask you to open an app and click through a dialog
- Never ask you to run a command it could run itself
- Never finish the job then tack on "by the way, you might want to fix your PATH" — same
  offload, politer wording
- Tell a genuinely missing thing apart from a connector that's merely unauthenticated or
  failing to connect. A broken GitHub integration costs nothing while the `gh` CLI works
- Ask once which shell you actually use, then stop mixing PowerShell and bash syntax at you
- Never write a file with a shell heredoc — it fails silently often enough to look like it worked

### Direct use

The skill runs itself, but the scripts work standalone:

```bash
python plugins/toolup/skills/toolup/ensure.py --plan     what's missing and what each gap costs
python plugins/toolup/skills/toolup/ensure.py --all      install every free, account-free tool
python plugins/toolup/skills/toolup/convert.py in.docx out.pdf
python plugins/toolup/skills/toolup/ocr.py scan.pdf out.txt
python plugins/toolup/skills/toolup/ocr.py --which       what OCR this machine has
```

### When OCR beats just looking at the image

A model can read an image directly, and for "what is this document" that's the right call. OCR
earns its place when the text is **evidence** — invoices, statements, records, anything whose
numbers end up in a file or a citation. Same input gives identical output every time, it can be
re-run and diffed, it scales to hundreds of pages, and it never leaves the machine. A figure read
off an image and typed out is an assertion with no provenance; if it's wrong, nobody can tell by
looking at it.

## Licence

MIT.
