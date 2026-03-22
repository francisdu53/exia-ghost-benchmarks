# Insight — LLM Hallucinations & the Cognitive Contract

> "A LLM respects an explicit constraint on a known state better than
> an implicit interdiction on an unknown state."

## The Discovery

When we tested 6 different LLMs (Mistral Large, GPT-4o, GPT-4.1, GPT-5.4,
Claude Sonnet 4.6, Llama 3.3 70B) on the same memory task, we expected
that some models would hallucinate more than others. That was true — but
the real insight was deeper.

**All 6 LLMs hallucinated when given vague instructions.** The differences
between models were far smaller than the difference between a vague prompt
and a precise Cognitive Contract.

## What We Found

### Hallucination patterns

- **Mistral Large**: 15 identity confusions + invented elaborate scenes
  (1,850+ characters of pure fabrication, including a dinner scene with
  wine and jazz that never happened)
- **GPT-4o**: invented visual scenes (imaginary bar settings)
- **Claude Sonnet 4.6**: zero errors from the start — followed the contract
  perfectly without any correction needed

### Root cause: implicit gaps

The hallucinations weren't random. They followed a pattern: the LLM
fabricated information to **fill gaps that the contract left implicit**.

Three specific gaps:

1. **No user identity** → the LLM confused different users
2. **Missing memories left blank** → the LLM didn't know it lacked memories,
   so it invented some
3. **Vague "don't lie" instructions** → not actionable enough for the LLM
   to follow consistently

## The Fix — Three Explicit Declarations

| Gap | Before | After |
|-----|--------|-------|
| User identity | (implied) | "You are talking to: [name]. Address only this person." |
| Empty memories | (section omitted) | "Relevant memories: NONE. Never fabricate." |
| Fabrication prohibition | "Don't lie" | "Never confirm what you can't verify. Never imagine a scene you didn't experience." |

### Results after fix

| Metric | Before | After |
|--------|--------|-------|
| Identity confusions | 33 | **0** |
| Scene fabrications | 3 | **0** |
| Models requiring fixes | 4/6 | **1/6** (Mistral residual) |

## The Principle

**The Cognitive Contract is more important than the LLM choice.**

A weak model with a strong contract outperforms a strong model with a
weak prompt. This is because:

1. LLMs are trained to be helpful — when they don't know, they guess
2. The only way to prevent guessing is to **explicitly tell the LLM
   what it doesn't know**
3. "You have NO memories about this" is more effective than
   "Don't hallucinate"

This principle — explicit state over implicit prohibition — is the
foundation of the Cognitive Contract architecture.

## Production Decision

Based on these findings, Claude Haiku 4.5 was selected for production:
- Same disciplined family as Sonnet (which required zero corrections)
- Faster and more cost-effective
- Follows the Cognitive Contract reliably

The architecture doesn't depend on model quality — it controls any LLM
through structural constraints.
