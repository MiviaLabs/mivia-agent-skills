---
name: mivia-image-generation
description: Generate or art-direct brand-consistent images for this repository, including README banners, documentation illustrations, social graphics, product visuals, and image-generation prompts. Use when the user requests a visual asset or wants an image in the Mivia dark control-plane and serious 8-bit pixel-art style.
---

# Mivia Image Generation

Create visual assets that make the repository and its engineering ideas recognizable without turning them into generic AI or game artwork.

## Inputs

Establish these before generating:

- purpose and audience: README, article, documentation, product, or social;
- subject and visual story;
- target placement, dimensions, crop behavior, and file format;
- whether to create a new image or edit an existing one;
- whether the image must include the exact Mivia logo.

If the request does not specify dimensions, choose a practical size for the placement and state it in the result. Use a wide 16:9 composition for README banners unless the layout requires another ratio.

## Workflow

1. Read [the visual style reference](references/mivia-pixel-art-style.md).
2. Inspect the current repository brand sources before generating:
   - use `docs-site/mivialabs-logo.v2.webp` as the exact logo reference when it exists;
   - use `docs-site/stylesheets/extra.css` to confirm current colors and typography;
   - prefer current repository assets over remembered or invented brand details.
3. Reduce the request to one visual story and one focal point. Use symbols, structure, and contrast instead of trying to render explanatory text.
4. Select the appropriate composition from the reference. Keep important elements inside the safe crop area for the target surface.
5. Build the generation prompt from the subject, composition, brand direction, output requirements, and negative constraints. Include the reference logo only when it is available and relevant.
6. Generate the image with the available image-generation capability. For a new image, do not invent local reference paths. For an edit, inspect every local reference image first and pass only the references needed for that edit.
7. Inspect the result for visual and technical failures:
   - no accidental readable text, fake labels, watermarks, or invented wordmarks;
   - no broken, distorted, or duplicated logo;
   - crisp pixel edges and deliberate dithering for pixel-art requests;
   - clear focal hierarchy at the requested size and crop;
   - palette and contrast remain consistent with the Mivia surface;
   - no generic robot, fantasy, game, or cyberpunk treatment unless explicitly requested.
8. Save or hand off the artifact at the requested path. Do not modify README files, site configuration, or other repository content unless the user explicitly asks for integration.
9. Report the output path, dimensions, format, alt text, and any unresolved limitation. If no image-generation capability is available, return the complete ready-to-use prompt and do not claim that an image was created.

## Generation constraints

- Treat the repository's current logo and CSS as the source of truth.
- Use the established style by default: serious technical editorial pixel art, dark near-black navy surfaces, electric blue, cyan, blue-violet accents, restrained green verification states, and small amber approval signals.
- For engineering subjects, favor task graphs, terminal symbols, verification evidence, human approval gates, repositories, commits, and draft pull requests.
- Do not use readable text inside generated images unless the user explicitly requests it and accepts text-rendering risk.
- Do not describe autonomous delivery as unreviewed or fully independent. Preserve the visual idea of human control and evidence-backed delivery.
- Keep the image useful without relying on a viewer knowing what Mivia is.

## Tool boundaries

Use the platform's supported image-generation capability when available. In Codex, follow the image-generation tool's rules for new images, edits, reference images, and visual inspection. Do not use Python or generic image-editing code as a substitute for the image-generation capability when the user asked for generated or edited artwork.

Do not activate this skill for ordinary Markdown layout, CSS-only styling, logo file conversion, image compression, or a request to write generic image prompts unrelated to this repository's visual system.

## Usage examples

- [README banner](references/examples/01-readme-banner.md)
- [Image capability unavailable](references/examples/02-image-capability-unavailable.md)
