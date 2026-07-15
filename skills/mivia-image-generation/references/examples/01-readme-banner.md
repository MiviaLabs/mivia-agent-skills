# Generate a README banner

## Use this when

Use this when a repository needs a wide Mivia-style README visual and the
supported image-generation capability and required local references are
available.

## Request template

Adapt this request to the target repository:

> Create a wide README banner for `{{README placement}}` showing
> `{{one engineering visual story}}` in the Mivia dark control-plane and
> serious 8-bit pixel-art style. Use `{{logo reference path}}` only if the
> exact logo is required and available. Confirm `{{CSS or palette reference}}`
> before prompting.
>
> Target `{{width}} x {{height}}` in `{{format}}`, keep important elements
> inside the safe crop, avoid readable generated text, and inspect the result
> before handing it off. Do not edit README or site files unless explicitly
> requested. Report the actual output metadata and any unresolved limitation.

## Replace before running

- `{{README placement}}`, visual story, dimensions, format, and output path.
- `{{logo reference path}}` with a real inspected asset or state that no exact
  logo is required.
- `{{CSS or palette reference}}` with current repository references.
- Replace the image-generation capability assumption with the available tool.
- State whether README integration is authorized.

## Required context

Provide the audience, target placement and crop, subject, dimensions, format,
output path, current logo and CSS references, style reference, alt-text goal,
and whether integration changes are in scope.

## What good looks like

- The prompt reduces the request to one focal story with repository-sourced
  visual references and a safe crop.
- The generated result is inspected for text, logo, palette, pixel-edge, and
  hierarchy failures before handoff.
- The handoff reports the actual path, dimensions, format, alt text, and
  unresolved limitations without claiming README integration.

## Illustrative handoff

This is an illustrative handoff shape, not an image output:

```text
Artifact: {{actual output path}}
Dimensions: {{actual width x height}}
Format: {{actual format}}
Alt text: {{concise description}}
Inspection: {{visual and technical checks actually performed}}
Limitations: {{unresolved issue, or None}}
```

## Verification checklist

- Inspect the current logo and CSS before generating when the request depends on
  exact repository branding.
- Confirm the output dimensions, format, crop safety, and requested path.
- Inspect for accidental readable text, fake labels, watermarks, broken logos,
  generic cyberpunk treatment, and weak focal hierarchy.
- Confirm README or site integration was not changed unless authorized.

## Failure or escalation signals

Do not report an image creation event when generation or local inspection is
unavailable. Ask for the missing source attachment when an edit needs one.
Escalate when exact logo fidelity, output path, dimensions, or integration scope
cannot be established.
