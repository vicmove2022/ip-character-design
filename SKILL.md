---
name: ip-character-design
description: >
  Design IP characters (IP形象 / 吉祥物 / 虚拟形象) for video creators and generate
  platform-agnostic prompts for them. Use when the user wants to create, describe,
  restyle or ship a character mascot - including anthropomorphic food, objects,
  plants and body parts - or needs character turnaround sheets, expression sheets,
  pose sheets, sticker/avatar sets, seamless loops, or image-to-video motion prompts.
  Triggers: "IP character", "mascot", "character design", "create a mascot", "IP形象",
  "吉祥物", "虚拟形象", "卡通形象", "角色设定", "三视图", "表情包", "turnaround sheet",
  "expression sheet", "character for my channel", "sticker pack", "avatar mascot",
  "character for TikTok / Reels / Shorts / Douyin / Bilibili", "loop animation",
  "anthropomorphic food/object/plant", "make my food channel mascot". Covers 36 named
  styles across 8 families crossed with 11 rendering media, plus video-delivery
  specs for short-form platforms.
license: MIT
---

# IP Character Design

Design IP characters for video creators, and produce the prompts that render
them consistently across a whole channel.

## The model

A prompt is built from two **independent** axes and one **character sheet**.

```
STYLE  (36 across 8 families)   what kind of character object is this
   ×
MEDIUM (11 rendering media)      how it is drawn — orthogonal, freely combinable
   +
16 SLOT SHEET                    who this specific character is
```

Style and medium never constrain each other. `media.json` records which
combinations engines handle reliably, but nothing is forbidden — the flagged
combinations are where the interesting hybrids live.

The **character sheet** is what you fill in for one specific character. Its
three load-bearing slots:

- **signature feature** — exactly one unforgettable physical thing
- **proportion** — numeric (`1:3`, `three-head-tall`). Engines default to 1:7
  human proportions no matter what you ask for.
- **palette** — 2-5 named colours, and always name the outline colour

## Workflow

Work in this order. Each step is cheaper than the next.

```
1. PICK       choose one style family + one medium for the whole channel
2. FILL       complete all 16 slots in data/anatomy.json
3. TEST       run `silhouette-test` FIRST — one cheap render that saves the rest
4. LOCK       run `identity`, keep the image as the reference for everything after
5. FREEZE     run `consistency`, save the identity block to a text file
6. PRODUCE    kit: turnaround → expression sheet → pose sheet → scene → loop → sticker → avatar → banner
7. SHIP       video prompts with the motion vocabulary
```

Never skip step 3. A character that needs interior detail to be recognisable
fails as a thumbnail, as a reaction GIF, and as a merchandise print. Fix the
silhouette, not the details.

## Commands

Both CLIs are equivalent and produce byte-identical output. Python: standard
library only. Node: zero dependencies.

```bash
python scripts/build_prompt.py <command>      # or: node scripts/build_prompt.mjs <command>
```

| command | purpose |
|---------|---------|
| `styles [--family F] [--search Q] [-v]` | list the 36 styles |
| `families` | list the 8 families with counts |
| `media [-v]` | list the 11 media with pairings |
| `show <id> [-v]` | full detail for a style or medium |
| `build` | one assembled prompt |
| `kit` | the full 10-deliverable set, JSON export |
| `consistency` | identity block + render block + lock checklist |
| `video --type ...` | image-to-video / text-to-video / camera prompt |
| `check` | validate all data files and the banned-word policy |

Ids accept aliases and both spellings: `watercolour`, `3D`, `chibi`, `food`,
`VTuber`, `animal mascot` all resolve. Unknown ids are errors on purpose — a
silent miss means a wrong character.

### Character flags

`--subject` what it is · `--signature` the one feature · `--silhouette` ·
`--palette` (name the outline) · `--material` · `--proportion` ·
`--expression` · `--pose` · `--world` · `--outfit` · `--role` · `--mark`
`--style` · `--medium` · `--ratio` · `--lighting` · `--quality`
`--negative` (repeatable) · `--show-negative` · `--format json`

Optional selectors on `kit`: `--only ID` · `--expressions ID` · `--poses ID`
· `--out FILE`. Video-only: `--motion` · `--camera` · `--lens` · `--type`.

## Examples

### One prompt

```bash
python scripts/build_prompt.py build \
  --style anthropomorphic-plant --medium cel-shading \
  --subject "a small round terracotta pot with a happy face" \
  --signature "three lime-green leaves sprouting from the rim" \
  --silhouette "a wide low mushroom silhouette" \
  --palette "warm terracotta pot, lime green foliage, charcoal outline" \
  --material "matte unglazed terracotta" \
  --expression happy --proportion 1-3 --ratio 9:16 --show-negative
```

### Full asset kit

```bash
python scripts/build_prompt.py kit \
  --style anthropomorphic-food --medium soft-3d-render \
  --subject "a single ripe peach with velvety skin" \
  --signature "one small red ribbon tied at the stem" \
  --silhouette "a round teardrop silhouette" \
  --palette "warm peach pink body, deep magenta shadow, sage green leaf, charcoal outline" \
  --material "velvety fruit skin with fine fuzz" \
  --expression excited --proportion 1-2 \
  --world "on a pale marble kitchen counter" \
  --ratio 1:1 --out peach-kit.json
```

### Subset, plus a lock

```bash
python scripts/build_prompt.py kit \
  --style blob-mascot --medium flat-color-digital \
  --subject "a small round slime creature with two eyes" \
  --signature "a single bright magenta diamond floating above it" \
  --expressions happy --expressions annoyed --expressions confused \
  --poses heart-hands --poses thumbs-up \
  --ratio 1:1 --out slime-kit.json

python scripts/build_prompt.py consistency \
  --style blob-mascot --medium flat-color-digital \
  --subject "a small round slime creature with two eyes" \
  --signature "a single bright magenta diamond floating above it" \
  --palette "electric teal body, magenta accent, dark outline"
```

Selecting fewer than 6 expressions or poses rewrites the panel count and grid
shape automatically.

### Video

```bash
python scripts/build_prompt.py video --type image-to-video \
  --style friendly-brand-mascot --medium flat-color-digital \
  --motion "a friendly wave with two wrist sways, the arm returning exactly to the start position"

python scripts/build_prompt.py video --type camera --camera orbit --lens portrait \
  --subject "a round vinyl figure with one antenna" \
  --signature "one antenna with a red bead on the tip"
```

The video templates append the constraints that stop drift: static camera,
unchanged identity, consistent lighting, no morphing. Add your own with
`--negative`.

## The ten deliverables

Generated in this order. Full notes in `references/deliverables.md`.

1. `silhouette-test` — solid black shape. The design gate.
2. `identity` — canonical hero shot. The reference everything else uses.
3. `turnaround` — front / side / three-quarter / back
4. `expression-sheet` — 6 heads-and-shoulders, 3x2
5. `pose-sheet` — 6 full-body poses, 2x3
6. `scene` — the character in its world
7. `loop` — seamless looping frame (static camera, plain background)
8. `sticker` — die-cut with white border
9. `avatar` — head-and-shoulders icon, detail deleted not shrunk
10. `banner` — character in one third, space clear for text

Aspect ratios: `9:16` short-form · `16:9` long-form and thumbnails · `1:1`
design this one first, it crops into everything · `4:5` feed · `3:4` poster ·
`2:3` print · `21:9` headers.

## Consistency, honestly

Text locks reduce drift. They do not eliminate it. Every generation is an
independent sample. Three mechanisms, increasing strength:

1. **Text locks** — the identity block, pasted verbatim. Free, weak.
2. **Seed** — some engines allow pinning. Does not let you change pose and keep
   the face, which is the real requirement.
3. **Reference image** — feed the identity shot back in as a character
   reference on every generation. This is what actually works.

This skill is platform-agnostic and emits no engine-specific flags. Where an
engine has character-reference, style-reference or image-to-image input, use it
alongside the prompts. Image locks beat text locks.

## Hard rules

1. **Never name artists, studios, franchises or brands in prompts.** Describe
   the visual feature instead. Reasons and a full rewrite table in
   `references/brand-safety.md`. `check` fails the build if a banned name
   reaches the style data.
2. **Never render real logos or text.** Add channel names in an editor.
   The `banner` template leaves space by design.
3. **One medium per channel.** Changing medium between episodes produces a
   different-looking character.
4. **Regenerate drift, never average it.** Two candidates blended is a third
   character nobody approved.
5. **Aspect ratio fixed for the whole series.** Changing it mid-series means
   regenerating every frame.
6. **Outfit and outline colour stated in every prompt.** Wardrobe and outline
   drift are the two most common consistency failures.

## Reference files

Read these on demand, not upfront.

| file | read when |
|------|-----------|
| `references/prompt-assembly.md` | slot order, emission order, prompt length limits, weight syntax per engine |
| `references/media-layers.md` | choosing a medium; the distinguishing phrases each one needs |
| `references/character-consistency.md` | the production workflow, drift diagnosis table, rebuild procedure |
| `references/deliverables.md` | the 10 deliverable types, loops, aspect ratios, transparent background |
| `references/video-production.md` | shot grammar, motion vocabulary, camera moves, platform specs |
| `references/anthropomorphic-playbook.md` | food / object / plant / body-part / creature design rules |
| `references/brand-safety.md` | the naming constraint, rewrite table, legal hygiene |
| `references/naming-and-glossary.md` | naming characters, style id vocabulary, prompt word banks, Chinese terms |
| `references/recipes.md` | eight complete copy-pasteable character builds |
| `references/troubleshooting.md` | symptom-first fixes for prompts, images, video and scripts |
| `showcase/ALL-STYLES.md` | one worked example per style, generated not hand-written |

## Data files

`data/*.json` is the single source of truth. Both CLIs read it; edit the JSON,
not the scripts. Run `check` after any edit.

| file | contents |
|------|----------|
| `styles.json` | 36 styles in 8 families, each with `core_en`, proportion, surface, lighting, zh keywords, video and loop notes, use/avoid cases |
| `media.json` | 11 media, orthogonal pairings, distinguishing phrases, default lighting |
| `anatomy.json` | the 16 slots with questions, examples and lock rules; 10 proportion presets |
| `negatives.json` | global, per-family, per-medium and video negative pools; 5 quality tails |
| `deliverables.json` | 7 ratios with safe areas, 10 templates, 11 expressions, poses, loop motions, camera moves, lenses |
| `brand-safe-words.json` | the naming policy and rewrite map |

## Showcase

`showcase/ALL-STYLES.md` holds one worked example per style — identity prompt,
negative, and a matching loop prompt — for all 36. It is generated by
`scripts/make_showcase.py`, which calls the CLI directly, so it cannot drift
from the data.

```bash
python scripts/make_showcase.py                 # rewrite showcase/ALL-STYLES.md
python scripts/make_showcase.py --id chibi-q-chibi   # one style as JSON
```

## Tests

```bash
python -m unittest discover -s tests    # 61 tests
node --test tests/build_prompt.test.mjs  # 14 tests, includes cross-runtime parity
node scripts/build_prompt.mjs check      # data validation
```

The suite asserts the two CLIs stay byte-identical. If you change one script,
port the change to the other and re-run.