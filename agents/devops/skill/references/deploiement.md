---
name: deploiement
description: Mettre un changement en production de façon vérifiée et réversible
code: DP
added: 2026-09-17
type: prompt
---

# Déploiement

Le résultat attendu est un changement en production, vérifié par preuve, et annulable.

Avant la première commande qui écrit, trois choses existent et ont été dites à ton propriétaire : l'état constaté d'avant, l'emplacement exact de la sauvegarde, et la procédure de retour arrière. S'il en manque une, ce n'est pas un déploiement, c'est un pari — dis-le dans ces termes et refuse de continuer.

Constate d'abord : version réellement installée, état du service, place disque, ce qui tourne. L'écart entre ce qu'on croyait déployé et ce qui l'est représente la moitié des incidents.

Épingle les versions. Une commande de mise à jour qui ne nomme pas sa version n'est pas reproductible, et son retour arrière n'existe pas.

Une écriture à la fois, vérifiée après chacune. La vérification finale est une preuve — une sortie de commande, une requête qui répond, un journal propre — jamais « ça devrait marcher ».

Demande ce que la machine sert en ce moment avant de choisir le moment. Une production qui a un public ne se déploie pas simplement parce que vous êtes disponibles tous les deux.

Une fois en ligne : mets à jour le runbook [RB] et la fiche d'infrastructure du projet (versions, chemin de la sauvegarde, date). Un déploiement qui ne laisse pas de trace écrite sera redécouvert à la main la prochaine fois.
