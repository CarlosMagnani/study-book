# Instagram Video Study Pipeline PRD

## Problem Statement

The project can download audio and metadata from an Instagram video, but it
cannot yet turn that material into useful study notes. The next learning goal
is a small, understandable local pipeline that produces a transcript and a
structured summary from one downloaded video.

## Solution

Extend the working ingestion step in this order:

1. Download an Instagram video's audio and metadata. This already works.
2. Transcribe the audio locally, including timestamps.
3. Classify the transcript into a topic and generate a concise summary.
4. Validate and save the analysis as structured JSON.
5. Run every stage from a small command-line interface.

Each completed stage saves its output beside the input video so that it can be
inspected, rerun, and understood independently.

## User Stories

1. As a learner, I want to supply an Instagram URL so that I can begin with a
   real video.
2. As a learner, I want the video audio and source metadata saved separately
   so that I can inspect what was downloaded.
3. As a learner, I want a local transcription step so that I can study spoken
   content without sending audio to a paid API.
4. As a learner, I want transcript segments with timestamps so that I can find
   the relevant point in the video.
5. As a learner, I want a topic and summary generated from the transcript so
   that I can quickly understand the video's main idea.
6. As a learner, I want the generated analysis validated before it is saved so
   that later code can rely on a stable structure.
7. As a learner, I want to run and verify one stage at a time so that I can
   understand the foundation rather than treat the pipeline as a black box.
8. As a learner, I want useful error messages when an expected input is absent
   so that I know which earlier stage to run.
9. As a learner, I want to rerun a stage without redownloading the video so
   that experimentation is quick.

## Implementation Decisions

- The pipeline remains local and free for this milestone.
- The existing ingestion behavior is retained as the first stage.
- Transcription uses Faster-Whisper with a CPU-friendly model as the initial
  configuration. Model selection stays easy to change after the baseline
  works.
- A transcript is the contract between transcription and analysis. It contains
  the source identifier, language when available, full text, and timestamped
  segments.
- Analysis uses a local Ollama model. It receives transcript text, not audio or
  video.
- The analysis contract contains a topic, concise summary, key points, and
  optional source timestamps when the model can support them reliably.
- Pydantic validates analysis data before it is written. Invalid model output
  is reported rather than saved as a successful result.
- Commands stay separate: ingest, transcribe, and analyze. A combined command
  is deferred until the individual steps are understood and working.
- Each stage reads the prior stage's saved artifact and writes one new artifact.
  No database is needed.

## Step-by-Step Implementation Plan

### Step 1 — Define the transcript contract

Create the minimal structured shape for a transcript and one small check that
proves it can be saved and loaded. Do not run transcription yet.

**Done when:** a sample timestamped transcript has a documented, stable JSON
shape.

### Step 2 — Add local transcription

Read saved audio, run Faster-Whisper, and write the transcript contract from
Step 1.

**Done when:** one downloaded video's audio produces a readable transcript
artifact with timestamps.

### Step 3 — Define the analysis contract

Create the validated shape for topic, summary, and key points. Validate a
sample response before connecting an LLM.

**Done when:** malformed analysis data fails clearly and valid data can be
saved.

### Step 4 — Add local transcript analysis

Send transcript text to Ollama and validate the returned analysis against the
Step 3 contract.

**Done when:** a real transcript produces a valid topic and summary artifact.

### Step 5 — Add stage commands and safeguards

Expose transcription and analysis as small commands. Check that prerequisite
artifacts exist and explain what command should run first when they do not.

**Done when:** each command can be executed and verified independently.

### Step 6 — Run one end-to-end example

Use one public Instagram video to run ingest, transcribe, and analyze. Inspect
every produced artifact manually.

**Done when:** the pipeline outputs audio metadata, a transcript, and
validated study notes for the same source video.

## Testing Decisions

- Tests focus on saved artifacts and command outcomes, not implementation
  details inside the transcription or LLM libraries.
- The transcript and analysis contracts each receive a small validation test.
- Transcription and LLM calls are not required for every fast test run; one
  manual real-video check verifies the installed local tools end to end.
- Existing URL validation remains covered by the current unit test.

## Out of Scope

- Video-frame, image, or scene analysis.
- A multimodal model.
- Embeddings, vector databases, retrieval, or chat over a video collection.
- Web UI, background jobs, accounts, or cloud deployment.
- Automatic language translation.

## Further Notes

Spoken-content study does not require a multimodal model. Add vision only if
the learning value depends on visual material not represented in speech, such
as slides, diagrams, demonstrations, or on-screen text.

The previous research is available in the local-stack and model-selection
documents. This PRD deliberately chooses the local stack for the first
implementation milestone.
