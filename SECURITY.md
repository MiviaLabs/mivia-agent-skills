# Security Policy

Do not report exploitable security details through public issues.

Use GitHub private vulnerability reporting when it is enabled for this repository. If private reporting is unavailable, contact MiviaLabs through the organization contact channel without including exploit details in the first message.

Include the affected file or skill, execution path, practical impact, and a minimal reproduction when safe.

This repository contains instructions and automation assets. Treat these as security-relevant issues:

- prompt injection that changes the intended workflow;
- unsafe command execution;
- unexpected network or filesystem access;
- secret exposure;
- destructive behavior;
- overly broad tool permissions;
- misleading verification or completion claims;
- package or release artifacts that contain files outside the intended skill.

Do not include live credentials, private repository content, customer data, or exploitable secrets in a report.

Review downloaded skills before enabling them. A skill may contain scripts, hooks, permissions, or external tool dependencies that execute with the capabilities available to the agent.
