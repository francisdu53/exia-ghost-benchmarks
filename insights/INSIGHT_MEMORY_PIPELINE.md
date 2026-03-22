# Insight — Memory Pipeline: When Everything Works But Nothing Connects

> The problem was never memory quality. It was memory disconnection.

## The Discovery

EXIA GHOST has 5 memory systems — contextual (short-term), semantic (facts),
episodic (events), procedural (skills), and prospective (plans). Each one
worked perfectly in isolation. Tests passed. Storage worked. Retrieval worked.

But in production, the AI had **no memory of previous conversations**.

## What Was Wrong

The memory systems were **not wired into the cognitive pipeline**. The memories
existed in storage but were never injected into the Cognitive Contract that
controls the LLM response. The LLM never saw the memories — so it responded
as if every conversation was the first.

```
What we thought was happening:
  User message → retrieve memories → inject into contract → LLM responds

What was actually happening:
  User message → empty contract → LLM responds (no memories)
  Memories stored → sitting unused in database
```

This is a classic integration bug: every component works, but the wiring
between them is missing.

## The Fix

Two integration points were added:

1. **Before the response** (consciousness stage):
   Query contextual + semantic + episodic memory in parallel.
   Inject the top results into the Cognitive Contract.

2. **After the response** (memorization stage):
   Store the user message and AI response into all relevant memory stores.

### Compression strategy

Memory injection adds tokens to the LLM prompt. To keep costs manageable:
- Top 5 memories per query
- 200 characters max per memory
- Total overhead: **+130 tokens per exchange (+18%)**
- With prompt caching (static contract cached by the LLM provider),
  the actual cost increase is minimal

### Explicit absence declaration

When no memories are found, the contract now explicitly states:
"NO relevant memories available — NEVER fabricate."

This prevents the LLM from hallucinating to fill the gap (see the
[LLM Hallucinations insight](INSIGHT_LLM_HALLUCINATIONS.md)).

## Verification Results

After the fix, both Claude Haiku 4.5 and Claude Sonnet 4.6 passed
all 4 verification tests with:
- **0 hallucinations**
- **Cost per exchange: ~$0.003** (Haiku)
- **Cognitive latency: ~20ms** (well under the 50ms budget)

## The Lesson

**Working components ≠ working system.** Memory systems are only valuable
when they're connected to the decision pipeline. A perfect database that
nobody reads is the same as no database.

This experience led to a design principle: every memory store must have
both a **read path** (retrieve → contract → LLM) and a **write path**
(user message → store). If either path is missing, the memory is dead.
