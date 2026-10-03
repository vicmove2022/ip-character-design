# Brand Safety and Naming

This skill never emits artist names, studio names, franchise names or brand
names in prompts. That is a deliberate design constraint, and this file
explains the reasoning plus the rewrite table.

## Why the constraint

**Engines throttle it.** Some image engines refuse prompts naming living
artists or studios outright. Others return visibly worse results, or quietly
weaken the request. On a redistributable skill, that makes prompts less
reliable for every user.

**It is legally risky.** "In the style of [living artist]" is a request to
reproduce a specific identifiable creative output. For a public repository
that anyone can run, that is the kind of term you do not want in your own text.

**It does not work as well.** Naming a studio gives the model a compression of
thousands of images. Describing the visual features — matte dielectric
material, soft area key light, pastel gradient backdrop — gives it the actual
rendering instructions. The description is both safer and more controllable.

**Generic descriptors are freely usable.** "Cel shaded", "low poly",
"watercolour", "oil impasto", "die-cut sticker" are techniques. They belong to
nobody.

## Policy

1. Never write `in the style of <artist>`, `<artist>-style`, or `like
   <movie / TV / game character>`.
2. Describe the visual **feature** you want, not the name of the thing that
   has it.
3. Never name a real product brand, logo, or franchise character.
4. Never request a real celebrity likeness.
5. If a user asks for a named artist, say the tradeoff once, then supply the
   generic-descriptor rewrite.

## Rewrite table

| Instead of | Write |
|------------|-------|
| flat vector illustration | flat vector illustration, modern editorial vector style |
| soft 3D render | soft matte 3D render, pastel studio 3D render |
| claymation stop motion | modelling clay character, clay stop-motion aesthetic |
| designer toy figure | glossy designer vinyl toy, collectible vinyl figure |
| Pixar-style 3D | soft matte 3D render with expressive eyes, stylised 3D animated-feature look |
| Disney-style 2D | classic hand-drawn animated feature style, traditional cel animation look |
| anime style | anime cel-shaded illustration, Japanese animation character illustration |
| Ghibli-style | painterly Japanese animation background art, lush hand-painted anime landscape |
| cartoon style | cartoon illustration with thick outline, stylised cartoon character design |
| cute style | cute stylised character with large eyes and soft forms, kawaii character design |
| realistic photo | photorealistic photography, documentary photograph |
| cinematic look | cinematic lighting with shallow depth of field, anamorphic framing |
| minimalist | minimal flat design with generous negative space |
| meme style | bold high-contrast comic illustration, impact-style reaction graphic |
| corporate friendly | clean flat illustration with a soft palette, approachable brand illustration |
| retro 8-bit | 8-bit pixel art sprite, 16-bit console pixel art |
| low poly | low-poly flat-shaded 3D, faceted geometric 3D |
| watercolor | watercolour with wet edges and granulation, loose watercolour illustration |
| oil painting | oil impasto painting, classical oil painting technique |
| pencil sketch | graphite pencil sketch, charcoal sketch |
| sticker | die-cut vinyl sticker, glossy laminated sticker |
| emoji style | flat emoji-style pictogram, simple face icon |
| line art | single-weight line art, minimal ink line drawing |

Machine-readable copy in `data/brand-safe-words.json`.

## Franchise characters

Describe, never name.

| Instead of | Write |
|------------|-------|
| a small round mouse with red shorts | a small round mouse with big round ears and red shorts |
| a yellow electric mouse | a small round yellow creature with pointed black ears and a lightning-bolt tail |
| a red-eared cat in a hat | a small red-eared cat wearing a pointed green hat |
| a robot mouse with a red nose | a small metal robot with round ears, a red button nose and a key on its back |
| a blue round-eared creature | a small blue round creature with large solid oval eyes and no nose |

The negative pool for `anthropomorphic` includes `real brand marks`,
`brand logos`, and `recognisable copyrighted creature` (on
`whimsical-creature`).

## Product brands

Never name a brand. Describe the generic object.

- `a yellow banana-shaped phone case`, not a phone case by name
- `a red aluminium soda can with a plain white band`, not a cola can
- `a white paper cup with a plain green sleeve`, not a coffee chain cup
- `a plain unbranded white cardboard box` — this is the default in the
  `holding-product` pose

The `holding-product` pose deliberately says *plain unbranded product box*.
Do not edit it to include a brand.

## Engine-blocking words

These commonly trigger filters or platform blocks. Treat them as blocked:

Pixar · Disney · Ghibli · Marvel · Sanrio · LEGO · Pokémon · Mario · Star Wars
· Harry Potter · Barbie · Hello Kitty · Transformers

The `check` command scans `styles.json` for these and fails the build if any
appear. Extend the list there if you add styles.

## What is safe to write

Technique and material vocabulary belongs to nobody:

cel shaded · flat vector · low poly · voxel · pixel art · matte 3D render ·
soft clay · needle felt · wool felt · oil impasto · watercolour · gouache ·
risograph print · linocut · art deco poster · mid-century modern poster ·
comic book ink · blueprint drawing · cyanotype · scratchboard · gouache ·
airbrush · halftone print · double exposure · bokeh · chiaroscuro

Generic period references are also fine when they describe a look, not an
artist: `1920s art deco poster style`, `1970srisograph print aesthetic`,
`mid-century modern advertising illustration`.

## Legal hygiene for a public repo

- MIT-licence the code and data. Prompts in this repo are original text.
- Do not include example prompts that name artists, brands or franchises.
- Do not commit reference images you do not have the right to redistribute.
- If you publish generated output commercially, check your engine's terms on
  artist-style references, and note the engine you used alongside the work.
- Do not claim a generated character resembles an existing character. Design
  from the slots, not from a target.

## The test before publishing

Ask: could someone read this prompt and name a specific living artist, studio,
brand or franchise as the source?

If yes, rewrite it with the feature description. If you cannot rewrite it
without losing the visual intent, the intent was a reference, not a
specification — specify the visual instead.