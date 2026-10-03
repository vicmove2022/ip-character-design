# Character Consistency

The hard part of IP character work is not designing the character. It is
generating the same character forty times.

`python scripts/build_prompt.py consistency` prints the two blocks and the
checklist. This file explains why they are split and what to do when a frame
drifts anyway.

## Two blocks, two lifetimes

```
IDENTITY BLOCK  -- never changes within a series
  subject, role, signature_feature, proportion, silhouette, palette,
  material, outfit, expression_default, signature_mark

RENDER BLOCK    -- constant within a series, changed deliberately between series
  style core, medium core, lighting, ratio, quality tail
```

`pose` and `world` are excluded from both. They are the variables you *want*
to change per shot.

The `expression` slot is in the identity block because it is set per character
for identity shots — you change it deliberately when building an expression
sheet, and the sheet template handles that.

## Why text locks are not enough

Text locks reduce drift. They do not eliminate it. Every generation is an
independent sample; the model reads the same sentence and produces a different
sample each time.

Three mechanisms, in increasing order of strength:

**1. Text locks** — the identity block, pasted verbatim. Weakest. Free.

**2. Seed / reproducibility** — some engines let you pin a seed. A fixed seed
plus an identical prompt reproduces a close result. It does not let you change
the pose and keep the face, which is the actual requirement.

**3. Reference image** — feed the locked identity shot back in as a character
reference on every subsequent generation. This is what actually works.

Every mainstream engine has some form of reference input, named differently:

| capability | generic name |
|------------|--------------|
| character identity from a reference image | character reference / `--cref` / face reference / IP-Adapter / InstantID / PuLID |
| style from a reference image | style reference / `--sref` |
| composition or pose from an image | image-to-image / ControlNet / `--cref` with pose control / reference-only |

This skill emits platform-agnostic prompts, so it does not write any of these
flags. Use them alongside the prompts.

## The workflow that holds a character

```
1. DESIGN      fill the 16 slots. Generate the identity shot.
2. VERIFY      silhouette test. If the black shape is not distinctive, redesign now.
3. LOCK        run `consistency`. Save the identity block to a text file.
4. ANCHOR      keep the best identity image as your reference file.
5. PRODUCE     regenerate with the identity block + reference image, varying only pose/world.
6. INSPECT     check against the checklist below. Regenerate, do not average.
```

Step 6 matters more than people expect. The failure mode is accepting a frame
that is 90% right. Two wrong eyes in a 240-frame series is a different-looking
character every time it appears.

## Pre-flight checklist

Run this before generating a batch.

- [ ] Silhouette test passed (solid black shape is recognisable)
- [ ] Signature feature is a physical thing, not an adjective
- [ ] Head-to-body ratio stated numerically (`1:3`, not `chibi`)
- [ ] Outline colour named (`charcoal outline`)
- [ ] Palette capped at 5 colours including the outline
- [ ] One primary material plus at most one secondary
- [ ] Outfit described or explicitly stated as "no clothing"
- [ ] Medium chosen and written down
- [ ] Lighting chosen for identity shots
- [ ] Aspect ratio fixed for the whole series
- [ ] Mouth shape specified (mouth carries more emotion than eyes)
- [ ] Neutral front-facing pose for the identity shot, not a dramatic one
- [ ] Plain background for the identity shot
- [ ] Reference image saved for every subsequent generation

## Diagnosing drift

Match the symptom to the cause.

| symptom | cause | fix |
|---------|-------|-----|
| face changes between frames | no reference image | add character reference |
| proportions drift toward 1:7 | ratio not numeric | state `1:3` every time |
| outline colour changes | outline unnamed | name it explicitly |
| outfit changes | outfit described loosely | write the full garment list |
| palette slowly shifts | more than 5 colours | cap at 5, name the outline |
| hands or eyes malformed | negative prompt missing | add the global negative set |
| style drifts mid-series | medium changed | hold the medium, always |
| lighting shifts | lighting not fixed | pin the lighting phrase |
| character looks like two characters | two design branches shipped | pick one identity image, discard the other |

## The unfixable-but-manageable cases

**Long animation runs.** No current tool holds a character perfectly across
hundreds of frames. The production answer is a keyframe workflow: generate the
turnaround, animate between locked keyframes, keep shots short (3-6 seconds),
and cut on motion. Do not attempt one continuous 30-second generation with a
character in it.

**Style swapping across a series.** Changing medium between episode 1 and
episode 2 produces a different-looking character. Either hold the medium or
accept the character has two identities. If you must change, change
everything at once (medium, lighting, outline) so the shift reads as
deliberate rather than drift.

**Crowded scenes.** Two characters in one prompt halves the fidelity of each.
Generate characters separately and composite. Multi-character prompts are for
establishing shots only.

## Rebuilding a drifted character

When a series has already drifted into two or three incompatible looks:

1. Pick the single most-successful image as the new canonical identity.
2. Re-run the silhouette test against it.
3. Rebuild the identity block from that image's attributes.
4. Regenerate the expression and pose sheets from the new block.
5. Re-shoot the oldest episodes, or re-edit them to favour whichever variant
   appears most.
6. From that point on, treat the identity image as immutable.

Shipping a fix forward is easier than reconciling a shipped archive.