# Handle an unavailable image capability

## Use this when

Use this when a repository image is requested but generation, a required source
image, or safe inspection is unavailable.

## Request template

Adapt this request before sending it to an agent or later image capability:

> Prepare a ready-to-use image-generation request for `{{target placement}}`
> showing `{{one visual story}}` in the Mivia style. The operation is
> `{{new image or edit}}`, but `{{missing capability or source path}}` is not
> available in this session.
>
> Inspect available references: `{{style, CSS, and logo paths}}`. Return the
> complete prompt, dimensions, format, crop guidance, negative constraints,
> alt text, and the exact missing input. Do not generate, save, or report a
> created artifact. Ask for a missing source attachment instead of inventing a path.

## Replace before running

- Replace target, visual story, operation, dimensions, format, and crop.
- Replace the missing capability or source placeholder with the actual gate.
- Use existing style, CSS, and logo paths; state integration authorization.

## Required context

Provide audience, visual story, target surface, output metadata, brand references, missing capability or attachment, and later handoff owner. Do not provide fictional output paths or visual results.
Approval owner: {{requester or repository owner}}.

## What good looks like

- The response contains a complete prompt and negative constraints without pretending generation occurred.
- The missing capability or attachment is named precisely with the next unblock action.
- The handoff is usable by a later image-capable agent and has no fabricated metadata.

## Illustrative handoff

This is an illustrative capability-gated handoff, not an image result:

```text
Status: GATED
Created artifact: none
Ready prompt: {{complete prompt text or saved handoff location}}
Missing input: {{capability, source attachment, or inspection access}}
Next action: {{provide attachment or run with supported capability}}
```

## Verification checklist

- Confirm references exist, and dimensions, format, crop, focal story, constraints, and alt text are explicit.
- Confirm no created-image path, dimensions, or inspection result is unverified.
- Confirm a missing attachment request names what must be supplied.

## Failure or escalation signals

Return a capability-gated prompt when generation is unavailable. Request the source image again when an edit cannot include every target. Stop when the visual story, output contract, or repository references are too ambiguous.
