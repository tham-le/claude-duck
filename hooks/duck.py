#!/usr/bin/env python3
"""Duck hooks. `prompt` tracks duck mode. `stop` rejects a reply that is not one short question."""
import json
import os
import re
import sys
import tempfile

MAX_WORDS = 40
MAX_RETRIES = 3
ON = re.compile(r"^/(duck:)?duck\b", re.I)
OFF = re.compile(r"^(duck off|stop duck)\b", re.I)
RULE = "Duck mode is on: reply with one question, under 40 words, no code, exactly one question mark."


def state_path(session):
    return os.path.join(tempfile.gettempdir(), f"claude-duck-{session}")


def read_tries(path):
    try:
        with open(path) as f:
            return int(f.read() or 0)
    except (OSError, ValueError):
        return 0


def write_tries(path, n):
    with open(path, "w") as f:
        f.write(str(n))


def prompt(data):
    path = state_path(data.get("session_id", "none"))
    text = (data.get("prompt") or "").strip()
    if OFF.match(text):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        return
    if ON.match(text):
        write_tries(path, 0)
    if os.path.exists(path):
        print(RULE)


def reply_text(transcript):
    """Fallback when the hook payload has no last_assistant_message. Rows of one message share its id."""
    rows = []
    with open(transcript) as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except ValueError:
                continue
    last_id = None
    parts = []
    for row in reversed(rows):
        kind = row.get("type")
        if kind == "user":
            break
        if kind != "assistant":
            continue
        msg = row.get("message") or {}
        if last_id is None:
            last_id = msg.get("id")
        if msg.get("id") != last_id:
            break
        for block in msg.get("content") or []:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
    return "\n".join(reversed(parts))


def check(text):
    """Why the reply breaks duck mode, or None."""
    if "```" in text:
        return "it has a code block"
    marks = text.count("?")
    if marks != 1:
        return f"it has {marks} question marks, need exactly 1"
    words = len(text.split())
    if words > MAX_WORDS:
        return f"it has {words} words, max {MAX_WORDS}"
    return None


def stop(data):
    path = state_path(data.get("session_id", "none"))
    if not os.path.exists(path):
        return
    text = data.get("last_assistant_message")
    if text is None:
        transcript = data.get("transcript_path", "")
        if not os.path.isfile(transcript):
            return
        text = reply_text(transcript)
    why = check(text)
    tries = read_tries(path)
    if why is None or tries >= MAX_RETRIES:
        write_tries(path, 0)
        return
    write_tries(path, tries + 1)
    print(json.dumps({"decision": "block", "reason": f"{RULE} Rejected: {why}. Write it again."}))


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
    except ValueError:
        data = {}
    {"prompt": prompt, "stop": stop}[sys.argv[1]](data)
