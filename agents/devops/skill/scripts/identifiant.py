#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["keyring>=25"]
# ///
"""Identifiants techniques dans le trousseau du système.

Un mot de passe, un jeton ou une clé d'API vit dans le trousseau : Trousseau
d'accès sous macOS, Gestionnaire d'identification sous Windows, Secret Service
sous Linux. Ce script n'en affiche jamais la valeur. Il dit si un identifiant
est présent, le fait saisir par le propriétaire dans son propre terminal, ou le
passe à une commande dans une variable d'environnement qui n'existe que pour
elle.

Tout autre trousseau, dont un stockage en clair, est refusé : rien n'est écrit
ailleurs.

Usage :
    uv run identifiant.py trousseau
    uv run identifiant.py verifier NOM
    uv run identifiant.py enregistrer NOM
    uv run identifiant.py supprimer NOM
    uv run identifiant.py executer NOM --variable VARIABLE -- COMMANDE [ARGUMENTS...]
"""

from __future__ import annotations

import argparse
import getpass
import os
import re
import subprocess
import sys

SERVICE = "cursor-equipe"
ACCEPTES = {
    "keyring.backends.macOS.Keyring",
    "keyring.backends.Windows.WinVaultKeyring",
    "keyring.backends.SecretService.Keyring",
    "keyring.backends.libsecret.Keyring",
    "keyring.backends.kwallet.DBusKeyring",
}
NOM = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
VARIABLE = re.compile(r"^[A-Z_][A-Z0-9_]*$")


class Refus(Exception):
    pass


def nom_complet(backend: object) -> str:
    return f"{type(backend).__module__}.{type(backend).__name__}"


def membres(actif: object) -> list[object]:
    from keyring.backends.chainer import ChainerBackend

    return list(actif.backends) if isinstance(actif, ChainerBackend) else [actif]


def trousseau():
    """Le trousseau actif, s'il n'est fait que de trousseaux du système."""
    import keyring

    actif = keyring.get_keyring()
    noms = [nom_complet(b) for b in membres(actif)]
    if not noms or noms == ["keyring.backends.fail.Keyring"]:
        raise Refus("aucun trousseau du système n'est disponible sur cette session")
    refuses = [n for n in noms if n not in ACCEPTES]
    if refuses:
        raise Refus(f"trousseau refusé : {', '.join(refuses)}")
    return actif


def verifier_nom(nom: str) -> str:
    if not NOM.match(nom):
        raise Refus(f"nom invalide : {nom!r} (minuscules, chiffres, point, tiret, souligné)")
    return nom


def cmd_trousseau(_args) -> int:
    for nom in (nom_complet(b) for b in membres(trousseau())):
        print(f"{nom} : accepté")
    return 0


def cmd_verifier(args) -> int:
    present = trousseau().get_password(SERVICE, verifier_nom(args.nom)) is not None
    print(f"{args.nom} : {'présent' if present else 'absent'}")
    return 0 if present else 1


def cmd_enregistrer(args) -> int:
    nom = verifier_nom(args.nom)
    actif = trousseau()
    if not sys.stdin.isatty():
        raise Refus("la saisie se fait dans un terminal interactif, par le propriétaire lui-même")
    valeur = getpass.getpass(f"Valeur de {nom} (rien ne s'affiche) : ")
    if not valeur:
        raise Refus("valeur vide, rien n'est enregistré")
    if getpass.getpass("Encore une fois : ") != valeur:
        raise Refus("les deux saisies diffèrent, rien n'est enregistré")
    actif.set_password(SERVICE, nom, valeur)
    print(f"{nom} : enregistré dans le trousseau")
    return 0


def cmd_supprimer(args) -> int:
    from keyring.errors import PasswordDeleteError

    try:
        trousseau().delete_password(SERVICE, verifier_nom(args.nom))
    except PasswordDeleteError:
        print(f"{args.nom} : absent, rien à supprimer")
        return 1
    print(f"{args.nom} : supprimé")
    return 0


def cmd_executer(args) -> int:
    nom = verifier_nom(args.nom)
    if not VARIABLE.match(args.variable):
        raise Refus(f"variable invalide : {args.variable!r} (majuscules, chiffres, souligné)")
    if not args.commande:
        raise Refus("aucune commande après --")
    valeur = trousseau().get_password(SERVICE, nom)
    if valeur is None:
        raise Refus(f"{nom} : absent du trousseau")
    try:
        return subprocess.run(args.commande, env={**os.environ, args.variable: valeur}, check=False).returncode
    except OSError as e:
        raise Refus(f"commande impossible à lancer : {type(e).__name__}") from None


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    commande: list[str] = []
    if "--" in argv:
        coupure = argv.index("--")
        argv, commande = argv[:coupure], argv[coupure + 1 :]
    parser = argparse.ArgumentParser(description="Identifiants techniques dans le trousseau du système.")
    commandes = parser.add_subparsers(dest="action", required=True)
    commandes.add_parser("trousseau", help="Afficher le trousseau utilisé et s'il est accepté").set_defaults(f=cmd_trousseau)
    for action, aide, f in (
        ("verifier", "Dire si l'identifiant est présent", cmd_verifier),
        ("enregistrer", "Saisir l'identifiant, au clavier, sans affichage", cmd_enregistrer),
        ("supprimer", "Retirer l'identifiant du trousseau", cmd_supprimer),
    ):
        sous = commandes.add_parser(action, help=aide)
        sous.add_argument("nom")
        sous.set_defaults(f=f)
    executer = commandes.add_parser("executer", help="Lancer une commande avec l'identifiant dans une variable d'environnement")
    executer.add_argument("nom")
    executer.add_argument("--variable", required=True)
    executer.set_defaults(f=cmd_executer)
    args = parser.parse_args(argv)
    args.commande = commande

    from keyring.errors import KeyringError

    try:
        return args.f(args)
    except Refus as e:
        print(f"Refus : {e}", file=sys.stderr)
        return 2
    except KeyringError as e:
        print(f"Trousseau inaccessible : {type(e).__name__}. Est-il déverrouillé ?", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
