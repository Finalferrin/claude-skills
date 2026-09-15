---
name: toolup
description: Use when a task needs a CLI tool, library, program, font, converter or connector and you are about to say it is missing, unavailable, not installed, or unsupported — or before proposing a workaround, a fallback, a manual method, or asking the user to install or run anything. Also use before converting any document (docx/xlsx/pptx/pdf/html), before reading a scan, photo or a PDF whose pages have no text layer, before typing out any figure you can only see in an image, when a file will not open or looks corrupt or has the wrong extension, before writing a file with a shell heredoc, and at the start of any terminal, scripting, data, image, audio or video task.
---

# Tool up

**Go and get it. Do not file a request with the human.**

## Agent runtime mapping

This is a portable instruction file for Claude Code and Codex. The operating rules below apply
to both. Use the current host's tool catalog and visible schema as authority for exact tool names,
parameters, persistence, and permissions; never copy a Claude-specific tool name into Codex or
the reverse.

| Need | Claude Code | Codex |
|---|---|---|
| Personal skill location | `~/.claude/skills/<name>` | `~/.codex/skills/<name>` |
| Plugin marketplace | This repository can be installed as a Claude plugin | Use the local skill directory; a Claude plugin manifest is not a Codex installation method |
| Tool absent from the visible list | It may be deferred or require its schema to be loaded | It may be deferred, unavailable for this host, or require its schema to be loaded |
| Writing a workspace file | Use the host's file-editing facility | Use the host's file-editing facility (normally `apply_patch`) |
| Free installation or configuration change | Proceed only within the host's permission model | Proceed only within the host's permission model; request an approval when the host requires it |

For either agent, a visible tool schema and the host's permission boundary outrank any general
wording in this skill. A permission prompt is not a reason to call a free tool unavailable or to
hand the work back to the user.

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
| mhtml saved as .doc (Confluence, Outlook) | html, txt, md, pdf — detected by content, not name |

No window opens, no dialog appears, nothing lands in the user's recent files.

- **Never say "you'll need LibreOffice / Acrobat / pandoc".** Install it or use what's there.
- **Never ask the user to open an application and click Save As.** Every route is headless.
- **Never complain about the format.** Legacy `.doc`, merged cells, scanned PDFs — that's the job.
- Route missing? Add it to `convert.py`. Do not hand the user a task.

## Reading a scan — never transcribe by eye

```
python skills/toolup/ocr.py IN [OUT]     image or PDF -> text
python skills/toolup/ocr.py --which      what OCR this machine has, and what it would use
```

**When to reach for it**

1. A PDF opens but `get_text()` returns nothing or near-nothing on a page — that page is an
   image of text, not text. OCR it. Do not report the document as empty or unreadable.
2. The input is a photo, a screenshot, a scan, a fax, a `.tif`.
3. You are about to read numbers, names or dates off an image and type them out yourself.
   **Don't.** Run the OCR and use its output.

**Never retype what you can see in an image.** Reading a figure off a screenshot and typing it
into a file, a table or a matrix row is a transcription with no record of where it came from,
and a single wrong digit is invisible afterwards. Run the OCR, use its text, and say which
engine produced it when the number matters.

**Say what OCR is and is not.** OCR output is `Derived` material — a reproducible transformation
of a source, never the source itself. Cite the original file alongside it. If a figure looks
wrong, go back to the image; never "correct" OCR output silently into a record.

### Why OCR and not just looking at the image

You can read an image directly. For some jobs that is fine and faster. For others it is the
wrong instrument, and the difference is not about capability — it is about what kind of claim
the output can support.

| | Reading it yourself | `ocr.py` |
|---|---|---|
| Same input twice | may differ | identical, every time |
| A figure you report | your reading of it | a transcript that can be re-run and diffed |
| Wrong value | looks exactly like a right one | still possible, but reproducible and checkable |
| 400 pages | not realistically | a loop |
| Sensitive records | goes through a model | stays on the machine |
| Reading order in a table | inferred | derived from box coordinates |

**Use OCR when the text is evidence.** Records, invoices, statements, census pages, transcripts,
anything whose numbers or names end up in a file, a table or a citation. The value of OCR is not
that it reads better — often it reads worse — it is that its output is a *transformation with a
method*, which can be re-run, compared and audited. A figure you read off an image and typed is
an assertion with no provenance, and if it is wrong nobody can tell by looking.

**Read it yourself when the question is about the image, not the text in it.** What kind of
document is this, is it signed, is the seal present, which of these three scans is legible,
what is this diagram showing. Also handwriting — print-oriented OCR is poor at it, and your
own reading is usually better, though it should be marked as a reading, not a transcript.

**Best on a hard page: do both.** OCR for the verbatim text, your own reading to catch where the
OCR clearly went wrong. Say which is which. Never quietly edit OCR output into what you think it
should say — that produces a transcript nobody can trust and no way to tell which parts are
machine-read.

### The engine matters more than it looks

`ocr.py` does not use the interpreter you happen to be running. It surveys every Python on the
machine, finds which can run an OCR engine, and shells out to the one with the highest
`rapidocr` version anywhere — because on one machine the newest version with a wheel for the
default interpreter **silently dropped isolated single digits**. It read multi-digit numbers
perfectly and lost every lone `3` and `2` in a table. Tesseract dropped the same digits. Only an
older `rapidocr` on an older interpreter read them all.

On a spreadsheet that is a curiosity. On a census page, a probate record or an invoice, it is a
wrong fact that reads as correct, and nothing errors.

**So: a capability that only works under an older interpreter is pinned, not dropped.** Keeping
a second Python alive to host a working engine is the right trade, and "simplifying" by moving
the capability onto the newest interpreter is a downgrade wearing the clothes of a cleanup.
`TOOLUP_OCR_PYTHON` overrides the choice; `--which` shows what would be used and why.

## The extension is not the format

Sniff the bytes before believing the name. Exports lie constantly: Confluence and Outlook both
save **MHTML with a `.doc` extension**, and handing one to Word gets "not a valid Word document"
for a file that is perfectly readable HTML. `convert.py` checks the magic bytes first and routes
MHTML to `.html`, `.txt`, `.md` or `.pdf`.

The general rule: when a file will not open, check what it actually is before telling anyone it
is corrupt, unsupported, or the wrong type. "This isn't a real Word file" is true and useless;
"this is a Confluence export, here is the text" is the answer.

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
| Tool absent from your tool list | **Deferred or host-specific** — its schema may be unloaded, or the current host may not provide it | Inspect the current tool catalog and load its schema when available. Do not call it unavailable without checking. |
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

## Anything published under the user's name gets only what was asked for

This skill produces outward-facing text — PR descriptions, marketplace entries, commit
messages, install docs — that appears under the user's identity, often at their employer.
Write what the thing is, how to use it, and what a reviewer needs to check. Nothing else.

**Never volunteer a case against the user's own change.** A section wondering whether this is
really the right repo, whether it fits, whether someone might object — nobody asked for it, and
it hands a reviewer the reason to say no. It reads as candour and functions as sabotage.

Doubts about scope or fit go to the user, in chat, before the thing is published. Once they have
decided, the artefact argues for the decision or stays silent. If a genuine caveat must appear —
a real limitation a reviewer needs — state it as a fact under review notes, never as an invitation
to reconsider.

The same applies to install docs and wiki pages: describe what it does, not your reservations
about whether it belongs.

## Red flags — stop

- "You'll need to install …" — install it yourself
- "Open it in Word and save as PDF" — automate it
- Asking the human to run a command you could run
- "X isn't available, so instead I'll…"
- "I don't have access to Y" — did you check the deferred list?
- "This PDF appears to be empty / is a scan and can't be read" — OCR it
- Typing out a number, name or date you can only see in an image — OCR it
- "This isn't a valid Word document" — check what the bytes actually say it is
- Writing "it's a fair question whether…" into a PR, doc or page the user is publishing
- Finishing the task, then adding "by the way, you may want to fix your PATH" — same offload,
  politer coat
- Writing a heredoc to create a file

## Not for

Deciding whether to *pay* for something, or installing anything that needs an account — those
stop at disclosure. Free software is yours to fetch; anything with a login is the human's call.
Never change a machine's configuration beyond what the task needs.
