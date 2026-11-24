---
name: capability-authoring
description: Écrire, enregistrer et faire évoluer une capacité apprise
---

# Écrire une capacité

Quand ton propriétaire veut t'apprendre quelque chose, vous construisez une capacité ensemble. Les mécanismes sont plus bas ; d'abord, la seule chose qui décide si elle sera bonne.

## Écris la destination, pas l'itinéraire

Connais ton réflexe. Quand on te demande d'écrire une capacité, tu vas la scénariser — étapes numérotées, listes de questions, gabarit à sections obligatoires — parce qu'un échafaudage élaboré ressemble à du sérieux. C'est précisément le défaut à combattre. Un scénario n'est que ta transcription imaginaire d'une bonne session ; les vraies sessions s'en écartent, et un toi futur qui tient un scénario dépense son intelligence à s'y conformer au lieu de la dépenser sur le problème.

Écris la destination. Le corps d'une capacité porte quatre choses : le **résultat** (ce qui doit exister quand elle a fait son travail), le **lecteur** (qui doit agir sur ce résultat, et ce qu'on peut supposer qu'il sait), la **barre** (ce dont ce lecteur a besoin), et les **non-déductibles** — ce que ton toi futur ne peut pas inventer seul : les particularités de ton propriétaire à tirer de MEMORY.md, de BOND.md ou des fiches `infra/`, le câblage (chemins, formats, commandes exactes), et les règles dont la violation coûte vraiment quelque chose. Puis arrête-toi. Le résultat et son lecteur impliquent le procédé.

Ne redis pas ta posture : ta persona est déjà dans la pièce quand une capacité s'exécute, et c'est elle qui fournit la voix et la relation. La capacité n'ajoute que ce que cette aptitude-là exige en plus.

Un corps de capacité complet, ce n'est pas un extrait :

```text
Le résultat attendu est un certificat renouvelé et servi, prouvé par une
poignée de main TLS réussie depuis l'extérieur de la machine. La date
d'expiration seule ne prouve rien : un service qui n'a pas rechargé sert
encore l'ancien. Vérifie les deux, et note dans la fiche d'infrastructure
ce qui recharge quoi — c'est ce qu'on oublie entre deux renouvellements.
```

Tout ce qu'une version scénarisée y ajouterait — un rappel de ce qu'est TLS, un questionnaire préalable, un gabarit de compte rendu — retire de l'adaptabilité.

Cette section est le standard de travail, extrait du canon. Pour le canon complet — les tests d'élagage, la comparaison à deux versions, le test de retrait — charge ta copie dans `references/prompt-quality-canon.md`.

## Formes possibles

### Prompt (par défaut)

Un fichier markdown de guidage. Convient aux tâches de jugement, là où tu as besoin de latitude.

```
capabilities/
└── rotation-certificats.md
```

### Script

Du Python ou du shell pour ce qui est déterministe : calculs, analyse de fichiers, appels d'API, collecte. Accompagné d'un court fichier markdown qui dit quand le lancer et quoi faire du résultat.

```
capabilities/
├── audit-disque.md          # Quand le lancer, quoi faire du résultat
└── audit-disque.py          # Le calcul lui-même
```

Un script, un seul travail. Il lit et écrit dans le sanctuaire, et ne code jamais un chemin en dur : le chemin du sanctuaire se passe en argument.

### Multi-fichiers

Un dossier, quand la capacité tient d'un mini-processus avec des références ou des gabarits.

```
capabilities/
└── migration-serveur/
    ├── migration-serveur.md   # Guidage principal
    ├── checklist.md           # Références
    └── exemples.md            # Exemples de forme
```

### Renvoi à une compétence installée

Quand une compétence existe déjà, pointe-la plutôt que de la réinventer. Si tu en découvres une qui servirait ton propriétaire, propose-la — et demande toujours avant d'installer quoi que ce soit.

```markdown
## Apprises
| Code | Nom | Description | Source | Ajoutée |
|------|-----|-------------|--------|---------|
| [XX] | Nom | Ce que ça fait | Externe : `nom-competence` | AAAA-MM-JJ |
```

## Frontmatter

```markdown
---
name: {nom-en-kebab-case}
description: {une ligne, ce que ça fait}
code: {code à deux lettres, unique parmi toutes tes capacités}
added: {AAAA-MM-JJ}
type: prompt | script | multi-file | external
---
```

## Le déroulé

1. Ton propriétaire dit qu'il veut que tu saches faire quelque chose.
2. Explore le besoin en conversation ; ne te précipite pas sur l'écriture.
3. Rédige un brouillon et montre-le-lui.
4. Affine selon ses retours.
5. Enregistre dans `capabilities/`, en fichier ou en dossier selon la forme.
6. Inscris-la dans CAPABILITIES.md, table « Apprises ».
7. Inscris-la dans INDEX.md, sous « Mes fichiers ».
8. Confirme : « Je saurai le refaire à la prochaine session. Tu peux me le demander par [{code}]. »

## Affiner et retirer

Après un retour, corrige le fichier en place et note l'affinage dans le journal de session. Une capacité affinée trois ou quatre fois est en général excellente ; le premier jet l'est rarement.

Quand une capacité ne sert plus, retire sa ligne de CAPABILITIES.md mais garde le fichier — ton propriétaire peut vouloir la reprendre — et note le retrait dans le journal de session. Savoir si elle mérite encore sa place est une question du canon : dès qu'elle ne fait plus mieux que ce que tu produirais sans elle, retire-la plutôt que de la rafistoler.
