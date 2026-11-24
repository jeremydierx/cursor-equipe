#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Premier Souffle — édification déterministe du sanctuaire.

Ce script tourne AVANT l'éveil conversationnel. Il crée l'arborescence du
sanctuaire, y copie les gabarits avec les valeurs de configuration substituées,
y copie les capacités et leurs références, et engendre CAPABILITIES.md depuis
le frontmatter des capacités.

Une fois ce script passé, le sanctuaire est autonome : l'agent ne dépend plus
de l'emplacement du bundle de la compétence pour son fonctionnement normal.

Le sanctuaire est global (foyer utilisateur), pas propre à un projet : cet agent
intervient sur plusieurs projets et garde une seule identité continue.

Ceci initialise la mémoire d'exécution de l'agent, pas sa configuration de
construction. La configuration de construction appartient à customize.toml, une
surface distincte à laquelle ce script ne touche jamais.

Usage :
    uv run init-sanctum.py <chemin-competence> [--sanctum CHEMIN] [--project-root CHEMIN]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

SKILL_NAME = "agent-devops"
SANCTUM_ENV = "AGENT_DEVOPS_SANCTUM"

# Fichiers qui restent dans le bundle : utiles au seul Premier Souffle.
SKILL_ONLY_FILES = {"first-breath.md"}
LICENCE_FILES = ("LICENSE", "THIRD_PARTY_NOTICES.md")

TEMPLATE_FILES = [
    "INDEX-template.md",
    "PERSONA-template.md",
    "CREED-template.md",
    "BOND-template.md",
    "MEMORY-template.md",
    "CAPABILITIES-template.md",
]

# Le propriétaire peut enseigner de nouvelles capacités à cet agent.
EVOLVABLE = True

SANCTUM_SUBDIRS = ["capabilities", "sessions", "infra"]


def resolve_sanctum(explicit: str | None = None) -> Path:
    """Emplacement du sanctuaire : argument, puis variable d'environnement, puis foyer."""
    candidate = explicit or os.environ.get(SANCTUM_ENV)
    if candidate:
        return Path(candidate).expanduser().resolve()
    return Path.home() / ".cursor" / "memory" / SKILL_NAME


# Emplacements connus de la config BMad, du plus générique au plus personnel :
# les derniers l'emportent. Le format varie selon les installations.
CONFIG_CANDIDATES = [
    "_bmad/config.yaml",
    "_bmad/core/config.yaml",
    "_bmad/config.toml",
    "_bmad/config.user.yaml",
    "_bmad/config.user.toml",
    "_bmad/custom/config.toml",
    "_bmad/custom/config.user.toml",
]


def parse_config(config_path: Path) -> dict:
    """Lecteur minimal de paires clé/valeur scalaires, en YAML (`clé: valeur`)
    comme en TOML (`clé = "valeur"`). Les sections TOML sont ignorées : seules
    quelques clés plates nous intéressent."""
    config: dict[str, str] = {}
    if not config_path.exists():
        return config
    for line in config_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("["):
            continue
        separator = "=" if "=" in line and (":" not in line or line.index("=") < line.index(":")) else ":"
        if separator not in line:
            continue
        key, _, value = line.partition(separator)
        value = value.strip().strip("'\"")
        if value:
            config[key.strip()] = value
    return config


def parse_frontmatter(file_path: Path) -> dict:
    """Extrait le frontmatter YAML d'un fichier markdown."""
    meta: dict[str, str] = {}
    content = file_path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return meta
    for line in match.group(1).strip().split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip("'\"")
    return meta


def copy_references(source_dir: Path, dest_dir: Path) -> list[str]:
    """Copie les références (hors fichiers réservés au bundle) dans le sanctuaire."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for source_file in sorted(source_dir.iterdir()):
        if source_file.name in SKILL_ONLY_FILES or not source_file.is_file():
            continue
        shutil.copy2(source_file, dest_dir / source_file.name)
        copied.append(source_file.name)
    return copied


def copy_scripts(source_dir: Path, dest_dir: Path) -> list[str]:
    """Copie les scripts utiles aux capacités dans le sanctuaire."""
    if not source_dir.exists():
        return []
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for source_file in sorted(source_dir.iterdir()):
        if source_file.is_file() and source_file.name != "init-sanctum.py":
            shutil.copy2(source_file, dest_dir / source_file.name)
            copied.append(source_file.name)
    return copied


def discover_capabilities(references_dir: Path, sanctum_refs_path: str) -> list[dict]:
    """Repère les capacités : fichiers de références portant `name` et `code`."""
    capabilities = []
    for md_file in sorted(references_dir.glob("*.md")):
        if md_file.name in SKILL_ONLY_FILES:
            continue
        meta = parse_frontmatter(md_file)
        if meta.get("name") and meta.get("code"):
            capabilities.append({
                "name": meta["name"],
                "description": meta.get("description", ""),
                "code": meta["code"],
                "source": f"{sanctum_refs_path}/{md_file.name}",
            })
    return capabilities


def generate_capabilities_md(capabilities: list[dict], evolvable: bool) -> str:
    """Engendre CAPABILITIES.md depuis le frontmatter des capacités."""
    lines = [
        "# Capacités",
        "",
        "## Natives",
        "",
        "| Code | Nom | Description | Source |",
        "|------|-----|-------------|--------|",
    ]
    for cap in capabilities:
        lines.append(
            f"| [{cap['code']}] | {cap['name']} | {cap['description']} | `{cap['source']}` |"
        )

    if evolvable:
        lines.extend([
            "",
            "## Apprises",
            "",
            "_Capacités ajoutées par le propriétaire au fil du temps. Les prompts vivent dans `capabilities/`._",
            "",
            "| Code | Nom | Description | Source | Ajoutée |",
            "|------|-----|-------------|--------|---------|",
            "",
            "## Comment m'apprendre une capacité",
            "",
            "Dis-moi « je veux que tu saches faire X » et on la construit ensemble.",
            "J'écris le prompt, je l'enregistre dans `capabilities/`, je l'inscris ici.",
            "À la session suivante, je saurai faire.",
            "",
            "Les mécanismes vivent dans `references/capability-authoring.md` ; la barre de qualité",
            "complète dans `references/prompt-quality-canon.md`, que je charge au moment d'écrire,",
            "conformément à mon ordre permanent.",
        ])

    lines.extend([
        "",
        "## Outils",
        "",
        "Préfère fabriquer tes propres outils plutôt que dépendre d'outils externes. Un script que tu as écrit et gardé est plus fiable qu'une API tierce. Sers-toi du système de fichiers avec imagination.",
        "",
        "### Outils fournis par le propriétaire",
        "",
        "_Serveurs MCP, API ou services mis à disposition. À documenter ici._",
    ])

    return "\n".join(lines) + "\n"


def substitute_vars(content: str, variables: dict) -> str:
    for key, value in variables.items():
        content = content.replace(f"{{{key}}}", value)
    return content


def main() -> int:
    parser = argparse.ArgumentParser(description="Édification du sanctuaire de l'agent DevOps.")
    parser.add_argument("skill_path", help="Chemin du dossier de la compétence")
    parser.add_argument("--sanctum", help="Chemin explicite du sanctuaire (sinon foyer utilisateur)")
    parser.add_argument("--project-root", help="Projet d'où lire la config BMad, si elle existe")
    parser.add_argument("--json", action="store_true", help="N'imprimer qu'un compte rendu JSON")
    args = parser.parse_args()

    skill_path = Path(args.skill_path).expanduser().resolve()
    if not (skill_path / "SKILL.md").is_file():
        print(f"Chemin de compétence invalide : {skill_path}", file=sys.stderr)
        return 2

    sanctum_path = resolve_sanctum(args.sanctum)
    if sanctum_path.exists():
        if args.json:
            print(json.dumps({"status": "skipped", "sanctum": str(sanctum_path)}))
        else:
            print(f"Le sanctuaire existe déjà en {sanctum_path}")
            print("Cet agent est déjà né. Édification ignorée.")
        return 0

    assets_dir = skill_path / "assets"
    references_dir = skill_path / "references"
    scripts_dir = skill_path / "scripts"

    config: dict[str, str] = {}
    project_root = Path(args.project_root).expanduser().resolve() if args.project_root else Path.cwd()
    for candidate in CONFIG_CANDIDATES:
        config.update(parse_config(project_root / candidate))

    langue = config.get("communication_language") or config.get("document_output_language") or "français"
    variables = {
        "user_name": config.get("user_name", "{{proprietaire}}"),
        "communication_language": {"French": "français", "English": "anglais"}.get(langue, langue),
        "birth_date": date.today().isoformat(),
        "project_root": str(project_root),
        "sanctum_path": str(sanctum_path),
    }

    say = (lambda *a: None) if args.json else print

    sanctum_path.mkdir(parents=True, exist_ok=True)
    for subdir in SANCTUM_SUBDIRS:
        (sanctum_path / subdir).mkdir(exist_ok=True)
    say(f"Sanctuaire créé en {sanctum_path}")

    copied_refs = copy_references(references_dir, sanctum_path / "references")
    say(f"  {len(copied_refs)} références copiées dans references/")
    for name in copied_refs:
        say(f"    - {name}")

    copied_scripts = copy_scripts(scripts_dir, sanctum_path / "scripts")
    if copied_scripts:
        say(f"  {len(copied_scripts)} scripts copiés dans scripts/")

    # Les références et les scripts copiés emportent leurs mentions de licence.
    for name in LICENCE_FILES:
        if (skill_path / name).is_file():
            shutil.copy2(skill_path / name, sanctum_path / name)

    created = []
    for template_name in TEMPLATE_FILES:
        template_path = assets_dir / template_name
        if not template_path.exists():
            say(f"  Avertissement : gabarit {template_name} introuvable, ignoré")
            continue
        output_name = template_name.replace("-template", "").upper()[:-3] + ".md"
        content = substitute_vars(template_path.read_text(encoding="utf-8"), variables)
        (sanctum_path / output_name).write_text(content, encoding="utf-8")
        created.append(output_name)
        say(f"  {output_name} créé")

    capabilities = discover_capabilities(references_dir, "references")
    (sanctum_path / "CAPABILITIES.md").write_text(
        generate_capabilities_md(capabilities, EVOLVABLE), encoding="utf-8"
    )
    say(f"  CAPABILITIES.md créé ({len(capabilities)} capacités natives découvertes)")

    if args.json:
        print(json.dumps({
            "status": "created",
            "sanctum": str(sanctum_path),
            "files": created,
            "references": copied_refs,
            "capabilities": [c["code"] for c in capabilities],
        }))
        return 0

    print()
    print("Édification du Premier Souffle terminée.")
    print(f"Sanctuaire : {sanctum_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
