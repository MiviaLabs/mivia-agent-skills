---
name: agent-readiness-audit-go
description: Audit Go repository controls governing named coding-agent actions after applying the generic agent-readiness contract. Use when the user asks whether an agent may inspect, edit, test, commit, open a pull request, or perform another named action in a Go repository. Do not use for application bug hunts, ordinary code-change verification, general security audits, or production readiness.
---

# Go Agent Readiness Audit

## Generic contract

Read and apply `../agent-readiness-audit/SKILL.md` before continuing. The
generic skill owns activation, bounded versus repository-wide mode, command
safety, evidence semantics, subagent coordination, report structure, and
fail-closed autonomy gates. If that dependency is unavailable, stop with
`MISSING_DEPENDENCY`; do not recreate or weaken its contract here.

Make the mode decision immediately. For a named small action sequence without
an explicit repository-wide request, use the generic skill's bounded mode and
do not read its bundled report, workstream, or broad command references.

For an explicitly repository-wide Go audit, inherit the generic skill's default
30-minute budget unless the user provides another deadline.

## Go-specific boundary

Use this adapter only when the target repository contains `go.mod` or
`go.work` and the user asks about named coding-agent actions. Apply the generic
skill's control-plane scope. Do not turn a readiness question into a general Go
correctness, security, supply-chain, deployment, or production-readiness audit.

Inspect Go application code only when it directly implements a named control or
is the minimum boundary needed to verify one. Route reachable Go defects to
`deep-bug-audit`; route verification of an implemented change to
`verify-code-change`.

## Go-specific preflight

Before running a Go command, inspect repository-native wrappers, Makefiles,
Taskfiles, hooks, build tags, generated-code rules, test fixtures, and CI jobs.
Record:

- Go version and module or workspace files;
- package or directory scope;
- build tags and relevant environment variables;
- whether tests, generators, or tools access services or credentials;
- whether dependency or tool resolution requires network access;
- exact command, exit code, duration, side effects, and limitation.

Use the narrowest repository-supported command. Candidate Go checks include:

```bash
gofmt -l <named paths>
go vet <named packages>
go test -count=1 <named packages>
go test -race <named packages>
go test -shuffle=on <named packages>
go build <named packages>
go mod verify
go list <named packages>
```

Do not run `go test ./...`, `go test -race ./...`, `go build ./...`,
`go mod tidy`, generators, migrations, or dependency resolution unless the
generic skill's safety preflight and the user's declared scope authorize them.
Record service-dependent, unavailable, or unneeded checks as `GATED` or
`NOT_RUN`.

## Go control surfaces

Prioritize only the surfaces governing the named actions:

- `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, and package instructions;
- `go.mod`, `go.work`, `Makefile`, `Taskfile`, and command wrappers;
- Git hooks and Go-specific validation scripts;
- CI jobs, required checks, branch permissions, and workflow policy;
- `golangci-lint`, Staticcheck, Semgrep, govulncheck, race, fuzz, and generated
  code configuration when they gate the named action;
- skill metadata, evaluations, packaging, and installation wiring when the
  agent action changes or consumes those artifacts.

Do not count a Go tool or configuration file as enforcement without evidence
that it runs, covers the named scope, blocks the intended action, and cannot be
silently weakened.

## Output

Follow the generic skill's bounded output contract for a bounded request and
its strict report template for an explicitly repository-wide request. Add Go
evidence for package scope, command flags, build tags, generated-code state,
and race or fuzz prerequisites where applicable.

Use these local examples:

- `references/examples/01-repository-autonomy-readiness.md`
- `references/examples/02-agent-runtime-readiness-gated.md`

## Failure handling

- Non-Go target: return `NOT_APPLICABLE` and route to the generic skill or a
  language-specific workflow.
- Missing generic dependency: return `MISSING_DEPENDENCY` and do not proceed.
- Missing Go tool, service, permission, or runtime evidence: return `GATED` or
  `NOT_RUN`; do not infer a clean result.
- Unsupported subagent claims: discard them or mark them as `LIKELY_RISK`.
