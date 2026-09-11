# claude-skills

Portable skills for Claude Code, distributed as a plugin marketplace.

## Install

**In Claude Code, two commands:**

```
/plugin marketplace add Finalferrin/claude-skills
/plugin install toolup@claude-skills
```

That's it. Same mechanism as any other plugin — it stays up to date and uninstalls cleanly.

<details>
<summary>Other ways, if the marketplace isn't an option</summary>

**Clone and run the installer**

```bash
git clone https://github.com/Finalferrin/claude-skills
cd claude-skills
./install.sh          # Windows: powershell -NoProfile -File install.ps1
```

**Or by hand** — drop the folder `plugins/toolup/skills/toolup` into `~/.claude/skills/`
(`%USERPROFILE%\.claude\skills\` on Windows). Nothing to configure.

Claude picks skills up on the next session.
</details>

Requires Python 3.9+. Everything else the skill installs for itself. Windows, macOS, Linux.

---

## `toolup`

**Stops Claude handing you homework.**

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

**Anything with a signup stops and tells you the truth first.** `wrangler`, `gh`, `aws` and
`gcloud` are never installed quietly. You get the real signup steps, including — stated plainly —
whether a payment card is required. **AWS and Google Cloud both want one even on their free
tiers.** Cloudflare and GitHub don't.

### Rules it holds Claude to

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
```

## Licence

MIT.
