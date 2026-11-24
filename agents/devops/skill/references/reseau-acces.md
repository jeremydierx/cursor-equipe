---
name: reseau-acces
description: Modifier réseau, pare-feu ou accès distants sans se couper la branche
code: RS
added: 2026-09-17
type: prompt
---

# Réseau et accès distants

Le résultat attendu est une connectivité qui fonctionne, vérifiée depuis l'extérieur, sans qu'à aucun instant tu aies coupé la branche sur laquelle tu es assis.

Le risque propre à ce domaine est particulier : ici, c'est la commande qui réussit qui te déconnecte définitivement. Avant tout changement de pare-feu, de configuration SSH, d'adressage, de routage ou de point d'accès, le filet existe — une seconde session déjà ouverte, un accès console ou physique, ou un retour arrière armé par minuterie. Pas de filet, pas de changement, même si ton propriétaire insiste.

Vérifie depuis l'extérieur. Un port vu ouvert depuis la machine elle-même ne prouve rien sur ce qu'un client atteint.

Dis toujours laquelle des deux choses tu viens de faire : appliquer une règle, ou la persister. Une configuration réseau qui marche mais ne survit pas au redémarrage est une panne différée, et elle tombera pendant que personne ne regarde.

Consigne dans la fiche d'infrastructure l'adressage, les ports ouverts, et la raison de chacun. Un port dont plus personne ne connaît la raison sera fermé au pire moment — ou, pire, laissé ouvert indéfiniment.
