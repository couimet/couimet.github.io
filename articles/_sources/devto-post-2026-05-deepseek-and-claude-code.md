# Eight env vars and Claude Code stops eating my paycheck

DeepSeek's quick-start page has been live for months. I'm late to it.

I love what Anthropic ships. Opus 4.7 is the best coding model I've used. I also can't run it all day on a family budget, and Pro's 5-hour quota wall stopped my flow more times than I want to count. So a few days ago I exported eight env vars, pointed Claude Code at DeepSeek, and went back to building [rangeLink](https://ouimet.info/projects/rangelink-extension.html). Since then I've only spent $4 and haven't seen a rate limit.

## The eight env vars

```bash
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_AUTH_TOKEN=<your-deepseek-key>
export ANTHROPIC_MODEL=deepseek-v4-pro
export ANTHROPIC_DEFAULT_OPUS_MODEL=deepseek-v4-pro
export ANTHROPIC_DEFAULT_SONNET_MODEL=deepseek-v4-pro
export ANTHROPIC_DEFAULT_HAIKU_MODEL=deepseek-v4-flash
export CLAUDE_CODE_SUBAGENT_MODEL=deepseek-v4-flash
export CLAUDE_CODE_EFFORT_LEVEL=max
```

Run that block in your terminal, then invoke `claude-code`.

## What's going on in there

The subagent model points to `deepseek-v4-flash` instead of `v4-pro`. Claude Code spawns subagents for grep-and-summarize work, and there's no reason to pay pro rates for "find the file that has this string." Flash is good enough for that, and it returns faster.

`CLAUDE_CODE_EFFORT_LEVEL=max` keeps the quality slider cranked on the cheap path. The flag exists; you may as well use it.

Anthropic's three tiers (Opus, Sonnet, Haiku) get collapsed onto DeepSeek's two. Opus and Sonnet both map to `v4-pro` because that's the strongest model DeepSeek serves. Haiku goes to `v4-flash` because nothing about Haiku-class work needs more than that.

## Why I'm still using this a week later

**Cost.** I bought $10 of `deepseek-v4-pro` credits last week. After five days of 3-6 hours a day on rangeLink, $6 is still on the meter. I stopped checking the balance after day three because it wasn't going anywhere fast.

**No 5-hour quota wall.** Anthropic Pro's quota window resets on a 5-hour cycle, and hitting it mid-task is the worst kind of interruption. You've built up context, you're in the middle of something, and now you're either waiting or paying for top-up. Since I switched: zero waits. Not "fewer." Zero.

The second one matters more than I expected. Going in, I was solving for cost. I figured rate limits were a nice-to-have.

## The catch I hit

Pasted images in the terminal don't make it through to DeepSeek's API. If your workflow leans on screenshots — "look at this dev-tools error" or "match this design" — this swap will hurt.

Community work is happening here. I'm not going to recommend anything I haven't fully tested.

## Same trick, different provider

A friend was already running DeepSeek with [OpenClaw](https://docs.openclaw.ai/) and happy with it, so I copied his pick when I made the switch. Two worth a look as of May 2026:

- **Moonshot Kimi K2.5** — `ANTHROPIC_BASE_URL=https://api.moonshot.ai/anthropic`, model `kimi-k2.5`. [Moonshot's Claude Code setup docs](https://platform.kimi.ai/docs/guide/agent-support).
- **Z.ai GLM-5.1** — `ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic`, model `glm-5.1`. [Z.AI Claude Code docs](https://docs.z.ai/devpack/tool/claude).

If you've run Kimi or GLM with Claude Code, I'd be curious how it went.

## A note on privacy

Your prompts go to DeepSeek's servers. Fine for my public-repo work. Pick a provider whose data policy matches your repos' sensitivity.

---

Five days, $4 spent, zero rate-limit walls.

If your employer foots the Anthropic bill, or your wallet can swing a Max plan, by all means — Opus 4.7 is still the best at the top end. If that's not you, eight env vars.

```
Co-Authored-By: Claude <noreply@anthropic.com> (running on deepseek-v4-pro)
```
