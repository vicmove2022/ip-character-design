#!/usr/bin/env node
/**
 * ip-character-design :: prompt assembler (Node.js, zero dependencies).
 *
 * Reads the same JSON data files as scripts/build_prompt.py and produces
 * byte-identical output. Use whichever runtime you already have.
 *
 *   node scripts/build_prompt.mjs styles --family anthropomorphic
 *   node scripts/build_prompt.mjs show soft-3d-render -v
 *   node scripts/build_prompt.mjs build --style blob-mascot --subject "a bean cloud" ...
 *   node scripts/build_prompt.mjs kit --style plush --subject "a grey cat" --out kit.json
 *   node scripts/build_prompt.mjs video --motion "a wave" --type image-to-video
 *   node scripts/build_prompt.mjs check
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const DATA = path.join(HERE, "..", "data");

const load = (name) =>
  JSON.parse(fs.readFileSync(path.join(DATA, name), "utf8"));

const loadStyles = () => load("styles.json").styles;
const loadFamilies = () => load("styles.json").families;
const loadMedia = () => load("media.json").media;
const loadAnatomy = () => load("anatomy.json");
const loadNegatives = () => load("negatives.json");
const loadDeliverables = () => load("deliverables.json");

// --------------------------------------------------------------------------
// lookup with alias folding
// --------------------------------------------------------------------------

const SPELLING = [
  ["colour", "color"],
  ["colours", "colors"],
  ["gray", "grey"],
  ["behaviour", "behavior"],
  ["stylised", "stylized"],
];

const norm = (text) => {
  let t = String(text ?? "").toLowerCase().replace(/[-_\s]/g, "");
  for (const [a, b] of SPELLING) t = t.split(a).join(b);
  return t;
};

const ALIASES = {
  watercolor: "watercolor",
  watercolour: "watercolor",
  waterscolour: "watercolor",
  sketch: "pencil-sketch",
  pencil: "pencil-sketch",
  graphite: "pencil-sketch",
  charcoal: "pencil-sketch",
  marker: "hand-drawn-marker",
  handdrawn: "hand-drawn-marker",
  ink: "ink-line",
  lineart: "ink-line",
  "3drender": "soft-3d-render",
  "3d": "soft-3d-render",
  clay: "clay-plasticine",
  plasticine: "clay-plasticine",
  claymation: "clay-plasticine",
  toy: "designer-vinyl-figure",
  vinyl: "designer-vinyl-figure",
  figma: "designer-vinyl-figure",
  plush: "felt-wool-plush",
  felt: "felt-wool-plush",
  wool: "felt-wool-plush",
  crochet: "crochet-amigurumi",
  amigurumi: "crochet-amigurumi",
  yarn: "crochet-amigurumi",
  flat: "flat-vector",
  vector: "flat-vector",
  flatvector: "flat-vector",
  sticker: "die-cut-sticker",
  diecut: "die-cut-sticker",
  memphis: "memphis-pop",
  pop: "memphis-pop",
  lineartminimal: "line-art-minimal",
  pixel: "pixel-8bit",
  pixelart: "pixel-8bit",
  "8bit": "pixel-8bit",
  "16bit": "pixel-16bit-rpg",
  sprite: "pixel-16bit-rpg",
  lowpoly: "low-poly-3d",
  voxel: "voxel-art",
  anime: "anime-cel-shaded",
  cel: "anime-cel-shaded",
  celshaded: "anime-cel-shaded",
  cute: "chibi-anime-cute",
  chibi: "chibi-q-chibi",
  qversion: "chibi-q-chibi",
  manga: "manga-line-art",
  storybook: "watercolor-storybook",
  impasto: "oil-impasto",
  oil: "oil-impasto",
  oilpaint: "oil-impasto",
  food: "anthropomorphic-food",
  object: "anthropomorphic-object",
  plant: "anthropomorphic-plant",
  creature: "whimsical-creature",
  monster: "whimsical-creature",
  human: "photoreal-virtual-human",
  vtuber: "styled-avatar-nonhuman",
  avatar: "styled-avatar-nonhuman",
  semireal: "semi-real-human-illustration",
  soft: "soft-3d-render",
  photo: "photoreal",
  photorealistic: "photoreal",
  real: "photoreal",
  pastel: "pastel-soft",
  chalk: "pastel-soft",
  gouache: "gouache",
  digital: "flat-color-digital",
  celshading: "cel-shading",
  blob: "blob-mascot",
  bean: "blob-mascot",
  simple: "blob-mascot",
  brandmascot: "friendly-brand-mascot",
  corporate: "friendly-brand-mascot",
  sports: "retro-sports-mascot",
  team: "retro-sports-mascot",
  animalmascot: "anthropomorphic-animal-mascot",
  papercraft: "paper-craft",
  resin: "resin-art-figure",
  minimal: "line-art-minimal",
  geometric: "geometric-shape-character",
  shapes: "geometric-shape-character",
  shape: "geometric-shape-character",
  doll: "stuffed-fabric-doll",
  stuffed: "stuffed-fabric-doll",
  patchwork: "button-felt-doll",
  folkart: "button-felt-doll",
  folk: "button-felt-doll",
  kawaii: "chibi-anime-cute",
  bodypart: "anthropomorphic-body-part",
  body: "anthropomorphic-body-part",
  hand: "anthropomorphic-body-part",
  wash: "watercolor",
};

const normTokens = (text) => {
  let t = String(text ?? "").toLowerCase().replace(/[-_]/g, " ");
  for (const [a, b] of SPELLING) t = t.split(a).join(b);
  return t.split(/\s+/).filter(Boolean);
};

const lookup = (items, key) => {
  if (!key) return null;
  const exact = items.find((i) => i.id === key);
  if (exact) return exact;
  const nk = norm(key);
  const loose = items.find((i) => norm(i.id) === nk);
  if (loose) return loose;
  const target = ALIASES[nk];
  if (target) return items.find((i) => i.id === target) ?? null;
  // last resort: the key is a subset of an id's words, e.g. "animal mascot" ->
  // "anthropomorphic-animal-mascot", "doll" -> "stuffed-fabric-doll".
  // Numeric-only keys are never fuzzy-matched: "1-1.5" must not land on "1-2".
  const parts = new Set(normTokens(key));
  if (![...parts].some((p) => /[a-z]/i.test(p))) return null;
  let best = null;
  let bestScore = 0;
  for (const item of items) {
    const toks = new Set(normTokens(item.id));
    let overlap = 0;
    for (const p of parts) if (toks.has(p)) overlap += p.length;
    if (overlap > bestScore) {
      best = item;
      bestScore = overlap;
    }
  }
  return best;
};

const findStyle = (id) => lookup(loadStyles(), id);
const findMedia = (id) => lookup(loadMedia(), id);
const findExpression = (id) => lookup(loadDeliverables().expression_defaults, id);
const findLoop = (id) => lookup(loadDeliverables().loop_motions, id);
const findCamera = (id) => lookup(loadDeliverables().camera_moves, id);
const findLens = (id) => lookup(loadDeliverables().lens_notes, id);
const findRatio = (id) => lookup(loadDeliverables().aspect_ratios, id);
const findProportion = (id) => lookup(loadAnatomy().proportion_presets, id);

// --------------------------------------------------------------------------
// text helpers
// --------------------------------------------------------------------------

const clean = (text) => (text ? String(text).trim().replace(/[,\.]+$/, "") : "");

function segments(text) {
  const parts = [];
  let depth = 0;
  let buf = "";
  for (const ch of text) {
    if (ch === "(" || ch === "[") depth += 1;
    if (ch === ")" || ch === "]") depth = Math.max(0, depth - 1);
    if (ch === "," && depth === 0) {
      parts.push(buf);
      buf = "";
    } else {
      buf += ch;
    }
  }
  parts.push(buf);
  return parts.map((p) => p.trim()).filter(Boolean);
}

function join(parts) {
  const seen = new Set();
  const out = [];
  for (const raw of parts.map(clean)) {
    if (!raw) continue;
    for (const seg of segments(raw)) {
      const key = seg.toLowerCase().replace(/[. ]+$/, "");
      if (!key || seen.has(key)) continue;
      seen.add(key);
      out.push(seg);
    }
  }
  return out.join(", ");
}

const sentence = (parts) => {
  const out = join(parts);
  if (!out) return "";
  return out[0].toUpperCase() + out.slice(1) + ".";
};

const LIGHT_WORDS = [" light", " lighting", "backlit", "backlight", "rim light", "key light", "lit "];

function stripLightSegments(clause) {
  return segments(clause)
    .filter((seg) => !LIGHT_WORDS.some((w) => (" " + seg.toLowerCase()).includes(w)))
    .join(", ");
}

function styleClause(style, media, stripLighting = false) {
  const parts = [];
  if (style && !(media && media.id === style.id)) {
    const core = stripLighting ? stripLightSegments(style.core_en) : style.core_en;
    if (core) parts.push(core);
  }
  if (media && media.core_en) parts.push(media.core_en);
  return parts.join(", ");
}

const RENDER_SLOTS = ["medium", "lighting", "composition", "quality"];
const VARIABLE_SLOTS = ["pose", "world", "role"];

function lockBlock(values, includeRender = true) {
  let order = loadAnatomy().prompt_slot_order;
  if (!includeRender) order = order.filter((k) => !RENDER_SLOTS.includes(k));
  return order.map((k) => values[k] ?? "").filter(Boolean).join(", ");
}

function identityBlock(values) {
  const order = loadAnatomy().prompt_slot_order.filter(
    (k) => !RENDER_SLOTS.includes(k) && !VARIABLE_SLOTS.includes(k)
  );
  return order.map((k) => values[k] ?? "").filter(Boolean).join(", ");
}

// A template preposition stranded by an empty slot reads as a typo. Only
// collapse when nothing but punctuation follows, so ", the character identity"
// survives untouched.
const DANGLING = [
  "with", "in", "on", "at", "of", "and", "or", "but", "from", "to",
  "the", "a", "an", "is", "are", "as", "by", "under", "over", "near",
  "beside", "inside", "onto", "into", "that", "which",
];
const DANGLING_COMMA_RE = new RegExp(`\\s+(?:${DANGLING.join("|")})\\s*(?=,)`);
const DANGLING_END_RE = new RegExp(`,\\s*(?:${DANGLING.join("|")})\\s*(?=[.;])`);

function fill(template, values) {
  let out = template;
  for (const [key, val] of Object.entries(values)) {
    out = out.split("{" + key + "}").join(clean(val));
  }
  out = out.replace(/\{\s*[a-z_]+\s*\}/g, "");
  out = out.split(", .").join(".").split("  ").join(" ").split(" ,").join(",");
  while (out.includes(", ,")) out = out.split(", ,").join(",");
  for (;;) {
    const stripped = out.replace(DANGLING_COMMA_RE, "").replace(DANGLING_END_RE, "");
    if (stripped === out) break;
    out = stripped;
  }
  out = out.replace(/(,\s*){2,}/g, ", ").replace(/\s+,/g, ",");
  return sentence(out.split(". "));
}

const resolveRatio = (ratio) => {
  if (!ratio) return "1:1";
  const r = findRatio(ratio);
  return r ? r.token : ratio;
};

const qualityTail = (kind) => {
  const tails = loadNegatives().quality_tails;
  const list = tails[kind ?? "default"] ?? tails.default;
  return list.join(", ");
};

function inferQuality(style, media) {
  // the style family wins over the medium: a pixel character on a flat vector
  // medium is still a pixel character and needs the pixel tail
  if (style?.family === "pixel-lowpoly") return "pixel";
  if (media) {
    const id = media.id;
    if (id === "photoreal" || id === "soft-3d-render") return "photo";
    if (["pixel-8bit", "pixel-16bit-rpg", "low-poly-3d", "voxel-art"].includes(id)) return "pixel";
    if (["flat-color-digital", "line-art-minimal", "cel-shading", "flat-vector",
         "pencil-sketch", "ink-line"].includes(id)) return "minimal";
    return "illustration";
  }
  if (style) {
    if (style.family === "realistic-avatar") return "photo";
    if (["craft-plush", "3d-toy"].includes(style.family)) return "photo";
    return "illustration";
  }
  return "default";
}

function collectNegatives(style, media, video, extra = []) {
  const negs = loadNegatives();
  const seen = [];
  const add = (items) => {
    for (const it of items ?? []) if (!seen.includes(it)) seen.push(it);
  };
  add(negs.global);
  if (style) {
    add(style.negative_add);
    add(negs.by_family[style.family]);
  }
  if (media) {
    add(media.negative_add);
    add(negs.by_medium[media.id]);
  }
  if (video) add(negs.video_negatives);
  add(extra);
  return seen;
}

function lockedBlock(opts, media) {
  const expr = findExpression(opts.expression);
  const loop = findLoop(opts.loop);
  const prop = findProportion(opts.proportion);
  let lighting = opts.lighting || "";
  if (!lighting && media) lighting = media.default_lighting || "";
  const block = {
    subject: opts.subject || "",
    role: opts.role || "",
    signature_feature: opts.signature || "",
    proportion: opts.proportionPhrase || (prop ? prop.en : "") || opts.proportion || "",
    silhouette: opts.silhouette || "",
    palette: opts.palette || "",
    material: opts.material || "",
    outfit: opts.outfit || "",
    expression: expr ? expr.en : opts.expressionPhrase || "",
    pose: opts.pose || "",
    world: opts.world || "",
    signature_mark: opts.mark || "",
    medium: opts.mediumPhrase || "",
    lighting,
    composition: resolveRatio(opts.ratio),
    quality: opts.qualityPhrase || (opts.quality ? qualityTail(opts.quality) : ""),
    loop_motion: loop ? loop.en : "",
  };
  const out = {};
  for (const [k, v] of Object.entries(block)) out[k] = clean(v);
  return out;
}

const COUNT_WORDS = {
  1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",
  7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve",
};

function gridShape(n) {
  if (n <= 1) return "1x1";
  if (n === 2) return "2x1";
  const cols = n >= 3 ? 3 : 2;
  return `${cols}x${Math.ceil(n / cols)}`;
}

function retuneGrid(text, n, oldShape) {
  let out = text.split(oldShape).join(gridShape(n));
  const head = out.split(".")[0];
  for (const word of ["Six", "Twelve", "Eight", "Ten", "Nine", "Seven", "Five", "Four", "Three", "Two", "One"]) {
    if (head.includes(word)) {
      out = out.replace(word, COUNT_WORDS[n] ?? String(n));
      break;
    }
  }
  return out;
}

// --------------------------------------------------------------------------
// arg parsing
// --------------------------------------------------------------------------

const BOOL_FLAGS = new Set(["-v", "--verbose"]);

function parseArgs(argv) {
  const opts = { _: [], negative: [], only: [], expressions: [], poses: [], format: "text" };
  for (let i = 0; i < argv.length; i += 1) {
    const tok = argv[i];
    if (BOOL_FLAGS.has(tok)) {
      opts.verbose = true;
      continue;
    }
    if (tok.startsWith("--")) {
      const eq = tok.indexOf("=");
      let key, val;
      if (eq > -1) {
        key = tok.slice(2, eq);
        val = tok.slice(eq + 1);
      } else {
        key = tok.slice(2);
        const next = argv[i + 1];
        if (next !== undefined && !next.startsWith("--")) {
          val = next;
          i += 1;
        } else {
          val = true;
        }
      }
      key = key.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      if (key === "negative" || key === "only" || key === "expressions" || key === "poses") {
        if (!Array.isArray(opts[key])) opts[key] = [];
        if (val !== true) opts[key].push(val);
      } else {
        opts[key] = val === true ? true : val;
      }
      continue;
    }
    opts._.push(tok);
  }
  return opts;
}

const say = (line = "") => process.stdout.write(line + "\n");

// --------------------------------------------------------------------------
// commands
// --------------------------------------------------------------------------

function cmdStyles(o) {
  let styles = loadStyles();
  const fams = Object.fromEntries(loadFamilies().map((f) => [f.id, f]));
  if (o.family) styles = styles.filter((s) => s.family === o.family);
  if (o.search) {
    const raw = String(o.search).toLowerCase();
    styles = styles.filter(
      (s) => JSON.stringify(s).toLowerCase().includes(raw) || findStyle(raw) === s
    );
  }
  if (o.format === "json") return say(JSON.stringify(styles, null, 2));
  if (o.format === "ids") return styles.forEach((s) => say(s.id));
  const width = Math.max(4, ...styles.map((s) => s.id.length));
  for (const s of styles) {
    const fam = fams[s.family]?.name_en ?? s.family;
    say(`${s.id.padEnd(width)}  ${fam.padEnd(22)}  ${s.tagline_en}`);
    if (o.verbose) {
      say(`${" ".repeat(width)}  zh: ${s.tagline_zh}`);
      for (const w of s.use_when ?? []) say(`${" ".repeat(width)}    - ${w}`);
    }
  }
}

function cmdFamilies(o) {
  const fams = loadFamilies();
  const styles = loadStyles();
  if (o.format === "json") return say(JSON.stringify(fams, null, 2));
  for (const f of fams) {
    const count = styles.filter((s) => s.family === f.id).length;
    say(`${f.id.padEnd(22)}  ${String(count).padStart(2)} styles  ${f.name_en} / ${f.name_zh}`);
    say(`${" ".repeat(22)}  ${f.blurb}`);
  }
}

function cmdMedia(o) {
  const media = loadMedia();
  if (o.format === "json") return say(JSON.stringify(media, null, 2));
  const width = Math.max(4, ...media.map((m) => m.id.length));
  for (const m of media) {
    say(`${m.id.padEnd(Math.max(22, width))}  ${m.name_en} / ${m.name_zh}`);
    if (o.verbose) {
      say(`${" ".repeat(22)}  pairs well: ${(m.pairs_well ?? []).join(", ")}`);
      say(`${" ".repeat(22)}  avoid:     ${(m.pairs_badly ?? []).join(", ")}`);
    }
  }
}

function cmdShow(o) {
  const node = findStyle(o._[0]) || findMedia(o._[0]);
  if (!node) {
    process.stderr.write(`Unknown style or media id: ${o._[0] ?? ""}\n`);
    return 1;
  }
  say(`# ${node.name_en} / ${node.name_zh ?? ""}`);
  say(`id:     ${node.id}`);
  if (node.family) say(`family: ${node.family}`);
  if (node.tagline_en) say(`\n${node.tagline_en}\n${node.tagline_zh}`);
  if (o.verbose) {
    if (node.use_when) {
      say("\nUse when:");
      for (const w of node.use_when) say(`  - ${w}`);
    }
    if (node.avoid_when) say(`\nAvoid when: ${node.avoid_when}`);
    for (const key of ["proportion", "surface", "surface_note", "lighting", "default_lighting"]) {
      if (node[key]) say(`\n${key}: ${node[key]}`);
    }
    if (node.kw_zh) say(`\nzh keywords: ${node.kw_zh.join(" / ")}`);
    if (node.pairs_well) {
      say(`\npairs well: ${node.pairs_well.join(", ")}`);
      say(`avoid:      ${node.pairs_badly.join(", ")}`);
    }
    if (node.core_en) say(`\ncore_en:\n${node.core_en}`);
    if (node.video) say(`\nvideo: ${node.video}`);
    if (node.loop) say(`loop:  ${node.loop}`);
  } else if (node.core_en) {
    say(`\ncore_en: ${node.core_en}`);
  }
  return 0;
}

function cmdBuild(o) {
  const style = o.style ? findStyle(o.style) : null;
  const media = o.medium ? findMedia(o.medium) : null;
  const values = lockedBlock(o, media);
  if (!values.quality) values.quality = qualityTail(inferQuality(style, media));
  const core = styleClause(style, media, true);
  const prompt = sentence([
    lockBlock(values, false),
    core,
    values.lighting,
    values.composition,
    values.quality,
  ]);
  const negs = collectNegatives(style, media, false, o.negative);
  if (o.format === "json") {
    return say(JSON.stringify({
      prompt,
      negative: negs.join(", "),
      style: style?.id ?? null,
      medium: media?.id ?? null,
      ratio: values.composition,
      lock_block: lockBlock(values),
    }, null, 2));
  }
  say(prompt);
  if (o.negative.length || o.showNegative === true) say(`\nNEGATIVE: ${negs.join(", ")}`);
}

function cmdKit(o) {
  const style = o.style ? findStyle(o.style) : null;
  const media = o.medium ? findMedia(o.medium) : null;
  const values = lockedBlock(o, media);
  if (!values.quality) values.quality = qualityTail(inferQuality(style, media));
  const core = styleClause(style, media, true);
  const ratio = values.composition;
  const deliverables = loadDeliverables();
  const only = o.only.length ? new Set(o.only) : null;

  const out = {
    character: {
      style: style?.id ?? null,
      style_name: style?.name_en ?? null,
      medium: media?.id ?? null,
      medium_name: media?.name_en ?? null,
      lock_block: lockBlock(values),
      ratio,
    },
    prompts: {},
  };

  const exprEntries = deliverables.expression_defaults.filter(
    (e) => !o.expressions.length || o.expressions.includes(e.id)
  );
  const exprList = exprEntries.map((e) => e.en).join(", ");
  const exprGrid = retuneGrid(
    (deliverables.expression_grid_default ?? "{list}").replace("{list}", exprList),
    exprEntries.length,
    "3x2"
  );

  let poses = (deliverables.extra_poses ?? []).filter((p) => o.poses.includes(p.id));
  if (!poses.length) {
    poses = (deliverables.pose_defaults ?? []).map((en, i) => ({ id: `p${i + 1}`, en, zh: "" }));
  }
  const poseList = poses.map((p) => p.en).join(", ");
  const poseGrid = retuneGrid(
    (deliverables.pose_grid_default ?? "{list}").replace("{list}", poseList),
    poses.length,
    "2x3"
  );

  for (const d of deliverables.deliverables) {
    if (only && !only.has(d.id)) continue;
    const extra = {
      ...values,
      style_core: core,
      medium_core: "",
      expression_grid: exprGrid,
      pose_grid: poseGrid,
    };
    if (d.id === "loop" && !extra.loop_motion) {
      extra.loop_motion = "a gentle breathing bob with a subtle chest rise and fall";
    }
    out.prompts[d.id] = {
      label_en: d.label_en,
      label_zh: d.label_zh,
      purpose: d.purpose,
      ratio: o.ratio ? ratio : d.ratio,
      prompt: fill(d.template, extra),
      negative: collectNegatives(style, media, d.id === "loop", []).join(", "),
      notes: d.notes,
    };
  }

  for (const [did, entry] of Object.entries(out.prompts)) {
    if (did === "expression-sheet") {
      entry.expression_palette = exprEntries.map((e) => ({ id: e.id, en: e.en, zh: e.zh }));
    } else if (did === "pose-sheet") {
      entry.pose_palette = poses.map((p) => ({ id: p.id, en: p.en, zh: p.zh }));
    }
  }
  
out.character.available_expressions = deliverables.expression_defaults.map((e) => ({
    id: e.id, en: e.en, zh: e.zh,
  }));
  out.character.available_poses = (deliverables.extra_poses ?? []).map((p) => ({
    id: p.id, en: p.en, zh: p.zh,
  }));

  if (o.out) {
    fs.writeFileSync(o.out, JSON.stringify(out, null, 2), "utf8");
    return say(`wrote ${o.out} (${Object.keys(out.prompts).length} prompts)`);
  }
  if (o.format === "json") return say(JSON.stringify(out, null, 2));

  say(`# ${out.character.style_name ?? "custom"} / ${out.character.medium_name ?? "no medium"}`);
  say(`ratio: ${ratio}`);
  say(`\nLOCK BLOCK (reuse verbatim in every shot):\n${out.character.lock_block}\n`);
  for (const [pid, entry] of Object.entries(out.prompts)) {
    say(`## ${pid} - ${entry.label_en} / ${entry.label_zh}  [${entry.ratio}]`);
    say(`purpose: ${entry.purpose}`);
    say(entry.prompt);
    say(`negative: ${entry.negative}`);
    say(`note: ${entry.notes}\n`);
  }
}

function cmdConsistency(o) {
  const style = o.style ? findStyle(o.style) : null;
  const media = o.medium ? findMedia(o.medium) : null;
  const values = lockedBlock(o, media);
  if (!values.quality) values.quality = qualityTail(inferQuality(style, media));
  const core = styleClause(style, media, true);
  say("IDENTITY BLOCK - copy verbatim into every prompt in the series.");
  say("Nothing in this block may change between shots:\n");
  say(identityBlock(values));
  say("\n\nRENDER BLOCK - hold constant within one series, change deliberately");
  say("between series:\n");
  say(join([core, values.lighting, values.composition, values.quality]));
  say("\n\nLOCK CHECKLIST");
  say(" 1. Subject phrase identical, character for character.");
  say(" 2. Signature feature phrase present in every prompt.");
  say(" 3. Outline colour named explicitly (e.g. 'charcoal outline').");
  say(" 4. Head-to-body ratio stated numerically.");
  say(" 5. Medium identical. Never change medium mid-series.");
  say(" 6. Outfit identical even when the pose changes.");
  say(" 7. Lighting identical for identity shots.");
  say(" 8. Same aspect ratio for the whole series.");
  say(" 9. Regenerate anything that drifts; do not average two candidates.");
  say("10. If the engine supports it, also pass a reference image or character");
  say("    reference on every frame (character reference / style reference /");
  say("    image-to-image). Text locks alone drift; image locks are stronger.");
}

function cmdVideo(o) {
  const style = o.style ? findStyle(o.style) : null;
  const media = o.medium ? findMedia(o.medium) : null;
  const values = lockedBlock(o, media);
  if (!values.quality) values.quality = qualityTail(inferQuality(style, media));
  const tpl = loadDeliverables().video_templates[o.type];
  const core = styleClause(style, media, true);
  const cam = o.camera ? findCamera(o.camera) : null;
  const lens = o.lens ? findLens(o.lens) : null;

  let fillMap;
  if (o.type === "camera") {
    fillMap = {
      subject: identityBlock(values),
      camera_move: cam ? cam.en : "static locked-off camera",
      lens_note: lens ? lens.en : "",
    };
  } else if (o.type === "text-to-video") {
    fillMap = {
      subject: identityBlock(values),
      style_core: core,
      medium_core: "",
      motion: clean(o.motion),
      lighting: values.lighting,
      ratio: values.composition,
    };
  } else {
    fillMap = { motion: clean(o.motion) || "a gentle breathing bob with a subtle blink" };
  }

  const prompt = fill(tpl, fillMap);
  const negs = collectNegatives(style, media, true, o.negative);
  if (o.format === "json") {
    return say(JSON.stringify({
      type: o.type,
      prompt,
      negative: negs.join(", "),
      camera: cam?.en ?? null,
      lens: lens?.en ?? null,
    }, null, 2));
  }
  say(prompt);
  say(`\nNEGATIVE: ${negs.join(", ")}`);
}

function cmdCheck() {
  const problems = [];
  const styles = loadStyles();
  const media = loadMedia();
  const families = new Set(loadFamilies().map((f) => f.id));
  const negs = loadNegatives();
  const deliverables = loadDeliverables();
  const anatomy = loadAnatomy();

  const ids = styles.map((s) => s.id);
  if (new Set(ids).size !== ids.length) problems.push("duplicate style ids");
  for (const s of styles) {
    for (const key of ["id", "name_en", "name_zh", "family", "tagline_en", "tagline_zh",
      "proportion", "surface", "lighting", "core_en", "kw_zh", "video", "loop"]) {
      if (!s[key]) problems.push(`style ${s.id}: missing ${key}`);
    }
    if (!families.has(s.family)) problems.push(`style ${s.id}: unknown family ${s.family}`);
    if (!negs.by_family[s.family]) problems.push(`style ${s.id}: family ${s.family} has no negative pool`);
  }

  const mids = media.map((m) => m.id);
  if (new Set(mids).size !== mids.length) problems.push("duplicate media ids");
  for (const m of media) {
    if (!negs.by_medium[m.id]) problems.push(`media ${m.id}: no negative pool`);
    if (!m.default_lighting) problems.push(`media ${m.id}: no default_lighting`);
    for (const ref of [...(m.pairs_badly ?? []), ...(m.pairs_well ?? [])]) {
      if (!families.has(ref) && !ids.includes(ref)) problems.push(`media ${m.id}: unknown pairing target ${ref}`);
    }
  }

  const slotIds = anatomy.slots.map((s) => s.id);
  for (const slot of slotIds) {
    if (!anatomy.prompt_slot_order.includes(slot)) problems.push(`slot ${slot} missing from prompt_slot_order`);
  }
  for (const slot of anatomy.prompt_slot_order) {
    if (!slotIds.includes(slot)) problems.push(`prompt_slot_order references unknown slot ${slot}`);
  }

  const ratioIds = new Set(deliverables.aspect_ratios.map((r) => r.id));
  const allowed = new Set([...slotIds, "style_core", "medium_core", "loop_motion",
    "composition", "quality", "expression_grid", "pose_grid"]);
  for (const d of deliverables.deliverables) {
    if (!ratioIds.has(d.ratio)) problems.push(`deliverable ${d.id}: unknown ratio ${d.ratio}`);
    for (const m of d.template.matchAll(/\{([a-z_]+)\}/g)) {
      if (!allowed.has(m[1])) problems.push(`deliverable ${d.id}: unknown token {${m[1]}}`);
    }
  }

  const banned = ["pixar", "disney", "ghibli", "marvel", "sanrio", "lego",
    "pokemon", "mario", "star wars", "harry potter"]
    .filter((w) => styles.some((s) => (s.core_en ?? "").toLowerCase().includes(w)));
  if (banned.length) problems.push(`banned names found in style data: ${banned}`);

  say(`styles:  ${styles.length}`);
  say(`families:${families.size}`);
  say(`media:   ${media.length}`);
  say(`slots:   ${slotIds.length}`);
  say(`deliverables: ${deliverables.deliverables.length}`);
  if (problems.length) {
    say(`\n${problems.length} problem(s):`);
    for (const p of problems) say("  -", p);
    return 1;
  }
  say("\nOK: all data files consistent, no banned names in style data.");
  return 0;
}

// --------------------------------------------------------------------------
// main
// --------------------------------------------------------------------------

const COMMANDS = {
  styles: cmdStyles,
  families: cmdFamilies,
  media: cmdMedia,
  show: cmdShow,
  build: cmdBuild,
  kit: cmdKit,
  consistency: cmdConsistency,
  video: cmdVideo,
  check: cmdCheck,
};

const USAGE = `ip-character-design prompt assembler

  styles [--family F] [--search Q] [-v] [--format text|json|ids]
  families [--format text|json]
  media [-v] [--format text|json]
  show <style-id|medium-id> [-v]
  build  --style S --medium M --subject "..." --signature "..." ...
  kit    ...same flags... [--only ID]... [--expressions ID]... [--poses ID]... [--out FILE]
  consistency --style S --medium M --subject "..." ...
  video  --type image-to-video|text-to-video|camera [--motion "..."] [--camera ID] [--lens ID]
  check
`;

function main() {
  const argv = process.argv.slice(2);
  const cmd = argv[0];
  if (!cmd || cmd === "-h" || cmd === "--help" || cmd === "help") {
    process.stdout.write(USAGE);
    return 0;
  }
  const fn = COMMANDS[cmd];
  if (!fn) {
    process.stderr.write(`Unknown command: ${cmd}\n\n${USAGE}`);
    return 1;
  }
  const opts = parseArgs(argv.slice(1));
  const rc = fn(opts);
  return typeof rc === "number" ? rc : 0;
}

process.exitCode = main();