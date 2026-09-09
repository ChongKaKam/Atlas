# Atlas Knowledge Base Specification v0.2

> Status: working specification for Atlas V1; defaults remain subject to real-use review  
> Scope: the structure and curation rules of an Atlas-managed Markdown knowledge base  
> Last updated: 2026-09-09

This document defines the knowledge contract for Atlas. V0.2 retains the initial KU model, six document types, and three statuses, and clarifies operational defaults following the user's request to build the complete Skill. Workflows and tools are specified separately in [SKILL.md](../SKILL.md) and [tooling](tooling.md). QMD and Obsidian remain optional future enhancements, not V1 dependencies. Initial pilot observations are limited self-review evidence, not an independent validation of these rules.

## 1. Design Goals

An Atlas knowledge base should be:

- **Local-first:** usable from an ordinary local directory without a service account or network connection.
- **Markdown-first:** Markdown files are the authoritative knowledge representation. Indexes, embeddings, databases, and GUI state are derived and disposable.
- **Git-friendly:** changes remain understandable as text diffs; moves, merges, and automated edits are reviewable.
- **Tool-agnostic:** the repository remains usable in a text editor and does not require QMD, Obsidian, or a particular AI client.
- **Human-readable:** a person can navigate, understand, and maintain it without reconstructing a machine-oriented schema.
- **AI-maintainable:** rules make document boundaries, provenance, and uncertainty explicit enough for an AI to propose safe changes.
- **Review-first:** Atlas proposes semantic changes and exposes conflicts; a human can inspect them before they become canonical.
- **Incrementally structured:** the repository can begin small and add directories or metadata only after repeated use proves their value.

The knowledge base is not intended to preserve every input document as-is. It preserves useful knowledge, provenance, scope, and unresolved disagreement. Git preserves edit history; the canonical Markdown should represent the best current understanding.

## 2. Atlas Decision Principles

Preservation of evidence, explicit conflict handling, and user authorization are constraints. Among the other principles, explain trade-offs in the integration plan: reducing duplication must not override clear knowledge boundaries. Review-first means concrete, reviewable changes; an already authorized change does not require repeated approval. See [Review and Apply](review-apply.md).

1. **Preserve meaning, evidence, and context.** Preserve useful knowledge, not necessarily the original wording or input-document boundary.
2. **Never silently resolve uncertainty or disagreement.** Qualify claims, retain relevant competing evidence, and request review when the evidence does not support a clear resolution.
3. **Maintain one preferred home for each Knowledge Unit.** Link to that home instead of copying the same explanation into several documents.
4. **Integrate before creating.** Merge or extend compatible existing knowledge when doing so keeps the document coherent; create a new document when the knowledge has an independent purpose or lifecycle.
5. **Keep knowledge boundaries clear.** A document should make one coherent promise to its reader. Split material that has materially different questions, audiences, contexts, or maintenance lifecycles.
6. **Match confidence to evidence.** Distinguish what a source states, what an experiment observed, and what the author or AI inferred.
7. **Prefer stable human concepts over speculative taxonomy.** Do not add directories, types, fields, or tags solely because they might be useful later.
8. **Use directories for primary ownership and links/tags for secondary relationships.** Semantic relationships matter more than making every topic fit a perfect tree.
9. **Keep Markdown authoritative and portable.** Optional tools may derive indexes or retrieval data but must not become the only location of knowledge.
10. **Make changes small, reviewable, and reversible.** Automated changes should produce focused Git diffs and must not mix unrelated reorganization with content changes.
11. **Optimize for readers first, conventions second, machines third.** Consistency is valuable where it reduces ambiguity, but not when it damages established technical terminology or readability.

These principles refine the initial candidates in three ways: “preserve knowledge” means preserving meaning rather than all text; extending an existing document is not preferred when it blurs a boundary; and evidence/confidence is explicit rather than implied by a generic source-preservation rule.

## 3. Directory Structure

### 3.1 Recommended shape

Use a shallow, domain-first structure:

```text
knowledge-base/
├── README.md
├── CONVENTIONS.md
├── knowledge/
│   ├── compiler/
│   ├── ai-compiler/
│   ├── llvm/
│   ├── mlir/
│   ├── isa/
│   ├── hardware/
│   ├── runtime/
│   ├── heterogeneous-programming/
│   └── programming-model/
├── projects/
│   └── <project-name>/
└── assets/                    # optional; only when Markdown needs local supporting media
    └── <document-slug>/
```

`knowledge/` contains reusable, curated technical knowledge. `projects/` contains context-bound working knowledge whose meaning depends on a particular project, implementation, or local decision. A project note that becomes generally useful should be promoted into `knowledge/` and replaced with a link rather than copied indefinitely.

The domain list is an initial vocabulary, not a requirement to create nine empty directories. Create a directory only when the first document needs it. Phase 2 should test whether `ai-compiler/` and `programming-model/` remain useful primary homes or are better represented through other domains and tags.

`assets/` may hold diagrams or other supporting files, but assets are not an alternative knowledge store. Important claims, captions, and interpretation remain in Markdown.

### 3.2 Domain-first, not type-first

Directories answer **“Which body of knowledge primarily owns this document?”** Document metadata answers **“How should this document be read?”** Therefore:

- Use `knowledge/llvm/SelectionDAG-legalization.md`, not `concepts/llvm/...`.
- Do not create parallel roots such as `concepts/`, `guides/`, and `experiments/`; one topic would otherwise be fragmented across type trees.
- Give a cross-domain document one primary home based on its main question, then represent the other domains with links and, when useful, tags.

Examples:

- An explanation of how LLVM implements RISC-V register pairs belongs under `llvm/`; `risc-v` may be a tag and the ISA rule may be linked.
- A description of the architectural register-pair constraint belongs under `isa/`, even if LLVM source code motivated the investigation.
- An explanation of the LLVM dialect belongs under `mlir/`; its name does not make it an `llvm/` document.

### 3.3 Depth rules

- Default to files directly within a domain.
- Add one subdomain level only after a real cluster is hard to browse or has a distinct ownership boundary, for example `llvm/codegen/`.
- Avoid more than two levels below `knowledge/` (`domain/subdomain/file.md`) unless Phase 2 demonstrates a concrete need.
- Do not create generic catch-all directories such as `misc/`, `notes/`, or `cross-domain/`. If ownership is unclear, treat that as an integration decision, not a folder name.
- Do not use directories to encode status, year, source type, or document type.

## 4. Knowledge Unit Model

### 4.1 Definition

A **Knowledge Unit (KU)** is the smallest coherent cluster of claims that:

1. answers one identifiable technical question or explains one identifiable subject;
2. shares the same material scope and context (for example architecture, implementation, version, target, or experiment conditions);
3. can be evaluated against evidence as a unit; and
4. has a useful independent retrieval or reuse boundary.

A KU is a semantic unit, not a storage unit. It may be a section within a larger document. One input document may contain several KUs, while several input documents may contribute evidence or explanation to one KU.

A Markdown document is a **curation boundary**: a reader-facing collection of one primary KU and any tightly coupled supporting KUs needed to fulfill one clear promise. This avoids both one-file-per-fact fragmentation and unsearchable omnibus documents.

### 4.2 Identifying a candidate KU

For each candidate, Atlas should be able to state:

- **Subject/question:** what does this teach or answer?
- **Scope/context:** under which version, target, configuration, project, or assumptions is it valid?
- **Claims:** what new or changed understanding does it contain?
- **Evidence/provenance:** why should the claims be trusted, and which parts are inferred?
- **Retrieval intent:** what future query should find it?

If two passages have different answers to several of these questions, they are likely separate KUs even if they occur in one input document.

### 4.3 Integration decisions

| Decision | Use when | Required behavior |
|---|---|---|
| **Create** | No existing document provides a coherent home, and the KU has an independent retrieval or maintenance boundary. | Create one canonical home with appropriate scope and provenance. Do not mirror the input document by default. |
| **Merge** | The candidate and existing content express substantially the same KU, and their claims are compatible or one is a clearer restatement. | Synthesize the strongest explanation, remove redundant wording, retain useful provenance, and preserve meaningful context differences. |
| **Extend** | An existing document has the same reader promise, but the candidate adds a compatible subsection, example, limitation, or evidence. | Add the smallest coherent section and connect it to the existing explanation. Do not append an unrelated mini-document. |
| **Split** | One document contains KUs with independent reader questions, types, scopes, or change lifecycles, or a KU is repeatedly needed without its surrounding material. | Move each durable KU to an appropriate home, leave contextual links, and avoid duplicating the moved explanation. Size alone is not sufficient reason. |
| **Skip** | The candidate adds no durable knowledge: it is an exact duplicate, unsupported noise, obsolete without historical value, or outside the knowledge-base scope. | In an integration plan, state what was skipped and why. Do not silently drop a potentially useful claim merely because it is difficult to place. |
| **Conflict** | Claims are mutually incompatible under the same material scope and terminology, and available evidence does not justify choosing one. | Preserve both positions and their evidence, make the unresolved point explicit, and do not overwrite either claim. See section 12. |

`Merge` removes semantic duplication. `Extend` adds adjacent coverage. Both are preferred to `Create` only when the resulting document still makes one coherent promise.

### 4.4 File-boundary heuristics

Create or retain a separate Markdown file when at least one of the following is true:

- readers are likely to search for the subject directly;
- it is linked from several independent contexts;
- its scope, provenance, or review lifecycle differs materially from its neighbors;
- it needs a different document type;
- keeping it embedded would make the parent document serve multiple unrelated reader goals.

Keep a KU as a section when it is hard to understand or unlikely to be useful without the parent subject, and it changes with that parent. Do not use word count as an automatic split threshold.

Different source provenance alone is not a split trigger: several sources supporting the same question should remain together. Source differences justify splitting only when they reflect independently useful context or maintenance boundaries. A short overview may summarize linked KUs without duplicating their full explanations. Skip can also mean explicitly deferred outside this integration's agreed scope; distinguish deferral from lack of knowledge value.

## 5. Document Types

Use six types. They describe the document’s dominant reader intent, not every section it contains.

| Type | Reader intent | Typical content | Boundary |
|---|---|---|---|
| `overview` | Orient me to an area. | Scope, mental map, major components, curated entry links. | Not a generated index or a shallow list of every file. |
| `concept` | Help me understand what this is and why it behaves this way. | Model, terminology, invariants, mechanisms, trade-offs. | May include short examples, but not a full operational procedure. |
| `guide` | Help me accomplish or diagnose something. | Preconditions, steps, decisions, checks, failure modes. | Includes debugging playbooks; not a chronological incident log. |
| `investigation` | Show what was tested or investigated and what the evidence supports. | Question, setup, observations, analysis, result, limitations. | Combines `experiment` and debugging case reports because both are evidence-led investigations. |
| `decision` | Record a consequential choice and its rationale. | Context, options, decision, consequences, revisit conditions. | A local preference without durable consequences belongs in a project note or guide, not a decision record. |
| `reference` | Let me look up precise facts quickly. | Tables, command/option summaries, mappings, syntax, stable factual catalogs. | Must add curation or context; it is not a wholesale copy of an upstream manual. |

Changes to the initial candidates:

- `experiment` and retrospective `debugging` records become `investigation`; both require reproducible context, observations, and evidence. A reusable debugging procedure is a `guide`.
- `project-note` is not a document type. Project scope is a location and lifecycle (`projects/<project-name>/`), while the note’s reader intent still maps to one of the six types. Informal scratch notes are outside the curated schema until integrated.

If a document appears to need two types, choose the dominant reader promise or split it. Do not add subtypes in v0.1; use headings and a small number of tags for meaningful secondary facets.

## 6. Frontmatter Schema

### 6.1 Canonical schema

```yaml
---
type: concept
status: draft
created: 2026-09-09
updated: 2026-09-09
aliases:
  - GlobalISel legalization
tags:
  - codegen
  - legalization
---

# LLVM GlobalISel Legalizer
```

Use ISO 8601 calendar dates (`YYYY-MM-DD`). Dates describe the knowledge document, not the publication date of its sources.

| Field | Level | Rule |
|---|---|---|
| `type` | Required | One value from section 5. |
| `status` | Required | One value from section 10. |
| `created` | Required | Date the curated document was first created. Preserve it across moves and renames. |
| `updated` | Required | Date of the last material knowledge change. Do not change it for formatting-only edits. |
| `aliases` | Optional | A short list of genuine alternative names or search terms. Omit when empty. |
| `tags` | Recommended | Usually 2–5 cross-cutting terms following section 9. Omit rather than add weak tags. |

### 6.2 Intentionally excluded fields

- `title` is excluded because the first H1 is the single canonical human title. Duplicating it in frontmatter creates drift without a demonstrated tool requirement.
- `source` is excluded from frontmatter because real provenance needs locators, versions, conditions, and notes that do not fit a stable scalar field. Use the body format in section 11.
- `related` is excluded because body links provide labels and explanatory context. Use inline links and, when valuable, a curated `See also` section.

If a future retrieval or publishing tool demonstrably requires one of these fields, Phase 2 may revisit the decision. Do not add null values, empty arrays, IDs, summaries, owners, confidence scores, or version fields speculatively.

## 7. Naming Rules

### 7.1 Directory names

- Use lowercase ASCII kebab-case: `ai-compiler`, `heterogeneous-programming`.
- Use established, durable domain names rather than organization names or temporary project phases.
- Project directory names may preserve a widely recognized product token, but prefer a filesystem-safe kebab-case slug.

### 7.2 Markdown filenames

- Use a short, descriptive filename ending in `.md`.
- Separate ordinary words with hyphens; avoid spaces or underscores used as word separators. Preserve underscores when they belong to a canonical technical identifier.
- Preserve the canonical spelling and case of technical identifiers: `GPRPair.md`, `SubRegIndex.md`, `SelectionDAG-legalization.md`, `RISC-V-register-pairs.md`.
- Use the expanded subject when an abbreviation would be ambiguous. Established names such as `LLVM`, `MLIR`, and `RISC-V` need not be expanded.
- Avoid numeric ordering prefixes, dates, status labels, and type suffixes unless they are part of the subject. A decision series may use an identifier only if the repository later adopts a deliberate decision-record convention.
- Prefer stable subject names over source-document titles such as `notes-from-LLVM-talk-2026.md`.

Technical identifier case is more important than uniform lowercase filenames. This is a deliberate application of **readability > consistency > machine convenience**. Case-only filename differences are forbidden because they are unsafe on common filesystems.

### 7.3 H1 titles and terminology

- Every curated document has exactly one H1, placed after frontmatter.
- The H1 is a natural human title and may contain spaces and punctuation: `# SelectionDAG Legalization`.
- Use upstream spelling for products, APIs, classes, instructions, and identifiers. Do not normalize `GPRPair`, `SubRegIndex`, or `SelectionDAG` to a house style.
- On first use, introduce an abbreviation when the expansion is useful: “instruction set architecture (ISA).” Do not expand well-known proper names such as LLVM.
- Use one preferred term consistently within a document; put genuine alternate terms in `aliases` or explain them in the body.

## 8. Linking Rules

### 8.1 Canonical link syntax

Use standard Markdown links with relative paths and explicit `.md` extensions:

```markdown
[GPRPair](../llvm/GPRPair.md)
```

Do not use WikiLinks (`[[GPRPair]]`) in canonical content. Standard relative Markdown links reduce reliance on tool-specific resolution. Compatibility with any future retrieval or GUI integration must be tested rather than assumed.

### 8.2 When to link

Create a link when it does at least one of the following:

- supplies a prerequisite needed to understand the current claim;
- points to the canonical explanation instead of repeating it;
- connects implementation evidence to the underlying concept or ISA rule;
- provides a useful next step for a likely reader;
- identifies a replacement for deprecated knowledge.

Do not link every occurrence of a term. Usually link the first contextually useful occurrence in a section. A link should communicate a relationship, not merely prove that another file exists.

Use descriptive inline links where the relationship appears in prose. Add `## See also` only when two or more high-value relationships do not fit naturally inline. Keep it curated—normally no more than about seven links—and add a short reason when the relationship is not obvious.

### 8.3 Moving files

Paths are not permanent identifiers. When moving or renaming a file:

1. update all inbound repository links and recompute the moved file's outbound relative links, including images and sources, in the same change;
2. review the move and link changes together;
3. run link validation when deterministic tooling exists; and
4. avoid compatibility stub files unless external links make them necessary.

Stable naming and shallow directories reduce link churn. A future tool may automate path rewriting, but the Markdown link remains authoritative.

## 9. Tagging Rules

### 9.1 Responsibility

- **Directory:** the document’s primary domain/owner.
- **Type:** the reader intent and content shape.
- **Tags:** cross-cutting technical facets that improve retrieval across domains.
- **Links:** specific semantic relationships between documents.

Do not repeat directory and type mechanically as tags. For example, a file under `knowledge/llvm/` with `type: concept` does not automatically need `llvm` or `concept` tags.

### 9.2 Syntax and vocabulary

- Use lowercase ASCII kebab-case: `register-allocation`, `codegen`, `memory-model`.
- Preserve a canonical lowercase form for proper-name tags: `risc-v`, not `RISC-V`, `riscv`, and `risc_v`.
- Use singular nouns or established uncountable terms where practical: `compiler`, not both `compiler` and `compilers`.
- Prefer technical concepts over vague organizational labels such as `important`, `misc`, `notes`, or `todo`.
- Keep tags flat in v0.1. Do not introduce `/` hierarchies or namespace prefixes until a real retrieval problem demonstrates the need.
- Reuse an existing tag whenever it has the same meaning. Creating a new tag is a vocabulary change and should be visible in review.

Use approximately 2–5 tags per document, but treat this as a diagnostic range rather than a validation limit. Zero strong tags is better than several weak ones. More than seven usually indicates that the tags are restating the document or replacing links.

The canonical vocabulary should live in the tagging section of root `CONVENTIONS.md` while it is small. A separate `TAGS.md` becomes justified only if the vocabulary needs definitions, aliases, or deprecation mappings too large for that file.

For automated vocabulary membership checks, keep one fenced `atlas-tags` block in CONVENTIONS.md or TAGS.md, with one tag per line. This remains Markdown, not a second data store. Older prose-only vocabularies are valid for human review; tools report that membership validation was skipped instead of guessing. See [tooling](tooling.md).

## 10. Status Model

Use three states:

| Status | Meaning | Reader expectation |
|---|---|---|
| `draft` | The document is incomplete, materially unreviewed, weakly sourced, or contains changes that still need verification. | Useful leads may exist, but do not rely on all claims without checking. |
| `reviewed` | A human has reviewed the document’s scope, claims, provenance, and uncertainty for its stated context. | The document is fit for normal use within that context; this does not mean timeless or universally true. |
| `deprecated` | The document is retained for history or inbound links but is no longer the recommended knowledge. | The opening paragraph must state why and link to the replacement or explain that none exists. |

Allowed transitions:

```text
draft ──review──> reviewed
reviewed ──material unreviewed change──> draft
draft|reviewed ──supersede──> deprecated
deprecated ──intentional revival──> draft|reviewed
```

Formatting, link repair, or typo fixes do not demote `reviewed`. A changed technical claim, scope, or conclusion normally does until reviewed. A carefully documented unresolved conflict may itself be `reviewed`: status describes the quality of the curation, not certainty of the underlying world.

Do not use `stable` in v0.1. It is ambiguous between content maturity, API stability, and expected change frequency; `reviewed` names an observable human action.

## 11. Source Tracking

### 11.1 Goal

Source tracking must let a future reader distinguish:

- what an external source states;
- what was directly observed or reproduced;
- what is personal or project-local understanding; and
- what was synthesized or inferred with AI assistance.

It is not intended to become a general citation database.

### 11.2 Body format

When a document contains externally derived, experimental, or non-obvious claims, add a `## Sources and evidence` section. Use ordinary Markdown bullets with a provenance kind and enough context to relocate or evaluate the evidence:

```markdown
## Sources and evidence

- **Official documentation:** [GlobalISel — LLVM documentation](https://llvm.org/docs/GlobalISel/), accessed 2026-09-09; basis for the pipeline overview.
- **Source code:** `llvm/lib/CodeGen/GlobalISel/Legalizer.cpp` at tag `llvmorg-21.1.0`; implementation behavior discussed in “Action selection.”
- **Experiment:** [Minimal legalization reproducer](../../projects/legalizer-study/reproducer.md), run on LLVM 21.1.0 for `riscv64`.
- **Personal inference:** The ordering explanation combines the source-code path and the experiment; it is not stated directly in the documentation.
- **AI-assisted synthesis:** Initial comparison drafted with AI, then checked against the sources above. Unverified portions remain marked in the text.
```

Recommended provenance kinds are:

- `official-documentation`
- `chip-manual`
- `paper`
- `source-code`
- `experiment`
- `internal-documentation`
- `personal-understanding`
- `ai-assisted-synthesis`

These are labels in prose, not mandatory schema values in v0.1. Use a direct link, document identifier, repository path plus revision, experiment link plus conditions, or other locator appropriate to the source. Record an access date for mutable web pages and a version/commit for version-sensitive code or manuals when available.

### 11.3 Claim-level qualification

Do not annotate every sentence. Add local wording such as “the manual states,” “observed on,” or “inferred from” when:

- a conclusion is easy to mistake for verified fact;
- sources support different contexts or versions;
- the claim is central, surprising, or safety-critical; or
- an unresolved conflict depends on provenance.

AI assistance is not evidence by itself. It is provenance of the synthesis process. A document based only on AI output remains `draft` until its material claims are checked or clearly framed as hypotheses.

Operational defaults: use Chinese explanatory prose with upstream technical terms for new notes, preserving existing document language and user preferences. Pin source-code-sensitive claims to a commit/tag whenever available; otherwise state the branch, access date, and missing revision. A mutable source is not proof of error, and pinned sources do not automatically earn `reviewed`. Do not invent access dates, execution results, or human reviews.

## 12. Conflict Handling

Classify apparent disagreement before editing existing knowledge:

| Classification | Test | Action |
|---|---|---|
| **Supplement** | Same subject and compatible scope; the new material adds detail without contradicting an existing claim. | Merge overlapping explanation or extend with the new detail and evidence. |
| **Correction** | The claims address the same scope, and stronger or more current evidence shows the existing claim is wrong. | Correct the canonical text, cite the evidence, and use Git for history. Add a brief correction note only when readers could otherwise be misled or the old claim remains common. |
| **Different context** | The claims differ because of version, target, configuration, abstraction level, terminology, or preconditions. Both can be true when qualified. | Preserve both with explicit scope, in separate sections or documents as their retrieval boundaries require. Link the contexts. |
| **True conflict** | After normalizing terminology and scope, the claims are mutually exclusive and the available evidence does not justify resolving them. | Preserve both claims and evidence under an `Unresolved conflict` section, describe what would resolve it, and request review. |

Before declaring a true conflict, compare at least:

- source version and publication date;
- target architecture, toolchain, optimization mode, and runtime conditions;
- whether one statement is normative and the other observed implementation behavior;
- whether terms are used at different abstraction levels; and
- evidence quality and reproducibility.

There is no universal ranking in which documentation, source code, or experiments always win. A manual may be normative but stale; source code may be current but target-specific; an experiment may be reproducible but incomplete. Prefer evidence that directly matches the claim’s stated context.

Suggested true-conflict format:

```markdown
## Unresolved conflict

**Shared scope:** LLVM 21.1.0, `riscv64`, default legalization pipeline.

- **Claim A:** ...  
  **Evidence:** ...
- **Claim B:** ...  
  **Evidence:** ...

**Why unresolved:** ...

**Resolution test:** Inspect ... or reproduce with ...
```

Never replace reviewed knowledge solely because a new input is newer, more confident, or phrased more clearly.

## 13. Root Control Files

Use the smallest stable set:

| File | v0.1 decision | Purpose |
|---|---|---|
| `README.md` | Required in an actual knowledge base | Explain scope, top-level navigation, how to start, and the distinction between `knowledge/` and `projects/`. Keep it short. |
| `CONVENTIONS.md` | Required in an actual knowledge base | Hold contributor-facing rules that Atlas and humans must follow: types, metadata, naming, linking, tags, status, and source format. It may summarize this specification rather than duplicate its rationale. |
| `INDEX.md` | Deferred | Add only when repository scale makes a generated or curated index demonstrably useful. If generated, label it as derived and never edit it as the source of truth. |
| `TAGS.md` | Deferred | Keep the small vocabulary in `CONVENTIONS.md`; split it out only when definitions and aliases become substantial. |
| `CHANGELOG.md` | Rejected for v0.1 | Git already records changes. Use decision documents for consequential policy choices rather than a second chronological log. |

The Skill bundles root-file templates for initializing a user-requested new knowledge base. Templates are not themselves curated knowledge documents and are not silently copied into an existing library. Existing repository conventions take precedence over default tooling expectations unless a migration is requested.

## 14. Examples

### 14.1 One input document, several KUs

Suppose an imported conference note contains:

1. an explanation of `GPRPair`;
2. a step-by-step debugging procedure for a failed legalization; and
3. benchmark observations on one LLVM revision.

These are three candidate KUs. A likely integration is:

```text
knowledge/llvm/GPRPair.md                         concept; merge or create
knowledge/llvm/debug-GlobalISel-legalization.md   guide; create or extend
projects/legalizer-study/benchmark-results.md     investigation; preserve exact setup
```

The input note itself need not become a fourth canonical knowledge document. Its source location may be recorded in the relevant `Sources and evidence` sections.

### 14.2 Several inputs, one KU

An LLVM manual section, a source-code reading note, and a local reproducer all explain how one legalization action is selected. Atlas should integrate them into one canonical concept document when they share the same reader question. The manual supports intended behavior, the code supports implementation detail, and the experiment supplies observed behavior; their different provenance does not require three files.

### 14.3 Complete concept skeleton

```markdown
---
type: concept
status: reviewed
created: 2026-09-09
updated: 2026-09-09
aliases:
  - GlobalISel legalization
tags:
  - codegen
  - legalization
  - risc-v
---

# LLVM GlobalISel Legalizer

The GlobalISel Legalizer transforms operations that are not legal for the
selected target into legal operations or supported lower-level forms.

## Mental model

...

## Target-specific context

For the architectural constraint, see
[RISC-V register pairs](../isa/RISC-V-register-pairs.md).

## Sources and evidence

- **Official documentation:** ...
- **Source code:** ...

## See also

- [GPRPair](GPRPair.md) — register-pair representation used by this example.
```

### 14.4 Different context, not conflict

“Operation X is legal” and “Operation X is expanded” do not conflict if one describes `aarch64` and the other `riscv64`, or if they refer to different LLVM versions. Qualify each claim at the smallest useful scope. Split by target only if each target develops an independent reader and maintenance boundary.

### 14.5 Correction

If a project note claims that a behavior is target-independent but current source code and two target experiments show otherwise, update the canonical concept to state the target-specific behavior. Preserve the experiment links and scope. Do not keep the incorrect assertion beside the corrected one merely to preserve history; Git holds the old text. Add a visible correction note only if the prior claim is likely to remain externally relevant.

## 15. Anti-patterns

- **Input mirroring:** creating one knowledge document for every imported document without extracting KUs.
- **Type trees:** storing the same topic separately under `concepts/`, `guides/`, and `experiments/`.
- **Atomic-note explosion:** creating a file for every definition or claim even when it has no independent retrieval value.
- **Omnibus dumping:** appending unrelated findings to one large domain note because it already exists.
- **Taxonomy as a substitute for thinking:** adding deep folders or a `misc/` bucket instead of choosing a primary home.
- **Tag restatement:** tagging every LLVM file with `llvm`, `compiler`, its type, and multiple spelling variants.
- **Link saturation:** linking every technical noun or maintaining a large uncurated `Related` list.
- **Tool lock-in:** using WikiLinks, plugin-only fields, canvas files, or a vector database as the only representation of a relationship.
- **Frontmatter database:** storing summaries, citations, confidence scores, source objects, and relationships in YAML when prose is clearer.
- **Status theater:** marking content `stable` or `reviewed` without a defined review event.
- **Silent overwrite:** replacing a scoped or reviewed claim merely because new text sounds authoritative.
- **False conflict:** treating version-, target-, or abstraction-specific differences as mutually exclusive truth claims.
- **Permanent scratch space:** allowing project notes or an inbox to become a second uncurated knowledge base.
- **AI as evidence:** presenting AI-generated synthesis as verified technical fact without sources, experiments, or explicit uncertainty.
- **Mixed-purpose diffs:** combining mass renames, taxonomy changes, and semantic rewrites in one review.

## 16. Open Questions

These are deliberately unresolved until Phase 2 supplies evidence:

1. **Domain vocabulary:** Do `ai-compiler/` and `programming-model/` accumulate enough independently owned knowledge to remain top-level domains, or do they mostly act as cross-cutting tags and overview documents?
2. **Subdomain threshold:** Which real LLVM/MLIR collections become hard to browse flat, and does one subdomain level solve the problem without encouraging premature taxonomy?
3. **Investigation type:** Does one `investigation` type serve both controlled experiments and debugging case reports, or do their repeated structures and retrieval intents diverge in practice?
4. **Project boundary:** Should `projects/` live in the same repository as reusable knowledge for all use cases, or should Atlas also support linking to separate project repositories?
5. **Alias value:** Do aliases materially improve retrieval enough to justify maintaining them, especially after QMD is evaluated?
6. **Provenance syntax:** Is the prose-based `Sources and evidence` format consistent enough across manuals, papers, source code, and experiments, or is a small optional convention needed?
7. **Filename casing:** Does preserving identifier case create friction in real cross-platform Git workflows that outweighs its readability benefit?
8. **Curated overview versus generated index:** At what repository size or navigation failure does `INDEX.md` become useful, and which parts should remain curated rather than generated?
9. **External inbound links:** Are compatibility stubs needed after moves, or are all consumers under repository control?
10. **Knowledge language:** What is the default prose language, how should bilingual aliases be handled, and when should translated technical terms defer to upstream English terminology?
11. **Source revision policy:** Must source-code-derived `reviewed` knowledge pin a commit or tag, or is a mutable branch plus access date sufficient for low-risk claims?

## 17. Phase 2 Validation Priorities

Phase 2 should test the specification with a small but deliberately varied corpus rather than a broad import. The highest-value hypotheses are:

1. **KU extraction and integration:** Use at least one mixed LLVM/MLIR note containing explanation, procedure, and observations, plus overlapping official documentation. Verify that `Create`, `Merge`, and `Extend` produce clearer canonical homes than input mirroring.
2. **Primary-domain ownership:** Use a topic spanning RISC-V ISA rules, LLVM backend implementation, and MLIR lowering. Check whether domain-first placement is predictable and whether tags/links adequately express the other dimensions.
3. **Document-type sufficiency:** Classify real experiments, debug reports, decisions, and lookup notes. Pay particular attention to whether `investigation` is too broad and whether `reference` is distinguishable from `concept`.
4. **Provenance ergonomics:** Integrate one official guide, one source-code reading, one paper, and one local experiment. Check whether readers can quickly tell “sourced,” “observed,” and “inferred” without heavy frontmatter.
5. **Conflict classification:** Seed examples of a real correction, a version difference, a target difference, and a genuine unresolved disagreement. Verify that Atlas does not overwrite old knowledge or preserve obsolete text unnecessarily.
6. **Naming and link durability:** Perform one realistic rename or move. Measure review clarity and link-repair cost using standard Markdown links.
7. **Metadata cost:** After several ADD and INTEGRATE operations, identify fields or tags that are routinely guessed, empty, duplicated, or ignored. Remove them before adding new metadata.

Do not treat these experiments as implementation requirements. Their purpose is to falsify or refine v0.1 before the workflows and deterministic tooling are formalized.
