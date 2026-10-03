#!/usr/bin/env python3
"""
Generate the full style showcase: one worked example per style in the library.

Every prompt below is produced by build_prompt.py, so the showcase cannot drift
from the data. Each style gets a subject, signature feature and medium chosen to
showcase what that style is actually good at.

Usage:
  python scripts/make_showcase.py                       # write showcase/ALL-STYLES.md
  python scripts/make_showcase.py --out docs/showcase.md
  python scripts/make_showcase.py --id soft-3d-render   # one style, to stdout
"""

from __future__ import annotations

import argparse
import io
import contextlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import build_prompt as bp  # noqa: E402


# One curated example per style: a subject that suits what the style is good at,
# plus the medium it reads best in. This is showcase content, not API surface,
# which is why it lives here rather than in data/.
SHOWCASE = {
    "blob-mascot": dict(
        medium="flat-color-digital", ratio="1:1",
        subject="a plump teardrop-shaped cloud with a cheerful face",
        signature="one tiny red mitten on its right side",
        silhouette="a soft round teardrop silhouette",
        palette="cream white body, coral accent, charcoal outline",
        material="smooth flat colour with a glossy top highlight",
        proportion="1-1", expression="happy",
        pose="centred icon composition, floating upright",
    ),
    "chibi-q-chibi": dict(
        medium="cel-shading", ratio="9:16",
        subject="a small brave fox courier with a huge round head",
        signature="one oversized yellow rain boot on the left foot",
        silhouette="a wide low triangle silhouette",
        palette="burnt orange fur, cream chest, teal scarf, charcoal outline",
        material="clean cartoon shading with soft fur shapes",
        proportion="1-2", expression="excited",
        pose="standing front-facing full body with both arms raised in triumph",
    ),
    "anthropomorphic-animal-mascot": dict(
        medium="cel-shading", ratio="1:1",
        subject="a sturdy badger standing upright on two legs",
        signature="a broad white stripe down the centre of the face",
        silhouette="a wide wedge silhouette with squared shoulders",
        palette="charcoal and white fur, rust scarf, charcoal outline",
        material="directional fur strokes over flat colour",
        proportion="1-3", expression="happy",
        pose="three-quarter turn with one hand raised in a wave",
    ),
    "retro-sports-mascot": dict(
        medium="cel-shading", ratio="9:16",
        subject="a chunky bull mascot with heavy shoulders and thick hooves",
        signature="a crimson scarf trailing behind it",
        silhouette="a heavy forward-leaning wedge silhouette",
        palette="crimson primary, cream secondary, deep navy accent, black outline",
        material="hard cel shading with thick black outline",
        proportion="1-2.5", expression="excited",
        pose="wide confident stance with both gloved fists raised",
    ),
    "friendly-brand-mascot": dict(
        medium="flat-color-digital", ratio="1:1",
        subject="a round smiling water-drop helper with tiny arms",
        signature="one small yellow star badge on its chest",
        silhouette="a simple round droplet silhouette",
        palette="soft blue body, warm cream accent, slate outline",
        material="smooth flat colour with a single soft highlight",
        proportion="1-2.5", expression="happy",
        pose="symmetrical front-facing pose with one arm raised in greeting",
    ),
    "soft-3d-render": dict(
        medium="soft-3d-render", ratio="1:1",
        subject="a small pear-shaped robot with a friendly face",
        signature="one antenna with a red bead on the tip",
        silhouette="a round teardrop silhouette",
        palette="off-white body, coral accent, deep charcoal outline",
        material="matte painted plastic with a slightly rough surface",
        proportion="1-2.5", expression="neutral",
        pose="centred full-body shot, standing upright with arms relaxed",
    ),
    "designer-vinyl-figure": dict(
        medium="photoreal", ratio="1:1",
        subject="a stout astronaut figure with a domed glass helmet",
        signature="one gold chevron painted on the left shoulder plate",
        silhouette="a wide barrel silhouette with a round top",
        palette="white suit, gold accents, one deep red stripe",
        material="glossy injection-moulded vinyl with a visible parting seam",
        proportion="1-3", expression="neutral",
        pose="standing on a round display base, facing forward",
    ),
    "clay-plasticine": dict(
        medium="gouache", ratio="1:1",
        subject="a lumpy hand-built cat with uneven ears",
        signature="one thumbprint pressed into its forehead",
        silhouette="a soft lopsided oval silhouette",
        palette="warm ochre, cream, single muted teal accent",
        material="matte plasticine with visible thumbprints and tool marks",
        proportion="1-3", expression="happy",
        pose="sitting with front paws together, centred",
    ),
    "paper-craft": dict(
        medium="gouache", ratio="1:1",
        subject="a folded paper bird with layered wing panels",
        signature="a single visible fold crease running down the body",
        silhouette="a wide arrow silhouette with swept wings",
        palette="warm yellow cardstock, one red wing panel, soft grey shadow",
        material="matte uncoated cardstock with visible fold creases and cut edges",
        proportion="1-3", expression="neutral",
        pose="in flight with wings spread, three-quarter view",
    ),
    "resin-art-figure": dict(
        medium="photoreal", ratio="2:3",
        subject="a slender dancer figure frozen mid-pose",
        signature="a swirl of gold leaf suspended inside the torso",
        silhouette="a tall S-curve silhouette with one raised arm",
        palette="translucent pale blue, gold inclusion, deep navy backdrop",
        material="semi-transparent cast resin with suspended glitter and bubbles",
        proportion="1-3", expression="neutral",
        pose="one leg extended, one arm arched overhead, on a small base",
    ),
    "flat-vector": dict(
        medium="flat-color-digital", ratio="1:1",
        subject="a geometric fox built entirely from triangles and circles",
        signature="one oversized coral ear",
        silhouette="a sharp angular fox silhouette",
        palette="deep teal body, cream belly, coral ear accent, charcoal outline",
        material="pure flat colour fills with no gradients",
        proportion="1-3", expression="neutral",
        pose="standing in profile facing right, tail extended",
    ),
    "die-cut-sticker": dict(
        medium="flat-color-digital", ratio="1:1",
        subject="a grinning avocado half with the pit as a belly button",
        signature="one tiny winking eye on the left side",
        silhouette="a rounded pear silhouette",
        palette="deep green skin, yellow-green flesh, cream pit, dark outline",
        material="glossy laminated print with a specular band",
        proportion="1-2", expression="excited",
        pose="three-quarter turn with both stub arms raised",
    ),
    "line-art-minimal": dict(
        medium="ink-line", ratio="1:1",
        subject="a single-line drawing of a whale",
        signature="one continuous unbroken line forming the whole body",
        silhouette="a long smooth teardrop silhouette",
        palette="black ink on a plain warm white ground",
        material="unfilled line only, no shading",
        proportion="1-3", expression="neutral",
        pose="facing right, tail raised, centred with generous margin",
    ),
    "memphis-pop": dict(
        medium="flat-color-digital", ratio="1:1",
        subject="a cheerful round cactus with two stubby arms",
        signature="one bright pink flower on top",
        silhouette="a squat rounded rectangle silhouette",
        palette="high-chroma green, hot pink accent, black outline, confetti",
        material="flat high-chroma colour with black squiggle decorations",
        proportion="1-2.5", expression="excited",
        pose="tilted dynamic stance with squiggles and dots around it",
    ),
    "geometric-shape-character": dict(
        medium="flat-color-digital", ratio="1:1",
        subject="a character built from a circular head, capsule limbs and a rounded rectangular body",
        signature="one small triangular antenna on the head",
        silhouette="a clean symmetrical capsule silhouette",
        palette="charcoal body, single teal accent, white highlights",
        material="perfectly consistent flat geometry with uniform stroke weight",
        proportion="1-2.5", expression="neutral",
        pose="centred symmetrical front-facing standing pose",
    ),
    "pixel-8bit": dict(
        medium="flat-color-digital", ratio="1:1",
        subject="a squat slime creature wearing a tiny helmet",
        signature="a single magenta diamond floating above it",
        silhouette="a blocky soft dome silhouette",
        palette="four colours only: cyan, magenta, dark navy, white",
        material="strict pixel grid with no anti-aliasing and ordered dithering",
        proportion="1-1.5", expression="happy",
        pose="front-facing sprite pose, centred, transparent background",
    ),
    "pixel-16bit-rpg": dict(
        medium="flat-color-digital", ratio="1:1",
        subject="a cloaked mage holding a crooked staff",
        signature="one glowing rune set into the top of the staff",
        silhouette="a tall robed silhouette with a raised staff",
        palette="deep purple robe, gold trim, cyan rune glow, black outline",
        material="multi-step pixel shading ramp with dithered gradients",
        proportion="1-3.5", expression="neutral",
        pose="three-quarter view, staff raised, transparent background",
    ),
    "low-poly-3d": dict(
        medium="flat-color-digital", ratio="1:1",
        subject="a faceted fox with clearly visible triangular planes",
        signature="one flat orange plane across one ear",
        silhouette="a wide triangular fox silhouette",
        palette="muted forest green, one amber accent, deep slate outline",
        material="flat-shaded triangular facets with hard edges and no texture",
        proportion="1-3", expression="neutral",
        pose="isometric three-quarter view, sitting upright",
    ),
    "voxel-art": dict(
        medium="flat-color-digital", ratio="1:1",
        subject="a blocky red lobster with two oversized claws",
        signature="one white cube on top of the head like a hat",
        silhouette="a wide low blocky silhouette with raised claws",
        palette="bright red, dark maroon shadow, sand, white",
        material="cubic voxels on a strict grid with nearest-neighbour sampling",
        proportion="1-3", expression="excited",
        pose="isometric three-quarter view, both claws raised",
    ),
    "felt-wool-plush": dict(
        medium="pastel-soft", ratio="1:1",
        subject="a small round grey cat with big amber eyes",
        signature="one tiny red knitted scarf",
        silhouette="a low round dome silhouette",
        palette="warm grey body, amber eyes, one red accent, charcoal outline",
        material="wool felt with visible individual fibres and embroidered features",
        proportion="1-2.5", expression="happy",
        pose="sitting upright, front paws together, centred",
    ),
    "stuffed-fabric-doll": dict(
        medium="pastel-soft", ratio="1:1",
        subject="a floppy-eared rabbit made of soft cotton",
        signature="a visible centre seam running down its front",
        silhouette="a rounded pear silhouette with long drooping ears",
        palette="warm cream body, one dusty pink bow, soft grey shadow",
        material="matte woven cotton with a centre seam and cotton-stuffing puffiness",
        proportion="1-3", expression="happy",
        pose="sitting slightly slumped, ears drooping forward",
    ),
    "crochet-amigurumi": dict(
        medium="pastel-soft", ratio="1:1",
        subject="a tiny crocheted whale with an oversized round head",
        signature="one loose yarn strand trailing from its tail",
        silhouette="a soft round ball silhouette with a small tail",
        palette="dusty blue yarn, cream belly, one pale yellow accent",
        material="yarn with visible crochet stitch loops and fibre twist detail",
        proportion="1-2", expression="happy",
        pose="floating upright, small nub arms spread wide",
    ),
    "button-felt-doll": dict(
        medium="pastel-soft", ratio="1:1",
        subject="a patchwork owl assembled from mismatched textile panels",
        signature="four mismatched buttons in a diamond on its chest",
        silhouette="a wide rounded owl silhouette with two ear tufts",
        palette="earthy ochre, muted rust, faded teal, natural linen",
        material="patchwork fabric panels with visible hand stitching and button joints",
        proportion="1-3", expression="thinking",
        pose="perched upright, head tilted to one side",
    ),
    "anime-cel-shaded": dict(
        medium="cel-shading", ratio="9:16",
        subject="a cheerful young swordswoman with a long braid",
        signature="one red hair ribbon trailing from her braid",
        silhouette="a tall upright silhouette with a diagonal sword line",
        palette="midnight blue coat, silver hair, red ribbon, hard black linework",
        material="clean anime linework with two-tone hard cel shading",
        proportion="1-6", expression="excited",
        pose="three-quarter view, sword held low, full body visible",
    ),
    "chibi-anime-cute": dict(
        medium="cel-shading", ratio="1:1",
        subject="a tiny star-witch with an oversized floppy hat",
        signature="one glowing star pinned to the hat brim",
        silhouette="a round triangular silhouette dominated by the hat",
        palette="lavender, cream, pastel gold, sparkle white",
        material="clean light linework with soft pastel gradient shading",
        proportion="1-3", expression="excited",
        pose="arms raised with both feet together, sparkles around",
    ),
    "manga-line-art": dict(
        medium="ink-line", ratio="4:5",
        subject="a detective in a long trench coat seen from a low angle",
        signature="one hat brim casting a hard black shadow across the eyes",
        silhouette="a tall narrow silhouette with strong diagonal coat lines",
        palette="black ink on white paper, screentone dots for tone",
        material="confident tapered brush linework with cross-hatching",
        proportion="1-7", expression="neutral",
        pose="low-angle dramatic pose with a deep shadow over the eyes",
    ),
    "watercolor-storybook": dict(
        medium="watercolor", ratio="1:1",
        subject="a small hedgehog wearing a folded leaf as a hat",
        signature="one single yellow wildflower tucked behind one ear",
        silhouette="a soft spiky dome silhouette with a small pointed face",
        palette="muted sage green, warm ochre, one soft yellow, cream paper",
        material="transparent watercolour washes with wet edges and granulation",
        proportion="1-3.5", expression="happy",
        pose="standing in profile facing right, looking up",
        world="in a quiet meadow with a few loose grass strokes",
    ),
    "oil-impasto": dict(
        medium="oil-impasto", ratio="2:3",
        subject="a weathered old sailor with a heavy knit scarf",
        signature="one thick impasto highlight across the bridge of the nose",
        silhouette="a broad heavy silhouette with a strong diagonal scarf",
        palette="deep sea green, burnt sienna, cream, near-black darks",
        material="thick oil paint with visible palette knife ridges and canvas weave",
        proportion="1-5", expression="thinking",
        pose="seated, turned three-quarters away, chin resting on one hand",
    ),
    "anthropomorphic-food": dict(
        medium="soft-3d-render", ratio="1:1",
        subject="a single ripe peach with velvety skin",
        signature="one small red ribbon tied at the stem",
        silhouette="a round teardrop silhouette",
        palette="warm peach pink body, deep magenta shadow, sage green leaf, charcoal outline",
        material="velvety fruit skin with fine fuzz",
        proportion="1-2", expression="excited",
        pose="standing upright in a centred full-body shot with one arm raised waving",
        world="on a pale marble kitchen counter",
    ),
    "anthropomorphic-object": dict(
        medium="cel-shading", ratio="9:16",
        subject="a dented metal kettle with a whistling spout",
        signature="one long steam curl shaped like a question mark",
        silhouette="a tall rounded triangle silhouette",
        palette="brushed steel body, one red enamel accent, charcoal outline",
        material="brushed metal with fingerprints and light scratching",
        proportion="1-3", expression="thinking",
        pose="three-quarter turn with both stub arms folded across the base",
        world="on a worn wooden kitchen counter",
    ),
    "anthropomorphic-plant": dict(
        medium="cel-shading", ratio="9:16",
        subject="a small round terracotta pot with a happy face",
        signature="three lime-green leaves sprouting from the rim",
        silhouette="a wide low mushroom silhouette",
        palette="warm terracotta pot, lime green foliage, charcoal outline",
        material="matte unglazed terracotta with real soil texture",
        proportion="1-3", expression="happy",
        pose="standing centred with both small arms resting on the rim",
        world="on a sunlit windowsill with potted plants blurred behind",
    ),
    "anthropomorphic-body-part": dict(
        medium="soft-3d-render", ratio="1:1",
        subject="a single white molar tooth with a small happy face",
        signature="one tiny gold star stuck to one corner",
        silhouette="a wide rounded square silhouette with two root legs",
        palette="warm ivory, one soft gold accent, charcoal outline",
        material="glossy enamel with fine surface detail",
        proportion="1-1", expression="neutral",
        pose="standing upright on two tiny root legs with small stub arms",
    ),
    "whimsical-creature": dict(
        medium="cel-shading", ratio="1:1",
        subject="a small six-legged forest creature with a leaf-shaped head",
        signature="three glowing dots along its back that change colour with mood",
        silhouette="a low wide dome silhouette",
        palette="moss green body, amber glow, deep charcoal outline",
        material="soft mossy skin with fine leaf texture",
        proportion="1-3", expression="surprised",
        pose="crouched low, head raised, looking directly at the viewer",
        world="on dark soil with blurred ferns behind",
    ),
    "photoreal-virtual-human": dict(
        medium="photoreal", ratio="9:16",
        subject="a friendly presenter in her thirties with shoulder-length dark hair",
        signature="one small gold star earring on the left ear",
        silhouette="a natural upright human silhouette",
        palette="navy blazer, warm skin tones, single gold accent",
        material="realistic skin with natural pore texture, real fabric with fine weave",
        proportion="1-7", expression="happy",
        pose="medium close-up, facing the viewer, hands relaxed",
        world="in a bright soft-lit studio with a neutral background",
    ),
    "semi-real-human-illustration": dict(
        medium="flat-color-digital", ratio="9:16",
        subject="a friendly host with short dark curls and a warm smile",
        signature="one thin red headband",
        silhouette="a natural human silhouette with graphic hair shape",
        palette="deep teal top, warm skin tones, one coral accent",
        material="painterly rendering with economical brushstrokes and simplified skin",
        proportion="1-7", expression="happy",
        pose="medium shot, three-quarter turn toward the viewer, one hand raised",
    ),
    "styled-avatar-nonhuman": dict(
        medium="cel-shading", ratio="9:16",
        subject="a virtual host with human features and tall wolf ears",
        signature="one silver ear cuff on the left wolf ear",
        silhouette="a human silhouette topped with two tall pointed ears",
        palette="charcoal hair, amber eyes, deep teal jacket, silver accent",
        material="semi-real skin shading blended with clean anime cel shading",
        proportion="1-7", expression="happy",
        pose="upper-body shot facing the viewer, slight forward lean",
    ),
}


# The loop motion that best shows each style, using loop_motions ids from
# deliverables.json. Mirrors the per-style loop advice in styles.json.
SHOWCASE_LOOPS = {
    "blob-mascot": "blink",
    "chibi-q-chibi": "breathe",
    "anthropomorphic-animal-mascot": "wave",
    "retro-sports-mascot": "bounce",
    "friendly-brand-mascot": "wave",
    "soft-3d-render": "turntable",
    "designer-vinyl-figure": "turntable",
    "clay-plasticine": "breathe",
    "paper-craft": "wave",
    "resin-art-figure": "turntable",
    "flat-vector": "idle-look",
    "die-cut-sticker": "bounce",
    "line-art-minimal": "idle-look",
    "memphis-pop": "bounce",
    "geometric-shape-character": "turntable",
    "pixel-8bit": "bounce",
    "pixel-16bit-rpg": "hair-sway",
    "low-poly-3d": "turntable",
    "voxel-art": "bounce",
    "felt-wool-plush": "breathe",
    "stuffed-fabric-doll": "bounce",
    "crochet-amigurumi": "breathe",
    "button-felt-doll": "hair-sway",
    "anime-cel-shaded": "hair-sway",
    "chibi-anime-cute": "bounce",
    "manga-line-art": "idle-look",
    "watercolor-storybook": "breathe",
    "oil-impasto": "hair-sway",
    "anthropomorphic-food": "bounce",
    "anthropomorphic-object": "blink",
    "anthropomorphic-plant": "hair-sway",
    "anthropomorphic-body-part": "blink",
    "whimsical-creature": "breathe",
    "photoreal-virtual-human": "blink",
    "semi-real-human-illustration": "blink",
    "styled-avatar-nonhuman": "hair-sway",
}


def build_prompt_for(style_id: str) -> dict:
    """Assemble the identity and loop prompts for one showcase example."""
    spec = SHOWCASE[style_id]
    flags = {
        "--style": style_id,
        "--medium": spec["medium"],
        "--subject": spec["subject"],
        "--signature": spec["signature"],
        "--silhouette": spec["silhouette"],
        "--palette": spec["palette"],
        "--material": spec["material"],
        "--proportion": spec["proportion"],
        "--expression": spec["expression"],
        "--pose": spec["pose"],
        "--ratio": spec["ratio"],
    }
    if spec.get("world"):
        flags["--world"] = spec["world"]

    argv = ["build", "--show-negative", "--format", "json"]
    for k, v in flags.items():
        argv += [k, v]

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = bp.main(argv)
    if rc != 0:
        raise RuntimeError(f"{style_id}: build failed")
    built = json.loads(buf.getvalue())

    # the loop motion that suits this style, by loop_motions id
    loop_id = SHOWCASE_LOOPS.get(style_id, "breathe")
    loop = bp.find_loop(loop_id)["en"]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        bp.main(["video", "--type", "image-to-video",
                 "--style", style_id, "--medium", spec["medium"],
                 "--motion", loop, "--format", "json"])
    video = json.loads(buf.getvalue())

    style = bp.find_style(style_id)
    return {
        "id": style_id,
        "name_en": style["name_en"],
        "name_zh": style["name_zh"],
        "family": style["family"],
        "tagline_en": style["tagline_en"],
        "tagline_zh": style["tagline_zh"],
        "medium": spec["medium"],
        "medium_name": bp.find_media(spec["medium"])["name_en"],
        "ratio": spec["ratio"],
        "loop_motion": loop,
        "identity_prompt": built["prompt"],
        "negative": built["negative"],
        "loop_prompt": video["prompt"],
        "video_note": style["video"],
        "loop_note": style["loop"],
    }


def render_markdown(entries: list) -> str:
    fams = {f["id"]: f for f in bp.load_families()}
    lines = [
        "# Style Showcase",
        "",
        "One worked example per style in the library. Every prompt below was",
        "generated by `scripts/make_showcase.py`, which calls `build_prompt.py`",
        "directly, so this file cannot drift from the data.",
        "",
        "Regenerate with:",
        "",
        "```bash",
        "python scripts/make_showcase.py",
        "```",
        "",
        f"{len(entries)} styles across {len(fams)} families. Each entry gives the",
        "identity prompt, the negative prompt, and a matching seamless-loop prompt.",
        "",
        "Characters are named in the copy as `the character` because a real",
        "series substitutes its own name; that keeps these examples reusable.",
        "",
        "## Contents",
        "",
    ]
    current = None
    for e in entries:
        if e["family"] != current:
            current = e["family"]
            fam = fams[current]
            lines += [f"### {fam['name_en']} / {fam['name_zh']}", ""]
        lines.append(f"- [`{e['id']}`](#{e['id']}) — {e['name_en']} · {e['name_zh']}")
    lines.append("")

    current = None
    for e in entries:
        if e["family"] != current:
            current = e["family"]
            fam = fams[current]
            lines += [
                "",
                f"## {fam['name_en']} / {fam['name_zh']}",
                "",
                fam["blurb"],
                "",
            ]
        lines += [
            f"### {e['id']}",
            "",
            f"**{e['name_en']} / {e['name_zh']}** · family `{e['family']}` · "
            f"medium `{e['medium']}` ({e['medium_name']}) · ratio `{e['ratio']}`",
            "",
            f"> {e['tagline_en']}",
            ">",
            f"> {e['tagline_zh']}",
            "",
            "**Identity prompt**",
            "",
            "```",
            e["identity_prompt"],
            "```",
            "",
            "**Negative**",
            "",
            "```",
            e["negative"],
            "```",
            "",
            f"**Loop prompt** — {e['loop_motion']}",
            "",
            "```",
            e["loop_prompt"],
            "```",
            "",
            f"*Video note:* {e['video_note']}",
            "",
            f"*Loop note:* {e['loop_note']}",
            "",
        ]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", help="write markdown here (default showcase/ALL-STYLES.md)")
    ap.add_argument("--json", help="also write JSON here")
    ap.add_argument("--id", help="render a single style to stdout")
    args = ap.parse_args(argv)

    if args.id:
        print(json.dumps(build_prompt_for(args.id), ensure_ascii=False, indent=2))
        return 0

    entries = [build_prompt_for(s["id"]) for s in bp.load_styles()]
    missing = {s["id"] for s in bp.load_styles()} - set(SHOWCASE)
    if missing:
        print(f"missing showcase entries: {sorted(missing)}", file=sys.stderr)
        return 1

    md = render_markdown(entries)
    out = args.out or os.path.join(ROOT, "showcase", "ALL-STYLES.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"wrote {out} ({len(entries)} styles)")

    if args.json:
        payload = {"generated_by": "scripts/make_showcase.py", "styles": entries}
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())