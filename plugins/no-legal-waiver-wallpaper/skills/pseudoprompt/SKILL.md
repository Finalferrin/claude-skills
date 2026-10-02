---
name: pseudoprompt
description: Use when the user asks for a message, paragraph or brief to be turned into a prompt for another agent — "make this a prompt", "pseudocode this", "turn this into a prompt", "write me the prompt for Claude / Codex", or /pseudoprompt — and wants it as a copy-paste block. Not for a long ask on its own; a long paragraph with no such request is work to do, not a prompt to convert.
---

# Pseudoprompt

**The block carries what the paragraph said, in code shape, and nothing else.**

A prose instruction leaves the receiving agent deciding where each step applies. A closed
conditional does not. That is the whole gain, and it is lost the moment the block says
something the author did not: the receiving agent cannot tell the author's words from the
converter's, so every addition becomes an instruction nobody gave.

## The two surfaces

**REQUIRED SUB-SKILL:** no-legal-waiver-wallpaper. The block is a written deliverable; it is
read by another agent, not by the person who asked.

| Surface | Carries |
|---|---|
| The block | What the paragraph said, section by section below |
| On screen, under the block | Gaps as questions, how an unclear word was read, typo readings, anything that would not fit a section. One line each. Not a restatement of the block. |

## The block

One fenced block. Plain text, not JSON. These sections, in this order. A section with nothing
in the paragraph to fill it is left out, heading and all.

```
PURPOSE
    one line: what done looks like, in the author's words

SCOPE
    IN   what the paragraph names as the job
    NOT  what the paragraph says is not the job, or is for later

VOCABULARY
    the author's names for things an agent could rename or has to find: products, folders,
    files, fields, features, the author's own coinages; one per line, spelled as the author
    spelled them (typos fixed); not every noun
    names only, no definitions; the receiving agent uses these names and no others
    a term the paragraph does not name is not here, whatever it is called elsewhere

EXCLUSIONS
    NEVER <each "not", "don't", "never", "only" in the paragraph, one per line>
    these sit before the steps so no step can override one
    NEVER lines only; a reason or a note is not an exclusion

STEPS
    FIRST  <action>
    THEN   <action>
    STOP WHEN <the author's stopping condition>
    one action per line, in the author's order
    reason: <the author's reason for a step, kept under that step>
    IF <condition>:
        <what the paragraph says happens then>

OUTPUT
    what the receiving agent hands back, and in what form (file, block, list, plan)
```

**Keywords.** Capitals for logic: IF, THEN, NEVER, ALWAYS, BEFORE, AFTER, WHEN, FIRST, STOP.
One rule per line. Indent what belongs under a condition. Lower case for the author's words.

**Gaps.** Where a step needs a value the paragraph does not give, write
`<PLACEHOLDER NAME>` in the block and put the question that fills it on screen. A placeholder
stands in for a value; a line or section the paragraph has nothing for is left out, not
placeholdered. No STOP WHEN if the author gave no stopping point; no OUTPUT if the author did
not say what comes back. A reasonable
default is still an invention: if a question is on screen, the thing it asks about is a
placeholder in the block, not a guess. The author's standing rules from CLAUDE.md, memory or
earlier chats are not in the paragraph; the receiving agent has its own copy of those.

**This skill is not in the block.** The section names, the keywords and the method on this
page are the converter's, not the author's. A line that describes how to convert a prompt,
or defines a term by this page's sections, is leakage. The author's paragraph is the only
source.

**Rules, not a task.** If the paragraph is how to behave rather than what to produce, there
are no sections. Write the flat form: IF / NEVER / ALWAYS / BEFORE, one rule per line,
indented under its condition.

## Before and after

Paragraph:

> read every page in full, not the summaries, and find anything on billing. don't touch
> the invoices folder. i want a list of what you found with the page each one came from.

> ❌ `PHASE 1: Research. Read all relevant pages thoroughly. Extract billing-related
> findings and categorise by theme. PHASE 2: Synthesise. DELIVERABLE: structured report with
> recommendations.`

> ✅
> ```
> PURPOSE
>     a list of everything on billing, with the page each item came from
>
> EXCLUSIONS
>     NEVER read a summary in place of the page
>     NEVER touch the invoices folder
>
> STEPS
>     FIRST  open every page in full
>     THEN   note each item on billing and the page it is on
>
> OUTPUT
>     a list: item, page
> ```

Categorise, synthesise, themes, recommendations: none of it was said, so none of it is in
the block.

## Before handing it over

Two passes, both directions.

1. **Paragraph to block.** Read the paragraph one sentence at a time and point to the line in
   the block each sentence became. A sentence with no line is missing content; add it.
2. **Block to paragraph.** Read the block one line at a time and point to the words in the
   paragraph it came from. A line with no source either comes out or becomes a
   `<PLACEHOLDER>` with its question on screen.

Two lines fail pass 2 every time, so check for them by name:

- A line whose content uses one of this page's section names (PURPOSE, SCOPE, VOCABULARY,
  EXCLUSIONS, STEPS, OUTPUT) or keywords as a thing the author asked for. Leakage. Out.
- A line that states, as fact, the thing an on-screen question asks about. The question
  proves the paragraph did not say it. The line becomes the `<PLACEHOLDER>`.
- A line whose source, if asked, is "memory", "CLAUDE.md", "earlier chats" or "what the
  author usually means". Not the paragraph. The line becomes the `<PLACEHOLDER>`.

Then hand it over: the block itself, in the message, not a description of it.
