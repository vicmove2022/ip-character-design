# ip-character-design

Design IP characters (IP形象 / 吉祥物 / 虚拟形象) for video creators, and
generate platform-agnostic prompts that render them consistently across a whole
channel.

**36 character styles × 11 rendering media × a 16-slot character sheet**, plus
turnaround sheets, expression sheets, pose sheets, sticker and avatar sets,
seamless loops, and image-to-video motion prompts.

For video creators: short-form and long-form aspect ratios with safe areas,
reaction cut-in grammar, loop construction, and per-platform delivery specs.

---

## Install

Drop the folder into your agent's skills directory. Nothing to install — no
Python packages, no npm packages.

```bash
git clone https://github.com/<you>/ip-character-design.git
```

Then point your agent at it:

| agent | location |
|-------|----------|
| Claude Code | `~/.claude/skills/ip-character-design/` |
| opencode | `~/.config/opencode/skills/ip-character-design/` |
| Cursor | `.cursor/rules/` or your rules directory |
| any agent reading `SKILL.md` | anywhere; reference it by path |

The CLIs work from any directory — data paths resolve relative to the script.

## Quick start

```bash
# what styles are there?
python scripts/build_prompt.py styles
python scripts/build_prompt.py families

# one character, one prompt
python scripts/build_prompt.py build \
  --style anthropomorphic-plant --medium cel-shading \
  --subject "a small round terracotta pot with a happy face" \
  --signature "three lime-green leaves sprouting from the rim" \
  --palette "warm terracotta pot, lime green foliage, charcoal outline" \
  --expression happy --proportion 1-3 --ratio 9:16

# the whole asset kit as JSON
python scripts/build_prompt.py kit \
  --style anthropomorphic-food --medium soft-3d-render \
  --subject "a single ripe peach with velvety skin" \
  --signature "one small red ribbon tied at the stem" \
  --palette "peach pink, magenta, sage green, charcoal outline" \
  --proportion 1-2 --expression excited --out peach-kit.json

# freeze the character so later shots match
python scripts/build_prompt.py consistency \
  --style anthropomorphic-food --medium soft-3d-render \
  --subject "a single ripe peach with velvety skin" \
  --signature "one small red ribbon tied at the stem"

# motion
python scripts/build_prompt.py video --type image-to-video \
  --motion "a friendly wave with two wrist sways, the arm returning exactly to the start position"
```

Prefer Node? Every command is identical:

```bash
node scripts/build_prompt.mjs styles
node scripts/build_prompt.mjs kit --style felt-wool-plush --medium pastel-soft --out cat.json
```

The two implementations are asserted byte-identical by the test suite.

## How it works

Three independent pieces.

**A style library.** 36 named character styles across 8 families — mascot and
chibi, 3D and toy, flat vector and sticker, pixel and low-poly, plush and
handmade, anime and illustration, anthropomorphic, realistic and avatar. Each
carries its proportion, surface, lighting, Chinese keywords, and notes on where
it works and where it fails.

**A medium layer.** 11 rendering media — hand-drawn marker, pencil, ink line,
watercolour, gouache, oil impasto, pastel, cel shading, flat vector, soft 3D,
photoreal. Orthogonal to the style: any character can be rendered in any medium,
so `felt-wool-plush` + `watercolor` is a felt character painted in watercolour.

**A 16-slot character sheet.** The parameters that make one character *this*
character: subject, role, signature feature, proportion, silhouette, palette,
material, outfit, expression, pose, world, signature mark, medium, lighting,
composition, quality.

Prompts are assembled from these in a fixed order, so every prompt in a series
has the same shape:

```
[identity slots] → [style core] → [medium core] → [lighting] → [ratio] → [quality]
```

The assembler handles the mechanical parts: conflicting lighting is stripped
from the style core when a medium is chosen, duplicate segments collapse, empty
slots drop out along with the prepositions they strand, and every output prompt
is validated to contain no unfilled tokens.

## Design gates

Three checks prevent most wasted renders.

**Silhouette test.** One cheap render, solid black shape on white. If the
outline is not recognisable with zero internal detail, the design fails as a
thumbnail, as a reaction GIF, and as merchandise. Run this first, every time.

**Numeric proportion.** Engines default to 1:7 human proportions regardless of
your request. `1:3` or `three-head-tall cartoon proportions` is what actually
moves them.

**Named outline colour.** `charcoal outline`, `cream outline`, `no outline`. An
unnamed outline gets redrawn differently on every generation. This is the
single most effective consistency lock available.

## Consistency, honestly

Text locks reduce drift. They do not eliminate it — every generation is an
independent sample. In increasing strength:

1. Text locks — the identity block, pasted verbatim. Free.
2. Seed — reproducible, but you cannot change pose and keep the face.
3. Reference image — feed the identity shot back in as a character reference
   on every generation. This is what actually holds a character.

The skill emits platform-agnostic prompts with no engine-specific flags. Where
your engine offers character-reference, style-reference or image-to-image input,
use it alongside the prompts.

The production workflow in `references/character-consistency.md` covers the
drift diagnosis table and the rebuild procedure for a series that has already
drifted.

## Video

Ten shot types — establishing, character beat, reaction cut-in, action, detail,
loop — each with camera guidance and length. A motion vocabulary with explicit
timing, seven camera moves, four lens notes, and specs for TikTok / Reels /
Shorts / Douyin / Kuaishou / WeChat Channels, YouTube, Bilibili, e-commerce and
live commerce.

Loops need three things: a static camera, a plain background, and an explicitly
stated return to the start pose. All three are baked into the loop template.

## Safety

No prompt from this skill names an artist, studio, franchise, brand or
celebrity. Descriptors name visual features instead, which is both legally
cleaner and more controllable — engines throttle artist-name prompts, and "in
the style of" is risky in a redistributable repository.

`brand-safe-words.json` holds the full rewrite table, and `check` fails the
build if a banned name reaches the style data. Real logos are never rendered:
the `holding-product` pose says *plain unbranded box*, and the banner template
leaves space for text you add in an editor.

## Showcase

`showcase/ALL-STYLES.md` — one worked example per style, all 36: the identity
prompt, the negative prompt, and a matching seamless-loop prompt. Generated by
`scripts/make_showcase.py`, so it never drifts from the data.

```bash
python scripts/make_showcase.py                      # rewrite the showcase
python scripts/make_showcase.py --id chibi-q-chibi   # one style as JSON
```

## Commands

| command | purpose |
|---------|---------|
| `styles [--family F] [--search Q] [-v]` | list 36 styles |
| `families` | 8 families with counts |
| `media [-v]` | 11 media with pairings |
| `show <id> [-v]` | detail for one style or medium |
| `build` | one prompt |
| `kit` | 10-deliverable set, JSON export |
| `consistency` | identity block, render block, lock checklist |
| `video --type image-to-video\|text-to-video\|camera` | motion prompts |
| `check` | validate data files and naming policy |

Ids accept aliases and both spellings — `watercolour`, `3D`, `chibi`, `food`,
`VTuber`, `animal mascot` all resolve.

## Tests

```bash
python -m unittest discover -s tests       # 61 tests
node --test tests/build_prompt.test.mjs    # 14 tests
node scripts/build_prompt.mjs check        # data validation
```

The suite asserts data integrity, prompt hygiene (no unfilled tokens, no empty
segments), grid retuning, and byte-level parity between the two CLIs.

## Extending

`data/*.json` is the single source of truth. Both CLIs read it — edit the JSON,
never the scripts.

**Add a style:** append to `data/styles.json` with every required field
(`python scripts/build_prompt.py check` names anything missing), add its family
to `data/negatives.json` `by_family`, and add aliases to `_ALIASES` in both
scripts.

**Add a medium:** append to `data/media.json` with a `default_lighting` value,
add its id to `data/negatives.json` `by_medium`.

**Add a slot:** add it to `data/anatomy.json` `slots` and
`prompt_slot_order`, add a flag in both scripts.

Then re-run both test suites — the parity test will catch a one-sided change.

## Repository layout

```
SKILL.md                    the skill entry point
data/                       single source of truth
  styles.json               36 styles, 8 families
  media.json                11 rendering media
  anatomy.json              16 slots, 10 proportion presets
  negatives.json            global / family / medium / video pools
  deliverables.json         ratios, 10 templates, expressions, poses, loops, cameras
  brand-safe-words.json     naming policy and rewrite map
scripts/
  build_prompt.py           CLI, standard library only
  build_prompt.mjs          CLI, zero dependencies
  make_showcase.py          regenerates showcase/ALL-STYLES.md
showcase/
  ALL-STYLES.md             one worked example per style, all 36
tests/
  test_build_prompt.py      44 tests
  test_docs_examples.py     17 tests incl. doc-drift and showcase checks
  build_prompt.test.mjs     14 tests incl. cross-runtime parity
references/
  prompt-assembly.md        slot order, emission order, weight syntax
  media-layers.md           choosing a medium; phrases each one needs
  character-consistency.md  workflow, drift diagnosis, rebuild
  deliverables.md          the 10 types, loops, ratios, transparency
  video-production.md       shot grammar, motion, cameras, platform specs
  anthropomorphic-playbook.md  food / object / plant / body-part / creature
  brand-safety.md           naming constraint and rewrites
  naming-and-glossary.md    naming, style ids, word banks, Chinese terms
  recipes.md                8 complete character builds
  troubleshooting.md        symptom-first fixes
```

## Licence

MIT. See `LICENSE`.

Generated output is yours; no claim of resemblance to any existing character is
made or implied.