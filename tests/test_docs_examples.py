"""Documentation-drift tests.

The docs are the skill's real interface for an agent reading it, so a broken
example is a real defect: it misleads the reader and produces wasted renders.
These tests execute every command that appears in the docs and verify every
flag mentioned exists in the CLI.

Run:  python -m unittest tests.test_docs_examples -v
"""

import io
import contextlib
import os
import re
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import build_prompt as bp  # noqa: E402

DOC_FILES = [
    "README.md",
    "SKILL.md",
    "references/prompt-assembly.md",
    "references/media-layers.md",
    "references/character-consistency.md",
    "references/deliverables.md",
    "references/video-production.md",
    "references/anthropomorphic-playbook.md",
    "references/brand-safety.md",
    "references/naming-and-glossary.md",
    "references/recipes.md",
    "references/troubleshooting.md",
]

# shell constructs that are illustrative rather than directly executable
SHELL_ONLY = re.compile(
    r"(^|\s)(do|done|then|fi|if|while|for|&&|\|\||\{|;|<<|\$\(|`)([;\s]|$)"
)


def _docs_text() -> dict:
    out = {}
    for rel in DOC_FILES:
        path = os.path.join(ROOT, rel)
        with open(path, encoding="utf-8") as fh:
            out[rel] = fh.read()
    return out


def _logical_lines(block: str):
    """Join backslash continuations, strip trailing comments, drop blanks."""
    lines = []
    buf = ""
    for raw in block.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.endswith("\\"):
            buf += line[:-1] + " "
            continue
        buf += line
        lines.append(buf)
        buf = ""
    if buf:
        lines.append(buf)
    out = []
    for line in lines:
        if line.startswith("#"):
            continue
        line = _strip_comment(line)
        if line:
            out.append(line)
    return out


def _strip_comment(cmd: str) -> str:
    """Remove a trailing `# note` that is outside quotes."""
    out, quote = [], None
    for i, ch in enumerate(cmd):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and (i == 0 or cmd[i - 1] in " \t"):
            return "".join(out).strip()
        out.append(ch)
    return "".join(out).strip()


def _runnable(cmd: str, td: str) -> str | None:
    """Rewrite --out targets into a temp dir; reject non-runnable templates."""
    if not cmd.startswith(("python ", "node ")):
        return None
    # placeholders like <id>, <command>, "..." mark a template, not a command
    if re.search(r"[<>{]|\.\.\.", cmd):
        return None
    if SHELL_ONLY.search(cmd):
        return None
    if " -m unittest" in cmd or " --test " in cmd or cmd.endswith(" --test"):
        return None
    return re.sub(r"(--out\s+)(\S+)", lambda m: m.group(1) + os.path.join(td, "out.json"), cmd)


def _bash_blocks(text: str):
    for match in re.finditer(r"```(?:bash|sh|console)\n(.*?)```", text, re.S):
        yield match.group(1)


def _cli_commands(docs: dict) -> list[tuple[str, str]]:
    """Every runnable CLI invocation found in the docs, with its source doc."""
    found = []
    for rel, text in docs.items():
        for block in _bash_blocks(text):
            for line in _logical_lines(block):
                if line.startswith(("python ", "node ")):
                    found.append((rel, line))
        for raw in re.findall(r"`((?:python|node)\s+scripts/[^`]+)`", text):
            line = _strip_comment(raw.replace("\\\n", " ").strip())
            if "\n" not in line and '"' not in line.split("--style")[0]:
                found.append((rel, line))
    return found


class DocumentedCommandsRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = _docs_text()
        cls.commands = _cli_commands(cls.docs)

    def test_docs_actually_contain_commands(self):
        self.assertGreater(len(self.commands), 20,
                           "doc extraction found suspiciously few commands")

    def test_every_documented_command_runs(self):
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        with tempfile.TemporaryDirectory() as td:
            for rel, cmd in self.commands:
                runnable = _runnable(cmd, td)
                if not runnable:
                    continue
                with self.subTest(doc=rel, cmd=cmd[:80]):
                    proc = subprocess.run(
                        runnable, shell=True, cwd=ROOT, env=env,
                        capture_output=True, text=True, encoding="utf-8",
                    )
                    self.assertEqual(
                        proc.returncode, 0,
                        f"{rel}: `{cmd}` failed\n{proc.stderr.strip()}",
                    )
                    self.assertIsNone(
                        re.search(r"\{[a-z_]+\}", proc.stdout),
                        f"{rel}: `{cmd}` emitted an unfilled token",
                    )

    def test_documented_commands_run_under_node_too(self):
        if not _which("node"):
            self.skipTest("node not installed")
        env = dict(os.environ, PYTHONUTF8="1")
        with tempfile.TemporaryDirectory() as td:
            for rel, cmd in self.commands:
                runnable = _runnable(cmd, td)
                # only the dual-runtime CLI has a Node port
                if not runnable or not runnable.startswith("python scripts/build_prompt.py"):
                    continue
                node_cmd = runnable.replace("python ", "node ", 1)
                node_cmd = node_cmd.replace("build_prompt.py", "build_prompt.mjs")
                with self.subTest(doc=rel, cmd=cmd[:80]):
                    proc = subprocess.run(
                        node_cmd, shell=True, cwd=ROOT, env=env,
                        capture_output=True, text=True, encoding="utf-8",
                    )
                    self.assertEqual(
                        proc.returncode, 0,
                        f"{rel}: `{node_cmd}` failed\n{proc.stderr.strip()}",
                    )


class DocumentedFlagsExist(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = _docs_text()
        parser = bp.build_parser()
        known = set()
        stack = [parser]
        while stack:
            p = stack.pop()
            for action in p._actions:
                known.add(action.dest)
                if hasattr(action, "choices") and isinstance(action.choices, dict):
                    stack.extend(
                        v for v in action.choices.values()
                        if hasattr(v, "_actions")
                    )
        cls.known = known

    def test_every_documented_flag_is_real(self):
        unknown = {}
        ignore = {"version", "test", "dry-run", "cref", "sref", "iw"}
        for rel, text in self.docs.items():
            for flag in set(re.findall(r"(?<![\w-])--([a-z][a-z-]*)", text)):
                key = flag.replace("-", "_")
                if key not in self.known and key not in ignore:
                    unknown.setdefault(rel, set()).add(key)
        self.assertEqual(unknown, {},
                         f"documented flags that do not exist: {unknown}")

    def test_documented_ids_exist(self):
        style_ids = {s["id"] for s in bp.load_styles()}
        media_ids = {m["id"] for m in bp.load_media()}
        expr_ids = {e["id"] for e in bp.load_deliverables()["expression_defaults"]}
        loop_ids = {l["id"] for l in bp.load_deliverables()["loop_motions"]}
        cam_ids = {c["id"] for c in bp.load_deliverables()["camera_moves"]}
        lens_ids = {l["id"] for l in bp.load_deliverables()["lens_notes"]}
        ratio_ids = {r["id"] for r in bp.load_deliverables()["aspect_ratios"]}
        prop_ids = {p["id"] for p in bp.load_anatomy()["proportion_presets"]}
        deliverable_ids = {d["id"] for d in bp.load_deliverables()["deliverables"]}
        deliverable_ids |= {p["id"] for p in bp.load_deliverables().get("extra_poses", [])}
        families = {f["id"] for f in bp.load_families()}
        flags = {
            "--style": style_ids, "--medium": media_ids, "--expression": expr_ids,
            "--loop": loop_ids, "--camera": cam_ids, "--lens": lens_ids,
            "--ratio": ratio_ids, "--proportion": prop_ids, "--only": deliverable_ids,
            "--expressions": expr_ids, "--poses": deliverable_ids,
            "--family": families,
        }
        problems = []
        for rel, text in self.docs.items():
            for flag, valid in flags.items():
                for m in re.finditer(re.escape(flag) + r'\s+([a-z0-9][\w:.+-]*)', text):
                    value = m.group(1)
                    if value in ("ID", "<id>", "a", "one", "..."):
                        continue
                    if bp._norm(value) not in {bp._norm(v) for v in valid}:
                        problems.append(f"{rel}: {flag} {value}")
        self.assertEqual(problems, [], f"documented ids that do not exist: {problems}")


class ShowcaseIsComplete(unittest.TestCase):
    """The showcase must cover every style and contain no mechanical artefacts."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import make_showcase
        cls.ms = make_showcase
        cls.style_ids = [s["id"] for s in bp.load_styles()]

    def test_every_style_has_a_showcase_entry(self):
        self.assertEqual(sorted(self.ms.SHOWCASE), sorted(self.style_ids))

    def test_every_showcase_id_resolves(self):
        for style_id, spec in self.ms.SHOWCASE.items():
            with self.subTest(style=style_id):
                self.assertIsNotNone(bp.find_style(style_id))
                self.assertIsNotNone(bp.find_media(spec["medium"]))
                self.assertIsNotNone(bp.find_proportion(spec["proportion"]))
                self.assertIsNotNone(bp.find_expression(spec["expression"]))
                self.assertIsNotNone(bp.find_ratio(spec["ratio"]))
                self.assertIn(style_id, self.ms.SHOWCASE_LOOPS)
                self.assertIsNotNone(bp.find_loop(self.ms.SHOWCASE_LOOPS[style_id]))

    def test_showcase_prompts_are_clean(self):
        for style_id in self.style_ids:
            entry = self.ms.build_prompt_for(style_id)
            for key in ("identity_prompt", "loop_prompt", "negative"):
                text = entry[key]
                with self.subTest(style=style_id, field=key):
                    self.assertTrue(text.strip(), "empty output")
                    self.assertNotIn("{", text)
                    self.assertNotIn("}", text)
                    self.assertNotIn(", ,", text)
                    self.assertNotIn(" with,", text)
                    self.assertLess(len(text.split()), 400,
                                    "implausibly long prompt")
            for key in ("identity_prompt", "loop_prompt"):
                self.assertTrue(entry[key].endswith("."), key)

    def test_showcase_has_no_duplicate_core_clause(self):
        """A style whose id equals the medium id must not emit its core twice."""
        entry = self.ms.build_prompt_for("soft-3d-render")
        self.assertEqual(
            entry["identity_prompt"].count("rounded organic volumes"), 1
        )

    def test_showcase_file_exists_and_is_current(self):
        path = os.path.join(ROOT, "showcase", "ALL-STYLES.md")
        self.assertTrue(os.path.exists(path), "run scripts/make_showcase.py")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for style_id in self.style_ids:
            self.assertIn(f"### {style_id}", text)
        self.assertNotIn("{", text)


class ReferencedFilesExist(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = _docs_text()

    def test_every_referenced_path_exists(self):
        docs = _docs_text()
        missing = []
        for rel, text in docs.items():
            for ref in set(re.findall(r"`((?:data|scripts|tests|references)/[\w./-]+)`", text)):
                if ref.endswith(("/", "*.json")) or "*" in ref:
                    continue
                if not os.path.exists(os.path.join(ROOT, ref)):
                    missing.append(f"{rel} -> {ref}")
        self.assertEqual(missing, [], f"referenced files that do not exist: {missing}")

    def test_every_doc_file_is_linked_from_skill_or_readme(self):
        index = self.docs["SKILL.md"] + self.docs["README.md"]
        orphans = [
            rel for rel in DOC_FILES
            if rel.startswith("references/")
            and os.path.basename(rel) not in index
        ]
        self.assertEqual(orphans, [], f"reference docs not linked anywhere: {orphans}")


class DocumentedCountsAreTrue(unittest.TestCase):
    """The docs state counts. Keep them honest."""

    @classmethod
    def setUpClass(cls):
        cls.docs = _docs_text()
        cls.index = cls.docs["SKILL.md"] + cls.docs["README.md"]

    def test_headline_counts_match_the_data(self):
        styles = len(bp.load_styles())
        families = len(bp.load_families())
        media = len(bp.load_media())
        slots = len(bp.load_anatomy()["slots"])
        deliverables = len(bp.load_deliverables()["deliverables"])
        self.assertIn(f"{styles} named", self.index)
        self.assertIn(f"{families} families", self.index)
        self.assertIn(f"{media} rendering media", self.index)
        self.assertIn(f"{slots}-slot", self.index)
        self.assertIn(f"{deliverables} templates", self.index)

    def test_test_counts_match_reality(self):
        python_count = _count_python_tests()
        self.assertIn(f"{python_count} tests", self.index,
                      f"SKILL.md/README.md must state '{python_count} tests'")
        node_count = _count_node_tests()
        self.assertIn(f"{node_count} tests", self.index,
                      f"SKILL.md/README.md must state '{node_count} tests'")


def _count_python_tests() -> int:
    loader = unittest.TestLoader()
    suite = loader.discover(HERE, pattern="test_*.py")
    return suite.countTestCases()


def _count_node_tests() -> int:
    with open(os.path.join(HERE, "build_prompt.test.mjs"), encoding="utf-8") as fh:
        text = fh.read()
    return len(re.findall(r'^test\(', text, re.M))


def _which(prog: str) -> str | None:
    from shutil import which
    return which(prog)


if __name__ == "__main__":
    unittest.main(verbosity=2)