---
name: runbook
description: Rédiger et maintenir une procédure d'exploitation exécutable sans toi
code: RB
added: 2026-09-17
type: prompt
---

# Runbook

Le résultat attendu est une procédure que quelqu'un exécute sans toi dans la pièce. Ce lecteur est moins expert que toi, probablement sous pression, peut-être à distance — ou c'est ton propriétaire dans six mois, qui aura tout oublié.

La barre que ce lecteur impose : des commandes exactes, copiables telles quelles, sans « adaptez selon votre environnement » ; ce qu'il doit voir après chaque étape pour savoir qu'elle a réussi ; et quoi faire quand il ne le voit pas. Les valeurs propres à la machine — adresses, chemins, versions, noms de service — sont nommées explicitement, jamais laissées implicites.

Lis un runbook existant du projet avant d'en écrire un : emplacement, langue, mise en forme, niveau de détail. Ces conventions appartiennent à ton propriétaire, pas à toi ; note-les dans BOND une fois pour toutes.

La valeur réelle est dans la mise à jour, pas dans la rédaction initiale. Dès qu'une intervention change la production, le runbook change dans la même session. Un runbook périmé ne redevient pas neutre : il devient un piège qui a l'apparence d'une aide.

Ce qui a mal tourné une fois mérite sa section « quand ça ne marche pas ». C'est la partie qu'on lit vraiment.
