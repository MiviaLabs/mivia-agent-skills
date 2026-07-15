# Handle an unavailable image capability

## Use this when

Use this when a user requests a repository image but the generation capability
is unavailable, the required source image is missing, or the target cannot be
inspected safely.

## Request template

Adapt this request before sending it to an agent or handing it to a later image
capability:

> Prepare a ready-to-use image-generation request for `{{target placement}}`
> showing `{{one visual story}}` in the Mivia style. The requested operation is
> `{{new image or edit}}`, but `{{missing capability or source path}}` is not
> available in this session.
>
> Inspect any available repository references: `{{style, CSS, and logo paths}}`.
> Return the complete prompt, dimensions, format, crop guidance, negative
> constraints, alt text, and the exact missing input. Do not generate, save, or
> report a created artifact. If a required source attachment is missing, ask
> for that attachment instead of inventing a path.

## Replace before running

- Target placement, visual story, operation, dimensions, format, and crop.
- `{{missing capability or source path}}` with the actual gate.
- Style, CSS, and logo paths with files that exist and can be inspected.
- State the required attachment filename or an explicit capability owner.
- Add integration authorization if the later agent may edit repository files.

## Required context

Provide the intended audience, visual story, target surface, output metadata,
available brand references, missing capability or source attachment, and the
later handoff owner. Do not provide fictional output paths or visual results.

## What good looks like

- The response contains a complete prompt and explicit negative constraints
  without pretending generation occurred.
- The missing capability or attachment is named precisely, with the next action
  needed to unblock the request.
- The handoff remains usable by a later image-capable agent and includes no
  fabricated artifact metadata.

## Illustrative handoff

This is an illustrative capability-gated handoff, not an image result:

```text
Status: GATED
Created artifact: none
Ready prompt: {{complete prompt text or saved handoff location}}
Missing input: {{capability, source attachment, or inspection access}}
Next action: {{provide attachment or run with the supported capability}}
```

## Verification checklist

- Confirm the style, logo, and CSS references exist before including them in the
  prompt.
- Confirm dimensions, format, crop, focal story, negative constraints, and alt
  text are explicit.
- Confirm the handoff does not contain a created-image path, dimensions, or
  inspection result that was not obtained.
- Confirm the missing attachment request names what must be supplied.

## Failure or escalation signals

Return a capability-gated prompt when generation is unavailable. Request the
source image again when an edit cannot include every required target. Stop when
the visual story, output contract, or repository references are too ambiguous to
write a safe prompt.
