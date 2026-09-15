---
name: no-legal-waiver-wallpaper
description: Use before writing anything that will be read outside this chat — a document, report, memo, deck, PR description, commit message, README, code comment, email, or any file handed to another person — and again before calling it finished. Not for replies in chat.
---

# No legal waiver wallpaper

**A written deliverable carries what was asked for and nothing else.** Doubt, caveats and pushback go to the person who asked, in chat, before the file is written. Once written, the document argues for the decision or says nothing.

## Why

The reader is paid to make the decision. A "Critical Caveat" section, a "treat as directional", a "proceed only if" tells them the author did not read their own work before sending it, and hands any reviewer a prepared reason to reject it. A team that already knows a model is a model does not need it said four times.

## The two surfaces

| Surface | Doubt, caveats, pushback |
|---|---|
| Chat with the person who asked | Say it. All of it. Before the file exists. |
| Anything written for someone else to read | Not on the page. |

## What the page contains

Every sentence is one of: a claim the given facts support, a number from those facts, a source, a decision, a step. A number the facts do not contain is not on the page.

A limitation the reader needs is **one sentence of fact, in the place the fact lives**: the basis-of-calculation table, the data section, or the next step that resolves it. It is not a heading, not a paragraph, not a condition on the decision, and not the last thing on the page. The document ends on the decision or the next step.

If the owner asked for a disclaimer or the document type requires regulatory text, it goes in as asked.

## Before and after

Same two facts. The first is wallpaper; the second is the page.

> ❌ **Critical Caveat.** These figures are modeled from your service architecture, not measured from actual production prompts. Luna has not been run against your classifier accuracy set. A 45% cost win is only real if Luna maintains your current classification performance. Schedule accuracy testing before switchover.

> ✅ Token counts are modelled from the service architecture (Appendix A). Next steps: 1. Run Luna against the classifier accuracy set. 2. Canary the switch for two weeks.

## Wallpaper: if it is on the page, take it off

- A section headed Caveats, Limitations, Disclaimer, Risks, Assumptions, What to Verify First. (A parameter table is a table, not a section of prose.)
- "should be noted", "it is important to", "treat as directional", "not a substitute for", "may vary", "further testing is required", "we cannot guarantee", "consult".
- A limitation stated twice.
- A limitation as the condition on the decision: "only real if", "proceed only if", "meaningless unless", "defer until".
- A sentence that restates the previous one as its consequence: "which means", "and that's why", "in other words".
- A closing that reopens the question: "it's a fair question whether", "happy to move it", "some might argue", "might not be the right".
- "roughly", "approximately", "about" on a figure the document itself computed.

The fact under each one either already sits somewhere on the page as a fact, or it goes to the chat. The sentence goes either way.

## Before calling it finished

Read the page once as the recipient. Every sentence that is not a supported claim, a given number, a source, a decision or a step comes off. Then send.
