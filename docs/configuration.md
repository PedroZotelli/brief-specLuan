# Configuration

Create a user or project configuration:

```bash
brief-spec config init
brief-spec config init --scope project
brief-spec config show --json
```

User configuration lives under the Brief-Spec state root. Project configuration is
`.brief-spec.toml`. The legacy `.briefspec.toml` remains readable. Only known presentation,
typing, and retention keys are read; configuration cannot inject
commands or arbitrary executable paths.

## Defaults

```toml
[checkpoint]
policy = "suggest" # off | manual | suggest | auto
default_mode = "orient" # orient | teach | spoken
elapsed_minutes = 12
turns = 8
assistant_chars = 16000
tool_calls = 12
cooldown_minutes = 6
minimum_turns_after_checkpoint = 2

[outcome]
policy = "suggest" # off | suggest | enforce
one_repair = true

[typing]
enabled = true
activation = "substantive"
default_type = "general"
sticky = true

[state]
retention_days = 14
```

### Proportional follow-ups

Once a session has a work type, each substantive prompt receives the type's full explanation
profile. A follow-up of fewer than four words that does not name Brief-Spec ("ok", "merge done",
"continue") instead receives a short instruction to answer in a few lines; the typed Outcome Brief
is still used when such a message closes a substantive task. The work type stays as it was.

A short **order** is a task, not a follow-up. A prompt that opens with a work verb ("Fix it",
"Run the tests", "Corrija o bug", "Rode os testes", optionally after "please" or "por favor")
keeps the full profile, and it classifies the task when the session has no work type yet.

### Languages

The local classifier reads English and Portuguese. Each Portuguese pattern extends the English
rule with the same id, so "Revise o pull request 42" and "Review pull request 42" produce the
same work type, subject, and rule ids. Accents are optional ("revisao"). Other languages fall back
to `general` unless the prompt carries an English or Portuguese keyword; state the type
explicitly (`type: review`) to override.

### Checkpoint policies

- `off`: no lifecycle checkpoint behavior; explicit skill use remains possible.
- `manual`: only explicit checkpoint requests.
- `suggest`: record eligibility and give the host context at a safe boundary.
- `auto`: request one checkpoint at the next agent-stop boundary.

### Outcome policies

- `off`: no lifecycle outcome behavior; explicit skill use remains possible.
- `suggest`: install the contract as session context.
- `enforce`: conservatively classify action requests and request one correction when the terminal
  handoff lacks a valid Outcome Brief.

Enforcement is intentionally opt-in. A stop hook cannot perfectly infer whether every conversational
turn is a terminal task boundary.

## State operations

```bash
brief-spec state list --json
brief-spec state prune --older-than 14
brief-spec state prune --older-than 14 --dry-run
brief-spec state reset --runtime codex --session SESSION_ID
```

Set `BRIEF_SPEC_HOME` to isolate state for automation or testing. Brief-Spec stores bounded metadata,
not raw session content. `BRIEFSPEC_HOME` remains a readable `0.x` compatibility alias.
