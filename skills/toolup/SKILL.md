---
name: toolup
description: Use when a task needs a CLI tool, library, program, font, converter or connector and you are about to say it is missing, unavailable, not installed, or unsupported — or before proposing a workaround, a fallback, a manual method, or asking the user to install or run anything. Also use before converting any document (docx/xlsx/pptx/pdf/html), before writing a file with a shell heredoc, and at the start of any terminal, scripting, data, image, audio or video task.
---

# Tool up

**Go and get it. Do not file a request with the human.**

The failure this exists to stop: hitting a gap, announcing it, and handing the user a shopping
list — when the thing is already installed somewhere you didn't look, or is a free download you
could have fetched in the time it took to write the complaint.

The user asked for a result. A list of software they now have to go and install is not a result.

## Order of operations

1. **Look properly.** Not just PATH. See *Not on PATH is not missing*.
2. **Get the free ones.** No account, no card, no permission. Just install them.
3. **Disclose the rest.** Anything needing a login or a card gets its signup and login steps
   printed in full, then stops for the human to decide.
4. **Only then** a workaround, and label it as one.

## Finding and installing

```
python skills/toolup/ensure.py --plan     what's missing, and what each gap costs
python skills/toolup/ensure.py --all      install every free, account-free tool
python skills/toolup/ensure.py --python   install the missing Python packages
python skills/toolup/ensure.py jq ffmpeg  install specific ones
```

Free and account-free — `jq`, `fd`, `rg`, `sqlite3`, `pandoc`, `7z`, `ffmpeg`, ImageMagick,
`tesseract`, `wget`, `make`, Go, Java, Rust — install silently via winget / brew / apt / dnf /
pacman. None of it costs money, so none of it needs asking.

**Account-gated tools are never installed silently.** `wrangler`, `gh`, `aws`, `gcloud` each
print what signing up actually involves — in plain words, including whether a payment card is
required — and then stop. AWS and Google Cloud demand a card even on their free tiers. Say that
before the human is halfway through a signup form, not after.

## Converting documents

```
python skills/toolup/convert.py IN OUT
```

Tries, in order: **Microsoft Office over COM** (Windows, headless, best fidelity, already on
most work machines) → **LibreOffice** → **a Chromium browser** for html→pdf → and if none of
those exist, **installs LibreOffice and carries on**.

| From | To |
|---|---|
| docx, doc, rtf, odt, txt, md | pdf |
| xlsx, xls, csv, ods | pdf |
| pptx, ppt, odp | pdf |
| pdf | docx |
| html, htm | pdf — needs no office suite at all |

No window opens, no dialog appears, nothing lands in the user's recent files.

- **Never say "you'll need LibreOffice / Acrobat / pandoc".** Install it or use what's there.
- **Never ask the user to open an application and click Save As.** Every route is headless.
- **Never complain about the format.** Legacy `.doc`, merged cells, scanned PDFs — that's the job.
- Route missing? Add it to `convert.py`. Do not hand the user a task.

## Not on PATH is not missing

Plenty of installers put a working program somewhere PATH never learns about. `command -v`
returning nothing proves nothing, and the honest-looking conclusion — "not installed, shall I
install it?" — is simply wrong.

In one session this misfired three times on one machine: Tesseract in `Program Files\Tesseract-OCR`,
7-Zip in `Program Files\7-Zip`, and `make` under GnuWin32. All three installed, all three working,
all three reported absent.

Check the package manager's own directories and the usual install locations before concluding
anything. `ensure.py` does this in `resolve()`; extend `OFF_PATH` when a new one turns up. Found
it off PATH? Add its directory to PATH so it just works next time — then finish the actual task.

## Never trust find_spec, and always name the interpreter

`importlib.util.find_spec()` reports packages installed into the **user** site-packages as
missing whenever that directory is off `sys.path` — and whether it is on `sys.path` can differ
between two shells on the same machine running the same `python`. Import the module for real.

Where several interpreters are installed, "is X installed?" has no single answer. Any claim
about a package names the interpreter it was checked against, or it is not a claim.

## Ask which shell, once, and write it down

Commands the human runs must match the shell they actually use. Ask at the first opportunity,
record the answer in their instructions file, and never mix syntax again. Bash-isms handed to a
PowerShell user — `$VAR`, forward-slash paths, `export`, `2>/dev/null`, `grep` — are defects.

What you use for your own tool calls is your business; they never see those.

## Never use a heredoc to write a file

Use the file-writing tool. Always.

A heredoc crosses JSON encoding, the tool's shell invocation and the shell's own parser — three
chances for a quote or backslash to break it, and it fails silently enough that you believe the
file was written when nothing ran at all. **No size exception. Not for four lines.**

## "Missing" has four flavours — say which one

| Symptom | Reality | Action |
|---|---|---|
| Tool absent from your tool list | **Deferred** — schema unloaded, tool is live | Load it. Never call it unavailable. |
| Server listed as needing auth | **Unauthenticated** — capability exists, no token | Name it; say where authorization happens. |
| Server listed as failed to connect | **Broken** — configured, unreachable | Name the server and the error, then check whether a CLI covers the same ground. |
| `command not found` | **Absent — maybe** | Check off-PATH locations first. Then install it. |

A broken connector is not a missing capability. A CLI often covers the same API using
credentials the machine already holds — a dead GitHub connector costs nothing while `gh` works.

## Migrating between interpreters or toolchains

Install into the destination and verify it before removing the source. Then sweep everything
that depends on the old one — venvs, shebangs, hardcoded paths, scheduled tasks, IDE settings,
`.bat` and `.ps1` wrappers — and update each as the new one moves in. Flipping PATH first and
discovering the breakage afterwards is how a working machine becomes a broken one.

## Red flags — stop

- "You'll need to install …" — install it yourself
- "Open it in Word and save as PDF" — automate it
- Asking the human to run a command you could run
- "X isn't available, so instead I'll…"
- "I don't have access to Y" — did you check the deferred list?
- Finishing the task, then adding "by the way, you may want to fix your PATH" — same offload,
  politer coat
- Writing a heredoc to create a file

## Not for

Deciding whether to *pay* for something, or installing anything that needs an account — those
stop at disclosure. Free software is yours to fetch; anything with a login is the human's call.
Never change a machine's configuration beyond what the task needs.
