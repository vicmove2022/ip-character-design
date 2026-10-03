# Rendering Medium Layers

The medium axis answers "how is this drawn", independently of "what kind of
character object is this". Same character, eleven media, ten different products.

Full data in `media.json`. List with pairings:

```bash
python scripts/build_prompt.py media -v
```

## The eleven media

| id | name | 中文 | reads as |
|----|------|------|----------|
| `hand-drawn-marker` | Marker & Ink Hand-Drawn | 马克笔手绘 | scanned sketchbook |
| `pencil-sketch` | Pencil & Graphite Sketch | 铅笔素描 | graphite on paper |
| `ink-line` | Ink Brush Line Art | 墨线笔绘 | sumi-e brush line |
| `watercolor` | Watercolour Wash | 水彩 | wet pigment washes |
| `gouache` | Gouache & Flat Paint | 水粉与平涂颜料 | matte opaque paint |
| `oil-impasto` | Oil Impasto | 油画厚涂 | palette-knife ridges |
| `pastel-soft` | Soft Pastel & Chalk | 粉彩与粉笔 | velvety powder |
| `cel-shading` | Cel / Flat Digital Shading | 赛璐璐平涂 | anime flats |
| `flat-color-digital` | Flat Digital Vector | 数字平涂矢量 | crisp vector art |
| `soft-3d-render` | Soft 3D Render | 柔光3D渲染 | matte studio 3D |
| `photoreal` | Photoreal / Photo | 写实摄影 | photograph of an object |

## Pairing guidance

`media.json` carries `pairs_well` and `pairs_badly` per medium. Read them as
tells about where engines are reliable, not as permission tables.

### Reliable combinations

| style family | media that hold up |
|--------------|-------------------|
| mascot-chibi | all hand media, cel-shading, flat-color-digital, soft-3d-render |
| 3d-toy | soft-3d-render, photoreal, gouache, pastel-soft |
| flat-sticker | flat-color-digital, gouache, ink-line, cel-shading, hand-drawn-marker |
| pixel-lowpoly | flat-color-digital only (any painterly medium destroys the grid) |
| craft-plush | pastel-soft, watercolor, gouache, photoreal, soft-3d-render |
| anime-illustration | cel-shading, ink-line, watercolor, oil-impasto, pencil-sketch |
| anthropomorphic | watercolor, soft-3d-render, cel-shading, gouache, photoreal |
| realistic-avatar | photoreal, soft-3d-render, pencil-sketch, oil-impasto |

### Combinations that need extra language

**`pixel-lowpoly` + anything painterly.** A 32-pixel sprite cannot have wet
edges. Add `strict pixel grid, hard edges, no anti-aliasing` and negative
`smooth gradients, soft edges, texture`. Better still: use
`flat-color-digital`.

**`3d-toy` + hand media.** Gouache-clay and paper-craft work because the medium
and the material agree. Watercolour-vinyl does not — the gloss has nowhere to
go. Add `matte, soft, no specular highlights` and it works.

**`mascot-chibi` + photoreal.** A chibi rendered photographically usually lands
in uncanny territory. Either commit (`miniature vinyl figure photographed on a
desk`) or use `soft-3d-render`.

**`craft-plush` + cel-shading.** Fibre texture and hard shadow bands fight.
Either pick the fibre (pastel, watercolor) or pick the graphic (cel).

## Medium-specific techniques

These are the phrases that make each medium actually land, rather than
defaulting to generic illustration.

### Marker & hand-drawn
Add `stroke overlap`, `paper tooth`, `slightly uneven stroke weight`. Without
these it renders as flat vector and the hand-made quality disappears.

### Pencil & graphite
Add `visible tonal hatching`, `cross-hatching`, `construction lines partially
visible`. Value must come from hatching or the engine skips to photoreal.

### Ink brush
Add `tapered strokes with thick-to-thin variation`, `dry-brush texture at
stroke ends`. Uniform line width kills it instantly.

### Watercolour
Reserve white paper. `reserved white paper highlights`, `cold-press paper
texture`. Full-canvas opaque coverage is the failure mode — it reads as
gouache.

### Gouache
`matte opaque fills`, `no gloss`, `slight value variation within each fill`. The
matte word matters; without it engines add a gloss that gouache does not have.

### Oil impasto
`visible palette knife ridges`, `paint peaks catching light`, `visible canvas
weave`. Physical thickness must be stated — "oil painting" alone renders flat.

### Pastel
`velvety matte powder texture`, `visible chalk grain`, `paper tooth showing
through`. Needs the tooth or it looks like soft digital.

### Cel shading
Name the band count: `two or three flat shading bands`. Add `crisp terminator
line`. Never `smooth gradient` or it collapses into generic 2D.

### Flat vector
Ban gradients explicitly: negative `gradient, texture, blur`. One accidental
soft transition and it stops reading as vector.

### Soft 3D render
`matte dielectric material`, `soft area key light`. Glossy materials turn it
into product photography, which is a different deliverable.

### Photoreal
Keep the imperfection: `real wear`, `subtle fingerprints`, `natural lighting
falloff`. Sterile perfect renders of characters read as uncanny. Give real
scale cues or the character looks like a floating doll.

## Choosing a medium

Ask what the deliverable is.

- **Sticker or emote pack** → flat-color-digital, die-cut
- **Video insert with dialogue** → cel-shading, flat-color-digital
- **ASMR or slow content** → watercolor, pastel-soft, pencil-sketch
- **Merchandise product shots** → soft-3d-render, photoreal, gouache
- **Narrative storytelling** → cel-shading, ink-line, watercolor, oil-impasto
- **Retro or game channel** → pixel or low-poly styles, flat-color-digital medium
- **Live commerce / presenter** → soft-3d-render, photoreal

## One style, eleven mediums

Same character, changing only the medium:

```bash
for m in watercolor pencil-sketch cel-shading soft-3d-render photoreal; do
  python scripts/build_prompt.py build \
    --style chibi-q-chibi --medium "$m" \
    --subject "a small round robot with a cheerful face" \
    --signature "one antenna with a red bead on the tip" \
    --palette "off-white body, coral accent, charcoal outline" \
    --material "matte painted plastic" \
    --expression happy --proportion 1-3 --ratio 1:1
done
```

Do not publish these as one character. Different mediums read as different
characters because surface language is part of identity. Pick one medium per
channel and hold it.