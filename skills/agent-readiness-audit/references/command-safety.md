# Safe Audit Command Policy

Repository commands are potentially executable code. Inspect their definitions,
hooks, build tags, fixtures, environment access, and service dependencies before
running them.

## Preflight questions

Before a command runs, determine:

- Can it write files, generated output, caches, databases, or artifacts?
- Can it execute hooks, generators, shell commands, or untrusted fixtures?
- Can it access credentials, tokens, production systems, or the network?
- Does it require services, containers, migrations, or external state?
- Is its tool version pinned and its scope bounded?
- Can it hang, consume excessive resources, or produce nondeterministic output?

If any answer is unknown for a high-impact command, classify it
`SAFE_WITH_PREREQUISITES` or `NOT_RUN` and record the missing evidence.

## Command classes

| Class | Meaning | Required handling |
| --- | --- | --- |
| SAFE | Read-only or isolated with known bounded behavior | Run with normal limits and record the result |
| SAFE_WITH_PREREQUISITES | Requires a service, flag, isolation, pinned tool, or network | Verify prerequisites, document them, then run only if safe |
| NOT_RUN | Unsafe, unavailable, unnecessary, or blocked | Do not run; record the reason and residual risk |

## Go command cautions

Do not run these unconditionally:

- `go test ./...`, `go test -race ./...`, and `go test -shuffle=on ./...` may
  contact services, mutate state, hang, or consume excessive resources.
- `go build ./...` may execute generators or build-time side effects.
- `go mod verify`, `go mod tidy -diff`, and `go list -deps ./...` may resolve
  dependency state or access the network.
- `semgrep`, `golangci-lint`, `staticcheck`, and `govulncheck` require bounded
  scope, known versions, and documented network behavior.

Use repository-native wrappers first. Run the narrowest command that provides
the needed evidence. Record the exact command, exit code, duration, side
effects, and environment limitation in the report.
