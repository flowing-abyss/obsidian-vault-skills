---
description: >-
  For each [?] or [? <note>] marker — fetch the primary source for the original
  claim, check replication (balanced: failures and best positive evidence) and
  all relevant competing theories (quality over quantity, each with required
  URL), patch only affected sentences proportionally, and insert a collapsible
  callout. Status uses emoji icons (✅/⚠️/❌). Callout title states the original
  claim neutrally. Framing: three elements (what was measured, conceptual gap,
  bridging assumptions). Alternatives use **bold** for theory names, never
  brackets. Practical status: three elements (what is empirically supported with
  effect size, where the claim overreaches, correct framing going forward).
  Multi-item fields use <br> for one item per line. Every URL must point to a
  primary source. No calques for untranslatable terms.
---

Find every [?] or [? <note>] marker in the current note.
If a note is present, treat it as a specific doubt or research direction.

For each marker, run this pipeline:

1. FETCH
   Find the most authoritative primary source for the original claim:
   the study, document, or specification the claim is based on.
   Call web_fetch on the full page — not snippets.
   If paywalled, find an open alternative.

2. CONTEXTUALIZE
   If the source is an empirical study:

   a) REPLICATION — search "<author> replication" or "<theory> replication failure".
      Fetch the actual replication papers. Present a balanced picture:
      include both replication failures AND the strongest positive evidence
      (e.g. replications that found a small but significant effect under
      improved methodology). One-sided reporting distorts the epistemic status.
      Every study mentioned must have a working URL — no bare citations.

   b) ALTERNATIVES — search for all relevant competing theories or
      better-supported explanations of the same phenomenon.
      Do not target a fixed count — find every alternative that meaningfully
      changes the interpretation of the claim. Quality over quantity:
      each alternative must offer a genuinely different mechanism or
      prediction, not a minor variation. For each:
      - what mechanism does it propose
      - what does it predict differently from the original theory
      - what evidence supports it
      - link to a primary source [Title](URL) — required, no exceptions
      When naming theories: if no established term exists in the language of
      the note, use the original in quotes with a plain-language explanation.
      Do not invent calques.

   Skip 2a–2b for technical specs, legal sources, or primary documents.

3. ASSESS
   - ✅ CONFIRMED — source directly supports the claim as written
   - ⚠️ CORRECTED — source contradicts or meaningfully refines it
   - ❌ UNSOURCEABLE — no credible source found after 3+ attempts

4. PATCH the marked sentence/paragraph:
   - Remove the [?] marker
   - Rewrite only the sentences that contain or directly support the
     marked claim — leave the rest of the paragraph untouched
   - Keep the rewrite proportional to the original
   - Remove any qualifiers not present in the source
   - If epistemic status is contested or failed: add a brief hedge
     in the paragraph — one clause, e.g. "хотя результаты воспроизводятся
     нестабильно". The callout is for detail; the paragraph must not
     misrepresent certainty on a quick read
   - Move supporting detail into the callout — not into the paragraph body
   - If UNSOURCEABLE: leave paragraph unchanged, replace marker with [⚠ unverified]
   - Append [^N] inline if a source was found; add at note bottom:
     [^N]: Author(s). Title — URL

5. CLASSIFY BACKLINKS
   Run in terminal:

     obsidian backlinks path="<vault-relative path of current note>"

   Read each returned note. For argumentative backlinks (notes that use
   this claim as a premise or derive conclusions from it), identify the
   specific epistemic role: does the backlink note build on the claim,
   extend it to a new domain, derive a practical strategy from it, or
   treat it as evidence for a broader argument?

6. INSERT a collapsible callout directly below the patched paragraph.

   TITLE RULE: the title names the original claim being verified —
   a brief neutral statement of what the marked text asserts.
   It is NOT the verdict (verdict belongs in Status) and NOT a fragment
   of the original sentence. It answers: "what claim did we examine?"
   Example: "Verification: decision-making depletes self-control"
   NOT: "Verification: original effect is overstated" (that is the verdict)

   FORMATTING RULES:
   - Multi-item fields (Replication, Alternatives, Downstream) use <br>
     to place each item on its own line — never run items into prose
   - Theory and model names in Alternatives use **bold** — never [brackets],
     as brackets conflict with Obsidian link syntax and suppress unlinked
     mention detection

> [!check]- Verification: <original claim, stated neutrally>
> | Field | |
> |---|---|
> | **Status** | ✅ CONFIRMED / ⚠️ CORRECTED / ❌ UNSOURCEABLE |
> | **Original** | verbatim text before patching |
> | **Source** | [Title](URL) — primary source for the original claim |
> | **Quote** | "exact quote from the primary source" |
> | **Framing** | Three required elements: (1) study design and what was concretely measured — list the specific dependent variables, not vague categories; (2) what the claim asserts that was NOT directly measured — name the conceptual gap explicitly; (3) what assumptions are needed to bridge the gap |
> | **Replication** | **Overall verdict: confirmed / mixed / contested / failed** <br> `[role]` [Title](URL) — key finding, N, effect size <br> `[role]` [Title](URL) — key finding, N, effect size <br> *(role = ❌ refutes \| ⚠️ partially confirms \| ✅ confirms)* |
> | **Alternatives** | **Theory name** — mechanism — key prediction — difference from original — [Title](URL) <br> **Theory name** — mechanism — key prediction — difference from original — [Title](URL) |
> | **Practical status** | Three required elements: (1) what is empirically supported — state the effect concretely (effect size, conditions); (2) where exactly the claim overreaches — name the specific gap between data and assertion; (3) correct framing going forward — how the claim should be stated to stay within the evidence |
> | **Downstream** | [[note]] — *role: what argument or conclusion depends on this claim* <br> [[note]] — *role: what argument or conclusion depends on this claim* |

   Omit Downstream if no argumentative backlinks found.
   Omit Alternatives if claim is fully confirmed and no competing theories exist.
   Every URL in every field must point to a primary source.

Footnotes at the bottom are for inline citation only —
do not duplicate full source details there.

Use web_search → web_fetch. Never write from snippets alone.
Process all markers before writing anything back to the note.
