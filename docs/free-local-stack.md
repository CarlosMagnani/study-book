# Free, local first analysis stage

## Recommendation

Use this two-process pipeline. It has no paid API calls or API keys; models
are downloaded once, then inference stays on the machine.

```text
downloads/<id>/audio.m4a
  -> faster-whisper (small, CPU INT8)
  -> transcript.json (text and timestamps)
  -> Ollama + qwen3:4b
  -> Pydantic validation
  -> analysis.json (topics and summary)
```

`faster-whisper` is the best small learning-project default. It supports CPU
INT8, needs Python 3.9+, and decodes audio through PyAV, whose package bundles
FFmpeg libraries—so the existing M4A files need no separate FFmpeg install.
Its documented CPU benchmark for the `small` model and INT8 used about 1.5 GB
RAM and transcribed 13 minutes of audio in 1m42s on an 8-thread i7-12700K.
That benchmark is directional, not a promise for another computer.
[faster-whisper README](https://github.com/SYSTRAN/faster-whisper#readme)

For text analysis, run `qwen3:4b` with Ollama. The published Ollama package is
2.5 GB and has a 256K context window. Use `qwen3:1.7b` (1.4 GB) only if RAM is
tight; start with 4B for better summaries. [Ollama Qwen3 library](https://ollama.com/library/qwen3)

## Minimal setup

```bash
python -m pip install faster-whisper ollama pydantic
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:4b
```

Ollama serves locally at `http://localhost:11434`; `ollama serve` starts it
when it is not already running. [Ollama Linux installation](https://docs.ollama.com/linux)

## Implementation shape

```python
from faster_whisper import WhisperModel

model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe("audio.m4a", beam_size=5)
segments = list(segments)  # transcribes and retains start/end/text
```

Keep each segment's `start`, `end`, and `text` in `transcript.json`. The
segments iterator must be consumed before transcription actually runs.
[faster-whisper usage](https://github.com/SYSTRAN/faster-whisper#usage)

Define one Pydantic `Analysis` model (for example: `topics`, `summary`,
`key_points`, `language`), pass `Analysis.model_json_schema()` as Ollama's
`format`, and parse the reply with `Analysis.model_validate_json(...)`. Ollama
documents this schema-plus-validation pattern and recommends temperature `0`
for more repeatable structured output. Do not save `analysis.json` if
validation fails. [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs)

## Alternatives and caveats

| Need | Choice | Trade-off |
| --- | --- | --- |
| Simplest CPU transcription | `faster-whisper`, `small`, INT8 | First model load downloads model weights. |
| Lowest resource use | `faster-whisper`, `base`, INT8 | Lower transcription accuracy. |
| Reference Whisper implementation | `openai-whisper` | Requires a system FFmpeg installation; use only if you need that implementation. [OpenAI Whisper](https://github.com/openai/whisper#setup) |
| Smallest text model | `qwen3:1.7b` | Less reliable topic labels and summaries than 4B. |

This phase does **not** need a multimodal model: topic classification and a
summary of spoken content come from the transcript. Add visual analysis only
when a video contains meaning that is not said aloud, such as slides,
on-screen text, charts, or demonstrations. Ollama also supports passing image
inputs with the same schema mechanism when that later step is warranted.
[Ollama vision structured outputs](https://docs.ollama.com/capabilities/structured-outputs#vision-with-structured-outputs)

Model and package downloads are still required, and local inference consumes
your CPU/RAM. Check the model's license before redistributing it; this note is
about avoiding per-request API costs, not legal advice.
