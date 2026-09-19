# First analysis stage

## Decision

Use two API calls:

1. Send `downloads/<id>/audio.m4a` to `gpt-transcribe` and save its text as
   `transcript.json`. OpenAI recommends it as the starting model for
   original-language transcription; M4A is supported and uploads are limited to
   25 MB. [Speech-to-text guide](https://developers.openai.com/api/docs/guides/speech-to-text)
2. Send the transcript text to `gpt-5.6-luna` with a strict JSON Schema. It is
   the cost-sensitive/high-volume option. If the summaries are not good enough,
   change that one model name to `gpt-5.6-terra`, which targets a better
   intelligence/cost balance. [Model catalog](https://developers.openai.com/api/docs/models)

Keep these calls separate: `gpt-transcribe` is audio-only and does not support
Structured Outputs. [gpt-transcribe model page](https://developers.openai.com/api/docs/models/gpt-transcribe)

## Structured result

Use a Pydantic model (or an equivalent JSON Schema) with fields such as
`topics`, `summary`, `key_points`, and `language`. Pass it to the Responses API
as `text.format` with `type: "json_schema"` and `strict: true`; Structured
Outputs guarantees the response conforms to the supplied schema. Define the
allowed topic list before implementation and include `other` as a fallback.
[Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs)

## Do we need multimodal?

No—not for transcription, topic classification, or a summary of what was
said. A transcript is enough.

Add vision only when the meaning depends on visuals: on-screen text, slides,
demonstrations, charts, or events that the speaker does not describe. At that
point, extract a small set of video frames and send the frames plus the
transcript to the analysis model. The API accepts image inputs alongside text;
it does not need a full-video upload for this first version.
[Vision guide](https://developers.openai.com/api/docs/guides/images-vision)

For simple time alignment, preserve transcript timestamps and map each time
range to a video frame. That is deterministic metadata work, not a reason to
add a multimodal model.
