# Project Coach AI

**Free open-source AI interview copilot, live interview assistant, and project defense coach**

Project Coach AI is a free, open-source interview coach that listens to live questions, drafts natural talking points in real time, and helps you answer without sounding like you are reading from a script.

It is designed for:

- live interview answers and speaking cues
- AI interview practice and mock interview preparation
- project defense, founder demos, oral exams, and technical walkthroughs
- people who want a free interview copilot instead of a paid subscription tool

Project Coach AI was created by **Abaka Daniel Ugonna** AKA **Big Dreams Web3**.

## Why People Use It

Many people search for tools like:

- free AI interview assistant
- live interview AI
- AI interview answer generator
- interview copilot free
- real-time AI interview helper
- project defense coach

Project Coach AI focuses on the part that matters most in a real conversation: it does not just print a long answer. It listens, generates short speaking cues, and tracks what you actually say so the next point feels natural.

## What Makes It Different

- It generates **speaking cues**, not heavy script paragraphs.
- It listens during live interview questions and drafts guidance before the interviewer fully finishes.
- It listens while you answer and moves a green `NEXT` cue as your spoken answer progresses.
- It uses AI to inspect observations and propose project-improvement rules when it detects a design, security, privacy, or architecture issue.
- It does local cue tracking after the AI response is generated, which helps reduce API cost.
- It can study a real project folder, a documentation folder, or a project brief file before generating guidance.
- It shows the configured AI models and the last model used in the console and UI.
- It is free and open source.

## How It Works

### 1. Study the source material

Point Project Coach AI to:

- a codebase
- a docs folder
- a pitch note or project brief
- multiple sources at once

### 2. Listen to the question

In live mode, the app listens to the interviewer, detects pauses, and generates answer cues in real time.

### 3. Coach the answer

Instead of showing a book-like paragraph, it gives short points to say next. As you speak, it listens locally and advances the cue list when your spoken answer covers the current point.

### 4. Propose project improvements

Project Coach AI appends questions, cues, and answer observations to the observations file. It also runs a small AI review on those observations and writes improvement proposals when it detects a real product-design issue, privacy leak, security concern, incorrect project premise, or weak architecture assumption.

Improvement proposals are not applied automatically. You approve them before they become active coach rules.

## Best Fit Use Cases

- free AI interview practice tool
- real-time interview answer support
- live interview speaking coach
- founder pitch and startup demo prep
- technical project defense prep
- behavioral interview practice
- engineering walkthrough rehearsal
- AI-assisted project design review
- privacy and security defense preparation

## Quick Start

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

The active rules file is fixed at `project-coach-rules.md`. It is loaded directly by the app and is not configurable through the env file.

Run the app:

```powershell
python -m project_coach
```

## Live Interview Mode

Live Interview Mode is the strongest part of the app for real-time use:

- it listens to the interviewer
- it detects silence and question boundaries
- it drafts answer cues with low-cost models
- it uses a transparent overlay so you can still see the interviewer
- it listens to your answer and advances the next cue locally

This makes it more useful than a plain AI answer generator, because the tool keeps coaching delivery, not just content.

## Practice Mode

Practice Mode is built for repetition:

- it generates project-aware practice questions
- it waits for a meaningful spoken answer instead of accepting random silence
- it keeps listening until enough useful context is captured
- it writes observations that can later be reviewed for product improvements
- it runs a low-token AI proposal review when a question or observation suggests a project-design problem

## Cost Control

Project Coach AI defaults to lower-cost settings:

- `gemini-2.5-flash-lite` first
- `claude-haiku-4-5` fallback
- smaller context windows
- shorter outputs
- small AI review budget for improvement proposals
- optional model answers disabled by default in practice mode
- local cue tracking after generation

Current budget controls in `project_coach\.env`:

```env
PROJECT_COACH_PROVIDER_ORDER=gemini,claude
PROJECT_COACH_PRACTICE_MODEL_ANSWER=false
PROJECT_COACH_QUESTION_MAX_TOKENS=90
PROJECT_COACH_ANSWER_MAX_TOKENS=220
PROJECT_COACH_LIVE_DRAFT_MAX_TOKENS=170
PROJECT_COACH_PROPOSAL_MAX_TOKENS=180
PROJECT_COACH_PRACTICE_CONTEXT_CHARS=3500
PROJECT_COACH_LIVE_CONTEXT_CHARS=2800
PROJECT_COACH_LIVE_REGENERATE_AFTER_CHARS=160
PROJECT_COACH_LIVE_WINDOW_ALPHA=0.52
PROJECT_COACH_MIN_ANSWER_WORDS=10
PROJECT_COACH_MIN_ANSWER_KEY_TERMS=4
PROJECT_COACH_OBSERVATIONS_PATH=project-coach-observations.md
PROJECT_COACH_IMPROVEMENT_PROPOSALS_PATH=project-coach-improvement-proposals.md
```

## How The Content Is Produced

Project Coach AI combines:

- AI-generated question and cue generation
- local speech recognition
- local cue matching
- local answer-quality checks
- local observation logging

The most important behavior after generation, especially cue progression and answer capture checks, happens locally rather than through repeated AI calls.

## Observation-To-Rule Flow

Project Coach observations do not automatically rewrite `project-coach-rules.md`.

When an observation suggests the coach misunderstood the architecture or surfaced a weak product-design premise, Project Coach asks the configured AI model to inspect the observation against the project context and active rules. If the model finds a real issue, Project Coach writes an improvement proposal to `PROJECT_COACH_IMPROVEMENT_PROPOSALS_PATH`.

A proposed rule becomes active only after you approve it from the UI, which appends it to `project-coach-rules.md`. This keeps AI useful without letting it silently rewrite the truth of the project.

## Folder Structure

- `ai/` contains provider clients and prompt builders.
- `coaching/` contains local cue tracking and answer-quality checks.
- `core/` contains config, constants, and shared types.
- `knowledge/` contains project/source loading.
- `observations/` contains the observation writer and improvement proposal flow.
- `speech/` contains microphone and transcription handling.
- `ui/` contains the practice/live interfaces and UI formatting helpers.

## Support The Project

If Project Coach AI helps you:

- star the repository
- share it with other founders, students, and job seekers
- tip the developer if you want to support future improvements

Solana tip address:
`GccmLozniucy66RnzDQYvBK2dtWgaAktN8gYfzkTobRM`

Project Coach AI is part of the broader work of **Abaka Daniel Ugonna** AKA **Big Dreams Web3**.
