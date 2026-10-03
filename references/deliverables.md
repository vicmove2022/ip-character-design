# Deliverables

Ten output types, each with a template in `deliverables.json`. Generate them in
this order; each one is cheaper to make after the previous one exists.

```bash
python scripts/build_prompt.py kit --style <id> --medium <id> \
  --subject "..." --signature "..." --palette "..." --out kit.json
python scripts/build_prompt.py kit --only identity --only loop --out partial.json
```

| # | id | what it is | ratio | why you need it |
|---|------|-----------|-------|-----------------|
| 1 | `silhouette-test` | solid black shape on white | 1:1 | cheap design gate — do this first |
| 2 | `identity` | the canonical hero shot | 1:1 | the reference every other asset derives from |
| 3 | `turnaround` | front / side / 3-4 / back on one sheet | 16:9 | reference for animators and modellers |
| 4 | `expression-sheet` | 6 heads-and-shoulders, 3x2 | 16:9 | the reaction library |
| 5 | `pose-sheet` | 6 full-body poses, 2x3 | 16:9 | reusable body positions |
| 6 | `scene` | character in its world | 16:9 | B-roll and establishing shots |
| 7 | `loop` | seamless looping frame | 1:1 | GIFs, stickers, background loops |
| 8 | `sticker` | die-cut with white border | 1:1 | overlay-ready, transparent variants |
| 9 | `avatar` | head-and-shoulders icon | 1:1 | profile pictures, app icons |
| 10 | `banner` | character left, space right | 21:9 | channel headers |

## Order matters

**Silhouette test first.** It costs one render and it is the only cheap way to
learn the design is not distinctive. A character that needs internal detail to
be recognisable is a character that fails as a thumbnail, a reaction GIF, and a
merch print. If the black shape fails, change the silhouette — not the
details.

**Identity second, neutral.** Front-facing, plain background, no props. You
want the reference image to be the most boring possible render.

**Sheets third, before any scene work.** Sheets are libraries. Every reaction
insert and every pose variant comes out of them.

## Turnaround

The template asks for four views in a row with consistent scale. In practice
engines disagree between views — the profile view drifts from the front.

Two approaches:

- **One sheet prompt** — fast, and usually good enough for 3D-adjacent styles
  (`soft-3d-render`, `designer-vinyl-figure`).
- **Four separate prompts** — slower and more reliable. Generate each view at
  1:1 with the identical identity block, then composite. Do this for
  illustration styles (`anime-cel-shaded`, `manga-line-art`, hand media).

Always add `consistent scale, even spacing, no perspective distortion`. A
turnaround shot in perspective is not a turnaround.

## Expression sheet

Eleven expressions ship in `deliverables.json`:

`neutral` · `happy` · `excited` · `surprised` · `confused` · `thinking` ·
`curious` · `annoyed` · `excited-point` · `sad` · `angry`

```bash
python scripts/build_prompt.py kit --style chibi-q-chibi \
  --expressions happy --expressions annoyed --expressions sad \
  --only expression-sheet --out sheet.json
```

Selecting a subset rewrites the panel count and grid shape automatically
(2 expressions → `Two ... 2x1 grid`). The full list is always returned in the
output JSON so you can pick from it.

**Describe the mouth.** Mouth shape carries more emotion than eye shape and is
the first thing engines get wrong. Every expression in the data describes the
mouth explicitly. If you write your own, do the same.

**Head and shoulders only.** Full-body expression sheets waste the panel on legs
and shrink the face, which is the only part that needs to read.

## Pose sheet

Six default poses ship; eight optional extras exist in `deliverables.json`:

`heart-hands` · `shaka` · `phone-hold` · `holding-product` · `thumbs-up` ·
`thinking-pose` · `shrugging` · `running`

```bash
python scripts/build_prompt.py kit --poses heart-hands --poses phone-hold \
  --only pose-sheet --out poses.json
```

`phone-hold` and `holding-product` exist for live commerce and live streams.
`holding-product` deliberately says *plain unbranded box* — never render a real
brand.

## Seamless loops

A clean loop needs two things, both stated in the template:

1. **Static camera.** Any camera movement breaks the seam.
2. **Plain background.** Parallax on the background makes the join visible.

Motion options: `breathe`, `blink`, `wave`, `turntable`, `bounce`,
`idle-look`, `hair-sway`.

If the engine needs separate first and last frames, generate both from an
identical prompt, changing only the pose to each loop extreme. Generate 3-4
candidates per frame and pair the closest matches.

Loop motions by style, from `styles.json`:

| style | best loop |
|-------|----------|
| `blob-mascot` | 2-frame colour blink |
| `chibi-q-chibi` | idle bob + blink |
| `retro-sports-mascot` | shoulder bounce, pumping arm |
| `friendly-brand-mascot` | slow wave, 2-frame nod |
| `soft-3d-render` | turntable or three-key idle |
| `designer-vinyl-figure` | 20° rotation with moving specular |
| `felt-wool-plush` | slow breathing, fibre shimmer |
| `stuffed-fabric-doll` | squash and stretch |
| `pixel-8bit` | classic 4-frame cycle |
| `whimsical-creature` | breathe with tail or antennae follow-through |

## Aspect ratios and safe areas

| ratio | use | safe area |
|-------|-----|-----------|
| `9:16` | TikTok, Reels, Shorts, Douyin, Kuaishou, WeChat Channels | head in the top 70%, bottom 25% clear of UI |
| `16:9` | YouTube, Bilibili, thumbnails | character centred, key detail inside the inner 80% |
| `1:1` | avatars, profile images, listings | symmetric even margins |
| `4:5` | Instagram, Pinterest feed | like 9:16 with more vertical room |
| `3:4` | poster base, thumbnail | 12% margin all round |
| `2:3` | print, poster, merch | feet above the bottom 8% |
| `21:9` | channel banners, headers | character in one third, centre clear |

Design `1:1` first. It crops safely into everything else. On `9:16`, never
centre the face vertically — the platform UI eats the lower third.

## Transparent background

Two paths.

**In the prompt.** Add `isolated on a transparent background`, and negative
`drop shadow`, `background elements`, `checkered pattern`. Works on current
engines; quality varies.

**In post.** Generate on a flat contrasting colour, then key it out. More
reliable, and it gives you a clean matte. This is the standard production
route for sticker packs.

Always generate both: a `sticker` prompt already carries the die-cut white
border variant, and the transparent variant needs its own prompt.

## Text in images

Do not render text. Channel names, captions, handle text and logo type all go
in your editor. Generated text is unreliable across every engine, wastes
renders, and creates avoidable trademark exposure.

The `banner` template therefore leaves the right two-thirds empty by design.