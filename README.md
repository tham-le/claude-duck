# claude-duck

A rubber duck for Claude Code. The duck asks. You think.

Explaining a problem out loud is often enough to solve it. The point is to do the thinking yourself, not hand it to the model. So in duck mode Claude never answers, never hints, never writes code. It asks one short question at a time, built from your own words, and waits.

## Install

As a plugin:

```
/plugin marketplace add tham-le/claude-duck
/plugin install duck@claude-duck
```

Or copy the skill folder by hand:

```
cp -r skills/duck ~/.claude/skills/duck
```

## Use

```
/duck
/duck my service drops the second connection
```

Say "duck off" to go back to normal mode.

## What the duck does

- One question per reply, under 25 words.
- Uses only words you have said. It does not bring in new ideas.
- Does not read code or logs for you. You walk it through.
- "Just tell me" gets "Duck does not tell." and a question.
- When you say "done", it repeats your own conclusion in one sentence.

The rules live in `skills/duck/SKILL.md`.
