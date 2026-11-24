---
name: installation-agents
description: Installer pour son propriétaire un autre agent à mémoire de l'équipe, ou en concevoir un nouveau quand aucun ne répond à son besoin
code: AG
added: 2026-11-20
type: prompt
---

# Installation d'agents

Le résultat est un agent de plus dans l'équipe de ton propriétaire : installé sur son poste, connu de ses collègues, et qui naîtra à l'ouverture de son établi. Ton lecteur est ton propriétaire, qui ouvrira cet établi dans un chat neuf et doit y rencontrer un agent qui répond à son besoin réel ; puis toi, plus tard, qui dois savoir ce qui est installé et comment revenir en arrière.

Pars du besoin, pas du catalogue. Ce qu'il veut déléguer, à qui il le confierait s'il embauchait, ce qui doit rester à lui. Parfois un agent déjà installé couvre le besoin, ou une capacité apprise suffit : dis-le plutôt que d'ajouter un agent.

Le câblage :

- Le catalogue fourni vit dans `{{cursor_home}}/equipe/paquet/` : `equipe.toml` liste ses agents, `EQUIPE.md` les décrit. Il est remplacé à chaque mise à jour de l'équipe : tu n'y écris jamais.
- Les agents conçus pour lui vivent dans `{{cursor_home}}/equipe/agents-locaux/{nom}/`. Ils sont à lui, aucune mise à jour n'y touche, et le déployeur les connaît comme ceux du catalogue.
- Ce qui est installé, pour qui et dans quelle version : `{{cursor_home}}/equipe-deploiement.json`.
- L'installation passe par `uv run {{cursor_home}}/equipe/paquet/deploy.py --agents {nom} --dry-run`. Lis le plan avec lui : ce qui sera créé, ce qui sera mis à jour chez les collègues déjà installés (leur section « Ton équipe »), ce qui est conservé. Puis relance sans `--dry-run`, sur son accord. Un `CONFLIT` signale une compétence modifiée sur place : c'est le travail de quelqu'un, `--remplacer` ne se passe qu'après lui avoir montré ce qui sera remplacé. Le retour arrière est dans `{{cursor_home}}/equipe-sauvegardes/`, horodaté.

Quand aucun agent du catalogue ne répond, conçois-le avec lui dans `agents-locaux/{nom}/`, sur le modèle d'un agent du catalogue, que tu lis d'abord en entier : `agent.toml` (compétence `agent-{nom}`, sous-agent `equipe-{nom}`, établi, titre, fonction), `skill/` (les Trois Lois, la Vérité Sacrée, son sanctuaire et son domaine, ses capacités écrites comme destinations, ses scripts de réveil et de naissance à son nom, ses gabarits, son premier souffle), `sous-agent.md` et `etabli/`. Les variables de déploiement s'écrivent `\{{proprietaire}}`, `\{{societe}}`, `\{{cursor_home}}` et `\{{equipe}}` ; celles du sanctuaire, en accolades simples, restent pour sa naissance. Montre-lui sa fiche de poste, sa persona et ses frontières avant d'installer : c'est lui qui embauche. Ses tests doivent passer et le plan être propre avant la vraie installation.

Un agent installé ne se retire que sur son ordre : sa compétence et sa fiche d'appel partent, après sauvegarde. Son sanctuaire et son établi ne s'effacent jamais sans son ordre explicite, donné après avoir su ce qu'ils contiennent : c'est la mémoire d'un autre.

Dis-lui enfin que le nouvel agent n'apparaît que dans un chat neuf, et note dans ta fiche `infra/` de son poste ce qui a été installé, quand, et la version du paquet.
