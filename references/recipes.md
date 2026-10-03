# Recipes

Eight complete character builds, each copy-pasteable. Every one passes
`check` and produces prompts with no empty slots.

All flags work identically in both CLIs:

```bash
python scripts/build_prompt.py <args>
node  scripts/build_prompt.mjs <args>
```

---

## 1. Food channel mascot — peach

Food is the highest-reach anthropomorphic lane and the cheapest to produce.

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

Then the lock block:

```bash
python scripts/build_prompt.py consistency \
  --style anthropomorphic-food --medium soft-3d-render \
  --subject "a single ripe peach with velvety skin" \
  --signature "one small red ribbon tied at the stem" \
  --palette "warm peach pink body, deep magenta shadow, sage green leaf, charcoal outline" \
  --material "velvety fruit skin with fine fuzz" \
  --proportion 1-2 --expression excited
```

---

## 2. Tech channel — matte 3D robot

The default modern tech-startup look.

```bash
python scripts/build_prompt.py kit \
  --style soft-3d-render --medium soft-3d-render \
  --subject "a small pear-shaped robot with a friendly face" \
  --signature "one antenna with a red bead on the tip" \
  --silhouette "a round teardrop silhouette" \
  --palette "off-white body, coral accent, deep charcoal outline" \
  --material "matte painted plastic with a slightly rough surface" \
  --expression neutral --proportion 1-2.5 \
  --ratio 1:1 --out robot-kit.json
```

---

## 3. Handmade / ASMR channel — felt cat

Plush plus pastel reads as hand-made and survives compression well.

```bash
python scripts/build_prompt.py kit \
  --style felt-wool-plush --medium pastel-soft \
  --subject "a small round grey cat with big amber eyes" \
  --signature "one tiny red knitted scarf" \
  --silhouette "a low round dome silhouette" \
  --palette "warm grey body, amber eyes, one red accent, charcoal outline" \
  --material "wool felt with visible individual fibres and embroidered features" \
  --expression happy --proportion 1-2.5 \
  --world "on a soft cream knitted blanket" \
  --ratio 1:1 --out cat-kit.json
```

Loop prompt:

```bash
python scripts/build_prompt.py video --type image-to-video \
  --style felt-wool-plush --medium pastel-soft \
  --motion "a slow gentle breathing bob with a soft blink near the end"
```

---

## 4. Kids / story channel — chibi explorer

Clean cel shading, wide palette, one strong silhouette.

```bash
python scripts/build_prompt.py kit \
  --style chibi-q-chibi --medium cel-shading \
  --subject "a small brave explorer child with a round face" \
  --signature "one oversized yellow rain boot on the left foot" \
  --silhouette "a wide low triangle silhouette" \
  --palette "mustard yellow jacket, teal shorts, one coral accent, charcoal outline" \
  --material "clean cartoon shading with soft fabric shapes" \
  --outfit "a mustard yellow hooded jacket, teal shorts, a small brown satchel" \
  --expression excited --proportion 1-2 \
  --world "at the edge of a mossy forest clearing" \
  --ratio 9:16 --out explorer-kit.json
```

---

## 5. Gaming / retro channel — pixel slime

Hard grid, four colours, no medium painterliness.

```bash
python scripts/build_prompt.py kit \
  --style blob-mascot --medium flat-color-digital \
  --subject "a small round slime creature with two eyes" \
  --signature "a single bright magenta diamond floating above it" \
  --silhouette "a soft round blob silhouette" \
  --palette "electric teal body, magenta accent, dark outline" \
  --material "smooth flat colour with a glossy top highlight" \
  --expression happy --proportion 1-1 \
  --ratio 1:1 --out slime-kit.json
```

Keep the medium flat here. Watercolour on a pixel character destroys the grid.

---

## 6. Live commerce presenter — semi-real host

Talking-head in illustration form, when a real presenter is not available.

```bash
python scripts/build_prompt.py kit \
  --style semi-real-human-illustration --medium flat-color-digital \
  --subject "a friendly young woman with shoulder-length dark hair" \
  --signature "one small gold star earring on the left ear" \
  --palette "warm skin tones, deep teal top, gold accent" \
  --expression happy --proportion 1-7 \
  --poses thumbs-up --poses holding-product \
  --ratio 9:16 --out host-kit.json
```

`holding-product` renders *plain unbranded box*. Do not edit it to name a
product.

---

## 7. Mindfulness / plant channel — terracotta pot

Growth arcs are the serial hook.

```bash
python scripts/build_prompt.py kit \
  --style anthropomorphic-plant --medium cel-shading \
  --subject "a small round terracotta pot with a happy face" \
  --signature "three lime-green leaves sprouting from the rim" \
  --silhouette "a wide low mushroom silhouette" \
  --palette "warm terracotta pot, lime green foliage, charcoal outline" \
  --material "matte unglazed terracotta with real soil texture" \
  --expression neutral --proportion 1-3 \
  --world "on a sunlit windowsill with potted plants blurred behind" \
  --ratio 9:16 --out plant-kit.json
```

---

## 8. Shorts / meme channel — retro mascot

Maximum contrast, minimum detail, reads at any size.

```bash
python scripts/build_prompt.py kit \
  --style retro-sports-mascot --medium cel-shading \
  --subject "a chunky bird mascot with a thick neck" \
  --signature "one crimson scarf trailing behind it" \
  --silhouette "a heavy forward-leaning wedge silhouette" \
  --palette "crimson primary, cream secondary, deep navy accent, black outline" \
  --material "hard cel shading with thick black outline" \
  --expression excited --proportion 1-2.5 \
  --ratio 9:16 --out mascot-kit.json
```

---

## Building your own

1. Pick one style family, one medium.
2. Fill all 16 slots. Required: subject, signature, silhouette, proportion,
   palette, material, expression, pose.
3. Run `silhouette-test` first. Redesign if the black shape is not
   recognisable.
4. Run `identity` and keep the image as your reference.
5. Run `consistency` and save the identity block.
6. Run the full `kit`, export JSON.
7. Build expression and pose sheets, then scenes, then the loop.
8. Generate video with `video` and the motion vocabulary.

## Variations worth making early

| variant | how |
|---------|-----|
| alternate expression | `--expression annoyed` |
| emotion subset sheet | `--expressions happy --expressions sad` |
| custom pose sheet | `--poses heart-hands --poses shaka` |
| single deliverable | `--only loop --out loop.json` |
| ratio override | `--ratio 9:16` on any command |
| extra negatives | `--negative "watermark" --negative "text"` |
| explicit lighting | `--lighting "hard key from upper left, no fill"` |
| free-text proportion | `--proportion-phrase "one and a half head tall"` |