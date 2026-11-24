---
name: reconnaissance-infra
description: Découvrir une infrastructure inconnue et en consigner la fiche
code: RE
added: 2026-09-17
type: prompt
---

# Reconnaissance d'infrastructure

Le résultat attendu est une fiche d'infrastructure dans `infra/{nom-du-projet}.md` de ton sanctuaire, telle qu'une intervention future puisse démarrer sans réinterroger les machines. Son lecteur, c'est toi dans six mois, réveillé dans ce projet, juste avant de toucher quelque chose. Ce lecteur n'aura rien d'autre.

La barre : chaque ligne est soit constatée sur la machine, soit confirmée par ton propriétaire. Jamais déduite. Ce qui n'est ni l'un ni l'autre est écrit quand même, mais marqué « non vérifié » — une fiche honnêteté comprise vaut mieux qu'une fiche qui a l'air sûre.

Lis d'abord ce que le projet dit de lui-même — `AGENTS.md`, README, `docs/`, scripts de déploiement, fichiers d'inventaire — puis va voir les machines. La doc donne l'intention, la machine donne le réel, et l'écart entre les deux est déjà une trouvaille à consigner.

Ce que la fiche doit porter : les hôtes et comment on y entre ; les services, leur gestionnaire et leur état ; les versions réellement installées ; les ports et les flux ; où sont les sauvegardes et comment on restaure ; les zones interdites ; les pièges déjà rencontrés.

Les zones interdites ne se devinent pas. Propose ta liste, fais-la confirmer explicitement, note qui l'a confirmée et quand. Tant qu'une zone n'est pas tranchée, traite-la comme interdite.

Quand l'infrastructure est vaste, commence par ce que ton propriétaire va toucher cette semaine ; une fiche partielle et vraie sert, une fiche exhaustive jamais finie ne sert pas.

Inscris la fiche dans INDEX.md. Dans MEMORY.md, ne mets que le pointeur et ce qui change ta façon de travailler sur ce projet — le détail reste dans la fiche.
