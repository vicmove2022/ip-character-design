# Anthropomorphic Playbook

Turning non-human things into characters is the highest-reach lane in this
skill. The reason is not charm — it is that viewers do not have a reference
frame for what the object is "supposed to" to look like, so they read intent
from the face instead of comparing it to a real animal.

Five families:

- `anthropomorphic-food` — food as characters
- `anthropomorphic-object` — everyday objects as characters
- `anthropomorphic-plant` — potted plants, flowers, succulents
- `anthropomorphic-body-part` — a hand, an eye, a tooth, a shoe
- `whimsical-creature` — invented species for lore-heavy channels

## The three-question test

Before generating anything, answer these three.

**Where do the eyes go?** This is the whole design. Not a detail.

- A mug: on the barrel, above the handle
- A microwave: on the door glass, or the dial becomes the eye
- A pear: upper third, above the widest point
- A sneaker: on the toe cap, laces as lashes
- A pot plant: on the pot, foliage as hair

Get this wrong and nothing else matters. If the eyes are in a plausible place
for the object but not a place a viewer can find instantly, move them.

**What is the body doing?** An object needs a stance before it needs a face.
Crossed arms, a lean, a tilt — stance carries personality at thumbnail size,
and the face carries it at full size. Do both.

**What is the one readable feature?** Every anthropomorphic character needs
one element that survives being shrunk. A chipped rim. A bent antenna. A
single missing tooth. A fraying edge.

## Food

`anthropomorphic-food` keeps the food's true surface and adds face and limbs.
That combination is the whole trick: appetising and appealing.

```bash
python scripts/build_prompt.py build \
  --style anthropomorphic-food --medium soft-3d-render \
  --subject "a single ripe peach with velvety skin" \
  --signature "one small red ribbon tied at the stem" \
  --silhouette "a round teardrop silhouette" \
  --palette "warm peach pink body, deep magenta shadow, sage green leaf, charcoal outline" \
  --material "velvety fruit skin with fine fuzz" \
  --expression excited --proportion 1-2 \
  --pose "standing upright in a centred full-body shot with one arm raised waving" \
  --ratio 1:1
```

Rules that matter:

- **Keep the surface honest.** `velvety skin with fine fuzz`, not glossy
  plastic. Audiences read food in the first 200ms, and a plastic peach is a
  toy, not lunch.
- **No gore, no rot, no insects, no mould.** The negative pool includes
  `sickly or rotten food`, `distressing imagery`, `horror gore`.
- **Food photography lighting**, not studio-flat. Appetising specular
  highlights on the subject, kitchen surface underneath.
- **Cast, not mascot.** A recurring cast of foods becomes a series format —
  one channel, one character per episode.

What works best: fruit, sandwiches, desserts, drinks, noodles. What tends to
fail: whole cooked animals, plated restaurant dishes (too much visual noise),
anything where the face lands on a busy textured region.

## Objects

`anthropomorphic-object` renders the object's real material and adds the
minimum anatomy needed to act.

```bash
python scripts/build_prompt.py build \
  --style anthropomorphic-object --medium cel-shading \
  --subject "a dented metal kettle with a whistling spout" \
  --signature "one long steam curl shaped like a question mark" \
  --silhouette "a tall rounded triangle silhouette" \
  --palette "brushed steel body, one red enamel accent, charcoal outline" \
  --material "brushed metal with fingerprints and light scratching" \
  --expression thinking --proportion 1-3 \
  --ratio 9:16
```

Rules that matter:

- **Never a real brand.** The negative pool blocks logos and brand marks.
  Describe `a yellow banana-shaped phone case`, not a phone case by name.
- **Real wear stays.** Fingerprints, scratches, dents, chipped enamel. Perfect
  surfaces make objects look like cheap 3D renders.
- **Face at the most characterful end.** The end of a whisk, the head of a
  hammer, the crown of a pineapple.
- **Product lighting, not studio-flat.** Soft key with controlled gradient
  backdrop, so the object reads as a real photographed object.

This lane is the strongest fit for tool channels, gadget channels, POV skits,
and everyday-life content. Objects are also the cheapest characters to keep
consistent, because the object itself constrains the design.

## Plants

`anthropomorphic-plant` uses the pot as the body and foliage as hair. The
proportion is settled by physics — a plant is a pot on the ground, so the pot
becomes the legs.

```bash
python scripts/build_prompt.py build \
  --style anthropomorphic-plant --medium cel-shading \
  --subject "a small round terracotta pot with a happy face" \
  --signature "three lime-green leaves sprouting from the rim" \
  --silhouette "a wide low mushroom silhouette" \
  --palette "warm terracotta pot, lime green foliage, charcoal outline" \
  --material "matte unglazed terracotta" \
  --expression happy --proportion 1-3 \
  --ratio 1:1
```

Rules that matter:

- **Face on the pot.** Foliage is hair, never a face.
- **Real botany.** `leaf veining`, `soil texture`, `matte unglazed terracotta`.
  Fake plant texture reads instantly as plastic.
- **Arms from the pot rim**, not from the leaves.
- **Growth is the narrative device.** Sprout to flower to fruiting is a
  built-in story arc. Slow leaf sway is the signature loop.
- Negative pool blocks `plastic plants`, `wilting or dying plant`,
  `desaturated colours`.

Fits gardening, plant-care, wellness, slow-living and eco content. Growth
progression is the strongest serial hook this style offers.

## Body parts

`anthropomorphic-body-part` turns one body part into the entire character.
The single part is the head and the body; the limbs are tiny.

```bash
python scripts/build_prompt.py build \
  --style anthropomorphic-body-part --medium soft-3d-render \
  --subject "a single white molar tooth with a happy face" \
  --signature "one small gold star stuck to one corner" \
  --silhouette "a wide rounded square silhouette" \
  --palette "warm ivory, one soft gold accent, charcoal outline" \
  --material "glossy enamel with fine surface detail" \
  --expression neutral --proportion 1-1 \
  --ratio 1:1
```

Rules that matter:

- **True-to-material rendering.** A tooth is enamel. An eye is wet and glossy.
  A hand is skin with knuckle creases.
- **Exaggerate proportions for comedy.** Tiny limbs, big eyes, elastic
  surface.
- **No gore, no clinical detail.** The negative pool blocks `graphic gore`,
  `blood`, `distressing medical detail`, `photoreal human face`. Keep it
  cheerful or comedic; medical realism is not this lane.
- Each new topic becomes a new character, which makes it a natural serial
  format.

Fits medical, dental, fitness and wellness explainers, plus any channel that
wants a talking hook with high meme potential.

## Invented creatures

`whimsical-creature` is the only lane that rewards a full cast and a world.
Use it when the channel is lore-driven rather than object-driven.

```bash
python scripts/build_prompt.py build \
  --style whimsical-creature --medium cel-shading \
  --subject "a small six-legged forest creature with a leaf-shaped head" \
  --signature "three glowing dots along its back that change colour with mood" \
  --silhouette "a low wide dome silhouette" \
  --palette "moss green body, amber glow, deep charcoal outline" \
  --material "soft mossy skin with fine leaf texture" \
  --expression curious --proportion 1-3 \
  --ratio 1:1
```

Rules that matter:

- **Signature feature carries the mood.** The colour-shifting dots mean one
  design serves ten episodes.
- **Silhouette first.** With invented species you have no prior, so the
  outline is the entire identity. Run the silhouette test before anything else.
- **Never a generic dragon or elf.** The negative pool blocks
  `existing franchise species`, `recognisable copyrighted creature`,
  `generic dragon or elf`. Add `original design` explicitly.
- **Secondary motion is free character.** Tail, antennae, tendrils give you
  idle loops for nothing.

## Cross-lane casts

A channel can mix lanes if the identity block is shared. The `signature_mark`
slot is what makes it work:

```
identity: a small mossy creature with a leaf-shaped head
mark: three glowing dots along the back
```

Give every member of the cast the same mark. Change species, proportions and
palette per member; keep the mark. That reads as a family without a caption.

## What fails in this lane

| failure | why | fix |
|---------|-----|-----|
| face on a busy textured region | cannot be found at thumbnail size | move it to a flat area |
| eyes too close together | reads as angry or injured | widen to about one eye-width apart |
| limbs too long | loses the object's identity | 1:2 to 1:3, tiny limbs |
| object renders glossy plastic | not a real object | add wear, use true material |
| real brand visible | legal exposure | block logos, describe generic products |
| character could be any object | no silhouette | silhouette test, add signature feature |
| too many colours | identity dissolves | cap at 5 including outline |

## Content formats this lane unlocks

- **Cast episodes** — one food or object per episode, recurring format
- **Object POV** — the camera is the partner, the object is the POV
- **Emotion reaction packs** — the expression sheet is the product
- **Growth arcs** — plants, fermentation, ripening, rusting, weathering
- **Comparison skits** — two objects arguing, one per side of frame
- **Assembly lines** — build a world from a creature family, one design per
  episode