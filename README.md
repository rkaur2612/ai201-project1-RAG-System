# The Unofficial Guide

Raman Deep Kaur — corpus: `city_guides`

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

This is a RAG system over `city_guides`, a corpus of 14 travel guides covering
nine fictional towns and five region-wide topics (eating, walking, transport,
seasons, accessibility). It answers specific, factual questions about the
region — prices, opening hours, travel times, and which town suits a
particular need — by retrieving the relevant document sections and generating
an answer grounded only in those sections. Every answer names the file it came
from, and a question the corpus doesn't cover gets an honest refusal instead
of a guess.

## Chunking Strategy

**Chunk size:** no fixed size. Each document is split on its `## ` section
headings (Getting there, Eat and drink, What to see, ...), so a chunk is one
section. A section longer than 500 characters is split further, on its own
paragraph breaks. Measured across all 84 sections in `city_guides`: average
310 characters, median 293. Only 7 sections exceed 500, and every one of
those 7 already breaks into 2–3 blank-line-separated paragraphs, so 500 is
the point past which a section gets split on structure it already has, not
an arbitrary cutoff.

**Overlap:** none. `city_guides` documents are Markdown, one `# Title` line
followed by several `## Heading` sections — the starter's fixed 800-character
windows cut straight through those headings, which is exactly the problem
worth solving (Milestone 3's brief for this corpus). Splitting on the
heading instead means chunks aren't getting cut mid-sentence at the
boundary, so there's no lost context at a cut point to recover with
overlap. What replaces overlap is prepending each document's title to every
one of its chunks: a section like "Getting there" or "Practical notes"
doesn't say which town it's about on its own, and nine of the town guides
share an identical "Practical notes" paragraph that never names its own
town. Nine of the fourteen documents also open with a 120–250 character
intro paragraph before their first heading (e.g. "Brightwater is a river
town of about 40,000 people..."); that's kept as its own chunk, labelled
"Overview", instead of being silently dropped.

I did not change strategy partway through — this is the first and only
chunker written for this project, replacing the starter's
`fallback_split` directly. One known imperfection: one of the five sample
chunks below (`guide_accessibility.md`'s "Overview") is a generic intro
sentence that doesn't name any town at all, which is a real gap in my own
"names a town" rule from `criteria.md` criterion 4 — reported here rather
than hidden.

Produced by: `chunker.py::split_documents`

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `guide_accessibility.md#0` — produced by: `chunker.py::split_documents`

```
Getting around the region with limited mobility

Overview
An honest assessment rather than a promotional one. Some of these places are
difficult and it is better to know in advance.
```

**Chunk 2** — source: `guide_corry_vale.md#3` — produced by: `chunker.py::split_documents`

```
Corry Vale

Eat and drink
One pub in the largest village serves food seven days a week. A second, in the third village, opens Thursday to Sunday. There is a farm shop at the valley mouth that sells bread, cheese and little else, and it closes at 4pm. Bring supplies; this is not a place with options.
```

**Chunk 3** — source: `guide_givens_mill.md#1` — produced by: `chunker.py::split_documents`

```
Givens Mill

Getting there
No station and no bus on Sundays; four buses a day from Brightwater on weekdays, taking 30 minutes. Driving is 20 minutes. The village car park holds about forty cars and is full by 11am on summer Saturdays.
```

**Chunk 4** — source: `guide_kestrelford.md#5` — produced by: `chunker.py::split_documents`

```
Kestrelford

Where to stay
Two inns on the square and a handful of rooms above the pubs. Booking ahead matters between May and September and not at all otherwise. There is no accommodation of any kind within four miles of the town in either direction.
```

**Chunk 5** — source: `guide_regional_transport.md#1` — produced by: `chunker.py::split_documents`

```
Getting around the region

Buses
Three operators run in the region and they do not accept each other's tickets,
which is the single most common source of confusion for visitors. Services
concentrate on weekday daytimes. Sunday service is minimal to non-existent
outside the Brightwater town routes.

The Kestrelford service is hourly on weekdays, two-hourly on Saturdays, and
does not run on Sundays. The Halden Bay coast service runs four times daily
year-round.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:** Until what time do kitchens in Marchwood serve food on Fridays and Saturdays?

**Answer:**

```
Kitchens in Marchwood serve until midnight on Fridays and Saturdays (guide_marchwood.md).

Sources retrieved: guide_eating.md, guide_kestrelford.md, guide_marchwood.md
```

**My relevance cutoff:** 0.6 (the starter's default, kept as-is).

I ran all five questions from `questions.py` and all five from `OUT_OF_SCOPE`
through `python app.py retrieve "..."` and recorded the best distance for
each. The five in-corpus questions all landed between 0.256 and 0.426; the
five out-of-scope questions all landed between 0.815 and 0.992. That's a gap
of almost 0.4 with nothing in between, so any cutoff from about 0.43 to 0.81
would separate the two groups cleanly here. 0.6 sits well inside that gap, so
I kept it rather than moving it without a reason to.

| Question | In corpus? | Best distance |
|---|---|---|
| How much does it cost to climb the tower of the parish church in Kestrelford? | Yes | 0.426 |
| Until what time do kitchens in Marchwood serve food on Fridays and Saturdays? | Yes | 0.256 |
| How much cheaper is eating on Corry Lane than on the riverside strip in Brightwater? | Yes | 0.295 |
| Where can I buy bread and cheese in Corry Vale? | Yes | 0.365 |
| Which town in the region is easiest to get around for someone with limited mobility? | Yes | 0.279 |
| What is the capital of Mongolia? | No | 0.815 |
| How do I change the oil in a diesel engine? | No | 0.880 |
| Who won the 1994 World Cup? | No | 0.992 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.841 |
| How do I write a for loop in Rust? | No | 0.870 |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.** I asked Claude to design and write the chunking function for
`city_guides`. Before writing any code, it measured section lengths across
all 84 sections in the corpus and used that to justify a 500-character cap,
past which a section splits on its own paragraph breaks instead of staying
whole. I reviewed the actual chunks it produced against the old fixed-window
ones and confirmed they read as complete thoughts. The one thing I changed
was the chunk format — I picked a plain, stacked layout (title, then heading,
then body) over the dash-joined style it also offered.

**2.** I asked Claude to draft the five questions in `questions.py` and their
`expects` phrases, since I wasn't sure how to write them myself. It proposed
a mix — Kestrelford's tower price, Marchwood's kitchen hours, two questions
whose answers appear in two different documents, and a question about
limited mobility — and checked that each `expects` phrase actually appears in
the documents before handing them back. I kept all five as drafted.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
