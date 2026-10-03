# Troubleshooting

Symptom-first. Find what you see, fix the cause.

## The prompt itself

**Empty segments or dangling words (`a pear with, yellow`)**
Fixed automatically by `fill`. If you see it, you are running an older copy —
update the script. Every generated prompt should pass `check`.

**Unfilled `{tokens}` left in the output**
The template references a slot the assembler does not know. `check` catches
this. Either add the token to `anatomy.json` slots or change the template.

**Prompt too long, engine truncating**
Drop slots in this order: `world`, `signature_mark`, `quality`, `material`.
Never drop `signature_feature`, `proportion` or `palette`. See
`prompt-assembly.md`.

**Duplicated phrases** (`grey, charcoal outline, charcoal outline`)
`join()` dedupes case-insensitively. If you see repeats, the duplication is
inside one style or medium core in the JSON — edit the core.

**Style lighting fights the medium**
Fixed by `strip_light_segments`. If you still see `studio lighting` inside a
watercolour prompt, check that `--medium` was actually resolved (run
`show <id>` to confirm).

## The generated image

### Design problems

**Silhouette not recognisable**
Run `silhouette-test`. If the solid black shape fails, the design fails. Change
the silhouette, not the interior details. Common fixes: exaggerate the head,
add one strong protrusion, narrow the waist, change the overall shape category
(round / tall / wide).

**Character reads as generic**
Usually one of three: too many palette colours, no signature feature, or a
proportion that defaults to 1:7. Cap at 5 colours, add one physical feature,
state the ratio numerically.

**Eyes hard to find**
Move them to a flatter region and widen to about one eye-width apart. For
anthropomorphic objects, the eyes define the design — reposition before
adjusting anything else.

**Looks like two different characters across shots**
Almost always missing a reference image, or the medium changed mid-series. See
`character-consistency.md`.

### Anatomy problems

| symptom | cause | fix |
|---------|-------|-----|
| extra or fused limbs | no negative prompt | add the global negatives (the assembler does this) |
| melted hands | too small in frame, or no hand description | `medium close-up`, or mitten hands |
| asymmetric eyes | low-quality anatomy control | `--negative "asymmetrical eyes"` |
| cropped feet | full body not requested | add `full body visible, head and feet in frame` |
| distorted face | wrong proportion slot | state ratio numerically |

### Surface problems

**Medium ignored, generic illustration returned**
The distinguishing phrases are missing. Compare your prompt against
`media-layers.md` for that medium. Test with a deliberately obvious case
(`strict 32 by 32 pixel grid, no anti-aliasing`) to see whether the engine is
respecting medium instructions at all.

**Style core contradicts the medium**
Should not happen. If it does, add the medium's conflicting term to
`--negative`.

**Glossy when you wanted matte**
Add `matte`, `no specular highlights`, `--negative "glossy surface, chrome reflection"`.

**Flat when you wanted texture**
Name the physical texture: `visible canvas weave`, `paper grain`,
`visible individual fibres`, `pigment granulation`.

**Palette drifting between generations**
Name the outline colour. It is the most effective single lock.

### Video problems

**Face morphs mid-clip**
Shorten the clip, use image-to-video with a reference, and state `no morphing`.
Character-holding models are best at 3-5 seconds.

**Texture crawls or shimmers**
Too much fine detail. Simplify the material, or move to a flatter medium
(`flat-color-digital`, `cel-shading`).

**Limbs appear or vanish**
Name proportions and add `no morphing`. Reduce the amount of body motion.

**Background warps**
Static camera, plain background. Any camera movement in an image-to-video
prompt causes warping.

**Colours shift between frames**
Pin the lighting. Also check that you did not change the medium between the
still and the video pass.

**Loop seam visible**
Asymmetric motion. State the return-to-start explicitly: `the arm returning
exactly to the start position`. Use a static camera and a plain background.

**Character too small on screen**
Add `medium close-up`, `head and shoulders in the upper two thirds`. On 9:16,
the head belongs in the top 70%.

### Consistency problems

| symptom | cause | fix |
|---------|-------|-----|
| face changes per frame | no reference image | character reference on every generation |
| proportions drift to 1:7 | ratio not numeric | `1:3` or `three-head-tall cartoon proportions` |
| outline colour shifts | outline unnamed | `charcoal outline` |
| outfit changes | loosely described | full garment list |
| style drifts | medium changed | hold the medium |
| lighting shifts | lighting unpinned | fix the lighting phrase |

## Data and scripts

**`check` fails**
Read the reported problem. It names the exact style, media or deliverable and
the missing key. Fix the JSON, not the script.

**`Unknown style or media id`**
List what exists:
```bash
python scripts/build_prompt.py styles --format ids
python scripts/build_prompt.py media
```
Aliases cover common variations (`watercolour`, `3D`, `chibi`, `VTuber`).
Unknown ids are errors on purpose — a silent miss means a wrong style.

**Chinese characters mangled in output**
Set UTF-8: `python -X utf8 scripts/build_prompt.py ...`, or
`chcp 65001` on Windows. Use `--format json --out file.json` for large runs.

**Python and Node output differ**
They should be byte-identical. The test suite asserts it for eleven command
shapes. If you changed one script, port the change to the other:

```bash
python -m unittest discover -s tests
node --test tests/build_prompt.test.mjs
```

The parity test compares outputs with CRLF normalised, since Python writes
CRLF on Windows and Node writes LF.

**Script not found**
Paths resolve relative to the script location, so any working directory works.
Verify: `python scripts/build_prompt.py check`.

## Design problems that are not bugs

Some issues are decisions, not defects.

**The character is too cute for the topic.** Pick a less cute style family —
`retro-sports-mascot`, `manga-line-art`, `photoreal-virtual-human`.

**The style fights the platform.** Photoreal characters read as generic on a
fast-scrolling feed. Graphic styles (`flat-sticker`, `memphis-pop`) win on
short-form.

**It works as a sticker but not in motion.** Some styles are excellent in flat
motion graphics and poor in 3D-inferred video. Check the `video` note on each
style with `show <id>`.

**Two styles look better than one.** You are not obliged to use a single
style. Many channels run one hero character plus occasional variants.

## Getting a clean series from scratch

The full reset, when a design has drifted:

1. Pick the single best existing image as the new canonical identity.
2. Re-run `silhouette-test` against it.
3. Rebuild the 16 slots from that image.
4. Save the identity block from `consistency`.
5. Regenerate expression and pose sheets.
6. Re-shoot or re-edit older episodes.
7. From here, treat the identity image as immutable.