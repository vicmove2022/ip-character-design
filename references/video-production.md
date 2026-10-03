# Video Production

Everything a character needs once the still images exist: aspect ratios for
each platform, motion prompts, camera language, and how to build a loop that
survives compression.

## Shot grammar

The character is not the shot. What the character *does in frame* is the shot.

| shot | camera | purpose | length |
|------|--------|---------|--------|
| establishing | wide, static or slow push | where we are, character's place in the world | 2-4s |
| character beat | medium close-up, static | the reaction or the line | 2-4s |
| reaction cut-in | tight on face, static | the punchline | 0.5-1.5s |
| action | tracking or handheld follow | movement that carries meaning | 2-3s |
| detail | macro or tight | the texture, the prop, the reaction | 1-2s |
| loop / idle | locked static | background presence, breathing room | 3-6s |

Reaction cut-ins are the highest-retention element in short-form. That is
what the expression sheet is for. Build it before you build anything else.

## Motion prompts

```bash
python scripts/build_prompt.py video --type image-to-video \
  --motion "a gentle breathing bob with a soft blink halfway through" \
  --style chibi-q-chibi --medium cel-shading
```

The template appends the constraints that matter: `camera stays completely
static`, `character identity and the background remain completely unchanged`,
`consistent lighting`, `no morphing`, `smooth continuous motion`.

Text-to-video, when you have no first frame:

```bash
python scripts/build_prompt.py video --type text-to-video \
  --style anthropomorphic-food --medium soft-3d-render \
  --subject "a single ripe peach with velvety skin" \
  --signature "one small red ribbon tied at the stem" \
  --palette "peach pink, magenta, sage green, charcoal outline" \
  --proportion 1-2 --expression happy --ratio 9:16 \
  --motion "the peach slowly turns to face the viewer and waves"
```

Image-to-video always looks better than text-to-video for characters. If the
engine supports a reference or first-frame input, use it — the drift term is
dramatically lower.

## Motion vocabulary

| intent | phrasing |
|--------|----------|
| idle presence | `a gentle breathing bob with a subtle chest rise and fall` |
| emphasis | `a small quick bounce with anticipation squash before landing` |
| agreement | `a single nod, twice, with a slight forward lean` |
| disagreement | `a slow head shake with raised eyebrows` |
| celebration | `two upward jumps with both arms raised` |
| surprise | `a sharp recoil backwards with widened eyes` |
| thinking | `looking up and to the side, then a slow return to centre` |
| presenting | `one arm extending toward the viewer, palm up` |
| secondary motion | `hair and fabric swaying gently with a one-second delay after the body stops` |

Two rules:

**State the timing.** `with a soft blink halfway through`, `over two seconds`.
Without timing you get one long drift.

**One action per clip.** Movement plus expression plus camera is three
variables; models handle one reliably and two unreliably.

## Camera moves

| id | move | use |
|----|------|-----|
| `static` | locked off, no movement | reaction cut-ins, loops, dialogue |
| `slow-push` | very slow push-in | emotional emphasis, reveal |
| `slow-pull` | slow pull-back | reveal the world, punchline setup |
| `orbit` | smooth 20° orbit | product-style showcase |
| `handheld-follow` | light handheld with natural shake | documentary energy |
| `pan-follow` | lateral pan tracking a walk | following movement |
| `tilt-reveal` | tilt from feet to head | dramatic reveal |

```bash
python scripts/build_prompt.py video --type camera \
  --camera orbit --lens portrait \
  --subject "a round vinyl figure with one antenna" \
  --signature "one antenna with a red bead" \
  --palette "off-white, coral, charcoal outline"
```

Lens: `wide` (24mm, deep focus, edge stretch) · `normal` (35mm) · `portrait`
(85mm, shallow depth, flattering) · `macro` (100mm, extreme shallow).

## Platform specs

### TikTok / Reels / Shorts / Douyin / Kuaishou / WeChat Channels

- 9:16
- Head inside the top 70%. Platform UI covers the lower third.
- Character centred horizontally, sized to occupy 40-60% of frame height.
- Fastest cuts in short-form: 1-3s. Reaction cut-ins at 0.5-1s.
- Motion should be small. Large character motion reads as noise on a phone.
- Hook the first 0.5s. The character's signature feature should be visible in
  frame one.

### YouTube / Bilibili

- 16:9
- Character off-centre with negative space on the opposite side for text.
- Longer beats allowed (4-8s). Character can hold a pose and talk.
- Thumbnails need the banner composition: character in one third.

### E-commerce / live commerce

- 1:1 for listings, 9:16 for live
- Needs the `holding-product` pose (plain unbranded box) and `phone-hold`
- Avatar icon must survive heavy downscaling — build `avatar` early
- Expression sheet matters more here than anywhere: it is the reaction face
  for a sales pitch

### Feed cards / profile images

- 1:1
- Avatar prompt must delete detail, not shrink it

## Building a clean loop

Four conditions, all non-negotiable.

1. **Static camera.** Any movement makes the seam visible.
2. **Plain background.** Background parallax reveals the join.
3. **Subject fully in frame with even margin.** A limb cropped at the edge will
   snap at the loop point.
4. **First and last pose match.** If the engine needs both frames, generate
   them from an identical prompt and vary only the pose.

```bash
python scripts/build_prompt.py video --type image-to-video \
  --motion "a friendly wave with two wrist sways, the arm returning exactly to the start position" \
  --style friendly-brand-mascot --medium flat-color-digital
```

Frame counts that loop cleanly: 2 (blink) · 8 (bob) · 12-16 (walk, wave) ·
24 (breathe) · 48+ (slow shimmer).

Duration targets: 2s for reactions, 3-4s for idle presence, 6s+ only for
slow tactile styles.

## Video negative prompts

The assembler adds these automatically for every video prompt:

```
flickering texture, texture crawling, morphing face, facial feature drift,
flipping geometry, warping background, jitter, temporal flicker,
inconsistent lighting between frames, colour shift between frames,
limb count change, character identity drift
```

Add more via `--negative`, repeatable. Useful additions:

- `--negative "walking"` when you need the character to stay planted
- `--negative "hair movement"` for bald or fixed-hair characters
- `--negative "camera shake"` to force a locked frame
- `--negative "text, watermark"`

## Failure patterns

| symptom | cause | fix |
|---------|-------|-----|
| face morphs mid-clip | image-to-video without a reference | add character reference, shorten clip |
| texture crawls | too much fine surface detail | simplify material description |
| limbs appear or vanish | anatomy not described | name proportions, add `no morphing` |
| colours shift between frames | lighting not consistent | pin lighting, use flat-color-digital medium |
| background warps | camera moved or parallax | static camera, plain background |
| loop seam visible | asymmetric motion | state the return-to-start explicitly |
| character too small on screen | framing not specified | `medium close-up`, 9:16, head in top 70% |
| motion reads as noise | multiple actions in one clip | one action, explicit timing |

## What actually drives retention

Not production value. The character's personality does.

- One clear personality trait (curious, deadpan, chaotic, gentle)
- One flaw (forgets things, bad at mornings, tries too hard)
- A default reaction (raises an eyebrow at everything)
- A signature gesture (the wave, the antenna bob, the leaf sway)

These live in the `role`, `expression` and `signature_feature` slots. Put
them in the identity block and the character performs without re-prompting.