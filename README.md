# claude-duck

A rubber duck for Claude Code that cannot answer, even if you beg. The duck asks. You think.

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

- One question per reply, under 40 words.
- Builds on the whole conversation. It asks about the facts you gave, with concrete options to pick from, never a plain "what do you mean?".
- Never names a cause, a fix, or a technique.
- Does not read code or logs for you. You walk it through.
- "Just tell me" gets "Duck does not tell." and a question.
- When you say "done", it repeats your own conclusion in one sentence.

## Enforced, not asked

A Stop hook reads each reply and sends it back if it has a code block, more or less than one question mark, or over 40 words. The model gets the reason and writes it again, up to three times. So the duck cannot answer even if you beg. The hook turns on with `/duck` and off with `duck off`. Needs `python3`.

The rules live in `skills/duck/SKILL.md`, the hook in `hooks/duck.py`.
