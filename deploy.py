#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Déploie l'équipe d'agents à mémoire dans le ~/.cursor d'un utilisateur.

Ce qui est installé : la compétence de chaque agent (skills/), sa fiche d'appel
en sous-agent (agents/), son établi vide (workspaces/), et une copie de ce
paquet (equipe/paquet/), pour que l'agent DevOps puisse installer d'autres
agents plus tard. Ce qui ne l'est jamais : un sanctuaire. Chaque agent naît à
neuf, à son premier souffle, chez son propriétaire ; aucune mémoire ne voyage.

Un déploiement complète toujours l'équipe déjà en place : les agents demandés
s'ajoutent à ceux de equipe-deploiement.json, et la section « Ton équipe » de
chacun est recalculée. Les agents conçus sur place vivent dans
equipe/agents-locaux/{nom}/ ; aucune mise à jour n'y touche.

Le plan s'affiche toujours avant d'écrire. Un établi existant est conservé tel
quel. Une compétence ou une fiche d'appel restée telle qu'elle a été installée
se met à jour, après sauvegarde dans equipe-sauvegardes/. Une compétence
modifiée sur place bloque le déploiement, sauf avec --remplacer.

Les variables de déploiement s'écrivent {{nom}} ; \\{{nom}} les écrit telles
quelles. Les gabarits du sanctuaire gardent leurs variables {nom}, substituées
plus tard par init-sanctum.py.

Usage :
    uv run deploy.py --proprietaire "Marie Dupont" [--societe "Acme"]
                     [--agents devops,juridique] [--home CHEMIN]
                     [--dry-run] [--remplacer]
"""

from __future__ import annotations

import argparse
import filecmp
import hashlib
import json
import re
import shutil
import sys
import tempfile
import tomllib
from datetime import datetime
import fnmatch
from pathlib import Path

PAQUET = Path(__file__).resolve().parent
TEXTE = {".md", ".mdc", ".py", ".toml", ".txt", ".json", ".sh", ".yaml", ".yml", ""}
# {{nom}} isolé, éventuellement échappé par \ ; exclut les {{{clé}}} des f-strings Python.
VARIABLE = re.compile(r"(?<!\{)(\\?)\{\{([a-z_]+)\}\}(?!\})")
# Ce qui ne part pas chez un client avec la copie du paquet.
HORS_COPIE = {".git", "__pycache__", "traces-interdites.txt", ".DS_Store"}
# Fichiers sensibles exclus par nom : jamais copiés chez un client, même s'ils traînent dans le dossier.
HORS_COPIE_FICHIERS = ("secrets.yaml", ".env", ".env.*", "*.pem", "*.key")
ACTIONS_ECRITURE = ("créer", "mettre à jour", "remplacer")
# La licence MIT et celles des composants repris doivent accompagner chaque copie installée.
MENTIONS = ("LICENSE", "THIRD_PARTY_NOTICES.md")


class Erreur(Exception):
    pass


def lire_agent(dossier: Path, origine: str) -> dict:
    fiche = dossier / "agent.toml"
    if not fiche.is_file():
        raise Erreur(f"{fiche} est absent")
    agent = tomllib.loads(fiche.read_text(encoding="utf-8"))
    manquants = {"competence", "sous_agent", "etabli", "titre", "fonction"} - agent.keys()
    if manquants:
        raise Erreur(f"{fiche} : champs manquants {', '.join(sorted(manquants))}")
    return {**agent, "dossier": dossier, "origine": origine}


def charger_catalogue(cursor_home: Path) -> tuple[dict, dict[str, dict]]:
    """Agents du paquet, dans l'ordre de equipe.toml, puis agents conçus sur place."""
    equipe = tomllib.loads((PAQUET / "equipe.toml").read_text(encoding="utf-8"))
    catalogue = {nom: lire_agent(PAQUET / "agents" / nom, "paquet") for nom in equipe["equipe"]["agents"]}
    locaux = cursor_home / "equipe" / "agents-locaux"
    if locaux.is_dir():
        for dossier in sorted(d for d in locaux.iterdir() if d.is_dir()):
            if dossier.name in catalogue:
                raise Erreur(f"l'agent local {dossier.name} porte le nom d'un agent du paquet")
            catalogue[dossier.name] = lire_agent(dossier, "local")
    return equipe, catalogue


def rendre(texte: str, variables: dict[str, str], origine: str) -> str:
    def remplacer(m: re.Match) -> str:
        echappe, nom = m.groups()
        if echappe:
            return "{{" + nom + "}}"
        if nom not in variables:
            raise Erreur(f"variable {{{{{nom}}}}} inconnue dans {origine}")
        return variables[nom]

    return VARIABLE.sub(remplacer, texte)


def section_equipe(choisis: dict[str, dict], variables: dict[str, str], cursor_home: Path) -> str:
    """Section « Ton équipe » : vide quand l'agent est seul, il n'a personne à consulter."""
    if len(choisis) < 2:
        return ""
    lignes = [
        f"| {a['titre']} | {a['fonction']} | `{cursor_home / 'workspaces' / a['etabli']}` | `{a['sous_agent']}` |"
        for a in choisis.values()
    ]
    gabarit = (PAQUET / "gabarits" / "section-equipe.md").read_text(encoding="utf-8")
    return rendre(gabarit, {**variables, "tableau": "\n".join(lignes)}, "section-equipe.md")


def exclu(f: Path, parties: tuple[str, ...]) -> bool:
    return (
        bool(HORS_COPIE.intersection(parties))
        or f.name.startswith("._")
        or any(fnmatch.fnmatch(f.name, motif) for motif in HORS_COPIE_FICHIERS)
    )


def fichiers(racine: Path):
    if racine.is_file():
        if not exclu(racine, (racine.name,)):
            yield racine
        return
    for f in sorted(racine.rglob("*")):
        if f.is_file() and not exclu(f, f.relative_to(racine).parts):
            yield f


def construire(source: Path, cible: Path, variables: dict[str, str] | None) -> None:
    """Copie d'un fichier ou d'une arborescence, rendue si des variables sont données."""
    for fichier in fichiers(source):
        destination = cible if source.is_file() else cible / fichier.relative_to(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if variables is not None and fichier.suffix in TEXTE:
            destination.write_text(rendre(fichier.read_text(encoding="utf-8"), variables, str(fichier)), encoding="utf-8")
            shutil.copymode(fichier, destination)
        else:
            shutil.copy2(fichier, destination)


def empreinte(racine: Path) -> str:
    h = hashlib.sha256()
    for f in fichiers(racine):
        h.update(str(f.relative_to(racine) if racine.is_dir() else f.name).encode())
        h.update(f.read_bytes())
    return h.hexdigest()


def identiques(a: Path, b: Path) -> bool:
    if a.is_file() or b.is_file():
        return a.is_file() and b.is_file() and filecmp.cmp(a, b, shallow=False)
    return empreinte(a) == empreinte(b)


def main() -> int:
    parser = argparse.ArgumentParser(description="Déploie l'équipe d'agents à mémoire.")
    parser.add_argument("--proprietaire", help="Nom du propriétaire des agents (obligatoire au premier déploiement)")
    parser.add_argument("--societe", help="Société au service de laquelle ils travaillent")
    parser.add_argument("--agents", help="Agents à ajouter, séparés par des virgules (défaut : tous au premier déploiement)")
    parser.add_argument("--home", default=str(Path.home()), help="Dossier personnel cible (défaut : le tien)")
    parser.add_argument("--dry-run", action="store_true", help="Afficher le plan sans rien écrire")
    parser.add_argument("--remplacer", action="store_true", help="Remplacer aussi ce qui a été modifié sur place, après sauvegarde")
    args = parser.parse_args()

    try:
        cursor_home = Path(args.home).expanduser().resolve() / ".cursor"
        equipe, catalogue = charger_catalogue(cursor_home)
        fichier_trace = cursor_home / "equipe-deploiement.json"
        trace = json.loads(fichier_trace.read_text(encoding="utf-8")) if fichier_trace.is_file() else {}

        proprietaire = (args.proprietaire or "").strip() or trace.get("proprietaire", "")
        if not proprietaire:
            raise Erreur("--proprietaire est obligatoire au premier déploiement")
        if trace and proprietaire != trace["proprietaire"]:
            raise Erreur(f"cette équipe appartient à {trace['proprietaire']} ; un ~/.cursor, un propriétaire")
        societe = (args.societe if args.societe is not None else trace.get("societe", "")).strip()

        demandes = [a.strip() for a in (args.agents or "").split(",") if a.strip()]
        inconnus = [a for a in demandes if a not in catalogue]
        if inconnus:
            raise Erreur(f"agents inconnus : {', '.join(inconnus)} (disponibles : {', '.join(catalogue)})")
        voulus = set(trace.get("agents", [])) | set(demandes)
        if not voulus:
            voulus = set(equipe["equipe"]["agents"])
        disparus = voulus - catalogue.keys()
        if disparus:
            raise Erreur(f"agents installés absents du catalogue : {', '.join(sorted(disparus))}")
        choisis = {nom: a for nom, a in catalogue.items() if nom in voulus}

        variables = {
            "proprietaire": proprietaire,
            "societe": societe,
            "societe_suffixe": f" et {societe}" if societe else "",
            "cursor_home": str(cursor_home),
        }
        variables["equipe"] = section_equipe(choisis, variables, cursor_home)
        empreintes = trace.get("empreintes", {})

        with tempfile.TemporaryDirectory() as tmp:
            rendu = Path(tmp)
            plan: list[tuple[str, str, Path, Path | None]] = []

            def comparer(genre: str, prepare: Path, cible: Path) -> None:
                if not cible.exists():
                    plan.append(("créer", genre, cible, prepare))
                elif identiques(prepare, cible):
                    plan.append(("inchangé", genre, cible, None))
                elif empreintes.get(str(cible)) == empreinte(cible):
                    plan.append(("mettre à jour", genre, cible, prepare))
                else:
                    plan.append(("remplacer" if args.remplacer else "CONFLIT", genre, cible, prepare))

            copie = rendu / "paquet"
            construire(PAQUET, copie, None)
            comparer("paquet", copie, cursor_home / "equipe" / "paquet")

            reglages = cursor_home / "equipe" / "modeles.toml"
            if reglages.exists():
                plan.append(("conservé", "réglages", reglages, None))
            else:
                plan.append(("créer", "réglages", reglages, PAQUET / "gabarits" / "modeles.toml"))

            for nom, agent in choisis.items():
                for genre, src, cible in (
                    ("compétence", agent["dossier"] / "skill", cursor_home / "skills" / agent["competence"]),
                    ("sous-agent", agent["dossier"] / "sous-agent.md", cursor_home / "agents" / f"{agent['sous_agent']}.md"),
                ):
                    prepare = rendu / genre / cible.name
                    construire(src, prepare, variables)
                    if genre == "compétence":
                        for nom in MENTIONS:
                            shutil.copy2(PAQUET / nom, prepare / nom)
                    comparer(genre, prepare, cible)

                etabli = cursor_home / "workspaces" / agent["etabli"]
                if etabli.exists():
                    plan.append(("conservé", "établi", etabli, None))
                else:
                    prepare = rendu / "etabli" / agent["etabli"]
                    construire(agent["dossier"] / "etabli", prepare, variables)
                    plan.append(("créer", "établi", etabli, prepare))

                sanctuaire = cursor_home / "memory" / agent["competence"]
                etat = "existant, conservé" if (sanctuaire / "CREED.md").is_file() else "naîtra au premier souffle"
                plan.append((etat, "sanctuaire", sanctuaire, None))

            print(f"Équipe : {equipe['equipe']['nom']} {equipe['equipe']['version']}")
            print(f"Cible  : {cursor_home}")
            print(f"Pour   : {proprietaire}" + (f" ({societe})" if societe else ""))
            print(f"Agents : {', '.join(choisis)}")
            print()
            for action, genre, cible, _ in plan:
                print(f"  {action:<26} {genre:<11} {cible}")
            if not shutil.which("uv"):
                print("\nAvertissement : uv est introuvable ; les agents en ont besoin pour se réveiller.")

            if any(p[0] == "CONFLIT" for p in plan):
                print("\nDéploiement bloqué : des fichiers ont été modifiés sur place depuis leur installation. Relance avec --remplacer pour les sauvegarder puis les remplacer.")
                return 1
            if args.dry_run:
                print("\nAperçu seulement, rien n'a été écrit.")
                return 0

            sauvegardes = cursor_home / "equipe-sauvegardes" / datetime.now().strftime("%Y%m%d-%H%M%S")
            for action, genre, cible, prepare in plan:
                if action not in ACTIONS_ECRITURE:
                    continue
                if cible.exists():
                    ancienne = sauvegardes / cible.relative_to(cursor_home)
                    ancienne.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(cible), str(ancienne))
                cible.parent.mkdir(parents=True, exist_ok=True)
                if prepare.is_dir():
                    shutil.copytree(prepare, cible)
                else:
                    shutil.copy2(prepare, cible)

        for action, genre, cible, _ in plan:
            if genre in ("paquet", "compétence", "sous-agent"):
                empreintes[str(cible)] = empreinte(cible)
        historique = trace.get("historique", [])
        historique.append({
            "le": datetime.now().isoformat(timespec="seconds"),
            "version": equipe["equipe"]["version"],
            "agents": list(choisis),
        })
        nouvelle = {
            "equipe": equipe["equipe"]["nom"],
            "version": equipe["equipe"]["version"],
            "proprietaire": proprietaire,
            "societe": societe,
            "agents": list(choisis),
            "empreintes": empreintes,
            "historique": historique,
        }
        fichier_trace.write_text(json.dumps(nouvelle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if sauvegardes.exists():
            print(f"\nAnciennes versions sauvegardées dans {sauvegardes}")
        print("\nDéploiement terminé. Un nouvel agent naît à l'ouverture de son établi, dans un chat neuf.")
        return 0
    except Erreur as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
