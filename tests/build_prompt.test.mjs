/**
 * Node-side tests. Covers the same behaviour as tests/test_build_prompt.py
 * plus native-parity helpers. Run:  node --test tests/
 */

import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(HERE, "..");
const CLI = path.join(ROOT, "scripts", "build_prompt.mjs");

// Python writes CRLF on Windows and Node writes LF; normalise before comparing.
const lf = (text) => text.replace(/\r\n/g, "\n");

const run = (...args) => lf(execFileSync(process.execPath, [CLI, ...args], {
  encoding: "utf8",
  cwd: ROOT,
}));
const readData = (name) =>
  JSON.parse(fs.readFileSync(path.join(ROOT, "data", name), "utf8"));

// --------------------------------------------------------------------------

test("data files are internally consistent", () => {
  const styles = readData("styles.json");
  const ids = styles.styles.map((s) => s.id);
  assert.equal(ids.length, new Set(ids).size, "duplicate style ids");
  assert.ok(ids.length >= 30, "expected 30+ styles");

  const fams = new Set(styles.families.map((f) => f.id));
  for (const s of styles.styles) {
    assert.ok(fams.has(s.family), `${s.id} family`);
    assert.ok(s.name_en && s.name_zh, `${s.id} bilingual labels`);
    assert.ok(s.kw_zh.length >= 3, `${s.id} zh keywords`);
  }
  for (const f of styles.families) {
    assert.ok(styles.styles.some((s) => s.family === f.id), `${f.id} has styles`);
  }
});

test("no banned names anywhere in style data", () => {
  const banned = [
    "pixar", "disney", "ghibli", "marvel", "sanrio", "lego",
    "pokemon", "mario", "star wars", "harry potter", "barbie", "hello kitty",
  ];
  const blob = JSON.stringify(readData("styles.json")).toLowerCase();
  for (const word of banned) {
    assert.ok(!blob.includes(word), `banned word present: ${word}`);
  }
});

test("every media has negatives and default lighting", () => {
  const negs = readData("negatives.json");
  for (const m of readData("media.json").media) {
    assert.ok(negs.by_medium[m.id], `${m.id} negatives`);
    assert.ok(m.default_lighting, `${m.id} lighting`);
  }
});

test("check command exits zero", () => {
  assert.match(run("check"), /OK: all data files consistent/);
});

test("styles listing covers every family", () => {
  const out = run("families");
  for (const f of readData("styles.json").families) {
    assert.ok(out.includes(f.id), `missing family ${f.id}`);
  }
});

test("build emits no unfilled tokens or empty slots", () => {
  const out = run(
    "build",
    "--style", "anthropomorphic-plant",
    "--medium", "cel-shading",
    "--subject", "a small round terracotta pot with a happy face",
    "--signature", "three lime-green leaves sprouting from the rim",
    "--palette", "warm terracotta pot, lime green foliage, charcoal outline",
    "--material", "matte unglazed terracotta",
    "--proportion", "1-3",
    "--expression", "happy",
    "--ratio", "9:16"
  );
  assert.ok(!out.includes("{"), "no { tokens");
  assert.ok(!out.includes("}"), "no } tokens");
  assert.ok(!out.includes(", ,"), "no empty segments");
  for (const token of ["terracotta", "three-head-tall", "charcoal outline", "cel shading", "9:16"]) {
    assert.ok(out.includes(token), `missing ${token}`);
  }
});

test("british spelling and aliases resolve", () => {
  assert.match(run("show", "watercolour"), /Watercolour Wash/);
  assert.match(run("show", "VTuber"), /Stylised Non-Human Avatar/);
  assert.match(run("show", "food"), /Anthropomorphic Food/);
});

test("unknown id exits non-zero", () => {
  assert.throws(() => run("show", "definitely-not-a-style"));
});

test("kit writes all ten deliverables", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "ipkit-"));
  const file = path.join(dir, "kit.json");
  run("kit", "--style", "blob-mascot", "--subject", "a bean cloud",
      "--signature", "one red mitten", "--palette", "cream, coral, charcoal outline",
      "--out", file);
  const data = JSON.parse(fs.readFileSync(file, "utf8"));
  const expected = readData("deliverables.json").deliverables.map((d) => d.id);
  assert.deepEqual(Object.keys(data.prompts).sort(), expected.sort());
  for (const entry of Object.values(data.prompts)) {
    assert.ok(!entry.prompt.includes("{"));
    assert.ok(!entry.prompt.includes("with ,"));
  }
});

test("expression subset rewrites the panel count and grid", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "ipkit-"));
  const file = path.join(dir, "kit.json");
  run("kit", "--style", "blob-mascot", "--subject", "a bean",
      "--expressions", "happy", "--expressions", "sad",
      "--only", "expression-sheet", "--out", file);
  const prompt = JSON.parse(fs.readFileSync(file, "utf8"))
    .prompts["expression-sheet"].prompt;
  assert.match(prompt, /Two head-and-shoulders panels/);
  assert.match(prompt, /2x1 grid/);
  assert.ok(!prompt.includes("confused"));
});

test("pose selection swaps the pose list", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "ipkit-"));
  const file = path.join(dir, "kit.json");
  run("kit", "--style", "blob-mascot", "--subject", "a bean",
      "--poses", "heart-hands", "--poses", "phone-hold",
      "--only", "pose-sheet", "--out", file);
  const entry = JSON.parse(fs.readFileSync(file, "utf8")).prompts["pose-sheet"];
  assert.match(entry.prompt, /heart shape/);
  assert.match(entry.prompt, /holding a phone/);
  assert.ok(!entry.prompt.includes("shaka"));
});

test("consistency separates the identity block from the render block", () => {
  const out = run("consistency", "--style", "blob-mascot",
                  "--medium", "flat-color-digital",
                  "--subject", "a bean-shaped cloud",
                  "--signature", "one red mitten",
                  "--palette", "cream, coral, charcoal outline");
  const identity = out.split("RENDER BLOCK")[0];
  assert.ok(identity.includes("a bean-shaped cloud"));
  assert.ok(identity.includes("one red mitten"));
});

test("video prompt type selects the right template", () => {
  const i2v = run("video", "--type", "image-to-video", "--motion", "a gentle wave");
  assert.match(i2v, /camera stays completely static/);

  const t2v = run("video", "--type", "text-to-video", "--motion", "turns to face the viewer",
                  "--style", "blob-mascot", "--subject", "a bean cloud");
  assert.match(t2v, /turns to face the viewer/);
  assert.match(t2v, /consistent character identity/);

  const cam = run("video", "--type", "camera", "--camera", "orbit", "--lens", "portrait",
                  "--subject", "a bean cloud");
  assert.match(cam, /20-degree orbit/);
  assert.match(cam, /85mm portrait lens/);
});

test("python and node produce identical output", { skip: !hasPython() }, () => {
  const py = (args) => lf(execFileSync("python", ["-X", "utf8",
    path.join(ROOT, "scripts", "build_prompt.py"), ...args],
    { encoding: "utf8", cwd: ROOT }));

  const cases = [
    ["styles"],
    ["families"],
    ["media"],
    ["check"],
    ["show", "chibi-q-chibi", "-v"],
    ["build", "--style", "anthropomorphic-plant", "--medium", "cel-shading",
      "--subject", "a small round terracotta pot with a happy face",
      "--signature", "three lime-green leaves sprouting from the rim",
      "--palette", "warm terracotta pot, lime green foliage, charcoal outline",
      "--material", "matte unglazed terracotta",
      "--proportion", "1-3", "--expression", "happy", "--ratio", "9:16"],
    ["build", "--style", "felt-wool-plush", "--medium", "watercolor",
      "--subject", "a round grey cat", "--signature", "one red scarf",
      "--palette", "warm grey, red, charcoal outline",
      "--expression", "excited", "--ratio", "1:1", "--format", "json"],
    ["build", "--style", "manga-line-art", "--medium", "ink-line",
      "--subject", "a detective cat", "--silhouette", "a tall narrow silhouette",
      "--palette", "black ink, white", "--ratio", "4:5", "--show-negative"],
    ["consistency", "--style", "blob-mascot", "--medium", "flat-color-digital",
      "--subject", "a bean-shaped cloud", "--signature", "one red mitten",
      "--palette", "cream, coral, charcoal outline"],
    ["video", "--type", "image-to-video", "--motion", "a gentle wave",
      "--style", "chibi-q-chibi", "--medium", "cel-shading"],
  ];

  for (const args of cases) {
    assert.equal(py(args), run(...args), `parity for: ${args.join(" ")}`);
  }
});

function hasPython() {
  try {
    execFileSync("python", ["--version"], { stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}