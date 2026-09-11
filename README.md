# claude-skills

Portable skills for Claude Code. Each one lives in `skills/<name>/` with a `SKILL.md` and
whatever scripts it needs.

## Skills

### `toolup`

Stops Claude handing you a shopping list instead of a result.

When a task needs a tool that isn't there, the default behaviour is to announce the gap and
propose a workaround — or to ask you to go and install something. `toolup` replaces that with:
look properly, install the free thing silently, and only stop for things that need an account
or a payment card.

It covers three failures that look different and are the same:

- **"You need to install LibreOffice."** No. Office automates headlessly over COM, LibreOffice
  installs itself in a single command, and a Chromium browser handles html→pdf with no office
  suite at all. `convert.py` tries all of them in order and installs one if none exist.
- **"That isn't installed."** Often it is, just not on PATH. Tesseract, 7-Zip and `make` were
  all reported missing on a machine where all three worked. `ensure.py` checks the package
  manager's directories and the usual install locations before concluding anything.
- **"Open it in Word and save as PDF."** Every conversion route here is headless. No window,
  no dialog, nothing in your recent files.

```
python skills/toolup/ensure.py --plan       what's missing and what each gap costs
python skills/toolup/ensure.py --all        install every free, account-free tool
python skills/toolup/convert.py in.docx out.pdf
```

Account-gated tools — `wrangler`, `gh`, `aws`, `gcloud` — are never installed silently. They
print what signing up actually involves, including whether a card is required, then stop. AWS
and Google Cloud both want a card even on their free tiers.

## Install

Copy the skill folders into your personal skills directory:

**Windows (PowerShell)**

```powershell
Copy-Item -Recurse -Force .\skills\* "$env:USERPROFILE\.claude\skills\"
```

**macOS / Linux**

```bash
cp -r skills/* ~/.claude/skills/
```

Or run `install.ps1` / `install.sh` from the repo root, which does the same thing and tells you
where it put them.

Claude picks skills up on the next session.

## Requirements

Python 3.9+. Everything else the skills install for themselves.

Windows, macOS and Linux. Office automation is Windows-only; elsewhere the conversion routes
fall through to LibreOffice, which installs itself if absent.

## Licence

MIT.
