# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses semantic versioning.

## [Unreleased]

### Added

- The classifier reads Portuguese. The keyword rules only knew English, so a
  Portuguese request fell back to `general` unless it contained an English term
  ("pull request", "deploy"): 7 of 9 sample requests did. Each rule now also
  carries Portuguese vocabulary under the same rule id (accents optional), with
  Portuguese subjects, prohibitions ("Não implemente…", "Sem alterar…") and
  pivots ("Nova tarefa", "Em vez disso"). Words that are also English or have
  an everyday meaning are restricted or left out ("revise it" stays English;
  "projeto", "quebra de linha" do not drive a type). The classifier adapter
  version is now `1.2`. `tests/test_portuguese.py` covers a 160-prompt corpus.

### Fixed

- A short order is no longer treated as a follow-up. Any prompt under four
  words got the few-lines context, so "Fix it", "Run the tests", "Corrija o bug"
  or "Rode os testes" lost the task's profile, and a session that opened with one
  was never classified. A prompt that opens with a work verb, in English or
  Portuguese, is now substantive and keeps the full profile; "ok", "continue",
  "Merge feito" and status questions stay short follow-ups.

### Changed

- Proportional answers: a follow-up of fewer than four words ("ok", "merge done",
  "continue") no longer receives the full work-type profile on every prompt; the
  hook asks for a few lines instead and keeps the session's work type. Prompts that
  name Brief-Spec, and every longer prompt, keep the full profile.

### Documentation

- README: Brief-Spec runs on Linux, macOS, and Windows; the install section is "From the tag (v0.5.0)" (it said "Public release (v0.2.0)" above a v0.5.0 command); release truth marks v0.2.0 as the original project's release and records 0.5.0's hosted CI and the pending live-host authorization.

### Changed

- The repository is now `PedroZotelli/brief-specAlicerce`, a standalone repository (no longer in the original's fork network). Links, install commands and manifests use the new name; GitHub redirects the old one.
- The contributor context file moved from `CLAUDE.md` to `.claude/CLAUDE.md`
  (Claude Code still loads it in this repository). A `CLAUDE.md` at a plugin
  root is not plugin context, and `claude plugin validate --strict` rejects it.
- The audio renderer smoke no longer requires two macOS renderings to be
  byte-identical: current macOS speech synthesis varies slightly between runs.
  It now requires matching duration within 2%; the bundle verifier still checks
  decoding, the source-Script hash and the AI disclosure. `docs/verification.md`
  no longer claims deterministic audio bytes. PDF stays byte-identical.
- CI builds and clean-room installs the exact-SHA candidate even when the
  retained live-host evidence does not match the source bytes; it then skips
  the release authorization and shows a "Not release-authorized" warning.
  `release.yml` still refuses to publish a candidate without that
  authorization, so a release still needs a fresh live-host matrix.

Pedro Zotelli's line of this fork (https://github.com/PedroZotelli/brief-specAlicerce).
Authorship of the original work stays with Luan Moreno Maciel; see `NOTICE`.

### Fixed

- The Chronicle project lock no longer orphans itself on Windows. A lock file
  another thread or process has open (a concurrent `stat`, an antivirus scan)
  raises `PermissionError` on create or delete; acquiring now treats that as
  contention and releasing retries briefly. Seen once on a hosted Windows
  runner as a lock timeout in the concurrent-ingestion test.
- Run on Windows as well as Linux and macOS. The Chronicle export builds its
  deterministic zip in memory, because Windows cannot reopen an open temporary
  file by name.
- Treat Windows directory junctions as links wherever symlinks are refused
  (`briefspec.portability.is_link`). A junction needs no privilege to create and
  `Path.is_symlink` does not see it.
- Pin LF line endings in `.gitattributes`, so CRLF checkouts no longer change
  hashed or executed files.

### Changed

- Install commands, plugin manifests, and marketplace ownership point to the fork,
  so nothing on the install path depends on the original repository. Schema `$id`
  identifiers keep their original values so existing briefs stay valid.

### Added

- `brief-spec frame` with versioned request and receipt schemas for bounded,
  presentation-only Human Frames. Lifecycle coordinators can delegate Markdown
  rendering without delegating approval or dispatch authority.

- Experimental `brief-spec-chronicle` package with explicit per-project activation, private
  append-only material-event segments, idempotent ingestion, hash-chain receipts, a rebuildable
  SQLite relation index, deterministic drift rules, canonical Project Chronicle snapshots, Human
  Review Packs, transactional exports, external receipts, archive/restore, doctor, exact deletion,
  and reviewed lesson export.
- Public `brief-spec-event/1.0` schema and dependency-free artifact primitives for canonical JSON,
  hashing, atomic output sets, manifests, and receipts.
- Method contexts for Seamwise, Task-Spec, Converge, and general work, kept independent from work
  type, subject, presentation, and lifecycle horizon.
- Harness capability reporting for Human Frame delivery tiers.
- Bounded source normalization for Brief-Spec delivery, Seamwise, Task-Spec, Converge, Exa,
  Tavily, Firecrawl, and RAFT records, plus correlation-based cross-harness deduplication.
- Ingest-order replay across monthly segments, explicit ledger cutoffs, visible late arrivals,
  human-approved pivot baselines, expanded deterministic drift rules, and a disposable
  Seamwise → Task-Spec → Converge end-to-end journey.
- Generic HTML-to-PDF and spoken-script-to-MP3 helpers that preserve the existing renderer
  contracts while allowing Chronicle to reuse their verified engines.
- Experimental `brief-spec-renderer-video` package for offline storyboard scenes, H.264/AAC MP4,
  captions, transcript, chapters, source hashes, and renderer-fingerprint-scoped determinism.
- Comprehensive behavior catalog covering all eight work types, four reading experiences, six
  continuity horizons, method-aware Human Frames, Outcome states, evidence edge cases, downloads,
  harnesses, Chronicle operations, and explicit non-goals.
- Enforced repository-layout contract that requires canonical package-directory/distribution name
  alignment while preserving the intentional `0.x` import and entry-point compatibility surfaces.

### Changed

- Renamed the PDF and audio renderer source directories to
  `packages/brief-spec-renderer-pdf` and `packages/brief-spec-renderer-audio`; their legacy internal
  Python modules and `briefspec.renderers` entry points remain operational through `0.x`.
- Expanded the README feature map, Human Continuity matrix, repository map, complete candidate
  installation, documentation index, development gates, and honest limits to match the current
  source tree.
- Documented the tracked multi-model `output/` corpus separately from runtime exports and defined
  the ownership and cleanup policy for tracked release inputs, local evidence, builds, and caches.

### Fixed

- Made path-rendering and POSIX-permission tests platform-aware so Windows validates native path
  behavior without pretending that Unix mode bits are enforceable.
- Chronicle doctor now reports the Windows permission boundary explicitly instead of producing a
  permanent false warning, while retaining `0700`/`0600` enforcement on POSIX systems.
- The hosted macOS audio gate now installs `ffmpeg`/`ffprobe` before rendering and verification.
- Installation snapshots now retain full-stack rollback commands when Chronicle and video wheels
  are present, including restoration of the separate Chronicle executable.
- OMP integration now injects the classification context through the turn system prompt
  (`before_agent_start` → `systemPrompt`) instead of a hidden transcript message, primes the model
  with session context, and enforces the terminal Outcome/typed wrapper at `session_stop`. The dead
  `agent_end` block path and the unmapped `SessionStop` event were removed.
- Grok Stop no longer continues a turn that already has a valid Outcome Brief or Session
  Checkpoint. Grok paints that message and opens suggested-question chips plus the follow-up
  queue before Stop runs; a continuation held the queue, wiped the chips, and could send the
  wrong next prompt. Stop still supplies one classification repair when the brief itself is
  missing.
- Grok Stop no longer forces an Outcome Brief onto a non-substantive follow-up. Sticky work
  type from an earlier review was wrapping a literal `PINEAPPLE` reply as a codebase review.

### Security

- Chronicle is disabled until explicit project initialization, writes only below
  `$BRIEF_SPEC_HOME/chronicles`, rejects credential/transcript/prompt/tool-output fields before
  persistence, bounds events to 64 KiB, and requires an exact project ID for deletion.
- Lesson approval creates an offline proposal export only; it cannot modify a knowledge system,
  method, skill, policy, or canonical project state.

## [0.5.0] - Unreleased candidate

### Added

- Canonical Brief-Spec identity: `brief-spec` distribution and CLI plus the
  `brief_spec` Python package, while preserving all `briefspec` 0.x aliases.
- Eight deterministic work-type profiles and open subject slugs with local,
  bounded classification; explicit, host, inferred, and fallback origins;
  categorical confidence; sticky task behavior; and pivot handling.
- `types list`, `types show`, and `classify` CLI commands, plus the universal
  `brief-spec` routing skill.
- Typed Markdown wrapper and `brief-spec-delivery/2.0` canonical schema with
  classification, ordered explanations, harness/model metadata, provenance,
  artifacts, work items, manifests, and receipts.
- Data-driven harness registry and native user/project installers for Codex,
  Claude Code, OMP, Grok Build, and Kimi Code; experimental adapters for
  Copilot, Cursor Agent, and Goose.
- OMP native extension lifecycle and Kimi user-plugin integration, including
  the project-scope skills-only capability boundary.
- Canonical `brief-spec-delivery/2.0` exports for deterministic Markdown,
  JSON, self-contained offline HTML, ZIP, spoken text, and SSML, with optional
  PDF and MP3 renderer packages.
- Provider-neutral provenance for Exa, Tavily, Firecrawl, local files, and
  future research systems without adding their SDKs to the core package.
- Ordered bundle manifests, external delivery receipts, SHA-256 integrity,
  fixed ZIP metadata, and structural, resolved, rendered, and delivered
  verification levels.
- Portable Outcome Brief, Session Checkpoint, evidence, delivery, manifest,
  and receipt schemas plus a self-contained offline compound schema bundle.
- Sanitized, source-fingerprinted live-host evidence and exact-SHA release
  authorization inputs for build-once publication.
- Browser, PDF, local-audio, clean-wheel, clean-sdist, rollback, hermetic-host,
  and cross-harness live acceptance gates.

### Changed

- The unpublished `0.3.0` delivery and `0.4.0` renderer candidates are folded
  into this release; no intermediate packages will be published.
- Canonical state uses `BRIEF_SPEC_HOME` and `~/.local/state/brief-spec`, while
  the legacy variable, state, markers, receipts, schemas, and renderer entry
  point group remain readable through the `0.x` line.
- Optional renderer distribution names are now `brief-spec-renderer-pdf` and
  `brief-spec-renderer-audio`, version-aligned at `0.5.0`.
- Human-facing Markdown, HTML, and PDF projections are status-first while the
  unchanged Outcome Brief and Session Checkpoint `1.0` contracts remain
  backward compatible.
- Verification is zero-network and no-plugin by default. Public URL checks and
  renderer code loading require explicit consent.
- Inferred classifications are capped at medium confidence; ambiguous or
  conflicting intent falls back to `general` instead of fabricating certainty.
- Harness maturity is evidence-based: Codex, Claude Code, OMP, Grok Build, and
  Kimi Code pass their required local live matrices; Copilot, Cursor, and Goose
  remain explicitly experimental.

### Fixed

- Grok Build now accepts native camelCase assistant payloads, obtains exact
  classification metadata through one bounded Stop-hook repair, and uses the
  actual `read_file`/`search_replace` native tool IDs for its disposable
  implementation gate.
- Receipt ownership now requires the recorded path and prior hash. Locally
  modified managed files are preserved and staged beside the new candidate
  rather than overwritten.
- Runtime auto-detection follows explicit payload, stable session identifier,
  mutually exclusive host markers, then deterministic fallback precedence.
- Doctor and installer tests no longer depend on optional host executables from
  the maintainer's real `PATH`.

### Security

- Resolved verification rejects loopback, private, link-local, metadata,
  multicast, unspecified, redirected-private, and other non-public network
  targets unless the relevant operation is explicitly permitted.
- File and archive verification now bounds input size, member count, expanded
  size, compression ratio, redirects, requests, headers, and fetched bodies.
- Path traversal, absolute archive members, duplicate names, special files,
  symlink escapes, command-like evidence, and silent workspace escapes are
  rejected.
- Hook input, transcript tails, session state, and repair behavior remain
  bounded; secrets and raw transcripts are excluded from artifacts and
  receipts.

## [0.4.0] - Unpublished candidate folded into 0.5.0

### Added

- Optional `briefspec-renderer-pdf` package using canonical offline HTML and Playwright Chromium,
  with A4/Letter output and Poppler-backed verification.
- Optional `briefspec-renderer-audio` package for local macOS `say` plus `ffmpeg` MP3 output and
  explicitly consented OpenAI text-to-speech.
- Renderer discovery through the `briefspec.renderers` Python entry-point group.
- Linux PDF/browser and macOS local-audio end-to-end CI jobs, plus mocked OpenAI boundaries.

## [0.3.0] - Unpublished candidate folded into 0.5.0

### Added

- Canonical `briefspec-delivery/1.0` envelope with source metadata, provenance, artifacts, and
  multi-agent work activity.
- Deterministic Markdown, JSON, self-contained HTML, and ZIP downloads generated from one object.
- External delivery receipts and structural, resolved, rendered, and delivered verification.
- `export`, `bundle`, `verify`, `deliver`, `setup`, and `capabilities` CLI commands.
- Atomic multi-runtime setup plus doctor repair, all-scope inventory, and version-drift checks.
- PyPI Trusted Publishing workflow, release manifest, restart-safe digest checks, and staged
  GitHub Release finalization.

### Changed

- Rich evidence annotations can include a safe `kind=` hint while legacy annotations remain valid.
- Spoken text and SSML are exportable only from a Spoken Checkpoint.

## [0.2.1] - Unpublished candidate from 2026-08-03

### Fixed

- Codex project hook commands resolve the Brief-Spec bundle from the Git root, so all lifecycle
  events continue to work when a task starts in a nested repository directory.
- Codex project installs include a PowerShell `commandWindows` override with the same root-stable
  behavior.
- The README badge, installation command, and verification record now stay aligned with the
  package version.
- Session Checkpoint JSON fields now match all Orient, Teach, and Spoken human-facing contracts.
- Markdown validation rejects proof without an inspectable locator and warns when evidence basis
  and result labels are missing.
- Repeat installation upgrades unchanged receipt-owned skill references while preserving
  independently modified files.

### Added

- Executable nested-directory regression coverage for Codex project hooks.
- A tag-driven release workflow that builds once, verifies the wheel, records SHA-256 checksums,
  generates GitHub build provenance, and attaches the artifacts to the release.
- Contract-equivalence tests for every Session Checkpoint mode.
- Full-SHA GitHub Actions pins with Dependabot maintenance.

## [0.2.0] - 2026-07-31

### Fixed

- Checkpoint suggestions are delivered once per pending checkpoint and repeat only after the
  configured cooldown, instead of on every completed tool call.

### Changed

- Claude Code project installs write skills to `.claude/skills/` so the host lists
  `outcome-brief` and `session-checkpoint` natively.
- Claude Code project hook commands anchor on `$CLAUDE_PROJECT_DIR` so they no longer depend
  on the session's working directory.
- `doctor` resolves scope automatically: a project install for the current directory wins,
  the user install is the fallback, and `--scope` forces either. The report header now names
  the scope it checked.

## [0.1.0] - 2026-07-31

### Added

- `outcome-brief` with five honest terminal statuses and an evidence-first field order.
- `session-checkpoint` with orient, teach, and spoken modes.
- Dependency-free Python control plane for validation, safe-boundary triggers, and bounded state.
- Codex, Claude Code, and GitHub Copilot lifecycle adapters.
- Native plugin and marketplace manifests for all three ecosystems.
- Reversible user and project installers with receipts and conflict preservation.
- Network-free Copilot cloud bridge built as a deterministic Python zipapp.
- Doctor, configuration, state-retention, and validation commands.
- Synthetic Apex experience pilot and clean-room verification surfaces.

[Unreleased]: https://github.com/luanmorenommaciel/brief-spec/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/luanmorenommaciel/brief-spec/compare/v0.2.0...v0.5.0
[0.4.0]: https://github.com/luanmorenommaciel/brief-spec/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/luanmorenommaciel/brief-spec/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/luanmorenommaciel/brief-spec/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/luanmorenommaciel/brief-spec/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/luanmorenommaciel/brief-spec/releases/tag/v0.1.0
