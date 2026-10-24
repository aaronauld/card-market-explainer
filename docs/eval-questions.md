# Eval questions: labelled price spikes

Each entry is a real price move where the cause is already known. Together they are the answer key for the eval harness:

- **Retrieval** is scored by recall@k: do the right event documents appear in the top k results?
- **Answers** are scored by whether they cite the real cause.

Rule: at least 40% of entries must need two sources to explain fully. These test whether retrieval can find more than one relevant document.

Copy the template below for each new entry, numbering them Q-001, Q-002, and so on.

---

## Template

### Q-000: <card name> (<set>, <card number>)

- **Card:**
- **Approximate date of move:** YYYY-MM (or YYYY-MM-DD if known)
- **Direction and size:** e.g. up ~3x over two weeks
- **Real cause:**
- **How I know:** links or references that confirm the cause
- **Sources needed:** 1 or 2
- **Event docs:** filenames in `data/events/` that should be retrieved (fill in once written)

---

## Entries

<!-- Add entries below, starting at Q-001 -->
