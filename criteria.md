# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:** One of my questions (question 5, about limited mobility) is answered in only one document, so if that chunk doesn't come back in the top 5, retrieval has nothing to fall back on.
<!-- e.g. "One of my questions is about a topic only two documents mention, so
     I expect that one to be hard." -->

---

## 2. Every answer names a source

Every answer the system produces names at least one source document. A refusal from the relevance gate isn't an answer and doesn't need a source.

**Why this target:** I picked 5 of 5 because the file names are fed into the prompt directly by the code, not left to the model to remember or guess, so there's little room for the model to simply forget.
<!-- Why all five and not four? What about your setup makes that achievable —
     or what would have to go wrong for it not to be? -->

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:** I don't know yet what the actual distances will look like. I'm accepting the pre-written 4 of 5 target for now and will judge it honestly against Milestone 4's real numbers.
<!-- What did your distances look like when you set the cutoff in Milestone 4?
     Was there a clean gap, or did the two groups overlap? -->

---

## 4. Something about your chunks

<!-- YOU WRITE THIS ONE.

     How would you know if your chunks were the right size? Name something
     countable or observable.

     Examples of the right shape — don't copy these, they should come from
     what you actually saw in Milestone 3:
       - "At least 4 of 5 sampled chunks read as a complete thought, with no
          sentence cut in half at either end."
       - "No chunk is shorter than 200 characters, since anything below that
          in my corpus turned out to be a heading with no content under it." -->

Pull five chunks using `chunks -n 5` after the new chunker has run, and check each one: a chunk counts as good if it ends cleanly at a sentence boundary and mentions a town by name (its own town for a town-guide chunk, or any town for a cross-cutting chunk). The check passes if at least three of the five chunks are good.



**Why this target:** I picked 3 because the "Practical notes" section is identical in all nine town guides and names only Brightwater, so in the other eight guides a chunk holding just that section fails the own-town test unless the chunker adds the town name. That means one or two of any five chunks could fail because of how the guides are written, so demanding 5 of 5 would be too strict. But if three or more fail, most of the sample is bad, and that points to the chunker itself rather than to that one repeated section. I also saw the starter's chunker cut mid-sentence and leave a 24-character fragment in Milestone 1, so the sentence-end test can fail too.

---

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. It could be about
     speed, about refusals, about a particular kind of question your corpus
     handles badly, about source attribution being correct rather than merely
     present — anything, as long as it names a number or an observable
     outcome. -->

The answers the system gives to my five test questions in `questions.py` stay faithful to the retrieved chunks. A fact is anything in the answer a person could check against the documents: a name, a number, a place, a time, a distance, or a claim like "the nearest full hospital is in Brightwater". Filler wording ("here's what I found") doesn't count. The check passes if, in at least 4 of the 5 answers, every fact can be found in one of the chunks sent to the model (visible with `python app.py ask "..." --show-prompt`). An answer fails if even one fact is missing from those chunks.



**Why this target:**
I chose this target because if LLM doesnt stay faithful to the context while answering, it will hallucinate and will not provide grounded answers. I picked 4 of 5 because one wrong fact fails the whole answer, so a perfect 5 of 5 is very hard and I allow one miss. I did not pick 3 of 5 because one bad answer could be an off day, but two of five means the model is often adding its own facts.


---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
