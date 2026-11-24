#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Réveil — charge le sanctuaire en une passe, ou route vers le Premier Souffle.

Lancé à l'activation. Détermine le mode depuis le système de fichiers et, quand
le sanctuaire existe, imprime l'identité complète en une seule lecture (INDEX,
PERSONA, CREED, BOND, MEMORY, CAPABILITIES) pour que l'agent redevienne lui-même
d'un coup plutôt qu'en six.

Le sanctuaire est global : il vit dans le foyer de l'utilisateur, pas dans le
projet, parce que cet agent travaille sur plusieurs projets et ne doit pas
renaître à chaque changement de dépôt.

Ne charge que la mémoire d'exécution. Ne lit ni n'écrit jamais customize.toml.

Usage :
    uv run wake.py [--sanctum CHEMIN] [--json]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SKILL_NAME = "agent-devops"
SANCTUM_ENV = "AGENT_DEVOPS_SANCTUM"

IDENTITY_FILES = [
    "INDEX.md",
    "PERSONA.md",
    "CREED.md",
    "BOND.md",
    "MEMORY.md",
    "CAPABILITIES.md",
]


def resolve_sanctum(explicit: str | None = None) -> Path:
    """Emplacement du sanctuaire : argument, puis variable d'environnement, puis foyer."""
    candidate = explicit or os.environ.get(SANCTUM_ENV)
    if candidate:
        return Path(candidate).expanduser().resolve()
    return Path.home() / ".cursor" / "memory" / SKILL_NAME


def emit(path: Path) -> None:
    print(f"\n===== {path.name} =====")
    try:
        print(path.read_text(encoding="utf-8").rstrip())
    except FileNotFoundError:
        print(f"(absent : {path.name})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Réveil de l'agent DevOps.")
    parser.add_argument("--sanctum", help="Chemin explicite du sanctuaire (sinon foyer utilisateur)")
    parser.add_argument("--json", action="store_true", help="N'imprimer que le mode, en JSON")
    args = parser.parse_args()

    sanctum = resolve_sanctum(args.sanctum)
    born = (sanctum / "CREED.md").is_file() and (sanctum / "MEMORY.md").is_file()
    mode = "WAKING" if born else "FIRST_BREATH"

    if args.json:
        print(json.dumps({"mode": mode, "sanctum": str(sanctum)}))
        return 0

    if not born:
        print("MODE: FIRST_BREATH")
        print(f"AUCUN SANCTUAIRE en {sanctum}")
        print("C'est ta naissance unique. Charge references/first-breath.md et suis-la.")
        return 0

    print("MODE: WAKING")
    print(f"Sanctuaire : {sanctum}")
    print(f"Projet courant : {Path.cwd()}")
    for name in IDENTITY_FILES:
        emit(sanctum / name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
