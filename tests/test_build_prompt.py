"""Parity + behaviour tests for the Python assembler, and a cross-runtime
parity check against the Node assembler.

Run:  python -m unittest discover -s tests -v
      node --test tests/
"""

import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import build_prompt as bp  # noqa: E402


def run(*args: str) -> str:
    return bp.main(list(args)) or 0


def _lf(text: str) -> str:
    """Normalise line endings: Python writes CRLF on Windows, Node writes LF."""
    return text.replace("\r\n", "\n")


class DataIntegrity(unittest.TestCase):
    def test_no_duplicate_style_ids(self):
        ids = [s["id"] for s in bp.load_styles()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_style_count(self):
        self.assertGreaterEqual(len(bp.load_styles()), 30)

    def test_every_style_has_bilingual_labels(self):
        for s in bp.load_styles():
            self.assertTrue(s["name_en"])
            self.assertTrue(s["name_zh"])
            self.assertTrue(s["tagline_en"])
            self.assertTrue(s["tagline_zh"])

    def test_every_style_has_zh_keywords(self):
        for s in bp.load_styles():
            self.assertGreaterEqual(len(s["kw_zh"]), 3)

    def test_every_family_referenced_exists(self):
        fams = {f["id"] for f in bp.load_families()}
        for s in bp.load_styles():
            self.assertIn(s["family"], fams)

    def test_every_family_has_styles(self):
        styles = bp.load_styles()
        for f in bp.load_families():
            self.assertTrue(
                any(s["family"] == f["id"] for s in styles),
                f"family {f['id']} has no styles",
            )

    def test_every_media_has_negatives_and_lighting(self):
        negs = bp.load_negatives()
        for m in bp.load_media():
            self.assertIn(m["id"], negs["by_medium"], m["id"])
            self.assertTrue(m.get("default_lighting"), m["id"])

    def test_no_banned_names_in_style_data(self):
        banned = ["pixar", "disney", "ghibli", "marvel", "sanrio", "lego",
                  "pokemon", "mario", "star wars", "harry potter", "barbie",
                  "hello kitty", "transformers"]
        for s in bp.load_styles():
            blob = json.dumps(s, ensure_ascii=False).lower()
            for word in banned:
                self.assertNotIn(word, blob, f"{s['id']} mentions {word}")

    def test_every_deliverable_ratio_is_known(self):
        known = {r["id"] for r in bp.load_deliverables()["aspect_ratios"]}
        for d in bp.load_deliverables()["deliverables"]:
            self.assertIn(d["ratio"], known, d["id"])

    def test_every_deliverable_token_resolves(self):
        slots = {s["id"] for s in bp.load_anatomy()["slots"]}
        allowed = slots | {"style_core", "medium_core", "loop_motion", "composition",
                           "quality", "expression_grid", "pose_grid"}
        import re
        for d in bp.load_deliverables()["deliverables"]:
            for token in re.findall(r"\{([a-z_]+)\}", d["template"]):
                self.assertIn(token, allowed, f"{d['id']} uses {token}")

    def test_check_command_passes(self):
        self.assertEqual(bp.main(["check"]), 0)


class Lookup(unittest.TestCase):
    def test_exact_ids(self):
        self.assertEqual(bp.find_style("blob-mascot")["id"], "blob-mascot")
        self.assertEqual(bp.find_media("watercolor")["id"], "watercolor")

    def test_british_spelling_resolves(self):
        self.assertEqual(bp.find_media("watercolour")["id"], "watercolor")
        self.assertEqual(bp.find_media("Water Colour")["id"], "watercolor")

    def test_aliases_resolve(self):
        self.assertEqual(bp.find_style("food")["id"], "anthropomorphic-food")
        self.assertEqual(bp.find_style("chibi")["id"], "chibi-q-chibi")
        self.assertEqual(bp.find_style("VTuber")["id"], "styled-avatar-nonhuman")
        self.assertEqual(bp.find_style("3D")["id"], "soft-3d-render")

    def test_unknown_returns_none(self):
        self.assertIsNone(bp.find_style("no-such-style"))
        self.assertIsNone(bp.find_media("no-such-medium"))

    def test_cross_family_lookups(self):
        self.assertEqual(bp.find_expression("happy")["id"], "happy")
        self.assertEqual(bp.find_loop("wave")["id"], "wave")
        self.assertEqual(bp.find_camera("orbit")["id"], "orbit")
        self.assertEqual(bp.find_ratio("9:16")["id"], "9:16")
        self.assertEqual(bp.find_proportion("1-3")["id"], "1-3")


class TextAssembly(unittest.TestCase):
    def test_segments_respects_brackets(self):
        segs = bp._segments("a light (red, blue) hat, b")
        self.assertEqual(len(segs), 2)

    def test_join_deduplicates(self):
        out = bp._join(["red hat, charcoal outline", "charcoal outline, blue"])
        self.assertEqual(out.lower().count("charcoal outline"), 1)

    def test_sentence_capitalises_and_periods(self):
        self.assertEqual(bp._sentence(["a small cat"]), "A small cat.")

    def test_strip_light_removes_lighting_segments(self):
        out = bp.strip_light_segments("rounded form, soft key light from above, matte skin")
        self.assertNotIn("key light", out)
        self.assertIn("rounded form", out)
        self.assertIn("matte skin", out)

    def test_fill_drops_empty_slots(self):
        out = bp.fill("{subject}, {signature_feature}, {palette}.", {
            "subject": "a pear", "signature_feature": "", "palette": "yellow",
        })
        self.assertEqual(out, "A pear, yellow.")


class PromptQuality(unittest.TestCase):
    CHAR = dict(
        style="anthropomorphic-plant",
        medium="cel-shading",
        subject="a small round terracotta pot with a happy face",
        signature="three lime-green leaves sprouting from the rim",
        palette="warm terracotta pot, lime green foliage, charcoal outline",
        material="matte unglazed terracotta",
        proportion="1-3",
        expression="happy",
        ratio="9:16",
    )

    def _build(self, **over):
        args = dict(self.CHAR)
        args.update(over)
        flags = []
        for k, v in args.items():
            flags += ["--" + k.replace("_", "-"), str(v)]
        return bp.build_one(flags) if hasattr(bp, "build_one") else bp.main(["build"] + flags)

    def test_prompt_contains_every_identity_slot(self):
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            bp.main(["build"] + self._flags())
        out = buf.getvalue()
        for token in ("terracotta", "leaves sprouting", "three-head-tall",
                      "lime green", "charcoal outline", "cel shading", "9:16"):
            self.assertIn(token, out, token)

    def _flags(self, **over):
        args = dict(self.CHAR)
        args.update(over)
        flags = []
        for k, v in args.items():
            flags += ["--" + k.replace("_", "-"), str(v)]
        return flags

    def test_no_double_comma_or_empty_slots(self):
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            bp.main(["build"] + self._flags())
        out = buf.getvalue()
        self.assertNotIn(", ,", out)
        self.assertNotIn("{", out)
        self.assertNotIn("}", out)

    def test_style_core_lighting_conflicts_are_stripped(self):
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            bp.main(["build"] + self._flags(medium="watercolor", style="designer-vinyl-figure"))
        out = buf.getvalue().lower()
        # watercolour must not carry the vinyl toy's specular studio language
        self.assertNotIn("blister", out)
        self.assertIn("granulation", out)

    def test_negative_pool_includes_family_and_global(self):
        negs = bp.collect_negatives(bp.find_style("anthropomorphic-plant"),
                                    bp.find_media("cel-shading"), video=False)
        self.assertIn("extra limbs", negs)
        self.assertIn("soft gradient shading", negs)

    def test_video_negatives_only_for_video(self):
        style, media = bp.find_style("blob-mascot"), bp.find_media("flat-color-digital")
        still = bp.collect_negatives(style, media, video=False)
        motion = bp.collect_negatives(style, media, video=True)
        self.assertNotIn("temporal flicker", still)
        self.assertIn("temporal flicker", motion)

    def test_infer_quality_per_family(self):
        self.assertEqual(bp.infer_quality(bp.find_style("pixel-8bit"), None), "pixel")
        self.assertEqual(bp.infer_quality(bp.find_style("photoreal-virtual-human"), None), "photo")
        self.assertEqual(bp.infer_quality(bp.find_style("blob-mascot"), None), "illustration")


class Consistency(unittest.TestCase):
    def test_identity_block_excludes_pose_and_world(self):
        values = {
            "subject": "a pear", "signature_feature": "red ribbon",
            "palette": "yellow, charcoal outline", "pose": "waving",
            "world": "on a table", "lighting": "soft light",
            "composition": "1:1", "quality": "clean render",
        }
        ident = bp.identity_block(values)
        self.assertIn("a pear", ident)
        self.assertNotIn("waving", ident)
        self.assertNotIn("on a table", ident)
        self.assertNotIn("soft light", ident)

    def test_full_block_includes_everything(self):
        values = {
            "subject": "a pear", "pose": "waving", "world": "on a table",
            "lighting": "soft light", "composition": "1:1", "quality": "clean render",
        }
        full = bp.lock_block(values)
        for token in ("a pear", "waving", "on a table", "soft light", "1:1"):
            self.assertIn(token, full)


class GridTuning(unittest.TestCase):
    def test_grid_shapes(self):
        self.assertEqual(bp._grid_shape(1), "1x1")
        self.assertEqual(bp._grid_shape(2), "2x1")
        self.assertEqual(bp._grid_shape(6), "3x2")
        self.assertEqual(bp._grid_shape(3), "3x1")

    def test_retune_grid_rewrites_count_and_shape(self):
        out = bp._retune_grid("Six panels in a 3x2 grid, each one", 3, "3x2")
        self.assertIn("3x1", out)
        self.assertIn("Three", out)
        self.assertNotIn("Six", out)

    def test_retune_grid_with_unknown_count(self):
        out = bp._retune_grid("Six panels in a 3x2 grid", 10, "3x2")
        self.assertIn("3x4", out)
        self.assertIn("Ten", out)


class CommandSmoke(unittest.TestCase):
    def test_all_commands_run(self):
        for argv in (
            ["styles"],
            ["styles", "--format", "ids"],
            ["families"],
            ["media", "-v"],
            ["show", "blob-mascot"],
            ["show", "watercolor", "-v"],
            ["check"],
        ):
            with self.subTest(argv=argv):
                self.assertEqual(run(*argv), 0)

    def test_unknown_show_returns_nonzero(self):
        self.assertEqual(run("show", "nope"), 1)

    def test_search_finds_by_alias(self):
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            bp.main(["styles", "--search", "food", "--format", "ids"])
        self.assertIn("anthropomorphic-food", buf.getvalue())

    def test_kit_writes_all_ten_deliverables(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "kit.json")
            rc = run("kit", "--style", "blob-mascot", "--subject", "a bean cloud",
                     "--signature", "one red mitten", "--palette", "cream, coral, charcoal outline",
                     "--out", path)
            self.assertEqual(rc, 0)
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            expected = {d["id"] for d in bp.load_deliverables()["deliverables"]}
            self.assertEqual(set(data["prompts"]), expected)
            for entry in data["prompts"].values():
                self.assertNotIn("{", entry["prompt"])
                self.assertNotIn("}", entry["prompt"])

    def test_kit_only_filter(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "kit.json")
            run("kit", "--style", "blob-mascot", "--subject", "a bean",
                 "--only", "identity", "--only", "loop", "--out", path)
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            self.assertEqual(set(data["prompts"]), {"identity", "loop"})

    def test_kit_keeps_each_template_designed_ratio(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "kit.json")
            run("kit", "--style", "blob-mascot", "--subject", "a bean", "--out", path)
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            designed = {d["id"]: d["ratio"] for d in bp.load_deliverables()["deliverables"]}
            self.assertEqual(
                {k: v["ratio"] for k, v in data["prompts"].items()}, designed
            )
            self.assertEqual(designed["banner"], "21:9")
            self.assertEqual(designed["turnaround"], "16:9")

    def test_kit_ratio_flag_overrides_all(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "kit.json")
            run("kit", "--style", "blob-mascot", "--subject", "a bean",
                "--ratio", "9:16", "--out", path)
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            for entry in data["prompts"].values():
                self.assertEqual(entry["ratio"], "9:16")

    def test_build_defaults_to_square(self):
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            bp.main(["build", "--style", "blob-mascot", "--subject", "a bean"])
        self.assertIn("1:1", buf.getvalue())

    def test_kit_expression_subset_changes_grid(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "kit.json")
            run("kit", "--style", "blob-mascot", "--subject", "a bean",
                 "--expressions", "happy", "--expressions", "sad",
                 "--only", "expression-sheet", "--out", path)
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            prompt = data["prompts"]["expression-sheet"]["prompt"]
            self.assertIn("Two", prompt)
            self.assertIn("2x1", prompt)
            self.assertNotIn("confused", prompt)
            self.assertNotIn("with,", prompt)


class NodeParity(unittest.TestCase):
    """The Node assembler must produce byte-identical output."""

    @classmethod
    def setUpClass(cls):
        node = shutil_which("node")
        if not node:
            raise unittest.SkipTest("node not installed")
        cls.node = node

    def _py(self, *args) -> str:
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            bp.main(list(args))
        return _lf(buf.getvalue())

    def _js(self, *args) -> str:
        proc = subprocess.run(
            [self.node, os.path.join(ROOT, "scripts", "build_prompt.mjs"), *args],
            capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
        )
        return _lf(proc.stdout)

    def test_styles_list_parity(self):
        self.assertEqual(self._py("styles"), self._js("styles"))

    def test_check_parity(self):
        self.assertEqual(self._py("check"), self._js("check"))

    def test_build_parity(self):
        args = ("build", "--style", "anthropomorphic-plant", "--medium", "cel-shading",
                "--subject", "a small round terracotta pot with a happy face",
                "--signature", "three lime-green leaves sprouting from the rim",
                "--palette", "warm terracotta pot, lime green foliage, charcoal outline",
                "--material", "matte unglazed terracotta",
                "--proportion", "1-3", "--expression", "happy", "--ratio", "9:16")
        self.assertEqual(self._py(*args), self._js(*args))

    def test_build_json_parity(self):
        args = ("build", "--style", "felt-wool-plush", "--medium", "watercolor",
                "--subject", "a round grey cat", "--signature", "one red scarf",
                "--palette", "warm grey, red, charcoal outline",
                "--expression", "excited", "--ratio", "1:1", "--format", "json")
        self.assertEqual(self._py(*args), self._js(*args))

    def test_consistency_parity(self):
        args = ("consistency", "--style", "blob-mascot", "--medium", "flat-color-digital",
                "--subject", "a bean-shaped cloud", "--signature", "one red mitten",
                "--palette", "cream, coral, charcoal outline")
        self.assertEqual(self._py(*args), self._js(*args))

    def test_video_parity(self):
        args = ("video", "--type", "image-to-video", "--motion", "a gentle wave",
                "--style", "chibi-q-chibi", "--medium", "cel-shading")
        self.assertEqual(self._py(*args), self._js(*args))


def shutil_which(prog: str) -> str | None:
    from shutil import which
    return which(prog)


if __name__ == "__main__":
    unittest.main(verbosity=2)