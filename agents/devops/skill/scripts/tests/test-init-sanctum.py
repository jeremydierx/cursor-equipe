#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Tests de init-sanctum.py — édification déterministe du sanctuaire."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent.parent
INIT = SKILL_ROOT / "scripts" / "init-sanctum.py"

CODES_ATTENDUS = {"RE", "DP", "IN", "RS", "RB", "EX", "AG"}


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(INIT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


class TestInitSanctum(unittest.TestCase):
    def test_chemin_de_competence_invalide_sort_en_erreur(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run(tmp, "--sanctum", str(Path(tmp) / "sanctum"))
            self.assertEqual(result.returncode, 2)

    def test_edification_cree_la_structure_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            sanctum = Path(tmp) / "sanctum"
            result = run(str(SKILL_ROOT), "--sanctum", str(sanctum), "--json")
            self.assertEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "created")

            for nom in ("INDEX.md", "PERSONA.md", "CREED.md", "BOND.md", "MEMORY.md", "CAPABILITIES.md"):
                self.assertTrue((sanctum / nom).is_file(), f"{nom} manquant")
            for dossier in ("capabilities", "sessions", "infra", "references"):
                self.assertTrue((sanctum / dossier).is_dir(), f"{dossier}/ manquant")

    def test_les_six_capacites_sont_inscrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            sanctum = Path(tmp) / "sanctum"
            payload = json.loads(run(str(SKILL_ROOT), "--sanctum", str(sanctum), "--json").stdout)
            self.assertEqual(set(payload["capabilities"]), CODES_ATTENDUS)
            contenu = (sanctum / "CAPABILITIES.md").read_text(encoding="utf-8")
            for code in CODES_ATTENDUS:
                self.assertIn(f"[{code}]", contenu)

    def test_premier_souffle_reste_dans_le_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            sanctum = Path(tmp) / "sanctum"
            run(str(SKILL_ROOT), "--sanctum", str(sanctum))
            self.assertFalse((sanctum / "references" / "first-breath.md").exists())
            self.assertTrue((sanctum / "references" / "deploiement.md").is_file())
            self.assertTrue((sanctum / "references" / "prompt-quality-canon.md").is_file())

    def test_aucune_graine_de_gabarit_ne_subsiste(self):
        """Les jetons substitués par le script ne doivent plus apparaître."""
        with tempfile.TemporaryDirectory() as tmp:
            sanctum = Path(tmp) / "sanctum"
            run(str(SKILL_ROOT), "--sanctum", str(sanctum))
            for nom in ("PERSONA.md", "BOND.md", "CREED.md"):
                contenu = (sanctum / nom).read_text(encoding="utf-8")
                for jeton in ("{birth_date}", "{user_name}", "{sanctum_path}", "{communication_language}"):
                    self.assertNotIn(jeton, contenu, f"{jeton} non substitué dans {nom}")

    def test_deuxieme_passage_est_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            sanctum = Path(tmp) / "sanctum"
            run(str(SKILL_ROOT), "--sanctum", str(sanctum))
            (sanctum / "MEMORY.md").write_text("# Mémoire\nintervention du 12 mars\n", encoding="utf-8")

            result = run(str(SKILL_ROOT), "--sanctum", str(sanctum), "--json")
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["status"], "skipped")
            self.assertIn("intervention du 12 mars", (sanctum / "MEMORY.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
