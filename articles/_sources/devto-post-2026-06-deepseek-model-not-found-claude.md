---
title: 'Fix: "There''s an issue with the selected model (deepseek-v4-pro)" in Claude CLI'
published:
tags: claudecode, deepseek, ai, debugging
cover_image:
---

# Fix: "There's an issue with the selected model (deepseek-v4-pro)" in Claude CLI

If you landed here from a search engine, here's the error you saw:

```text
There's an issue with the selected model (deepseek-v4-pro). It may not exist or you may not have access to it. Run /model to pick a different model.
```

You had the eight env vars from my [previous article](https://dev.to/couimet/eight-env-vars-and-claude-code-stops-eating-my-paycheck-2659) set. You opened a fresh terminal, typed `claude`, and got that. Same.

A quick glossary for this article: `claude-code` is the brew package. `claude` is the command you type in your terminal.

## I thought Anthropic was on to me

I'll admit where my brain went first: Anthropic had patched `claude-code` to block non-Anthropic API keys. DeepSeek built a fully backwards-compatible API: same endpoints, same request shape, same response format. Anthropic ships a new `claude-code` version, I run `brew upgrade` without thinking, and suddenly my DeepSeek setup breaks. The timing was too clean.

And here's the really self-absorbed part of this theory: my article explaining the DeepSeek setup had been live on dev.to for a couple weeks. It was getting reads. What if someone at Anthropic saw it and that was their "alright, that's enough" moment? A human being in San Francisco read my post, opened a Jira ticket, and a week later the validation shipped.

Classic Coyote: draw the plan, check the ground later. Anthropic, a company with thousands of employees building frontier AI, was not reacting to my dev.to post. They probably have bigger things to worry about than one person's $10 DeepSeek bill. But the theory *felt* good, and the error message didn't give me much else to work with.

I also googled the exact error string. Zero English results. A few forum posts, all written in 中文. That vacuum didn't help. When nobody in English is talking about an error, your brain writes its own screenplay. Mine went full [Wile E. Coyote](https://en.wikipedia.org/wiki/Wile_E._Coyote_and_the_Road_Runner), sketching elaborate traps that weren't there.

## What was actually happening

`claude` wasn't contacting DeepSeek at all. It was talking to Anthropic.

The reason was a missing newline in my setup script. After publishing the original article, I'd moved the eight `export` lines into `~/point-to-deepseek.sh` so I could `source` the file instead of pasting the block into my terminal. API keys are like underwear: you don't share them, and pasting one into a terminal left it sitting in my scrollback for anyone to see.

In that file, two lines had merged into one. The line starting with `export ANTHROPIC_BASE_URL=...` had the `export ANTHROPIC_AUTH_TOKEN=...` line glued to its end, with no newline between them. The shell saw one corrupt line. `ANTHROPIC_AUTH_TOKEN` never got exported. `ANTHROPIC_BASE_URL` got set to nonsense.

Coyote looked down.

```bash
# what the shell saw (broken)
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic export ANTHROPIC_AUTH_TOKEN=sk-xxx

# what it should look like (fixed)
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_AUTH_TOKEN=sk-xxx
```

## A related edge case: resuming a DeepSeek session in an Anthropic context

I said my panic was a false alarm, but one thing has actually changed since I wrote the original setup guide. When I first published it, I was routinely starting sessions on one provider and resuming them on the other — mostly DeepSeek sessions that I'd pick back up on Anthropic after my 5-hour quota reset. That stopped working about a week or two ago.

If you start a `claude` session pointed at DeepSeek, `/exit`, then try to `/resume` it from a `claude` instance pointed at Anthropic, you get:

```text
API Error: 400 messages.1.content.0: Invalid `signature` in `thinking` block
```

The reverse still works. I resume Anthropic sessions on DeepSeek every day with no issues. So it's not a two-way wall — it's a one-way door, and it only catches you going in one direction.

Whether it's a deliberate countermeasure or a format mismatch between two implementations of the same API is unconfirmed. But unlike my imaginary `claude-code` patch, this one is real.

## Why I'm really writing this

I said zero English results. That vacuum is the real reason this article exists. Somebody is going to hit this error, google it, and land here. That's the bet.

And now I'm publishing a second article about a missing newline, SEO-optimized around an error message, hoping Google indexes it before the next person loses time to this.

I'd spent half an hour convinced I was the protagonist in a David-and-Goliath story about API compatibility. Anthropic had noticed my workaround. They'd shipped a countermeasure. I was drafting the exposé in my head. Classic Coyote.

The eight env vars still work. I'm still using them.

---

If you got here from the error message, I hope this saved you the 30 minutes I lost. Never saw the original setup? [It's here.](https://dev.to/couimet/eight-env-vars-and-claude-code-stops-eating-my-paycheck-2659)

---

*My friend Joel, after I shared [a recent article on LinkedIn](https://www.linkedin.com/feed/update/urn:li:activity:7463240605780074496/): "You can't teach old dogs new tricks, but you can force them to become LinkedIn influencers!" I am now publishing a second one about a missing newline. Yeah, I'm looking at you, dear Joel. 😉*
