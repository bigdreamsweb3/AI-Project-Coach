# Project Coach AI

**Think in Code. Speak in Systems.**

---

## What is Project Coach AI?

Project Coach AI is an **AI Project Understanding Engine**.

It studies real software projects and helps developers understand, explain, defend, and improve them.

The interview assistant is only one capability. The real purpose is to become an **AI Project Understanding Engine**—the same way an experienced engineer, auditor, architect, founder, investor, or interviewer would understand a software project.

Project Coach AI understands entire software projects by examining:

- source code structure and patterns
- documentation and comments
- APIs and endpoints
- functions and classes
- configuration and architecture
- project briefs and design notes

It then communicates that understanding using **systems-level concepts**—not implementation details.

> **Example:** It internally understands `POST /api/auth/login` but externally communicates "Login Authentication Flow."

---

## Why Does It Exist?

Developers often build systems they understand while writing them. Later, they struggle to explain:

- **Why** an architecture exists
- **Why** a security model was chosen
- **What** tradeoffs were accepted
- **How** to defend decisions during interviews, demos, audits, or presentations

The gap between building and explaining is real. Project Coach AI closes that gap.

After using Project Coach AI, developers finish sessions not only better prepared—they have a deeper understanding of their own project.

---

## The Understanding Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PROJECT INPUT                                   │
├─────────────────────────────────────────────────────────────────────────┤
│   Source Code    Documentation    Project Briefs    Comments          │
│   ───────────    ────────────    ─────────────    ─────────          │
│   *.py, *.ts     README.md       ARCHITECTURE     docstrings          │
│   *.js, *.rs     DESIGN.md       product specs    // why notes        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      SYSTEM TRANSLATOR                                 │
├─────────────────────────────────────────────────────────────────────────┤
│   Implementation Patterns ──────► System Concepts                      │
│   ──────────────────────        ────────────────                       │
│   auth endpoints      ──────►  Authentication Flow                    │
│   payment handlers    ──────►  Payment Authorization                  │
│   encrypt/decrypt     ──────►  Privacy Protection                      │
│   database models     ──────►  Data Persistence                       │
│   audit logging       ──────►  Audit Trail                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       WHY EXTRACTION                                    │
├─────────────────────────────────────────────────────────────────────────┤
│   Purpose statements    Design rationale    Tradeoffs made             │
│   ────────────────     ───────────────    ──────────────             │
│   "protects against"   "designed to"      "tradeoff is"               │
│   "prevents"           "because"          "妥协 (compromise)"         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     UNDERSTANDING OUTPUT                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   Project Defense          Architecture Explanation                     │
│   ──────────────          ──────────────────────                       │
│   "Why settlement         "The payment flow protects                  │
│    before authorization?"   against unauthorized                      │
│                            transfer by requiring..."                   │
│                                                                       │
│   Interview Coaching      Security Review                             │
│   ────────────────       ────────────────                            │
│   "How would you          "What assumptions does                      │
│    explain this to         this privacy model                        │
│    an investor?"           rely on?"                                  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Think in Code. Speak in Systems.

The core design philosophy:

**Internally**, the coach may inspect:
- Files and folders
- Endpoints and APIs
- Functions and classes
- Database models
- Smart contracts
- Configuration

**Externally**, it explains:
- Authentication flows
- Settlement processes
- Identity verification
- Payment authorization
- Trust boundaries
- Privacy protections
- Security models
- Architecture decisions
- Product tradeoffs

**Implementation details become supporting evidence—not the primary explanation.**

### Example Transformations

| Instead of asking... | The coach asks... |
|---------------------|-------------------|
| "What does `/api/auth/login` do?" | "Why does the authentication flow validate identity before creating a trusted session?" |
| "What does `transfer_vault()` do?" | "What responsibility does the settlement layer have during a payment?" |
| "Explain the encryption module." | "How does this privacy protection build user trust?" |

### Answer Style

Answers are designed for **speaking**, not documentation:

> "Before anyone can proceed, the system double-checks that the identity presented is still trusted—similar to showing your boarding pass again before entering the aircraft instead of only at the airport entrance."

---

## Product Capabilities

Project Coach AI provides these capabilities:

| Capability | Description |
|------------|-------------|
| **Project Understanding** | Deep analysis of architecture, patterns, and decisions |
| **Architecture Explanation** | Clear communication of design rationale |
| **Technical Interview Preparation** | Practice answering questions confidently |
| **Project Defense** | Defend technical decisions to reviewers |
| **Security Review** | Prepare for security-focused questioning |
| **Privacy Review** | Explain privacy protections clearly |
| **Founder Demo Preparation** | Explain technical work to investors |
| **Audit Question Generation** | Generate auditor-level questions |
| **Live Speaking Coach** | Real-time cue generation while you speak |
| **Observation-Based Learning** | Coach improves from experience |

### How Capabilities Map to Features

- **Practice Mode** → Interview preparation, architecture review, security review, project defense
- **Live Mode** → Live speaking coach, real-time cue generation
- **System Translator** → Project understanding, architecture explanation
- **Observation Engine** → Observation-based learning, continuous improvement
- **Audience Settings** → All capabilities adapt to different audiences

---

## Advanced Features

### Audience Switching Mid-Session

Change the explanation audience without restarting the session. Future questions, answers, and cues adapt immediately.

In Practice Mode or Live Mode, use the audience dropdown to switch between:
- **non-technical** — Simple language, analogies for investors/clients
- **semi-technical** — Balanced approach for founders/product people
- **technical** — More detail for engineers
- **expert** — Full precision for auditors/security reviewers

### System Concept Editor

Review and refine auto-detected system concepts.

Click **Edit Concepts** to:
- View detected concepts (Authentication Flow, Payment Authorization, etc.)
- Add custom analogies for specific concepts
- Save changes to persist across sessions

The editor saves to `project-coach-concepts.md` by default.

### Custom Analogy Library

Define project-specific analogies that the coach uses when explaining concepts.

Example custom analogies:
```
TSN settlement like: a secure middle office that checks both sides before releasing value
TINS like: a phonebook for payments that doesn't expose full personal details
```

Custom analogies are saved and reused for future coaching sessions.

### Why Extraction with Categories

The why extraction now categorizes findings:

- `[purpose]` — Why something exists
- `[protection]` — What it protects against
- `[tradeoff]` — Design compromises made
- `[risk]` — Potential failure scenarios
- `[todo]` — Developer notes with reasoning

### Quality Analytics (Lightweight)

Explanation quality is tracked in observations:

- **Helpful** — Cues helped explain clearly
- **Needs Work** — Cues need improvement
- **Not Useful** — Cues didn't help

Quality ratings are logged alongside generated cues for future analysis.

---

## Real Workflow Examples

### Preparing for a Software Engineering Interview

1. Point Project Coach to your portfolio project
2. Practice Mode generates questions like:
   - "Why is this authentication step placed before session creation?"
   - "What would break if this validation check disappeared?"
3. Answer while speaking; the coach tracks your delivery
4. Rate explanation quality to improve future sessions

### Defending a Startup Architecture

1. Set audience to `semi-technical` for investor meetings
2. Point to your technical architecture documentation
3. Practice explaining system purposes, not implementation
4. Use Live Mode during actual demos for real-time support

### Explaining a Blockchain Protocol

1. Point to your smart contracts and documentation
2. Set audience based on who you're addressing (investors, developers, regulators)
3. The system translates contract functions to protocol concepts
4. Generate questions an auditor might ask about settlement logic

### Reviewing a Security-Sensitive Application

1. Set audience to `expert` for security reviews
2. The coach surfaces privacy and security patterns in your code
3. Practice explaining attack surfaces and protections
4. Generate auditor-level questions about assumptions

### Preparing for an Investor Demo

1. Set audience to `non-technical`
2. The coach emphasizes analogies and simple explanations
3. Practice explaining what the system does for users, not how it works
4. Live Mode provides speaking cues during the actual demo

### Rehearsing a University Project Defense

1. Point to your project codebase and documentation
2. Practice Mode generates questions an examiner might ask
3. The coach helps you articulate design decisions
4. Explanation quality tracking identifies areas to improve

---

## The Observation Engine

Observations are not merely logs. They are **institutional knowledge** that helps the coach better understand and explain your project over time.

### What Gets Observed

- Questions asked during practice
- Answers given (captured via speech)
- Generated speaking cues
- Explanation quality ratings (Helpful / Needs Work / Not Useful)
- Approved coach rules

### How It Improves Coaching

```
Observation Recorded
       │
       ▼
┌─────────────────────┐
│ Coach Review       │
│ (AI analyzes if    │
│ coaching can        │
│ improve)            │
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│ Improvement         │
│ Proposal Generated  │
│ (if warranted)       │
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│ YOU Review &       │
│ Approve            │
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│ Approved Rule      │
│ (Improves future   │
│ coaching)           │
└─────────────────────┘
```

**Proposals are never auto-applied.** You always review and approve before they become active rules. This keeps AI useful without letting it silently change project truth.

---

## Use Cases

- **Interview preparation** — practice answering technical questions confidently
- **Architecture reviews** — understand and defend design decisions
- **Security reviews** — prepare for security-focused questioning
- **Founder demos** — explain your technical work to investors
- **Team onboarding** — document and communicate system purposes
- **Self-reflection** — deepen your own understanding of your architecture

---

## Quick Start

### 1. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 2. Configure environment

Create `.env` from the example:

```powershell
Copy-Item .env.example .env
```

Set at least one AI provider:

```env
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
```

### 3. Point to your project

```env
PROJECT_COACH_PROJECT_NAME=Your Project Name
PROJECT_COACH_SPEAKER_NAME=Your Name
PROJECT_COACH_SOURCE_PATHS=C:\path\to\your\project
```

### 4. Set audience type (optional)

```env
PROJECT_COACH_AUDIENCE_TYPE=non-technical
```

Options: `non-technical` (default), `semi-technical`, `technical`, `expert`

### 5. Run

```powershell
python -m project_coach
```

Choose Practice Mode or Live Interview Mode.

---

## Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `PROJECT_COACH_AUDIENCE_TYPE` | Explanation depth | `non-technical` |
| `PROJECT_COACH_PRACTICE_MODEL_ANSWER` | Show model answers | `false` |
| `PROJECT_COACH_QUESTION_MAX_TOKENS` | Question length | `90` |
| `PROJECT_COACH_ANSWER_MAX_TOKENS` | Answer length | `220` |
| `PROJECT_COACH_LIVE_DRAFT_MAX_TOKENS` | Live cue length | `170` |

---

## Architecture

```
project_coach/
├── ai/
│   ├── clients.py       # AI provider routing (Gemini, Claude)
│   └── prompts.py       # Prompt builders with audience awareness
├── coaching/
│   ├── cue_coach.py     # Local cue extraction and tracking
│   ├── rule_proposals.py # Improvement proposal generation
│   └── answer_quality.py  # Answer quality assessment
├── core/
│   ├── config.py        # Configuration and environment
│   ├── constants.py     # Defaults and limits
│   └── types.py         # Type definitions
├── knowledge/
│   ├── loader.py        # Project knowledge loading
│   ├── system_translator.py # Code to concepts translation
│   └── analogies.py     # Analogy library
├── observations/
│   ├── log.py          # Observation recording
│   └── rule_proposals.py # Rule proposal handling
├── speech/
│   └── recognizer.py    # Microphone and transcription
└── ui/
    ├── practice.py      # Practice mode interface
    └── live.py          # Live interview interface
```

### Data Flow

```
Source Files → Knowledge Loader → System Translator → ProjectUnderstanding
                                      │
                                      ▼
                              Why Extraction
                                      │
                                      ▼
                              Audience-Adjusted Prompts
                                      │
                                      ▼
                              AI Response Generation
                                      │
                                      ▼
                              Speaking Cues → UI Display
                                      │
                                      ▼
                              Observation Recording → Quality Tracking
```

---

## Cost Control

Built for efficiency:

- Prioritizes lower-cost AI models (`gemini-2.5-flash-lite`)
- Local speech recognition and cue tracking
- Small context windows by default
- Token budget controls for each operation
- No repeated AI calls for cue progression (handled locally)

---

## About

Project Coach AI was created by **Abaka Daniel Ugonna** AKA **Big Dreams Web3**.

Part of the broader mission to make every developer an expert communicator of their own architecture.
