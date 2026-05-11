# Reproduce-Script Generator and Template

Every failing request captured in the bundle gets a generated Python script that reproduces the request **offline** against a mock provider that replays the recorded provider response. The script makes the bug reproducible during the postmortem without re-hitting production providers (cost, rate-limits, side effects) and without re-triggering the bug for customers.

## Generator

```python
# tools/ai_reproduce.py
from __future__ import annotations
from pathlib import Path
import json
from textwrap import dedent

def generate_reproduce_script(trace: TraceRecord, out: Path) -> Path:
    """Write a self-contained reproduce script for a single failing request."""
    payload = {
        "request_id": trace.request_id,
        "feature": trace.feature_id,
        "tenant_id": trace.tenant_id,
        "model": trace.model_id,
        "prompt_version": trace.prompt_version,
        "messages": trace.resolved_messages(),
        "context": trace.retrieval_set(),
        "tools_called": trace.tool_calls(),
        "expected_output": trace.output,
        "captured_at": trace.captured_at.isoformat(),
    }
    fixture_path = out.with_suffix(".fixture.json")
    fixture_path.write_text(json.dumps(payload, indent=2))

    script = dedent(f'''
        """
        Reproduce script for {trace.request_id}
        Incident: {trace.incident_id}
        Feature:  {trace.feature_id}
        Model:    {trace.model_id}
        Prompt:   {trace.prompt_version}

        Run:  python {out.name}
        """
        from __future__ import annotations
        import json, pathlib
        from ai_replay import MockProvider, Replay, AssertSameOutput

        FIXTURE = pathlib.Path(__file__).with_suffix(".fixture.json")
        payload = json.loads(FIXTURE.read_text())

        replay = Replay(payload)
        provider = MockProvider.from_replay(replay)

        result = provider.chat(
            model=replay["model"],
            messages=replay["messages"],
            context=replay["context"],
        )

        print("=== Replay ==================================")
        print(f"request_id     : {{replay['request_id']}}")
        print(f"feature        : {{replay['feature']}}")
        print(f"model          : {{replay['model']}}")
        print(f"prompt_version : {{replay['prompt_version']}}")
        print("=== Expected (recorded) =====================")
        print(replay["expected_output"][:2000])
        print("=== Got =====================================")
        print(result.output[:2000])
        print("=============================================")

        # Postmortem use: change the model / prompt and rerun.
        # provider.chat(model="anthropic/claude-sonnet-4-5-20250929", ...)

        AssertSameOutput(replay["expected_output"], result.output).report()
    ''').strip() + "\n"
    out.write_text(script)
    return out
```

## ai_replay Module (Skeleton)

```python
# ai_replay/__init__.py
from dataclasses import dataclass
from typing import Any

@dataclass
class Replay:
    payload: dict
    def __getitem__(self, k): return self.payload[k]

@dataclass
class MockProviderResult:
    output: str
    raw: dict

class MockProvider:
    """A provider that returns the recorded response for the recorded inputs.
    If inputs differ from the recording (input drift), raise."""
    def __init__(self, replay: Replay):
        self._r = replay
    @classmethod
    def from_replay(cls, replay): return cls(replay)
    def chat(self, model, messages, context=None):
        if model != self._r["model"]:
            raise RuntimeError(f"model drift: recorded={self._r['model']} got={model}")
        if messages != self._r["messages"]:
            raise RuntimeError("messages drift — replay only matches the recorded input")
        return MockProviderResult(output=self._r["expected_output"], raw={})

class AssertSameOutput:
    def __init__(self, expected, got): self.e, self.g = expected, got
    def report(self):
        if self.e == self.g:
            print("[OK] output matches recording")
        else:
            print("[DRIFT] output differs from recording — provider non-determinism or model change")
            print(diff_preview(self.e, self.g))
```

## Postmortem Use

Postmortem authors take the reproduce script and modify it to **answer questions**:

- "What does the new prompt v19 do on this same request?" — change `replay["messages"]` to the v19 system prompt; run.
- "What does Claude Sonnet do that GPT-4o didn't?" — swap provider; rerun.
- "What if retrieval returned the correct chunk?" — modify `replay["context"]`; rerun.

The script is the seed for a **new golden** — failing-request → fixed-request → permanent regression test.

## Anti-Patterns

- Reproduce script calls the live provider — recurses the bug, costs money, triggers customer harm.
- Reproduce script bundled but `ai_replay` module not bundled — script won't run.
- Reproduce script bundled, fixture not bundled — script has nothing to replay.
- Replay tolerates input drift silently — gives a false "I reproduced it" signal when the inputs differ.
- No drift assertion in output — postmortem authors believe they reproduced when they didn't.
