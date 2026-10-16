"""Run: python3 hooks/test_duck.py"""
import contextlib
import io
import json
import os
import tempfile

import duck


def row(kind, mid, blocks):
    return json.dumps({"type": kind, "message": {"id": mid, "content": blocks}})


def text(t):
    return {"type": "text", "text": t}


def run(fn, data):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        fn(data)
    return out.getvalue()


assert duck.check("What did you expect?") is None
assert duck.check("Why? Really?") == "it has 2 question marks, need exactly 1"
assert duck.check("The bug is the mutex.") == "it has 0 question marks, need exactly 1"
assert duck.check("Try this:\n```\nx = 1\n```\nok?") == "it has a code block"
assert duck.check("word " * 25 + "end?") == "it has 26 words, max 25"

with tempfile.TemporaryDirectory() as tmp:
    tempfile.tempdir = tmp
    transcript = os.path.join(tmp, "t.jsonl")
    with open(transcript, "w") as f:
        f.write("\n".join([
            row("user", "u1", [text("hi")]),
            row("assistant", "m1", [text("Old blocked answer with no mark")]),
            row("assistant", "m2", [{"type": "thinking", "thinking": "x"}]),
            row("assistant", "m2", [text("What did you expect?")]),
            json.dumps({"type": "api-request"}),
        ]))
    assert duck.reply_text(transcript) == "What did you expect?"

    sid = {"session_id": "s1"}
    assert run(duck.prompt, {**sid, "prompt": "hello"}) == ""
    assert duck.RULE in run(duck.prompt, {**sid, "prompt": "/duck my bug"})
    assert duck.RULE in run(duck.prompt, {**sid, "prompt": "next"})
    assert run(duck.stop, {**sid, "transcript_path": transcript}) == ""

    with open(transcript, "a") as f:
        f.write("\n" + row("assistant", "m3", [text("The bug is the mutex.")]))
    for _ in range(duck.MAX_RETRIES):
        assert '"block"' in run(duck.stop, {**sid, "transcript_path": transcript})
    assert run(duck.stop, {**sid, "transcript_path": transcript}) == ""

    assert run(duck.prompt, {**sid, "prompt": "duck off"}) == ""
    assert run(duck.prompt, {**sid, "prompt": "next"}) == ""
    assert run(duck.stop, {**sid, "transcript_path": transcript}) == ""

print("ok")
