# Mivia Pixel-Art Style

Use this reference when generating artwork for the Mivia Agent Skills repository.

## Visual objective

Make the image communicate governed AI-assisted software delivery:

1. work starts from a scoped request;
2. tasks form a dependency-aware graph;
3. implementation runs against a real repository;
4. verification leaves evidence;
5. a human controls review and delivery.

The image should feel like a serious engineering system, not a game screenshot, fantasy scene, generic AI illustration, or marketing collage.

## Core palette

Use a restrained dark palette derived from the repository's live documentation theme:

- surface 0: `oklch(14% 0.012 250)`;
- surface 1: `oklch(17% 0.012 250)`;
- surface 2: `oklch(20% 0.012 250)`;
- surface 3: `oklch(24% 0.012 250)`;
- foreground: `#f2f1ee`;
- muted text: `#b7b6b2`;
- primary blue: `hsl(225 97% 60%)`;
- cyan: `hsl(197 96% 50%)`;
- indigo: `hsl(258 52% 45%)`;
- verification green: `hsl(153 60% 46%)`;
- approval amber: approximate `hsl(37 87% 59%)`;
- signal gradient: `hsl(213 100% 65%)` to `hsl(235 95% 67%)` to `hsl(258 90% 66%)`.

For image models that work better with hex values, use approximate equivalents: `#0d111a`, `#171c27`, `#202632`, `#3d63fc`, `#08b9f2`, `#7664f2`, `#2eb879`, `#e5a642`, and `#f2f1ee`.

## Pixel-art rules

- use a visible logical pixel grid and hard edges;
- use limited colors and deliberate dithering rather than smooth photographic shading;
- use pixel clusters to create glow, depth, and hierarchy;
- keep silhouettes and symbols recognizable at README display size;
- avoid anti-aliased text, photorealism, soft 3D rendering, and noisy micro-detail;
- use subtle glow only around primary blue, cyan, and violet signals.

## Composition patterns

### README banner

Use a 16:9 landscape composition with one central control console. Show a left-to-right flow from reusable skill or contract cards, through a six-stage dependency graph, to verification evidence and a human-controlled draft pull request. Represent intake, plan, build, verify, review, and handoff with symbols, not labels. Keep the edges and focal symbols inside the center safe area for mobile crops.

### Article illustration

Use a 4:3 or square composition with one mechanism in focus: a task DAG, a verification gate, a review boundary, or an evidence trail. Use fewer elements than a banner and leave enough negative space for the article layout.

### Product or social graphic

Use a compact central symbol or control panel with a clear hierarchy. Do not add explanatory paragraphs to the image. Provide the copy separately so the image remains legible and reusable.

## Logo handling

When available, the exact logo is at `docs-site/mivialabs-logo.v2.webp`. Use it as a shape and color reference, preserve its geometric M form, and keep it small unless the user asks for a logo-focused asset. Never invent a Mivia wordmark or rely on generated lettering.

If the logo is not available, ask for it when exact brand reproduction matters. Otherwise use only an abstract geometric M-like signal and state that it is not the official logo.

## Negative constraints

Unless explicitly requested, exclude:

- readable words, random letters, fake labels, and illegible interface copy;
- invented logos, watermarks, stock-photo artifacts, and UI screenshots;
- humanoid robots, smiling mascots, fantasy elements, and generic brains;
- excessive neon, visual clutter, unrelated screens, and equal emphasis on every object;
- claims that agents can merge or ship without human review;
- gradients that erase the pixel structure.

## Handoff requirements

Return:

- the generated image or exact output path;
- dimensions and format;
- concise alt text describing the actual visible content;
- the prompt or material prompt changes when the user asks for reproducibility;
- any limitation, such as missing logo reference, unavailable generation capability, or text-rendering risk.
