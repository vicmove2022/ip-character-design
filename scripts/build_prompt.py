#!/usr/bin/env python3
"""
ip-character-design :: prompt assembler (Python, standard library only).

Assembles platform-agnostic IP character prompts from the shared JSON data in
../data. Works from any working directory.

Commands
--------
  styles                    list all styles, optionally filtered by family
  families                  list families
  media                     list rendering media
  show <style-id>           full detail for one style or medium
  build                     assemble one prompt from flags
  kit                       assemble a full deliverable kit (all prompt types)
  consistency               print the lock block for a character sheet
  video                     assemble an image-to-video / text-to-video prompt
  check                     validate the data files and the banned-word policy

Examples
--------
  python build_prompt.py styles --family anthropomorphic
  python build_prompt.py show soft-3d-render
  python build_prompt.py build --style blob-mascot --subject "a bean-shaped cloud" \
      --signature "one red mitten" --palette "cream body, coral accent, charcoal outline" \
      --expression excited --ratio 9:16
  python build_prompt.py kit --style anthropomorphic-food --subject "a peach" \
      --signature "a single red ribbon on top" --palette "peach skin, cream, coral leaf" \
      --out kit.json
  python build_prompt.py video --style plush-felt --subject "a round grey cat" \
      --motion "a gentle breathing bob" --type image-to-video
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))


# --------------------------------------------------------------------------
# data loading
# --------------------------------------------------------------------------

def _load(name: str) -> dict[str, Any]:
    path = os.path.join(DATA, name)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_styles() -> list[dict[str, Any]]:
    return _load("styles.json")["styles"]


def load_families() -> list[dict[str, Any]]:
    return _load("styles.json")["families"]


def load_media() -> list[dict[str, Any]]:
    return _load("media.json")["media"]


def load_anatomy() -> dict[str, Any]:
    return _load("anatomy.json")


def load_negatives() -> dict[str, Any]:
    return _load("negatives.json")


def load_deliverables() -> dict[str, Any]:
    return _load("deliverables.json")


def load_brand() -> dict[str, Any]:
    return _load("brand-safe-words.json")


_SPELLING = (
    ("colour", "color"),
    ("colours", "colors"),
    ("gray", "grey"),
    ("behaviour", "behavior"),
    ("stylised", "stylized"),
    ("realism", "realism"),
)


def _norm(text: str) -> str:
    """Loose key for id matching: lowercase, drop separators, fold spellings."""
    t = text.lower().replace("-", "").replace("_", "").replace(" ", "")
    for a, b in _SPELLING:
        t = t.replace(a, b)
    return t


def _norm_tokens(text: str) -> list[str]:
    """Words of a key, spellings folded, separators and spaces split out."""
    t = text.lower().replace("-", " ").replace("_", " ")
    for a, b in _SPELLING:
        t = t.replace(a, b)
    return [w for w in t.split() if w]


_ALIASES: dict[str, str] = {
    # British / American spellings and common synonyms
    "watercolor": "watercolor",
    "watercolour": "watercolor",
    "waterscolour": "watercolor",
    "sketch": "pencil-sketch",
    "pencil": "pencil-sketch",
    "graphite": "pencil-sketch",
    "charcoal": "pencil-sketch",
    "marker": "hand-drawn-marker",
    "handdrawn": "hand-drawn-marker",
    "ink": "ink-line",
    "lineart": "ink-line",
    "3drender": "soft-3d-render",
    "3d": "soft-3d-render",
    "clay": "clay-plasticine",
    "plasticine": "clay-plasticine",
    "claymation": "clay-plasticine",
    "toy": "designer-vinyl-figure",
    "vinyl": "designer-vinyl-figure",
    "figma": "designer-vinyl-figure",
    "plush": "felt-wool-plush",
    "felt": "felt-wool-plush",
    "wool": "felt-wool-plush",
    "crochet": "crochet-amigurumi",
    "amigurumi": "crochet-amigurumi",
    "yarn": "crochet-amigurumi",
    "flat": "flat-vector",
    "vector": "flat-vector",
    "flatvector": "flat-vector",
    "sticker": "die-cut-sticker",
    "diecut": "die-cut-sticker",
    "memphis": "memphis-pop",
    "pop": "memphis-pop",
    "lineartminimal": "line-art-minimal",
    "pixel": "pixel-8bit",
    "pixelart": "pixel-8bit",
    "8bit": "pixel-8bit",
    "16bit": "pixel-16bit-rpg",
    "sprite": "pixel-16bit-rpg",
    "lowpoly": "low-poly-3d",
    "voxel": "voxel-art",
    "anime": "anime-cel-shaded",
    "cel": "anime-cel-shaded",
    "celshaded": "anime-cel-shaded",
    "cute": "chibi-anime-cute",
    "chibi": "chibi-q-chibi",
    "qversion": "chibi-q-chibi",
    "manga": "manga-line-art",
    "storybook": "watercolor-storybook",
    "impasto": "oil-impasto",
    "oil": "oil-impasto",
    "oilpaint": "oil-impasto",
    "food": "anthropomorphic-food",
    "object": "anthropomorphic-object",
    "plant": "anthropomorphic-plant",
    "creature": "whimsical-creature",
    "monster": "whimsical-creature",
    "human": "photoreal-virtual-human",
    "vtuber": "styled-avatar-nonhuman",
    "avatar": "styled-avatar-nonhuman",
    "semireal": "semi-real-human-illustration",
    "soft": "soft-3d-render",
    "photo": "photoreal",
    "photorealistic": "photoreal",
    "real": "photoreal",
    "pastel": "pastel-soft",
    "chalk": "pastel-soft",
    "gouache": "gouache",
    "vector": "flat-color-digital",
    "digital": "flat-color-digital",
    "celshading": "cel-shading",
    "blob": "blob-mascot",
    "bean": "blob-mascot",
    "beanclear": "blob-mascot",
    "simple": "blob-mascot",
    "brandmascot": "friendly-brand-mascot",
    "corporate": "friendly-brand-mascot",
    "sports": "retro-sports-mascot",
    "team": "retro-sports-mascot",
    "animalmascot": "anthropomorphic-animal-mascot",
    "papercraft": "paper-craft",
    "resin": "resin-art-figure",
    "minimal": "line-art-minimal",
    "geometric": "geometric-shape-character",
    "shapes": "geometric-shape-character",
    "shape": "geometric-shape-character",
    "doll": "stuffed-fabric-doll",
    "stuffed": "stuffed-fabric-doll",
    "patchwork": "button-felt-doll",
    "folkart": "button-felt-doll",
    "folk": "button-felt-doll",
    "kawaii": "chibi-anime-cute",
    "bodypart": "anthropomorphic-body-part",
    "body": "anthropomorphic-body-part",
    "hand": "anthropomorphic-body-part",
    "watercolourwash": "watercolor",
    "wash": "watercolor",
    "graphite": "pencil-sketch",
}


def _lookup(items: list[dict[str, Any]], key: str) -> dict[str, Any] | None:
    if not key:
        return None
    for item in items:
        if item["id"] == key:
            return item
    nk = _norm(key)
    for item in items:
        if _norm(item["id"]) == nk:
            return item
    target = _ALIASES.get(nk)
    if target:
        for item in items:
            if item["id"] == target:
                return item
    # last resort: the key is a subset of an id's words, e.g. "animal mascot" ->
    # "anthropomorphic-animal-mascot", "doll" -> "stuffed-fabric-doll".
    # Token split keeps word boundaries so multi-word keys still match.
    # Numeric-only keys are never fuzzy-matched: "1-1.5" must not land on "1-2".
    parts = set(_norm_tokens(key))
    if not any(p for p in parts if any(c.isalpha() for c in p)):
        return None
    best: dict[str, Any] | None = None
    best_score = 0
    for item in items:
        toks = set(_norm_tokens(item["id"]))
        overlap = parts & toks
        if not overlap:
            continue
        score = sum(len(p) for p in overlap)
        if score > best_score:
            best, best_score = item, score
    return best


def find_style(style_id: str) -> dict[str, Any] | None:
    return _lookup(load_styles(), style_id)


def find_media(media_id: str) -> dict[str, Any] | None:
    return _lookup(load_media(), media_id)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _clean(text: str | None) -> str:
    if not text:
        return ""
    return text.strip().rstrip(",.")


def _segments(text: str) -> list[str]:
    """Split an assembled clause list on commas, respecting brackets."""
    parts, depth, buf = [], 0, ""
    for ch in text:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            parts.append(buf)
            buf = ""
        else:
            buf += ch
    parts.append(buf)
    return [p.strip() for p in parts if p.strip()]


_COUNT_WORDS = {
    1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",
    7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve",
}


def _retune_grid(text: str, n: int, old_shape: str) -> str:
    """Rewrite the panel count and grid shape to match n panels."""
    out = text.replace(old_shape, _grid_shape(n))
    for word in ("Six", "Twelve", "Eight", "Ten", "Nine", "Seven", "Five",
                 "Four", "Three", "Two", "One"):
        if word in out.split(".")[0]:
            out = out.replace(word, _COUNT_WORDS.get(n, str(n)), 1)
            break
    return out


def _grid_shape(n: int) -> str:
    """Grid descriptor for a sheet of n panels. Prefers 3 columns."""
    if n <= 1:
        return "1x1"
    if n == 2:
        return "2x1"
    cols = 3 if n >= 3 else 2
    rows = -(-n // cols)
    return f"{cols}x{rows}"


def _join(parts: list[str]) -> str:
    """Join, dropping segments already present (case-insensitive)."""
    seen: set[str] = set()
    out: list[str] = []
    for p in (_clean(x) for x in parts):
        if not p:
            continue
        for seg in _segments(p):
            key = seg.lower().rstrip(" .")
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(seg)
    return ", ".join(out)


def _sentence(parts: list[str]) -> str:
    out = _join(parts)
    if not out:
        return ""
    return out[0].upper() + out[1:] + "."


def find_expression(expression_id: str) -> dict[str, Any] | None:
    return _lookup(load_deliverables()["expression_defaults"], expression_id)


def find_loop(loop_id: str) -> dict[str, Any] | None:
    return _lookup(load_deliverables()["loop_motions"], loop_id)


def find_camera(camera_id: str) -> dict[str, Any] | None:
    return _lookup(load_deliverables()["camera_moves"], camera_id)


def find_lens(lens_id: str) -> dict[str, Any] | None:
    return _lookup(load_deliverables()["lens_notes"], lens_id)


def find_ratio(ratio_id: str) -> dict[str, Any] | None:
    return _lookup(load_deliverables()["aspect_ratios"], ratio_id)


def find_proportion(prop_id: str) -> dict[str, Any] | None:
    return _lookup(load_anatomy()["proportion_presets"], prop_id)


def resolve_ratio(ratio: str | None) -> str:
    if not ratio:
        return "1:1"
    r = find_ratio(ratio)
    return r["token"] if r else ratio


def collect_negatives(
    style: dict[str, Any] | None,
    media: dict[str, Any] | None,
    video: bool,
    extra: list[str] | None = None,
    minimal: bool = False,
) -> list[str]:
    negs = load_negatives()
    seen: list[str] = []

    def add(items: Any) -> None:
        if not items:
            return
        for it in items:
            if it not in seen:
                seen.append(it)

    if not minimal:
        add(negs["global"])
        if style:
            add(style.get("negative_add"))
            add(negs["by_family"].get(style.get("family")))
    if media:
        add(media.get("negative_add"))
        add(negs["by_medium"].get(media.get("id")))
    if video:
        add(negs["video_negatives"])
    add(extra)
    return seen


def quality_tail(kind: str | None) -> str:
    tails = load_negatives()["quality_tails"]
    return ", ".join(tails.get(kind or "default", tails["default"]))


def _style_and_media(
    style_id: str | None, medium_id: str | None
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    style = find_style(style_id) if style_id else None
    media = find_media(medium_id) if medium_id else None
    return style, media


def _locked_block(
    args: argparse.Namespace, media: dict[str, Any] | None = None
) -> dict[str, str]:
    """The identity block that must stay byte-identical across a series."""
    expr = find_expression(getattr(args, "expression", None) or "")
    loop = find_loop(getattr(args, "loop", None) or "")
    prop = find_proportion(getattr(args, "proportion", None) or "")
    lighting = getattr(args, "lighting", "") or ""
    if not lighting and media:
        lighting = media.get("default_lighting", "")
    block = {
        "subject": getattr(args, "subject", "") or "",
        "role": getattr(args, "role", "") or "",
        "signature_feature": getattr(args, "signature", "") or "",
        "proportion": (
            getattr(args, "proportion_phrase", "")
            or (prop["en"] if prop else "")
            or (getattr(args, "proportion", "") or "")
        ),
        "silhouette": getattr(args, "silhouette", "") or "",
        "palette": getattr(args, "palette", "") or "",
        "material": getattr(args, "material", "") or "",
        "outfit": getattr(args, "outfit", "") or "",
        "expression": expr["en"] if expr else (getattr(args, "expression_phrase", "") or ""),
        "pose": getattr(args, "pose", "") or "",
        "world": getattr(args, "world", "") or "",
        "signature_mark": getattr(args, "mark", "") or "",
        "medium": getattr(args, "medium_phrase", "") or "",
        "lighting": lighting,
        "composition": resolve_ratio(getattr(args, "ratio", None)),
        "quality": getattr(args, "quality_phrase", "") or (
            quality_tail(getattr(args, "quality", None)) if getattr(args, "quality", None) else ""
        ),
        "loop_motion": loop["en"] if loop else "",
    }
    return {k: _clean(v) for k, v in block.items()}


# A template preposition stranded by an empty slot reads as a typo:
#   "{subject} with {signature_feature}, {palette}"  ->  "a pear with, yellow"
# Only collapse when the word has nothing but punctuation after it, so real
# clauses like ", the character identity" are never damaged.
_DANGLING = (
    "with", "in", "on", "at", "of", "and", "or", "but", "from", "to",
    "the", "a", "an", "is", "are", "as", "by", "under", "over", "near",
    "beside", "inside", "onto", "into", "that", "which",
)
_DANGLING_COMMA_RE = re.compile(
    r"\s+(?:" + "|".join(_DANGLING) + r")\s*(?=,)"
)
_DANGLING_END_RE = re.compile(
    r",\s*(?:" + "|".join(_DANGLING) + r")\s*(?=[.;])"
)


def fill(template: str, values: dict[str, str]) -> str:
    """Replace {slot} tokens, dropping slots that were left empty."""
    out = template
    for key, val in values.items():
        out = out.replace("{" + key + "}", _clean(val))
    out = re.sub(r"\{\s*[a-z_]+\s*\}", "", out)
    out = out.replace(", .", ".").replace("  ", " ").replace(" ,", ",")
    while ", ," in out:
        out = out.replace(", ,", ",")
    # a template preposition left dangling by an empty slot reads as a typo
    while True:
        stripped = _DANGLING_COMMA_RE.sub("", out)
        stripped = _DANGLING_END_RE.sub("", stripped)
        if stripped == out:
            break
        out = stripped
    out = re.sub(r"(,\s*){2,}", ", ", out)
    out = re.sub(r"\s+,", ",", out)
    return _sentence(out.split(". "))


_LIGHT_WORDS = (" light", " lighting", "backlit", "backlight",
                "rim light", "key light", "lit ")


def strip_light_segments(clause: str) -> str:
    """Drop lighting segments from a style core when lighting is chosen explicitly.

    Style cores carry a default lighting hint. When a medium or an explicit
    --lighting is set, that hint usually contradicts it, so remove it.
    """
    keep = []
    for seg in _segments(clause):
        low = " " + seg.lower()
        if any(w in low for w in _LIGHT_WORDS):
            continue
        keep.append(seg)
    return ", ".join(keep)


def style_clause(
    style: dict[str, Any] | None,
    media: dict[str, Any] | None,
    strip_lighting: bool = False,
) -> str:
    parts = []
    if style:
        # a style whose id matches the medium would emit the same core twice
        if not (media and media["id"] == style["id"]):
            core = style["core_en"]
            if strip_lighting:
                core = strip_light_segments(core)
            parts.append(core)
    if media:
        parts.append(media["core_en"])
    return ", ".join(p for p in parts if p)


RENDER_SLOTS = ("medium", "lighting", "composition", "quality")
# slots that legitimately change between shots of the same character
VARIABLE_SLOTS = ("pose", "world", "role")


def lock_block(values: dict[str, str], include_render: bool = True) -> str:
    """Canonical identity sentence, reusable verbatim in every shot prompt.

    Pass include_render=False to drop the medium / lighting / composition /
    quality tail (they are appended separately when assembling).
    """
    order = load_anatomy()["prompt_slot_order"]
    if not include_render:
        order = [k for k in order if k not in RENDER_SLOTS]
    parts = [values.get(k, "") for k in order]
    parts = [p for p in parts if p]
    return ", ".join(parts)


def identity_block(values: dict[str, str]) -> str:
    """Only the slots that must NEVER change across a character series."""
    order = [k for k in load_anatomy()["prompt_slot_order"]
             if k not in RENDER_SLOTS and k not in VARIABLE_SLOTS]
    parts = [values.get(k, "") for k in order]
    return ", ".join(p for p in parts if p)


def infer_quality(
    style: dict[str, Any] | None, media: dict[str, Any] | None
) -> str:
    """Pick the default quality tail that matches the style and medium.

    The style family wins over the medium: a pixel character on a flat vector
    medium is still a pixel character and needs the pixel tail.
    """
    if style and style["family"] == "pixel-lowpoly":
        return "pixel"
    if media:
        mid = media["id"]
        if mid == "photoreal" or mid == "soft-3d-render":
            return "photo"
        if mid in ("pixel-8bit", "pixel-16bit-rpg", "low-poly-3d", "voxel-art"):
            return "pixel"
        if mid in ("flat-color-digital", "line-art-minimal", "cel-shading", "flat-vector",
                   "pencil-sketch", "ink-line"):
            return "minimal"
        return "illustration"
    if style:
        if style["family"] == "realistic-avatar":
            return "photo"
        if style["family"] in ("craft-plush", "3d-toy"):
            return "photo"
        return "illustration"
    return "default"


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------

def cmd_styles(args: argparse.Namespace) -> int:
    styles = load_styles()
    fams = {f["id"]: f for f in load_families()}
    if args.family:
        styles = [s for s in styles if s["family"] == args.family]
    if args.search:
        raw = args.search.lower()
        styles = [
            s for s in styles
            if raw in json.dumps(s, ensure_ascii=False).lower()
            or find_style(raw) is s
        ]
    if args.format == "json":
        print(json.dumps(styles, ensure_ascii=False, indent=2))
        return 0
    if args.format == "ids":
        for s in styles:
            print(s["id"])
        return 0
    width = max((len(s["id"]) for s in styles), default=4)
    for s in styles:
        fam = fams.get(s["family"], {}).get("name_en", s["family"])
        print(f"{s['id']:<{width}}  {fam:<22}  {s['tagline_en']}")
        if args.verbose:
            print(f"{'':<{width}}  zh: {s['tagline_zh']}")
            for w in s.get("use_when", []):
                print(f"{'':<{width}}    - {w}")
    return 0


def cmd_families(args: argparse.Namespace) -> int:
    fams = load_families()
    styles = load_styles()
    if args.format == "json":
        print(json.dumps(fams, ensure_ascii=False, indent=2))
        return 0
    for f in fams:
        count = sum(1 for s in styles if s["family"] == f["id"])
        print(f"{f['id']:<22}  {count:>2} styles  {f['name_en']} / {f['name_zh']}")
        print(f"{'':<22}  {f['blurb']}")
    return 0


def cmd_media(args: argparse.Namespace) -> int:
    media = load_media()
    if args.format == "json":
        print(json.dumps(media, ensure_ascii=False, indent=2))
        return 0
    width = max((len(m["id"]) for m in media), default=4)
    for m in media:
        print(f"{m['id']:<22}  {m['name_en']} / {m['name_zh']}")
        if args.verbose:
            print(f"{'':<22}  pairs well: {', '.join(m['pairs_well'])}")
            print(f"{'':<22}  avoid:     {', '.join(m['pairs_badly'])}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    node = find_style(args.id) or find_media(args.id)
    if not node:
        print(f"Unknown style or media id: {args.id}", file=sys.stderr)
        return 1
    print(f"# {node['name_en']} / {node.get('name_zh', '')}")
    print(f"id:     {node['id']}")
    if "family" in node:
        print(f"family: {node['family']}")
    if "tagline_en" in node:
        print(f"\n{node['tagline_en']}\n{node['tagline_zh']}")
    if args.verbose:
        if node.get("use_when"):
            print("\nUse when:")
            for w in node["use_when"]:
                print(f"  - {w}")
        if node.get("avoid_when"):
            print(f"\nAvoid when: {node['avoid_when']}")
        for key in ("proportion", "surface", "surface_note", "lighting"):
            if node.get(key):
                print(f"\n{key}: {node[key]}")
        if node.get("kw_zh"):
            print(f"\nzh keywords: {' / '.join(node['kw_zh'])}")
        if node.get("pairs_well"):
            print(f"\npairs well: {', '.join(node['pairs_well'])}")
            print(f"avoid:      {', '.join(node['pairs_badly'])}")
        if node.get("core_en"):
            print(f"\ncore_en:\n{node['core_en']}")
        if node.get("video"):
            print(f"\nvideo: {node['video']}")
        if node.get("loop"):
            print(f"loop:  {node['loop']}")
    else:
        if node.get("core_en"):
            print(f"\ncore_en: {node['core_en']}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    style, media = _style_and_media(args.style, args.medium)
    values = _locked_block(args, media)
    if not values["quality"]:
        values["quality"] = quality_tail(infer_quality(style, media))
    core = style_clause(style, media, strip_lighting=True)
    prompt = _sentence([
        lock_block(values, include_render=False),
        core,
        values["lighting"],
        values["composition"],
        values["quality"],
    ])
    negs = collect_negatives(style, media, video=False, extra=args.negative)
    if args.format == "json":
        print(json.dumps({
            "prompt": prompt,
            "negative": ", ".join(negs),
            "style": style["id"] if style else None,
            "medium": media["id"] if media else None,
            "ratio": values["composition"],
            "lock_block": lock_block(values),
        }, ensure_ascii=False, indent=2))
        return 0
    print(prompt)
    if args.negative or args.show_negative:
        print("\nNEGATIVE:", ", ".join(negs))
    return 0


def cmd_kit(args: argparse.Namespace) -> int:
    style, media = _style_and_media(args.style, args.medium)
    values = _locked_block(args, media)
    if not values["quality"]:
        values["quality"] = quality_tail(infer_quality(style, media))
    core = style_clause(style, media, strip_lighting=True)
    lock = lock_block(values)
    ratio = values["composition"]
    deliverables = load_deliverables()
    only = set(args.only) if args.only else None

    out: dict[str, Any] = {
        "character": {
            "style": style["id"] if style else None,
            "style_name": style["name_en"] if style else None,
            "medium": media["id"] if media else None,
            "medium_name": media["name_en"] if media else None,
            "lock_block": lock,
            "ratio": ratio,
        },
        "prompts": {},
    }

    expr_entries = [
        e for e in deliverables["expression_defaults"]
        if not args.expressions or e["id"] in args.expressions
    ]
    expr_list = ", ".join(e["en"] for e in expr_entries)
    expr_grid = _retune_grid(
        deliverables.get("expression_grid_default", "{list}").format(list=expr_list),
        len(expr_entries), "3x2")

    pose_ids = args.poses or []
    poses = [p for p in deliverables.get("extra_poses", []) if p["id"] in pose_ids]
    if not poses:
        poses = [{"id": f"p{i+1}", "en": en, "zh": ""}
                 for i, en in enumerate(deliverables.get("pose_defaults", []))]
    pose_list = ", ".join(p["en"] for p in poses)
    pose_grid = _retune_grid(
        deliverables.get("pose_grid_default", "{list}").format(list=pose_list),
        len(poses), "2x3")

    for d in deliverables["deliverables"]:
        if only and d["id"] not in only:
            continue
        extra: dict[str, str] = dict(values)
        extra["style_core"] = core
        extra["medium_core"] = ""
        extra["expression_grid"] = expr_grid
        extra["pose_grid"] = pose_grid
        if d["id"] == "loop" and not extra.get("loop_motion"):
            extra["loop_motion"] = "a gentle breathing bob with a subtle chest rise and fall"
        prompt = fill(d["template"], extra)
        negs = collect_negatives(
            style, media,
            video=(d["id"] == "loop"),
            minimal=False,
        )
        out["prompts"][d["id"]] = {
            "label_en": d["label_en"],
            "label_zh": d["label_zh"],
            "purpose": d["purpose"],
            "ratio": ratio if args.ratio else d["ratio"],
            "prompt": prompt,
            "negative": ", ".join(negs),
            "notes": d["notes"],
        }

    # attach the selectable paletes so callers can reuse them as libraries
    for did, entry in out["prompts"].items():
        if did == "expression-sheet":
            entry["expression_palette"] = [
                {"id": e["id"], "en": e["en"], "zh": e["zh"]} for e in expr_entries
            ]
        elif did == "pose-sheet":
            entry["pose_palette"] = [
                {"id": p["id"], "en": p["en"], "zh": p["zh"]} for p in poses
            ]
    out["character"]["available_expressions"] = [
        {"id": e["id"], "en": e["en"], "zh": e["zh"]}
        for e in deliverables["expression_defaults"]
    ]
    out["character"]["available_poses"] = [
        {"id": p["id"], "en": p["en"], "zh": p["zh"]}
        for p in deliverables["extra_poses"]
    ]

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)
        print(f"wrote {args.out} ({len(out['prompts'])} prompts)")
        return 0

    if args.format == "json":
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    print(f"# {out['character']['style_name'] or 'custom'} / {out['character']['medium_name'] or 'no medium'}")
    print(f"ratio: {ratio}")
    print(f"\nLOCK BLOCK (reuse verbatim in every shot):\n{lock}\n")
    for pid, entry in out["prompts"].items():
        print(f"## {pid} - {entry['label_en']} / {entry['label_zh']}  [{entry['ratio']}]")
        print(f"purpose: {entry['purpose']}")
        print(entry["prompt"])
        print(f"negative: {entry['negative']}")
        print(f"note: {entry['notes']}\n")
    return 0


def cmd_consistency(args: argparse.Namespace) -> int:
    style, media = _style_and_media(args.style, args.medium)
    values = _locked_block(args, media)
    if not values["quality"]:
        values["quality"] = quality_tail(infer_quality(style, media))
    core = style_clause(style, media, strip_lighting=True)
    print("IDENTITY BLOCK - copy verbatim into every prompt in the series.")
    print("Nothing in this block may change between shots:\n")
    print(identity_block(values))
    print("\n\nRENDER BLOCK - hold constant within one series, change deliberately")
    print("between series:\n")
    print(", ".join(p for p in [core, values["lighting"], values["composition"],
                               values["quality"]] if p))
    print("\n\nLOCK CHECKLIST")
    print(" 1. Subject phrase identical, character for character.")
    print(" 2. Signature feature phrase present in every prompt.")
    print(" 3. Outline colour named explicitly (e.g. 'charcoal outline').")
    print(" 4. Head-to-body ratio stated numerically.")
    print(" 5. Medium identical. Never change medium mid-series.")
    print(" 6. Outfit identical even when the pose changes.")
    print(" 7. Lighting identical for identity shots.")
    print(" 8. Same aspect ratio for the whole series.")
    print(" 9. Regenerate anything that drifts; do not average two candidates.")
    print("10. If the engine supports it, also pass a reference image or character")
    print("    reference on every frame (character reference / style reference /")
    print("    image-to-image). Text locks alone drift; image locks are stronger.")
    return 0


def cmd_video(args: argparse.Namespace) -> int:
    style, media = _style_and_media(args.style, args.medium)
    values = _locked_block(args, media)
    if not values["quality"]:
        values["quality"] = quality_tail(infer_quality(style, media))
    tpl = load_deliverables()["video_templates"][args.type]
    core = style_clause(style, media, strip_lighting=True)
    lock = lock_block(values)
    cam = find_camera(args.camera) if args.camera else None
    lens = find_lens(args.lens) if args.lens else None

    if args.type == "camera":
        fill_map = {
            "subject": identity_block(values),
            "camera_move": cam["en"] if cam else "static locked-off camera",
            "lens_note": lens["en"] if lens else "",
        }
    elif args.type == "text-to-video":
        fill_map = {
            "subject": identity_block(values),
            "style_core": core,
            "medium_core": "",
            "motion": _clean(args.motion),
            "lighting": values["lighting"],
            "ratio": values["composition"],
        }
    else:
        fill_map = {
            "motion": _clean(args.motion) or "a gentle breathing bob with a subtle blink",
        }

    prompt = fill(tpl, fill_map)
    negs = collect_negatives(style, media, video=True, extra=args.negative)
    if args.format == "json":
        print(json.dumps({
            "type": args.type,
            "prompt": prompt,
            "negative": ", ".join(negs),
            "camera": cam["en"] if cam else None,
            "lens": lens["en"] if lens else None,
        }, ensure_ascii=False, indent=2))
        return 0
    print(prompt)
    print("\nNEGATIVE:", ", ".join(negs))
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    problems: list[str] = []
    styles = load_styles()
    media = load_media()
    families = {f["id"] for f in load_families()}
    negs = load_negatives()
    deliverables = load_deliverables()

    ids = [s["id"] for s in styles]
    if len(ids) != len(set(ids)):
        problems.append("duplicate style ids")
    for s in styles:
        for key in ("id", "name_en", "name_zh", "family", "tagline_en", "tagline_zh",
                    "proportion", "surface", "lighting", "core_en", "kw_zh", "video", "loop"):
            if not s.get(key):
                problems.append(f"style {s['id']}: missing {key}")
        if s["family"] not in families:
            problems.append(f"style {s['id']}: unknown family {s['family']}")
        if s["family"] not in negs["by_family"]:
            problems.append(f"style {s['id']}: family {s['family']} has no negative pool")

    mids = [m["id"] for m in media]
    if len(mids) != len(set(mids)):
        problems.append("duplicate media ids")
    for m in media:
        if m["id"] not in negs["by_medium"]:
            problems.append(f"media {m['id']}: no negative pool")
        for ref in m.get("pairs_badly", []) + m.get("pairs_well", []):
            if ref not in families and ref not in ids:
                problems.append(f"media {m['id']}: unknown pairing target {ref}")

    anatomy = load_anatomy()
    slot_ids = [s["id"] for s in anatomy["slots"]]
    for slot in slot_ids:
        if slot not in anatomy["prompt_slot_order"]:
            problems.append(f"slot {slot} missing from prompt_slot_order")
    for slot in anatomy["prompt_slot_order"]:
        if slot not in slot_ids:
            problems.append(f"prompt_slot_order references unknown slot {slot}")

    for d in deliverables["deliverables"]:
        if d["ratio"] not in {r["id"] for r in deliverables["aspect_ratios"]}:
            problems.append(f"deliverable {d['id']}: unknown ratio {d['ratio']}")
        for tok in ("{", "}"):
            pass
        import re as _re
        for used in _re.findall(r"\{([a-z_]+)\}", d["template"]):
            if used not in slot_ids and used not in (
            "style_core", "medium_core", "loop_motion", "composition",
            "quality", "expression_grid", "pose_grid",
        ):
                problems.append(f"deliverable {d['id']}: unknown token {{{used}}}")

    banned = [w for w in ("pixar", "disney", "ghibli", "marvel", "sanrio", "lego",
                          "pokemon", "mario", "star wars", "harry potter")
              if any(w in (s.get("core_en") or "").lower() for s in styles)]
    if banned:
        problems.append(f"banned names found in style data: {banned}")

    print(f"styles:  {len(styles)}")
    print(f"families:{len(families)}")
    print(f"media:   {len(media)}")
    print(f"slots:   {len(slot_ids)}")
    print(f"deliverables: {len(deliverables['deliverables'])}")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print("  -", p)
        return 1
    print("\nOK: all data files consistent, no banned names in style data.")
    return 0


# --------------------------------------------------------------------------
# argument parsing
# --------------------------------------------------------------------------

def add_character_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--subject", default="", help="what the character is (required for a real prompt)")
    p.add_argument("--role", default="", help="host / guide / reactor / sidekick / challenger / mascot / puppet")
    p.add_argument("--signature", default="", help="the one unforgettable feature")
    p.add_argument("--silhouette", default="", help="one-phrase silhouette read")
    p.add_argument("--palette", default="", help="2-5 named colours, include the outline colour")
    p.add_argument("--material", default="", help="what it is physically made of")
    p.add_argument("--outfit", default="", help="what it wears")
    p.add_argument("--world", default="", help="where it lives")
    p.add_argument("--mark", default="", help="signature mark, e.g. a small three-dot mark on the shoulder")
    p.add_argument("--pose", default="", help="body doing and framing")
    p.add_argument("--lighting", default=None,
                   help="one light setup; defaults to the medium's default lighting")
    p.add_argument("--proportion", default="", help="proportion preset id (1-2, 1-3, 1-7 ...) or free text")
    p.add_argument("--proportion-phrase", default="", help="explicit proportion phrase, overrides --proportion")
    p.add_argument("--expression", default="", help="expression id (happy, excited, confused ...)")
    p.add_argument("--expression-phrase", default="", help="explicit expression phrase, overrides --expression")
    p.add_argument("--ratio", default="1:1", help="aspect ratio id or token (9:16, 1:1, 16:9 ...)")
    p.add_argument("--quality", default=None, help="quality tail: default / illustration / photo / pixel / minimal")
    p.add_argument("--quality-phrase", default="", help="explicit quality tail, overrides --quality")
    p.add_argument("--loop", default="", help="loop motion id (breathe, blink, wave, turntable ...)")
    p.add_argument("--medium-phrase", default="", help="explicit medium clause, overrides --medium")


def add_core_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--style", default=None, help="style id from `styles`")
    p.add_argument("--medium", default=None, help="medium id from `media`")
    p.add_argument("--negative", action="append", default=[], help="extra negative term, repeatable")
    p.add_argument("--format", choices=["text", "json"], default="text")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="build_prompt",
        description="Assemble platform-agnostic IP character prompts.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("styles", help="list styles")
    s.add_argument("--family", help="filter by family id")
    s.add_argument("--search", help="free-text search across all style fields")
    s.add_argument("-v", "--verbose", action="store_true")
    s.add_argument("--format", choices=["text", "json", "ids"], default="text")
    s.set_defaults(func=cmd_styles)

    f = sub.add_parser("families", help="list families")
    f.add_argument("--format", choices=["text", "json"], default="text")
    f.set_defaults(func=cmd_families)

    m = sub.add_parser("media", help="list rendering media")
    m.add_argument("-v", "--verbose", action="store_true")
    m.add_argument("--format", choices=["text", "json"], default="text")
    m.set_defaults(func=cmd_media)

    sh = sub.add_parser("show", help="show one style or medium")
    sh.add_argument("id")
    sh.add_argument("-v", "--verbose", action="store_true")
    sh.set_defaults(func=cmd_show)

    b = sub.add_parser("build", help="assemble one prompt")
    add_character_flags(b)
    add_core_flags(b)
    b.add_argument("--show-negative", action="store_true", help="print the negative prompt too")
    b.set_defaults(func=cmd_build)

    k = sub.add_parser("kit", help="assemble the full deliverable kit")
    add_character_flags(k)
    add_core_flags(k)
    k.add_argument("--only", action="append", help="deliverable id to include, repeatable")
    k.add_argument("--expressions", action="append", help="expression id to include on the sheet, repeatable")
    k.add_argument("--poses", action="append", help="pose id from the pose library, repeatable")
    k.add_argument("--out", help="write JSON to this path")
    k.set_defaults(func=cmd_kit)

    c = sub.add_parser("consistency", help="print the lock block and checklist")
    add_character_flags(c)
    c.add_argument("--style", default=None)
    c.add_argument("--medium", default=None)
    c.set_defaults(func=cmd_consistency)

    v = sub.add_parser("video", help="assemble a video prompt")
    add_core_flags(v)
    v.add_argument("--type", choices=["image-to-video", "text-to-video", "camera"],
                   default="image-to-video")
    v.add_argument("--motion", default="", help="motion description")
    v.add_argument("--camera", help="camera move id (static, slow-push, orbit ...)")
    v.add_argument("--lens", help="lens id (wide, normal, portrait, macro)")
    add_character_flags(v)
    v.set_defaults(func=cmd_video)

    ch = sub.add_parser("check", help="validate the data files")
    ch.set_defaults(func=cmd_check)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    sys.exit(main())