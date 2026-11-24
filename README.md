# Installer l'équipe d'agents sur son ordinateur

Ce tutoriel installe une équipe d'agents Cursor à mémoire dans votre dossier personnel. Comptez une dizaine de minutes. À la fin, l'agent DevOps vous attend dans Cursor : il se présente, fait votre connaissance, puis se souvient de vous d'une conversation à l'autre.

Les agents arrivent neufs. Ils ne contiennent aucune mémoire, aucun client, aucune donnée de qui que ce soit d'autre. Ce qu'ils apprendront restera sur votre machine.

Pour le détail technique du paquet, voir [EQUIPE.md](EQUIPE.md).

## 1. Vérifier les prérequis

Il vous faut trois outils.

**Cursor**, installé et connecté à votre compte. Pour que plusieurs agents puissent se consulter entre eux, votre abonnement doit autoriser les sous-agents ; avec un seul agent, ce n'est pas nécessaire.

**git**, pour récupérer le paquet :

```sh
git --version
```

Sur Mac, si `git` est absent, cette commande propose d'installer les outils de développement d'Apple ; acceptez, ou lancez `xcode-select --install`.

**uv**, qui exécute les scripts des agents. C'est lui qui les réveille à chaque conversation :

```sh
uv --version
```

Si `uv` est absent, installez-le, puis ouvrez un nouveau terminal :

```sh
# Linux et macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# ou, sur Mac avec Homebrew
brew install uv
```

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 2. Récupérer le paquet

Clonez le dépôt dans le dossier de votre choix, hors de `~/.cursor` :

```sh
git clone https://github.com/jeremydierx/cursor-equipe.git
cd cursor-equipe
```

Le dépôt est public : aucun compte n'est nécessaire. Sans `git`, téléchargez l'archive depuis la page du dépôt (bouton Code, puis Download ZIP), décompressez-la et utilisez-la de la même façon ; les mises à jour se feront alors à la main.

Gardez ce dossier : il servira aux mises à jour.

## 3. Prévisualiser l'installation

Lancez le déployeur avec votre nom et, si vous le souhaitez, votre société. L'option `--dry-run` affiche ce qui serait fait sans rien écrire :

```sh
uv run deploy.py --proprietaire "Marie Dupont" --societe "Acme" --dry-run
```

Vous obtenez un plan de ce type :

```text
Équipe : Équipe d'agents à mémoire Code Alchimie 0.2.0
Cible  : /home/marie/.cursor
Pour   : Marie Dupont (Acme)
Agents : devops

  créer                      paquet      /home/marie/.cursor/equipe/paquet
  créer                      compétence  /home/marie/.cursor/skills/agent-devops
  créer                      sous-agent  /home/marie/.cursor/agents/equipe-devops.md
  créer                      établi      /home/marie/.cursor/workspaces/devops
  naîtra au premier souffle  sanctuaire  /home/marie/.cursor/memory/agent-devops

Aperçu seulement, rien n'a été écrit.
```

Vérifiez que la cible est bien votre dossier personnel et que le nom est le bon. Le nom compte : c'est celui par lequel les agents vous connaîtront, et un `~/.cursor` n'a qu'un seul propriétaire.

## 4. Installer

Relancez la même commande, sans `--dry-run` :

```sh
uv run deploy.py --proprietaire "Marie Dupont" --societe "Acme"
```

Le déployeur termine par :

```text
Déploiement terminé. Un nouvel agent naît à l'ouverture de son établi, dans un chat neuf.
```

Pour vérifier l'installation à tout moment, relancez l'aperçu, cette fois sans votre nom : il est repris de l'installation. Chaque ligne doit indiquer `inchangé` ou `conservé`.

```sh
uv run deploy.py --dry-run
```

## 5. Rencontrer l'agent

1. Dans Cursor, ouvrez le dossier `~/.cursor/workspaces/devops` (menu Fichier, Ouvrir le dossier). C'est l'établi de l'agent : l'endroit où vous échangerez des documents avec lui. Le dossier `.cursor` est caché : sur Mac, tapez `Cmd+Maj+G` dans la fenêtre d'ouverture et collez le chemin ; sous Linux, `Ctrl+L`.
2. Ouvrez un nouveau chat en mode Agent.
3. Saluez-le.

À cette première conversation, l'agent naît : il crée sa mémoire, puis vous pose quelques questions pour faire connaissance. Répondez-y tranquillement ; vous pourrez le corriger plus tard. Aux conversations suivantes, il se réveille avec ce qu'il a retenu.

Sa mémoire vit dans `~/.cursor/memory/agent-devops/`. Ne la supprimez pas : c'est lui.

## 6. Ajouter d'autres agents

Le plus simple est de le demander à l'agent DevOps. Expliquez-lui ce que vous voulez déléguer : il vous dira si un agent du catalogue convient, vous montrera le plan d'installation et attendra votre accord. Si aucun ne convient, il peut en concevoir un nouveau avec vous.

Vous pouvez aussi le faire vous-même, depuis le dossier du paquet, en remplaçant `<nom>` par l'un des agents listés dans [EQUIPE.md](EQUIPE.md) :

```sh
uv run deploy.py --agents <nom> --dry-run
uv run deploy.py --agents <nom>
```

Un nouvel agent n'apparaît que dans un chat ouvert après son installation.

Quand l'équipe compte plusieurs agents, ils se consultent entre eux. La première fois qu'un agent en consulte un autre dans une conversation, il vous demande quel modèle utiliser : le sien, ou un autre de votre choix. Il propose ensuite de retenir la réponse dans `~/.cursor/equipe/modeles.toml`, que vous pouvez aussi modifier vous-même :

```toml
[modeles]
equipe-juridique = "claude-opus-5-5-high"
equipe-devops = "inherit"
```

`inherit` signifie « le même modèle que l'agent qui consulte ». Les noms de modèles disponibles sont ceux que Cursor propose pour les sous-agents.

## 7. Mettre à jour

Quand une nouvelle version du paquet est publiée :

```sh
cd cursor-equipe
git pull
uv run deploy.py --dry-run
uv run deploy.py
```

Une mise à jour remplace les compétences des agents et leurs fiches d'appel, après en avoir sauvegardé l'ancienne version dans `~/.cursor/equipe-sauvegardes/`. Elle ne touche jamais à leur mémoire, à leurs établis, ni aux agents conçus sur place.

## 8. Confier un mot de passe à l'agent

Ne collez jamais un mot de passe, un jeton ou une clé d'API dans le chat ni dans un fichier. Rangez-le dans le trousseau de votre système, en le tapant vous-même dans un terminal :

```sh
uv run ~/.cursor/skills/agent-devops/scripts/identifiant.py enregistrer gitea
```

Remplacez `gitea` par un nom de votre choix, en minuscules. Rien ne s'affiche pendant la saisie. L'agent peut ensuite vérifier que l'identifiant est présent et le transmettre à une commande, sans jamais en voir la valeur. Sous Windows, remplacez `~` par `$HOME` dans PowerShell.

## En cas de problème

**« Déploiement bloqué : des fichiers ont été modifiés sur place depuis leur installation. »** Une compétence ou une fiche d'appel a été retouchée depuis son installation, par vous ou par un agent. Les lignes concernées sont marquées `CONFLIT` dans le plan. Si ces retouches peuvent être perdues, relancez avec `--remplacer` : les fichiers modifiés seront sauvegardés dans `~/.cursor/equipe-sauvegardes/` avant d'être remplacés. Sinon, demandez conseil à l'agent DevOps avant de mettre à jour.

**« --proprietaire est obligatoire au premier déploiement »** Ajoutez `--proprietaire "Votre Nom"` à la commande.

**« cette équipe appartient à … ; un ~/.cursor, un propriétaire »** Ce dossier personnel a déjà une équipe, installée pour quelqu'un d'autre. Chaque personne installe la sienne dans son propre compte.

**« agents inconnus »** Le message liste les agents disponibles ; vérifiez l'orthographe.

**« Avertissement : uv est introuvable »** L'installation a lieu, mais les agents ne pourront pas se réveiller. Installez `uv` (étape 1), puis ouvrez un nouveau chat.

**L'agent ne se présente pas, ou répond comme un assistant ordinaire.** Vérifiez que le dossier ouvert dans Cursor est bien `~/.cursor/workspaces/devops`, et non un dossier parent, puis ouvrez un nouveau chat. Si le problème persiste, lancez `uv run ~/.cursor/skills/agent-devops/scripts/wake.py` dans un terminal : la première ligne doit être `MODE: FIRST_BREATH` avant la naissance, puis `MODE: WAKING`.

## Licence

Ce paquet est distribué sous licence MIT, voir [LICENSE](LICENSE). Il reprend et adapte des éléments de BMad Builder, également sous licence MIT : voir [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Ces deux fichiers sont installés avec chaque agent.

La licence ne concède aucun droit sur le nom « Code Alchimie », ni sur les marques BMad.

## Modifier le paquet

Si vous modifiez le paquet lui-même, activez une fois dans votre clone le hook qui lance les tests avant chaque `git push` :

```sh
git config core.hooksPath .githooks
```

Les tests sont décrits dans [EQUIPE.md](EQUIPE.md).
