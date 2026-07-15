# Generate a README banner

## Use this when

Use this when a repository needs a wide Mivia-style README visual and the
image-generation capability and local references are available.

## Request template

Adapt this request to the target repository:

> Create a wide README banner for `{{README placement}}` showing
> `{{one engineering visual story}}` in the Mivia dark control-plane and
> serious 8-bit pixel-art style. Use `{{logo reference path}}` only when the
> exact logo is required and available. Confirm `{{CSS or palette reference}}`.
>
> Target `{{width}} x {{height}}` in `{{format}}`, keep the focal subject in
> the safe crop, avoid readable generated text, inspect the result, and report
> actual metadata. Do not edit README or site files unless authorized.

## Replace before running

- Replace placement, visual story, dimensions, format, and output path.
- Replace logo and CSS placeholders with inspected files or state they are not needed.
- Replace the capability assumption with the available tool and state integration scope.

## Required context

Provide audience, placement and crop, subject, dimensions, format, output path, logo and CSS references, style reference, alt-text goal, and integration scope.
Approval owner: {{README or brand owner}}.

## What good looks like

- The prompt defines one focal story with repository-sourced visual references.
- The result is inspected for text, logo, palette, pixel edges, crop, and hierarchy.
- The handoff reports actual path, dimensions, format, alt text, and limitations without claiming integration.

## Illustrative handoff

This is an illustrative handoff shape, not an image output:

```text
Artifact: {{actual output path}}
Dimensions: {{actual width x height}}
Format: {{actual format}}
Alt text: {{concise description}}
Inspection: {{checks actually performed}}
Limitations: {{unresolved issue, or None}}
```

## Verification checklist

- Inspect current logo and CSS before generating when exact branding matters.
- Confirm dimensions, format, crop safety, requested path, and accidental text or watermarks.
- Confirm README or site integration was not changed unless authorized.

## Failure or escalation signals

Do not report image creation when generation or inspection is unavailable. Ask for a missing source attachment. Escalate when logo fidelity, output metadata, or integration scope cannot be established.
