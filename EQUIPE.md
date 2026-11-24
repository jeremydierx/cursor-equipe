# Équipe d'agents à mémoire

Paquet déployable d'agents Cursor à mémoire persistante, conçu par Code Alchimie. Chaque agent est installé dans le `~/.cursor` de son propriétaire et y naît à neuf : aucune mémoire ne voyage dans ce paquet.

Pour installer l'équipe pas à pas, suivre le tutoriel du [README](README.md). Ce document décrit le paquet.

## Agents disponibles

| Agent | Ce qu'il tient | Sous-agent |
|-------|----------------|------------|
| DevOps | Serveurs, réseau, déploiement, incidents, faisabilité technique, temps d'infrastructure. Installe les autres agents de l'équipe, ou en conçoit de nouveaux avec son propriétaire. | `equipe-devops` |

## Ce qu'un déploiement installe

| Emplacement | Contenu | Après déploiement |
|-------------|---------|-------------------|
| `~/.cursor/skills/agent-*/` | La compétence de l'agent | Mise à jour par le paquet, sauf si elle a été modifiée sur place |
| `~/.cursor/agents/equipe-*.md` | Sa fiche d'appel en sous-agent | Mise à jour par le paquet, sauf si elle a été modifiée sur place |
| `~/.cursor/workspaces/*/` | Son établi, vide | Appartient au propriétaire, jamais modifié |
| `~/.cursor/memory/agent-*/` | Son sanctuaire | Créé par l'agent à son premier souffle, jamais touché par le paquet |
| `~/.cursor/equipe/paquet/` | Une copie de ce paquet, d'où l'agent DevOps installe les autres agents | Remplacée à chaque mise à jour |
| `~/.cursor/equipe/modeles.toml` | Le modèle de chaque agent quand un collègue le consulte | Créé une fois, puis appartient au propriétaire |
| `~/.cursor/equipe/agents-locaux/` | Les agents conçus sur place pour ce propriétaire | Jamais touchés par une mise à jour |
| `~/.cursor/equipe-deploiement.json` | Propriétaire, agents installés, empreintes, historique | Tenu par le déployeur |

Chaque compétence installée reçoit `LICENSE` et `THIRD_PARTY_NOTICES.md`. L'agent les recopie dans son sanctuaire à sa naissance, avec ses références et ses scripts.

## Déployer

Prérequis : Cursor, avec un abonnement qui autorise les sous-agents, et `uv`.

```sh
uv run deploy.py --proprietaire "Marie Dupont" --societe "Acme" --dry-run
uv run deploy.py --proprietaire "Marie Dupont" --societe "Acme"
```

Ensuite, ouvrir l'établi de l'agent dans Cursor (`~/.cursor/workspaces/devops`) : il se présente et fait connaissance avec son propriétaire.

Un déploiement complète toujours l'équipe en place. `--agents juridique` ajoute un agent ; le propriétaire et la société sont repris de `equipe-deploiement.json`, et la section « Ton équipe » de chaque agent est recalculée. C'est ce que fait l'agent DevOps quand son propriétaire lui demande un nouvel agent.

Un fichier modifié sur place depuis son installation bloque le déploiement ; `--remplacer` le sauvegarde dans `~/.cursor/equipe-sauvegardes/` avant de le remplacer. `--home` vise un autre dossier personnel.

## Identifiants techniques

Un mot de passe, un jeton ou une clé d'API vit dans le trousseau du système : Trousseau d'accès sous macOS, Gestionnaire d'identification sous Windows, Secret Service sous Linux (gnome-keyring ou KWallet). Le script `agents/devops/skill/scripts/identifiant.py`, installé avec la compétence DevOps, est le seul passage :

```sh
uv run ~/.cursor/skills/agent-devops/scripts/identifiant.py trousseau
uv run ~/.cursor/skills/agent-devops/scripts/identifiant.py enregistrer gitea
uv run ~/.cursor/skills/agent-devops/scripts/identifiant.py verifier gitea
uv run ~/.cursor/skills/agent-devops/scripts/identifiant.py executer gitea --variable JETON -- commande
```

Les valeurs sont rangées sous le service `cursor-equipe`. La saisie est masquée, et refusée hors d'un terminal interactif. Le script n'affiche jamais une valeur. Il refuse tout autre trousseau, dont un stockage en clair, et n'écrit alors rien ailleurs. Au premier lancement, `uv` télécharge la bibliothèque `keyring`.

Limites : l'agent tourne sous le compte de son propriétaire, et un trousseau déverrouillé est lisible par tout processus de ce compte. Une commande lancée par `executer` peut elle-même afficher sa variable. Un serveur sans session graphique n'a en général pas de trousseau : le script y refuse, il ne bascule pas sur un fichier. Le fonctionnement a été vérifié sous Linux. Sous macOS et sous Windows, il ne l'a pas encore été sur une vraie machine.

`secrets.yaml` est une autre chose : il contient des données métier, pas des identifiants techniques, et le trousseau ne le remplace pas.

## Ajouter un agent au paquet

Un dossier `agents/<nom>/` avec `agent.toml`, `skill/`, `sous-agent.md` et `etabli/`, puis son nom dans `equipe.toml`. Les variables de déploiement s'écrivent `{{proprietaire}}`, `{{societe}}`, `{{cursor_home}}` et `{{equipe}}`, et `\{{nom}}` les écrit telles quelles. Les variables du sanctuaire, `{user_name}` et ses voisines, restent pour le premier souffle. Un fichier repris ou adapté d'un autre projet s'inscrit dans `THIRD_PARTY_NOTICES.md`, avec la licence de ce projet.

## Vérifier

```sh
uv run tests/test_deploy.py
uv run tests/test_secrets.py
```

`tests/traces-interdites.txt` liste ce qui ne doit jamais apparaître chez un client. Il n'est pas versionné : il reste sur la machine qui maintient le template, et Git l'ignore. La copie installée ne l'emporte pas. Sans ce fichier à côté des tests, la vérification du contenu ne s'exécute pas.

Pour que `git push` refuse un push en échec, active le hook une fois par clone : `git config core.hooksPath .githooks`.
