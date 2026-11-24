#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Tests de deploy.py — déploiement à neuf de l'équipe dans un faux dossier personnel."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PAQUET = Path(__file__).resolve().parent.parent
DEPLOY = PAQUET / "deploy.py"
SOURCE_DEVOPS = PAQUET / "agents" / "devops" / "skill"
PROPRIETAIRE = "Marie Dupont"
RESTE_VARIABLE = re.compile(r"(?<!\{)\{\{[a-z_]+\}\}(?!\})")
ECHAPPEE = re.compile(r"\\\{\{[a-z_]+\}\}")
_liste = Path(__file__).with_name("traces-interdites.txt")
TRACES_ORIGINE = re.compile(
    "|".join(l for l in _liste.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")),
    re.IGNORECASE,
) if _liste.is_file() else None


def deployer(home: Path, *args: str, script: Path = DEPLOY, proprietaire: str | None = PROPRIETAIRE) -> subprocess.CompletedProcess:
    options = ["--proprietaire", proprietaire] if proprietaire else []
    return subprocess.run(
        [sys.executable, str(script), *options, "--home", str(home), *args],
        capture_output=True, text=True, check=False,
    )


def lancer(script: Path, home: Path, *args: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "HOME": str(home)}
    env.pop("AGENT_DEVOPS_SANCTUM", None)
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, check=False, env=env)


def textes(racine: Path):
    if racine.is_file():
        yield racine, racine.read_text(encoding="utf-8")
        return
    for f in racine.rglob("*"):
        if f.is_file() and "__pycache__" not in f.parts:
            yield f, f.read_text(encoding="utf-8")


def creer_agent_local(cursor: Path, nom: str = "veille") -> Path:
    dossier = cursor / "equipe" / "agents-locaux" / nom
    (dossier / "skill").mkdir(parents=True)
    (dossier / "etabli").mkdir()
    (dossier / "agent.toml").write_text(
        f'competence = "agent-{nom}"\nsous_agent = "equipe-{nom}"\netabli = "{nom}"\n'
        'titre = "Veille"\nfonction = "Veille concurrentielle"\n',
        encoding="utf-8",
    )
    (dossier / "skill" / "SKILL.md").write_text("# Veille de {{proprietaire}}\n\n{{equipe}}## Conventions\n", encoding="utf-8")
    (dossier / "sous-agent.md").write_text(f"---\nname: equipe-{nom}\n---\nVeille de {{{{proprietaire}}}}.\n", encoding="utf-8")
    (dossier / "etabli" / ".gitignore").write_text(".env\n", encoding="utf-8")
    return dossier


class TestDeploiement(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name)
        self.cursor = self.home / ".cursor"
        self.skill = self.cursor / "skills" / "agent-devops"
        self.carte = self.cursor / "agents" / "equipe-devops.md"
        self.etabli = self.cursor / "workspaces" / "devops"
        self.copie = self.cursor / "equipe" / "paquet"

    def tearDown(self):
        self._tmp.cleanup()

    def trace(self) -> dict:
        return json.loads((self.cursor / "equipe-deploiement.json").read_text(encoding="utf-8"))

    def test_apercu_n_ecrit_rien(self):
        r = deployer(self.home, "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("créer", r.stdout)
        self.assertFalse(self.cursor.exists())

    def test_deploiement_installe_competence_carte_etabli_et_paquet_sans_sanctuaire(self):
        r = deployer(self.home)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.skill / "SKILL.md").is_file())
        self.assertTrue((self.skill / "scripts" / "identifiant.py").is_file())
        self.assertTrue(self.carte.is_file())
        self.assertTrue((self.etabli / ".cursor" / "rules" / "agent-devops.mdc").is_file())
        self.assertTrue((self.etabli / ".gitignore").is_file())
        self.assertTrue((self.copie / "deploy.py").is_file())
        self.assertFalse((self.cursor / "memory").exists())
        self.assertEqual(self.trace()["agents"], ["devops"])

    def test_la_copie_du_paquet_n_emporte_ni_git_ni_traces_interdites(self):
        deployer(self.home)
        self.assertFalse((self.copie / ".git").exists())
        self.assertFalse((self.copie / "tests" / "traces-interdites.txt").exists())
        if TRACES_ORIGINE:
            for f, contenu in textes(self.copie):
                if f.name not in {"EQUIPE.md", "README.md", "equipe.toml", "LICENSE"}:
                    self.assertIsNone(TRACES_ORIGINE.search(contenu), f"trace d'origine dans {f}")

    @unittest.skipIf(TRACES_ORIGINE is None, "liste des traces interdites absente (copie installée)")
    def test_rien_ne_trahit_l_origine_dans_ce_qui_est_deploye(self):
        deployer(self.home)
        for racine in (self.skill, self.carte, self.etabli):
            for f, contenu in textes(racine):
                if f.name != "LICENSE":
                    self.assertIsNone(TRACES_ORIGINE.search(contenu), f"trace d'origine dans {f}")

    def test_les_mentions_de_licence_accompagnent_chaque_copie(self):
        deployer(self.home)
        lancer(self.skill / "scripts" / "init-sanctum.py", self.home, str(self.skill), "--json")
        sanctuaire = self.cursor / "memory" / "agent-devops"
        for nom in ("LICENSE", "THIRD_PARTY_NOTICES.md"):
            source = (PAQUET / nom).read_text(encoding="utf-8")
            for racine in (self.copie, self.skill, sanctuaire):
                self.assertEqual((racine / nom).read_text(encoding="utf-8"), source, f"{nom} dans {racine}")
        self.assertIn("BMad Code, LLC", (self.skill / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8"))

    def test_toute_variable_est_rendue_sauf_les_echappees(self):
        deployer(self.home)
        for f, contenu in textes(self.skill):
            source = SOURCE_DEVOPS / f.relative_to(self.skill)
            attendues = len(ECHAPPEE.findall(source.read_text(encoding="utf-8"))) if source.is_file() else 0
            self.assertEqual(len(RESTE_VARIABLE.findall(contenu)), attendues, f"variables dans {f}")
        for racine in (self.carte, self.etabli):
            for f, contenu in textes(racine):
                self.assertIsNone(RESTE_VARIABLE.search(contenu), f"variable non rendue dans {f}")
        self.assertIn(PROPRIETAIRE, self.carte.read_text(encoding="utf-8"))
        self.assertIn(str(self.skill), self.carte.read_text(encoding="utf-8"))

    def test_un_agent_seul_n_a_pas_de_section_equipe(self):
        deployer(self.home)
        self.assertNotIn("## Ton équipe", (self.skill / "SKILL.md").read_text(encoding="utf-8"))

    def test_l_agent_deploye_nait_a_neuf_et_sait_installer_d_autres_agents(self):
        deployer(self.home)
        etat = json.loads(lancer(self.skill / "scripts" / "wake.py", self.home, "--json").stdout)
        self.assertEqual(etat["mode"], "FIRST_BREATH")
        self.assertEqual(etat["sanctum"], str(self.cursor / "memory" / "agent-devops"))

        naissance = lancer(self.skill / "scripts" / "init-sanctum.py", self.home, str(self.skill), "--json")
        self.assertEqual(json.loads(naissance.stdout)["status"], "created", naissance.stderr)
        sanctuaire = self.cursor / "memory" / "agent-devops"
        self.assertIn(PROPRIETAIRE, (sanctuaire / "BOND.md").read_text(encoding="utf-8"))
        self.assertIn("[AG]", (sanctuaire / "CAPABILITIES.md").read_text(encoding="utf-8"))
        capacite = (sanctuaire / "references" / "installation-agents.md").read_text(encoding="utf-8")
        self.assertIn(f"uv run {self.copie / 'deploy.py'}", capacite)
        self.assertIn("`{{proprietaire}}`", capacite)
        self.assertEqual(json.loads(lancer(self.skill / "scripts" / "wake.py", self.home, "--json").stdout)["mode"], "WAKING")

    def test_les_tests_de_la_competence_passent_une_fois_deployee(self):
        deployer(self.home)
        for test in sorted((self.skill / "scripts" / "tests").glob("test-*.py")):
            r = lancer(test, self.home)
            self.assertEqual(r.returncode, 0, f"{test.name}\n{r.stderr}")

    def test_redeploiement_identique_ne_change_rien_et_conserve_l_etabli(self):
        deployer(self.home)
        (self.etabli / "note-du-client.md").write_text("à garder\n", encoding="utf-8")
        r = deployer(self.home)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("inchangé", r.stdout)
        self.assertIn("conservé", r.stdout)
        self.assertEqual((self.etabli / "note-du-client.md").read_text(encoding="utf-8"), "à garder\n")

    def test_les_reglages_de_modele_sont_crees_une_fois_puis_laisses_au_proprietaire(self):
        deployer(self.home)
        reglages = self.cursor / "equipe" / "modeles.toml"
        self.assertIn("[modeles]", reglages.read_text(encoding="utf-8"))
        reglages.write_text('[modeles]\nequipe-devops = "un-modele"\n', encoding="utf-8")
        r = deployer(self.home, "--remplacer", proprietaire=None)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(reglages.read_text(encoding="utf-8"), '[modeles]\nequipe-devops = "un-modele"\n')

    def test_un_sanctuaire_existant_n_est_jamais_touche(self):
        deployer(self.home)
        sanctuaire = self.cursor / "memory" / "agent-devops"
        sanctuaire.mkdir(parents=True)
        for nom in ("CREED.md", "MEMORY.md"):
            (sanctuaire / nom).write_text("mémoire du client\n", encoding="utf-8")
        (self.skill / "SKILL.md").write_text("modifié\n", encoding="utf-8")
        r = deployer(self.home, "--remplacer")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("existant, conservé", r.stdout)
        self.assertEqual((sanctuaire / "MEMORY.md").read_text(encoding="utf-8"), "mémoire du client\n")

    def test_une_competence_modifiee_sur_place_bloque_sans_remplacer(self):
        deployer(self.home)
        (self.skill / "SKILL.md").write_text("modifié\n", encoding="utf-8")
        r = deployer(self.home)
        self.assertEqual(r.returncode, 1)
        self.assertIn("CONFLIT", r.stdout)
        self.assertEqual((self.skill / "SKILL.md").read_text(encoding="utf-8"), "modifié\n")

    def test_les_fichiers_du_finder_ne_sont_pas_des_modifications(self):
        deployer(self.home)
        (self.skill / ".DS_Store").write_bytes(b"\x00")
        (self.skill / "references" / "._first-breath.md").write_bytes(b"\x00")
        r = deployer(self.home, "--dry-run", proprietaire=None)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("CONFLIT", r.stdout)

    def test_remplacer_sauvegarde_puis_restaure_la_version_du_paquet(self):
        deployer(self.home)
        (self.skill / "SKILL.md").write_text("modifié\n", encoding="utf-8")
        r = deployer(self.home, "--remplacer")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotEqual((self.skill / "SKILL.md").read_text(encoding="utf-8"), "modifié\n")
        copies = list((self.cursor / "equipe-sauvegardes").glob("*/skills/agent-devops/SKILL.md"))
        self.assertEqual(len(copies), 1)
        self.assertEqual(copies[0].read_text(encoding="utf-8"), "modifié\n")

    def test_ajouter_un_agent_depuis_la_copie_installee_met_l_equipe_a_jour(self):
        deployer(self.home)
        creer_agent_local(self.cursor)
        r = deployer(self.home, "--agents", "veille", script=self.copie / "deploy.py", proprietaire=None)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("mettre à jour", r.stdout)
        self.assertEqual(self.trace()["agents"], ["devops", "veille"])
        section = (self.skill / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## Ton équipe", section)
        self.assertIn("`equipe-veille`", section)
        self.assertIn(f"`{self.cursor}/equipe/modeles.toml`", section)
        self.assertIn("`equipe-devops`", (self.cursor / "skills" / "agent-veille" / "SKILL.md").read_text(encoding="utf-8"))
        self.assertIn(PROPRIETAIRE, (self.cursor / "agents" / "equipe-veille.md").read_text(encoding="utf-8"))
        self.assertTrue((self.cursor / "workspaces" / "veille" / ".gitignore").is_file())
        self.assertEqual(len(list((self.cursor / "equipe-sauvegardes").glob("*/skills/agent-devops/SKILL.md"))), 1)

    def test_les_agents_locaux_survivent_a_une_mise_a_jour_du_paquet(self):
        deployer(self.home)
        local = creer_agent_local(self.cursor)
        (self.copie / "EQUIPE.md").write_text("ancienne version\n", encoding="utf-8")
        trace = self.trace()
        trace["empreintes"].pop(str(self.copie))
        (self.cursor / "equipe-deploiement.json").write_text(json.dumps(trace), encoding="utf-8")
        r = deployer(self.home, "--remplacer")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((local / "agent.toml").is_file())
        self.assertNotEqual((self.copie / "EQUIPE.md").read_text(encoding="utf-8"), "ancienne version\n")

    def test_ajouter_un_agent_bloque_si_un_collegue_a_ete_modifie_sur_place(self):
        deployer(self.home)
        creer_agent_local(self.cursor)
        (self.skill / "SKILL.md").write_text("modifié\n", encoding="utf-8")
        r = deployer(self.home, "--agents", "veille", proprietaire=None)
        self.assertEqual(r.returncode, 1)
        self.assertIn("CONFLIT", r.stdout)
        self.assertFalse((self.cursor / "skills" / "agent-veille").exists())

    def test_un_seul_proprietaire_par_dossier_cursor(self):
        deployer(self.home)
        r = deployer(self.home, proprietaire="Paul Martin")
        self.assertEqual(r.returncode, 2)
        self.assertIn(PROPRIETAIRE, r.stderr)

    def test_premier_deploiement_sans_proprietaire_refuse(self):
        r = deployer(self.home, proprietaire=None)
        self.assertEqual(r.returncode, 2)
        self.assertFalse(self.cursor.exists())

    def test_agent_inconnu_refuse(self):
        r = deployer(self.home, "--agents", "devops,comptable")
        self.assertEqual(r.returncode, 2)
        self.assertIn("comptable", r.stderr)
        self.assertFalse(self.cursor.exists())


class TestSectionEquipe(unittest.TestCase):
    def test_plusieurs_agents_ont_leur_tableau(self):
        spec = importlib.util.spec_from_file_location("deploy", DEPLOY)
        deploy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(deploy)
        choisis = {
            "devops": {"titre": "DevOps", "fonction": "Serveurs", "etabli": "devops", "sous_agent": "equipe-devops"},
            "juridique": {"titre": "Juridique", "fonction": "Contrats", "etabli": "juridique", "sous_agent": "equipe-juridique"},
        }
        variables = {"proprietaire": PROPRIETAIRE, "societe": "Acme", "societe_suffixe": " et Acme", "cursor_home": "/x/.cursor"}
        section = deploy.section_equipe(choisis, variables, Path("/x/.cursor"))
        self.assertIn("## Ton équipe", section)
        self.assertIn("`equipe-juridique`", section)
        self.assertIn("`/x/.cursor/workspaces/devops`", section)
        self.assertIn(f"{PROPRIETAIRE} et Acme", section)
        self.assertIsNone(RESTE_VARIABLE.search(section))


if __name__ == "__main__":
    unittest.main()
