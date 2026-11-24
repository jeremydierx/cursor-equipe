#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["keyring>=25"]
# ///
"""Garde-fous sur les données sensibles : rien de sensible n'est versionné ni copié chez un client."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import keyring
from keyring.backend import KeyringBackend
from keyring.errors import PasswordDeleteError

PAQUET = Path(__file__).resolve().parent.parent
VALEUR = "valeur-bidon-7f3a"


def charger(nom: str, chemin: Path):
    spec = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def charger_deploy():
    return charger("deploy", PAQUET / "deploy.py")


class FauxTrousseau(KeyringBackend):
    priority = 1

    def __init__(self) -> None:
        super().__init__()
        self.valeurs: dict[tuple[str, str], str] = {}

    def get_password(self, service, username):
        return self.valeurs.get((service, username))

    def set_password(self, service, username, password):
        self.valeurs[(service, username)] = password

    def delete_password(self, service, username):
        if (service, username) not in self.valeurs:
            raise PasswordDeleteError(username)
        del self.valeurs[(service, username)]


class SecretsNonVersionnes(unittest.TestCase):
    def test_aucun_secrets_yaml_versionne(self) -> None:
        try:
            sortie = subprocess.run(
                ["git", "-C", str(PAQUET), "ls-files"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout
        except (OSError, subprocess.CalledProcessError):
            self.skipTest("hors dépôt git : rien à vérifier")
        fautifs = [chemin for chemin in sortie.splitlines() if Path(chemin).name == "secrets.yaml"]
        self.assertEqual(
            fautifs,
            [],
            "secrets.yaml est versionné : le retirer de l'index avec « git rm --cached »",
        )

    def test_gitignore_exclut_secrets_yaml(self) -> None:
        lignes = (PAQUET / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("secrets.yaml", [ligne.strip() for ligne in lignes])


class SecretsNonCopies(unittest.TestCase):
    def test_la_copie_n_emporte_aucun_fichier_sensible(self) -> None:
        deploy = charger_deploy()
        sensibles = ["secrets.yaml", ".env", ".env.local", "cle.pem", "cle.key"]
        with tempfile.TemporaryDirectory() as tmp:
            racine = Path(tmp)
            (racine / "agent.md").write_text("ok", encoding="utf-8")
            for nom in sensibles:
                (racine / nom).write_text("valeur", encoding="utf-8")
            copiés = sorted(f.name for f in deploy.fichiers(racine))
        self.assertEqual(copiés, ["agent.md"])

    def test_un_fichier_sensible_copie_seul_ne_part_pas(self) -> None:
        deploy = charger_deploy()
        with tempfile.TemporaryDirectory() as tmp:
            fichier = Path(tmp) / "secrets.yaml"
            fichier.write_text("valeur", encoding="utf-8")
            self.assertEqual(list(deploy.fichiers(fichier)), [])


class IdentifiantsDansLeTrousseau(unittest.TestCase):
    def setUp(self) -> None:
        self.script = charger("identifiant", PAQUET / "agents" / "devops" / "skill" / "scripts" / "identifiant.py")
        self.faux = FauxTrousseau()
        self.precedent = keyring.get_keyring()
        keyring.set_keyring(self.faux)
        self.accepte = mock.patch.object(self.script, "ACCEPTES", self.script.ACCEPTES | {self.script.nom_complet(self.faux)})

    def tearDown(self) -> None:
        keyring.set_keyring(self.precedent)

    def lancer(self, *args: str) -> tuple[int, str]:
        sortie, erreurs = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(erreurs):
            code = self.script.main(list(args))
        return code, sortie.getvalue() + erreurs.getvalue()

    def test_verifier_dit_present_sans_jamais_afficher_la_valeur(self) -> None:
        self.faux.set_password(self.script.SERVICE, "gitea", VALEUR)
        with self.accepte:
            code, texte = self.lancer("verifier", "gitea")
        self.assertEqual(code, 0)
        self.assertIn("présent", texte)
        self.assertNotIn(VALEUR, texte)

    def test_verifier_un_absent_echoue(self) -> None:
        with self.accepte:
            code, texte = self.lancer("verifier", "gitea")
        self.assertEqual(code, 1)
        self.assertIn("absent", texte)

    def test_un_trousseau_non_reconnu_est_refuse(self) -> None:
        self.faux.set_password(self.script.SERVICE, "gitea", VALEUR)
        code, texte = self.lancer("verifier", "gitea")
        self.assertEqual(code, 2)
        self.assertIn("refusé", texte)
        self.assertNotIn(VALEUR, texte)

    def test_la_saisie_est_refusee_hors_terminal(self) -> None:
        with self.accepte, mock.patch.object(sys, "stdin", io.StringIO(VALEUR + "\n")):
            code, texte = self.lancer("enregistrer", "gitea")
        self.assertEqual(code, 2)
        self.assertEqual(self.faux.valeurs, {})
        self.assertNotIn(VALEUR, texte)

    def test_executer_passe_la_valeur_a_la_seule_commande(self) -> None:
        self.faux.set_password(self.script.SERVICE, "gitea", VALEUR)
        controle = f"import os, sys; sys.exit(0 if os.environ.get('JETON') == {VALEUR!r} else 3)"
        with self.accepte:
            code, texte = self.lancer("executer", "gitea", "--variable", "JETON", "--", sys.executable, "-c", controle)
        self.assertEqual(code, 0, texte)
        self.assertNotIn(VALEUR, texte)
        self.assertNotIn("JETON", os.environ)

    def test_un_nom_hors_convention_est_refuse(self) -> None:
        with self.accepte:
            code, _ = self.lancer("verifier", "../Gitea")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
