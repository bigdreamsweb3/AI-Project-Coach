# Project Coach

Project Coach is a live interview and project-defense trainer. It listens through your microphone, builds a transcript in short real audio chunks, detects when the speaker has paused, and generates a suggested answer while the question is still being asked.

## Setup

Install the Python packages:

```powershell
python -m pip install -r project_coach\requirements.txt
```

Create the app env file:

```powershell
Copy-Item project_coach\.env.example project_coach\.env
```

Open `project_coach\.env` and set at least one AI provider key:

```env
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
```

Set the project identity and the material the coach should study:

```env
PROJECT_COACH_PROJECT_NAME=TrustLink Pay
PROJECT_COACH_SPEAKER_NAME=Daniel
PROJECT_COACH_SOURCE_PATHS=C:\Users\codepara\Desktop\trust-link
```

`PROJECT_COACH_SOURCE_PATHS` can point to a code folder, a documentation folder, a single project brief, or multiple sources separated with semicolons:

```env
PROJECT_COACH_SOURCE_PATHS=C:\Projects\my-app;C:\Projects\my-app\pitch-notes.md
```

## Run

```powershell
python -m project_coach
```

Choose Practice Mode to generate project-defense questions and model answers from the configured knowledge sources.

Choose Live Interview Mode to listen to a real interviewer, show the transcript, detect pauses, and draft an answer before the interviewer fully finishes the question.

When the answer is ready, Project Coach shows short speaking cues instead of a script. As you answer out loud, it listens locally and moves the green `NEXT` marker through the cues so you know what point to say next without sounding like you are reading.

## Model Configuration

Project Coach defaults to:

- Claude: `claude-haiku-4-5`
- Gemini: `gemini-2.5-flash-lite`

Override them in `project_coach\.env` with `PROJECT_COACH_ANTHROPIC_MODEL` and `PROJECT_COACH_GEMINI_MODEL`.

## Budget Controls

The default settings favor low API cost:

```env
PROJECT_COACH_PROVIDER_ORDER=gemini,claude
PROJECT_COACH_PRACTICE_MODEL_ANSWER=false
PROJECT_COACH_QUESTION_MAX_TOKENS=90
PROJECT_COACH_ANSWER_MAX_TOKENS=220
PROJECT_COACH_LIVE_DRAFT_MAX_TOKENS=170
PROJECT_COACH_PRACTICE_CONTEXT_CHARS=3500
PROJECT_COACH_LIVE_CONTEXT_CHARS=2800
PROJECT_COACH_LIVE_REGENERATE_AFTER_CHARS=160
```

Set `PROJECT_COACH_PRACTICE_MODEL_ANSWER=true` only when you want the app to spend an extra API call generating a sample answer for each practice question.

Increase `PROJECT_COACH_LIVE_REGENERATE_AFTER_CHARS` if live interviews are costing too much. Decrease it only when you need faster draft updates while the interviewer is still speaking.

Cue tracking does not call the AI again. The AI is used to create the cue list; matching your spoken words to the next cue happens locally.
