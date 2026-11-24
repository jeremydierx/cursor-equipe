#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Tests de wake.py — routage du mode et chargement du sanctuaire."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

WAKE = Path(__file__).resolve().parent.parent / "wake.py"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(WAKE), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def build_sanctum(root: Path) -> Path:
    sanctum = root / "sanctum"
    sanctum.mkdir()
    (sanctum / "CREED.md").write_text("# Creed\nRéversible ou rien.\n", encoding="utf-8")
    (sanctum / "MEMORY.md").write_text("# Mémoire\nvide\n", encoding="utf-8")
    (sanctum / "PERSONA.md").write_text("# Persona\nNom : Test\n", encoding="utf-8")
    return sanctum


class TestWake(unittest.TestCase):
    def test_sans_sanctuaire_route_vers_premier_souffle(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run("--sanctum", str(Path(tmp) / "absent"))
            self.assertEqual(result.returncode, 0)
            self.assertIn("MODE: FIRST_BREATH", result.stdout)
            self.assertIn("first-breath.md", result.stdout)

    def test_sanctuaire_incomplet_route_vers_premier_souffle(self):
        with tempfile.TemporaryDirectory() as tmp:
            sanctum = Path(tmp) / "sanctum"
            sanctum.mkdir()
            (sanctum / "CREED.md").write_text("# Creed\n", encoding="utf-8")
            result = run("--sanctum", str(sanctum))
            self.assertIn("MODE: FIRST_BREATH", result.stdout)

    def test_sanctuaire_complet_imprime_identite(self):
        with tempfile.TemporaryDirectory() as tmp:
            sanctum = build_sanctum(Path(tmp))
            result = run("--sanctum", str(sanctum))
            self.assertEqual(result.returncode, 0)
            self.assertIn("MODE: WAKING", result.stdout)
            self.assertIn("Réversible ou rien.", result.stdout)
            self.assertIn("Nom : Test", result.stdout)

    def test_fichier_manquant_signale_sans_planter(self):
        with tempfile.TemporaryDirectory() as tmp:
            sanctum = build_sanctum(Path(tmp))
            result = run("--sanctum", str(sanctum))
            self.assertEqual(result.returncode, 0)
            self.assertIn("(absent : BOND.md)", result.stdout)

    def test_json_donne_le_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            sanctum = build_sanctum(Path(tmp))
            result = run("--sanctum", str(sanctum), "--json")
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode"], "WAKING")
            self.assertEqual(payload["sanctum"], str(sanctum))

    def test_variable_environnement_prise_en_compte(self):
        with tempfile.TemporaryDirectory() as tmp:
            sanctum = build_sanctum(Path(tmp))
            result = subprocess.run(
                [sys.executable, str(WAKE), "--json"],
                capture_output=True,
                text=True,
                check=False,
                env={"PATH": "/usr/bin:/bin", "AGENT_DEVOPS_SANCTUM": str(sanctum)},
            )
            self.assertEqual(json.loads(result.stdout)["mode"], "WAKING")


if __name__ == "__main__":
    unittest.main()
