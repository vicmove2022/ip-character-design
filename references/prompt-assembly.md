# Prompt Assembly

How a prompt gets built in this skill, and why it is shaped that way.

## The two orthogonal axes

Every prompt is the product of **one style** (what kind of character object is
this) crossed with **one medium** (how it is rendered). They are independent:

```
        medium →
style ↓  watercolor   pencil    cel-shading   soft-3d   pixel
────────────────────────────────────────────────────────────────
mascot      ✓            ✓          ✓            ✓        ✓
3D-toy      ✗            ✗          ✗            ✓        ✗
pixel       ✗            ✗          ✗            ✗        ✓
```

Full lists: `styles.json` (36 styles, 8 families) and `media.json`
(11 media). `media.json` records `pairs_well` / `pairs_badly` as guidance, not
rules. The combinations marked `✗` are not forbidden — they are where the
interesting hybrids live. They are flagged because most engines produce
inconsistent results there unless you add extra language.

Read: `python scripts/build_prompt.py media -v`

## The sixteen slots

Slots are emitted in a fixed order so every prompt in a series has the same
shape. Full definitions with examples and lock rules in `anatomy.json`.

| # | slot | flag | required |
|---|------|------|----------|
| 1 | subject | `--subject` | yes |
| 2 | role | `--role` | no |
| 3 | signature_feature | `--signature` | yes |
| 4 | proportion | `--proportion` | yes |
| 5 | silhouette | `--silhouette` | yes |
| 6 | palette | `--palette` | yes |
| 7 | material | `--material` | yes |
| 8 | outfit | `--outfit` | no |
| 9 | expression | `--expression` | yes |
| 10 | pose | `--pose` | yes |
| 11 | world | `--world` | no |
| 12 | signature_mark | `--mark` | no |
| 13 | medium | `--medium` | yes |
| 14 | lighting | `--lighting` | yes (defaults from medium) |
| 15 | composition | `--ratio` | yes |
| 16 | quality | `--quality` | yes (auto-derived) |

Three of these carry more weight than their position suggests.

**signature_feature** is the character. One feature, described so it survives
being shrunk to a thumbnail. `one oversized round yellow rain boot` works.
`a charming little adventurer` does not.

**proportion** must be numeric. Every image engine defaults toward 1:7 human
proportions regardless of what you asked for. `1:3` or `three-head-tall
cartoon proportions` is what actually moves it.

**palette** must include the outline colour. Naming it (`charcoal outline`,
`cream outline`, `no outline`) is the single most effective consistency lock
across generations. An unnamed outline gets redrawn differently every time.

## Emission order

```
[identity slots 1-12] → [style core] → [medium core] → [lighting] → [ratio] → [quality]
```

Identity first, because early tokens get more weight. Style before medium,
because the medium is the modifier applied to the character, not the other way
round. Render controls last, because they are the most per-frame variable.

## Automatic conflict resolution

Style cores carry a default lighting hint (`food photography lighting with
appetising specular highlights` on Anthropomorphic Food). That hint fights the
medium you chose, so the assembler strips lighting segments from the style core
whenever a medium or an explicit `--lighting` is present.

Verified: `felt-wool-plush` + `watercolor` produces a felt character in
watercolour, not a felt character with vinyl-toy studio lighting on top.

## Clean-up rules

The assembler never emits a mechanical artefact:

- duplicate comma segments collapse (case-insensitive)
- empty slots drop out, along with the preposition they stranded
  (`{subject} with {signature_feature}, {palette}` → `a pear, yellow`)
- unfilled `{tokens}` are stripped
- the final string is capitalised once and given one terminal period

## Worked example

```bash
python scripts/build_prompt.py build \
  --style anthropomorphic-plant \
  --medium cel-shading \
  --subject "a small round terracotta pot with a happy face" \
  --signature "three lime-green leaves sprouting from the rim" \
  --silhouette "a wide low mushroom silhouette" \
  --palette "warm terracotta pot, lime green foliage, charcoal outline" \
  --material "matte unglazed terracotta" \
  --expression happy \
  --proportion 1-3 \
  --ratio 9:16 \
  --show-negative
```

Emits:

```
A small round terracotta pot with a happy face, three lime-green leaves
sprouting from the rim, three-head-tall cartoon proportions, a wide low
mushroom silhouette, warm terracotta pot, lime green foliage, charcoal
outline, matte unglazed terracotta, warm open smile with raised cheeks and
slightly narrowed happy eyes, an anthropomorphic potted plant character,
terracotta pot as the body with a simple expressive face, large lush foliage
and leaves forming the character's hair, real botanical leaf veining and soil
texture, small simple arms growing from the pot rim, calm neutral studio
styling, gentle plant-care aesthetic, digital cel shading, clean lineart with
two or three flat shading bands, crisp terminator lines between bands, flat
saturated local colour, hard-edged shadows, subtle rim light, high-key
lighting, single hard key from upper left with graphic shadow shapes and a
rim light, 9:16, clean high-quality render, sharp focus on the subject,
professional composition.
```

Read the sentence in three beats: *what it is and what makes it that character*
→ *what kind of object and how it is drawn* → *how it is lit, framed and
finished*. If a beat is wrong, that tells you which slot to fix.

## Prompt length

The full sixteen slots produce roughly 90-140 words. That is fine for
Midjourney, Flux, SDXL, Seedream and current image models. Older engines and
some regional models truncate around 60 words or weight the tail negligibly.

If you hit a short-engine limit, drop in this order: `world`, `signature_mark`,
`quality`, then `material`. Never drop `signature_feature`, `proportion` or
`palette`.

## Weight syntax

This skill is deliberately platform-agnostic, so it emits no weighting syntax.
Every major engine has one, and it differs:

| engine | syntax |
|--------|--------|
| Midjourney | `--style`, plus emphasis by repeating a term |
| SDXL / Flux (A1111-style) | `(term:1.4)` |
| ComfyUI | `(term:1.4)` in the CLIP text encode |
| Gemini / Nano Banana | natural language emphasis ("most important: ...") |
| Seedream, Kling, Veo | natural language; ignore weights |

If your engine wants weights, wrap the identity slots at 1.2-1.4 and leave the
style core at 1.0. Do not weight everything — it flattens the result.