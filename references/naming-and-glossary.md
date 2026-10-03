# Naming a Character

Character names, style ids and prompt vocabulary for people who need to name
things. The style ids in `styles.json` are fixed API surface — those you copy
exactly. This file is for the rest.

## Style id vocabulary

`--style` accepts the exact id, or any alias. Both work:

| exact id | accepted aliases |
|----------|------------------|
| `blob-mascot` | blob, bean, simple mascot |
| `chibi-q-chibi` | chibi, qversion, chibi q |
| `anthropomorphic-animal-mascot` | animal mascot |
| `retro-sports-mascot` | retro mascot, sports mascot |
| `friendly-brand-mascot` | friendly mascot, brand mascot |
| `soft-3d-render` | soft, 3d, 3drender |
| `designer-vinyl-figure` | vinyl, toy, figma |
| `clay-plasticine` | clay, plasticine, claymation |
| `paper-craft` | papercraft, paper |
| `resin-art-figure` | resin |
| `flat-vector` | flat, vector |
| `die-cut-sticker` | sticker, diecut |
| `line-art-minimal` | minimal, lineart |
| `memphis-pop` | memphis, pop |
| `geometric-shape-character` | geometric, shapes |
| `pixel-8bit` | pixel, pixelart, 8bit |
| `pixel-16bit-rpg` | 16bit, sprite |
| `low-poly-3d` | lowpoly, low poly |
| `voxel-art` | voxel |
| `felt-wool-plush` | felt, wool, plush |
| `stuffed-fabric-doll` | doll, stuffed |
| `crochet-amigurumi` | crochet, yarn, amigurumi |
| `button-felt-doll` | patchwork, folk art |
| `anime-cel-shaded` | anime, cel, celshading |
| `chibi-anime-cute` | cute, kawaii |
| `manga-line-art` | manga, ink |
| `watercolor-storybook` | storybook, watercolor book |
| `oil-impasto` | oil, impasto |
| `anthropomorphic-food` | food |
| `anthropomorphic-object` | object |
| `anthropomorphic-plant` | plant |
| `anthropomorphic-body-part` | bodypart |
| `whimsical-creature` | creature, monster |
| `photoreal-virtual-human` | human, photoreal |
| `semi-real-human-illustration` | semireal |
| `styled-avatar-nonhuman` | vtuber, avatar |

`--medium` accepts: `hand-drawn-marker` (marker) · `pencil-sketch` (sketch,
graphite) · `ink-line` (ink) · `watercolor` (watercolour) · `gouache` ·
`oil-impasto` (oil) · `pastel-soft` (pastel) · `cel-shading` ·
`flat-color-digital` (vector, digital) · `soft-3d-render` · `photoreal` (photo)

British and American spellings both resolve. `check` validates the canonical
ids.

## Naming patterns

Names for IP characters work best when they are short, sound out loud, and do
not describe appearance.

### Sound-alike names
`Momo`, `Pip`, `Bix`, `Nori`, `Kiko`, `Zuzu`, `Waffle`, `Toast`, `Bun`

### Compound of a plain noun
`Bread Loaf`, `Paper Moon`, `Tiny Kettle`, `Quiet Storm`, `Slow Morning`

### One syllable plus a suffix
`-o`, `-ee`, `-ie`, `-kin`, `-let`: `Bobo`, `Suki`, `Mikki`, `Fenkin`, `Larklet`

### Onomatopoeia
`Ploop`, `Boing`, `Snork`, `Chirp`, `Thunk`, `Wobble`

Avoid: names that describe appearance (`Red Blob`), names that describe
personality (`Happy`), and long names that do not survive a caption.

## Naming by style family

| family | fits | avoid |
|--------|------|-------|
| mascot-chibi | short, punchy, one syllable | long or formal |
| 3d-toy | collectible-sounding, product-like | organic, wordy |
| flat-sticker | meme-native, funny, literal | elegant, quiet |
| pixel-lowpoly | game-like, shortened | long full names |
| craft-plush | cosy, food-adjacent, warm | techy, sharp |
| anime-illustration | Japanese or invented, single word | generic English given names |
| anthropomorphic | the object's own logic (a pear named `Pip`) | unrelated human names |
| realistic-avatar | a plausible human name | invented, cute, short |

For anthropomorphic characters, naming from the object works best. A peach
called `Pip`, a kettle called `Kettle`. The name confirms what it is instead
of competing with the visual.

## Signature mark naming

The small repeatable graphic device in the `signature_mark` slot. Name it so
you can reference it in shot lists:

| name | description |
|------|-------------|
| three-dot | three dots, position varies |
| stitched-x | an X stitch, often on an ear or sleeve |
| single-stripe | one diagonal stripe, chest or arm |
| notched-ear | a notch or nick in one ear |
| freckle-cluster | a group of small spots |
| brass-stud | one small metal stud or rivet |
| tail-knot | a knot or band at the base of the tail |
| pocket-patch | a small contrasting patch on one garment |

Keep the mark identical across the whole cast. It is the cheapest identity
lock available, and it is what makes a family of characters read as related.

## Prompt vocabulary reference

Words that reliably change the output, by intent.

### Shape and proportion
`two-head-tall chibi proportions` · `three-head-tall cartoon proportions` ·
`realistic seven-head-tall human proportions` · `blocky cubic limbs` ·
`a round teardrop silhouette` · `a wide low mushroom silhouette` ·
`a tall thin hourglass silhouette` · `a low wide dome silhouette`

### Surface
`matte painted plastic with a slightly rough surface` ·
`wool felt with visible individual fibres` ·
`glossy injection-moulded vinyl with a parting seam` ·
`matte unglazed terracotta` · `velvety fruit skin with fine fuzz` ·
`brushed metal with fingerprints and light scratching` ·
`soft mossy skin with fine leaf texture`

### Colour
`warm grey body, amber eyes, one red accent, charcoal outline` ·
`primary teal, secondary cream, accent coral, deep charcoal outline` ·
`off-white body, coral accent, deep charcoal outline` ·
`mustard yellow, teal, one coral accent, black outline`

Always name the outline colour. Always cap at five.

### Expression (mouth-first)
`warm open smile with raised cheeks and slightly narrowed happy eyes` ·
`small round open mouth with huge widened eyes and raised eyebrows` ·
`one eyebrow raised with a crooked mouth and one eye half closed` ·
`flat unimpressed stare with a straight-line mouth and flat eyebrows` ·
`downturned mouth with inner-brow raise and heavy upper eyelids`

### Framing
`standing front-facing in a centred full-body shot` ·
`three-quarter turn with one hand on the hip` ·
`leaning forward in a medium close-up, looking straight at the viewer` ·
`head and shoulders only, centred` ·
`full body visible, head and feet in frame`

### Lighting
`soft large-area key from upper front with a gentle rim light` ·
`single hard key from upper left with graphic shadow shapes` ·
`flat even lighting with no cast shadow` ·
`warm backlight exploiting translucency` ·
`backlit rim lighting against a dark gradient background`

### Quality tails
`clean high-quality render, sharp focus on the subject, professional composition` ·
`clean high-quality illustration, sharp focus on the subject, professional art direction` ·
`professional photography, sharp focus on the subject, natural lighting, high detail` ·
`crisp pixel edges, no anti-aliasing, limited palette` ·
`clean minimal composition, sharp focus on the subject`

## Chinese prompt vocabulary

Useful when a model responds better to Chinese prompts, or when handing prompts
to a Chinese-speaking team. These are the same descriptors in Chinese.

| intent | 中文 |
|--------|------|
| proportion | 两头身 / 三头身 / 五头身 / 七头身写实比例 |
| matte surface | 哑光表面, 无高光 |
| felt | 羊毛毡, 可见绒毛纤维, 刺绣五官 |
| glossy vinyl | 搪胶质感, 注塑接缝, 高光反射 |
| clay | 黏土, 指纹, 工具刮痕 |
| watercolour | 水彩, 透明水彩, 湿边, 颗粒沉积, 留白高光 |
| oil paint | 厚涂油画, 刮刀堆叠, 浓郁暗部 |
| pencil | 铅笔素描, 排线阴影, 草图线可见 |
| cel shading | 赛璐璐, 平涂色块, 硬边阴影, 两阶阴影 |
| pixel | 像素网格, 无抗锯齿, 四色限制, 抖动渐变 |
| low poly | 低多边形, 三角面, 平面着色 |
| flat vector | 扁平矢量, 纯平涂, 无渐变, 统一线宽 |
| silhouette | 剪影, 单色黑, 无内部细节 |
| expression | 表情, 张嘴笑, 挑眉, 瞪大眼睛, 面无表情 |
| framing | 全身入镜, 正面居中, 中近景, 头肩特写 |
| lighting | 柔光箱主光, 边缘光, 硬光投影, 无投影平光 |
| negative | 多余肢体, 多余手指, 文字水印, 变形, 模糊 |

Style names in Chinese are in `styles.json` under `name_zh`, and per-style
keyword lists under `kw_zh`:

```bash
python scripts/build_prompt.py show anthropomorphic-plant
```

The skill emits English prompts by default, since every mainstream engine
handles them and they stay portable across regions. Use the Chinese vocabulary
as a translation layer for specific engines, or for briefs.

## Tag conventions for your own asset library

```
<channel>/<character>/<style>-<medium>/<deliverable>-<ratio>-v<n>
```

Example:
```
cooking-channel/peach/anth-food-soft3d/identity-1x1-v3.png
cooking-channel/peach/anth-food-soft3d/expr-sheet-16x9-v1.png
cooking-channel/peach/anth-food-soft3d/loop-1x1-v2.gif
```

Version the identity shot separately and reference it everywhere else. The
identity image is the contract; bump its version only when the character
changes deliberately.