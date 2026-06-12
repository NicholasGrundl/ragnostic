# Hierarchical Retrieval Design

> **Status of this document.** This captures the *intent and design decisions*
> for RAGnostic's hierarchical retrieval approach, worked out through design
> discussion. Each decision is tagged:
>
> - **[CONCRETE]** — decided; we intend to build it this way.
> - **[OPEN]** — deliberately left open; a downstream mechanic we'll settle when we implement it.
> - **[DEFERRED]** — intentionally *not* building now; captured with the trigger that should make us revisit.
>
> Nothing here is implemented yet. The current codebase ships a simpler
> two-tier MVP (see `docs/3_MVP_RAG_Pipeline.md`); this document describes where
> we intend to take it.

---

## 1. The core idea (one sentence)

Parse each document into its **native structural tree** (ragged, variable
depth), embed only **uniform leaf-size chunks**, and recover all higher-level
relevance by **merging chunk hits upward** through the tree — so structure
provides organization and context, while a single flat field of honest
embeddings provides search.

### Motivating example

Searching a chemical-engineering textbook for "crystallization", we want to
surface *both* a section on crystal structure/solubility (fundamentals) *and* a
section on crystallizer unit operations (equipment) — which live in different
chapters — while **not** surfacing an incidental one-line mention of
"crystallization" buried in an unrelated reactor-design chapter.

The hierarchy delivers this: a section genuinely *about* crystallization returns
many leaf hits → high density → strong signal; the incidental mention is one
chunk in a large section → low density → correctly downranked. This "aboutness"
discrimination is the thing flat top-k retrieval cannot do.

---

## 2. Relationship to prior art

This design is **not novel** — and that is intentional. It fuses three
well-established patterns, which means there is prior art to borrow and a known
list of traps:

- **Small-to-big / auto-merging retrieval** (LlamaIndex `AutoMergingRetriever`,
  LangChain parent-document retriever): match on small chunks, merge upward to
  return the parent. This is the core of our approach.
- **RAPTOR** (Sarthi et al., ICLR 2024): recursive hierarchical retrieval.
  We build the tree **top-down from native document structure** rather than
  bottom-up by semantic clustering. We also follow RAPTOR's finding that
  searching all granularities at once ("collapsed tree") beats strict top-down
  traversal — see §6.
- **Contextual retrieval** (prepending document/section context to chunks before
  embedding): our ancestor-path enrichment (§4) is exactly this, and the
  hierarchy gives us the context text for free.

The value of being un-novel: high confidence it's sound, and a clear map of
where it breaks.

---

## 3. Parse into a ragged structural tree **[CONCRETE]**

- Docling labels headings (H1/H2/H3…). We descend those headings to build a
  tree: chapter → section → subsection, **as deep as each branch goes**.
- **No global depth.** A journal branch may bottom out at depth 2; a textbook
  branch at depth 4. The tree is intentionally *ragged* — it mirrors the
  document. We never assume or configure a depth; we descend until a branch has
  no more child headings.
- **Why this dissolves the variable-depth problem:** we never need to *know* or
  *intuit* a document's depth. Each branch bottoms out naturally. The same
  merge-up algorithm then walks however many levels exist on each branch.

### Key distinction: "deepest heading" ≠ "leaf node"

There are two trees layered together:

1. The **structural tree** — what docling labels (headings). Document-defined,
   variable depth.
2. The **text-unit tree** — the actual prose. Under the deepest heading there is
   still a *block of text* of arbitrary size.

The deepest heading is the last *structural* node, but it still contains an
arbitrary amount of text. Structure decomposes the document for free with
perfect semantic boundaries **until it runs out**; then chunking (§4) takes over
on the residual text. Structure and chunking are **sequential, not competing.**

### Assumption we are making **[CONCRETE decision to defer]**

We **assume docling produces usable granularity** and handle failures as
exceptions later (see §8). We are explicitly *not* building structure recovery
or giant-leaf handling now. Rationale: don't engineer for unobserved failure
modes; let the eval (§7) surface them.

---

## 4. Chunk leaf text — uniform, clean-boundary, enriched **[CONCRETE]**

- Whatever text sits at a node becomes **chunks**. A node is "big" only in that
  it produces more chunks. There is **no distinction** between a naturally small
  leaf and a chunked-down big leaf — both are just nodes with N chunks. This
  keeps merge-up uniform.
- **One chunker, two bounds:**
  - a **hard ceiling** = the embedding model's token limit (a chunk must always
    be legally embeddable);
  - a **soft target** = the leaf-granularity knob (sentence / paragraph /
    packed-to-N-words), well under the ceiling.
- **Clean boundaries [CONCRETE]:** never cut mid-sentence. Prefer paragraph
  boundaries; fall back to sentence boundaries; pack small pieces up to a
  minimum-size floor so we don't produce noisy ~6-word vectors.
- **No overlap [CONCRETE]:** continuity is restored by merge-up, not by physical
  overlap. Overlap and merge-up both solve continuity; we chose merge-up, so
  overlap would be double-paying.
- **Ancestor-path enrichment [CONCRETE, payload OPEN]:** each chunk is embedded
  with its heading path prepended (e.g. "Crystallizer Design → Hydrodynamics →
  <chunk text>"). A 15-word sentence is nearly meaningless to an embedder alone
  but searchable with its path. The structure does double duty: it defines the
  merge tree *and* supplies enrichment context for free.
  - **[OPEN]** exactly what travels with each chunk: full ancestor path? nearest
    heading only? document title too? To be settled at implementation.

### The single tunable knob

The only free parameter is **leaf granularity** (how finely we chunk residual
text). Everything above the leaf is determined by the document's own structure;
all cross-chunk continuity is handled by merge-up. Finer chunks → sharper merge
density signal but more/noisier vectors (mitigated by enrichment); coarser
chunks → fewer richer units but blunter signal. This is a single eval-able knob,
not an architectural fork.

---

## 5. Embed — one model, one object type **[CONCRETE]**

**Decision: a single embedding model, one legal input size, applied uniformly.
Only chunks are embedded.** No summaries, no mean-of-children, no special
node-level vectors.

- Sections, chapters, and the document are **structural nodes** that *own*
  chunks but are never themselves embedded.
- If a node's text exceeds the model's token limit, we **chunk it to legal-size
  pieces and embed those.** A big node's relevance is recovered through merge-up
  over its chunks (§6), never through a single node-level vector.
- **There is therefore exactly one kind of embedded object: a legal-size text
  chunk.** The hierarchy is *navigational metadata on chunks*, not a parallel
  set of embedded objects.

### Why we rejected node-level vectors (the reasoning, so we don't relitigate it)

Embeddings have two hard limits:

1. **A token ceiling on input.** Exceed it and the model **silently truncates**
   — you embed the first few pages of a chapter and call it the chapter. A
   ~30-page chapter (~27k tokens) overflows every common model.
2. **A fixed-size output regardless of input.** A multi-topic chapter is pooled
   toward a **centroid** — "near everything, crisply near nothing"
   (the dilution problem). This is geometric, not configurable.

Small, single-topic nodes embed faithfully as raw text; **big multi-topic nodes
do not.** Rather than build a reduction strategy (summary / representative
passages / vector averaging) to force a big node into one vector, we represent
big nodes by their chunks and infer relevance via merge density. **Merge-up is
the correct answer to "big nodes don't embed well."**

### The trade we are accepting **[CONCRETE, with a named escape hatch]**

By embedding *only* chunks, we give up a dedicated **thematic / diffuse-topic
recall source.** A chapter that is *thematically* about a topic but has no dense
cluster of strongly-matching chunks (relevance spread thinly everywhere,
concentrated nowhere) may be missed.

- In practice this is usually fine: "about X" and "contains many chunks matching
  X" correlate strongly.
- The failure case is narrow (pervasively diffuse topics) and **measurable**.
- If the eval shows such misses, the lever is to add **high-node proxy vectors
  for big nodes only** — see §8. We record this now so the fix is a known lever,
  not a rediscovery.

---

## 6. Retrieve — leaf search, then merge up **[CONCRETE shape, stop rule OPEN]**

1. Embed the query with the same model.
2. Search the flat chunk field for top hits across **all granularities at once**
   (RAPTOR "collapsed tree" style — avoids the compounding recall loss of strict
   top-down traversal, where one high-level miss is unrecoverable).
3. **Merge up:** group hits by `section_id`, then climb the ancestor path.
4. **De-conflict:** a returned set must never contain both a node and its
   ancestor; multi-granularity hits collapse to one representative per path.
   Merge-up *is* the dedup mechanism — embedding multiple granularities and
   merging up are two views of one thing.
5. **Assemble context:** a small merged node → return full text; an oversized
   node → return its top-scoring chunks. This is the **only** place compression
   is needed, and it is an *assembly-time* decision, not an index-time one.

### The merge-up stop rule **[OPEN — the heart of the system]**

We climb from a hit leaf toward its parent **only while** the parent is densely
hit, and we **stop** when the next level up is sparse **or** the merged text
exceeds a size budget. Two guards must be defined at implementation:

- **Normalized density [OPEN]:** raw `retrieved_children / total_children`
  punishes high-fan-out nodes (2-of-2 = 1.0 beats 9-of-30 = 0.30 even when the
  latter carries more signal). Combine the ratio with **absolute hit count** and
  **summed/aggregate similarity**; pick the multi-level propagation operator
  (sum/max/mean) deliberately.
- **Size budget [OPEN]:** the cap past which a merged node stops being useful
  context (approaching "the whole document"). Drives the full-text-vs-top-chunks
  assembly choice.

"Merge up as many levels as coverage justifies" is the intent; the stop rule is
what prevents every query collapsing to "return the whole chapter."

---

## 7. Evaluate — flat baseline alongside, from day one **[CONCRETE]**

- Build a **flat top-k retriever** next to the hierarchical one so "is the
  hierarchy earning its complexity?" is a *measurement*, not an argument. Cheap
  to keep, easy to compare.
- The eval also **surfaces the deferral triggers** in §8 — fat-tail leaf sizes,
  diffuse-topic misses, collapsed sections all show up as retrieval misses you
  can see rather than guess at.
- **[OPEN]** what "better" means here and the query/relevance set we measure
  against. (Back-of-book index pages are a candidate eval oracle — see §8.)

### Vocabulary mismatch is the embedder's job, not the hierarchy's

The hierarchy improves *aboutness* discrimination. It does **not** fix
vocabulary mismatch (query "crystallization" vs. text "supersaturation,
nucleation"). That is the embedding model's responsibility — weak with TF-IDF,
much better with a semantic model. Don't expect the tree to rescue weak
embeddings; they solve different problems.

---

## 8. Schema obligations we honor NOW (so deferrals stay cheap) **[CONCRETE]**

"Handle it later" is cheap **only if the data model doesn't have to change when
we do.** Two properties, decided now, cost nothing and prevent a future
migration / corpus re-parse:

1. **A node is a node regardless of origin.** Add a node **`origin`/`source`
   marker** (`docling_heading` / `synthetic` / `recovered`) so future fixes can
   insert synthetic levels or recovered headings using the *same* record type,
   distinguishable but treated identically by merge-up unless we choose
   otherwise.
2. **Merge-up reads the tree; never hardcodes depth.** It climbs `parent_id`
   links until the stop rule fires. Inserting a synthetic level later then
   changes *data*, not *algorithm*.

The existing schema already supports ragged arbitrary-depth trees
(`document_sections.parent_section_id` + `level`) and the chunk→node link
(`document_chunks.section_id`). The only addition required now is the `origin`
marker.

---

## 9. Deferred ideas — captured, with triggers **[DEFERRED]**

| Idea | Why deferred | What it would add | Trigger to revisit |
|---|---|---|---|
| **Higher-level node embeddings** (a vector per section/chapter) | Big nodes can't embed faithfully (token limit + dilution); merge-up recovers their relevance | A dedicated **thematic / diffuse-topic** recall source | Eval shows misses on pervasively-diffuse topics |
| **Summaries** | Reframed as length-compression, not content; we chose chunk-and-merge, avoiding LLM index cost | Token-legal proxy vectors for big nodes; human-readable abstracts | Same as above — summaries are *how* you'd build high-node vectors |
| **Index-page parsing** (back-of-book) | Fiddly to parse; depends on structural parse working first | High-precision concept→page map; a strong **eval oracle** | After structural parse is proven; or when building the eval set |
| **TOC-page parsing** | Same | Independent depth/structure oracle; often cleaner than inferred headings | If inferred headings prove unreliable (case b below) |
| **Structure recovery** (headings docling missed — "case b") | Don't build for unobserved failures | Recovers real sections collapsed into one node | You eyeball output and see collapsed sections |
| **Giant-leaf splitting** (coherent-but-huge text — "case a") | Chunker already won't crash on it | Synthetic sub-levels so merge-up has something to aggregate within a huge block | Leaf-size distribution has a fat tail / merge returns over-budget single nodes |
| **Cross-reference links** (lateral concept links across chapters) | A tree models containment, not cross-reference | Captures "ch. 9 relies on notation from ch. 2" | Out of scope for now; named so it's a choice |
| **N-level recursive merge-depth tuning** | Two-level merge captures most value | Deeper auto-merge for very deep textbooks | Eval shows we stop too shallow on deep docs |

---

## 10. Status summary

**Settled [CONCRETE]:** ragged variable-depth structural tree; per-branch
bottoming-out; uniform clean-boundary leaf chunks with ancestor enrichment and
no overlap; single embedding model, chunk-only embedding; merge-up as both
relevance-recovery and dedup; flat baseline + eval alongside; depth-agnostic
schema with an `origin` marker.

**Open [OPEN] (downstream mechanics, not concept):**
1. **Merge-up stop rule** — normalized-density threshold + size budget *(the heart; settle first)*.
2. **Enrichment payload** — exactly what ancestor context travels with each chunk.
3. **Eval definition** — what "better" means and the query/relevance set.

**Deferred [DEFERRED]:** everything in §9, each with a trigger.

---

## 11. How this relates to the current codebase

The shipped MVP (`docs/3_MVP_RAG_Pipeline.md`) is a **two-tier** system
(document-summary search → chunk search → single-level section-coverage rerank).
This design **generalizes** that:

- The MVP's single-level "section-coverage rerank" becomes **recursive merge-up**
  over a ragged tree.
- The MVP's **document summaries** (currently a tier-1 recall source) become a
  **[DEFERRED]** option, since chunk-only embedding + merge-up is intended to
  cover their role.
- The MVP's flat chunking becomes **structure-aware, clean-boundary, enriched**
  chunking.
- The schema already carries the hierarchy (`parent_section_id`, `level`,
  `section_id`); the migration path is additive (the `origin` marker + deeper
  trees), not a reshape.
