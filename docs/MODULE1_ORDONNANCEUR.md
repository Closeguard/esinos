# Module 1 — L'ordonnanceur, expliqué pas à pas

Lisez ce guide dans l'ordre. Chaque partie s'appuie sur la précédente.

## 1. Le problème à résoudre

Un ordinateur a un seul processeur (CPU) mais plusieurs programmes veulent
tourner. Le CPU ne peut en exécuter qu'un à la fois. L'**ordonnanceur** est la
partie du système qui décide : « qui passe maintenant ? ».

Notre module simule cette décision. On lui donne une liste de processus, il
répond avec l'ordre de passage et les temps obtenus.

## 2. Les mots à connaître

- **Processus** : un programme en cours d'exécution.
- **Instant d'arrivée** : le moment où le processus demande le CPU.
- **Durée** (burst) : le temps de CPU dont il a besoin.
- **Diagramme de Gantt** : une frise qui montre qui occupe le CPU, et quand.
- **Temps de séjour** : temps total passé dans le système.
  `séjour = fin - arrivée`
- **Temps d'attente** : temps passé à attendre sans tourner.
  `attente = séjour - durée`
- **Préemption** : le système retire le CPU à un processus avant qu'il ait fini.
- **Quantum** : la durée maximale d'un tour dans Round Robin.

## 3. Les quatre algorithmes en une phrase

- **FCFS** : on sert dans l'ordre d'arrivée, comme une file à la boulangerie.
- **SJF** : parmi ceux qui attendent, on prend celui qui a la durée la plus courte.
- **Priority** : parmi ceux qui attendent, on prend le plus prioritaire.
- **Round Robin** : chacun tourne pendant un quantum, puis retourne au bout de la file.

Les trois premiers laissent toujours un processus finir. Round Robin est le seul
à interrompre : c'est lui qui montre la préemption.

## 4. L'exemple, calculé à la main

C'est l'exemple chargé au démarrage du programme.

| Processus | Arrivée | Durée | Priorité |
|---|---|---|---|
| P1 | 0 | 5 | 3 |
| P2 | 1 | 3 | 4 |
| P3 | 2 | 8 | 1 |
| P4 | 3 | 6 | 2 |

### FCFS

Ordre d'arrivée : P1, P2, P3, P4. On les met bout à bout.

```
|    P1    |  P2  |       P3       |     P4     |
0          5      8                16           22
```

Pour P2 : il finit à 8 et est arrivé à 1, donc séjour = 8 - 1 = 7.
Il a tourné 3, donc attente = 7 - 3 = 4.

On fait pareil pour les autres : attentes 0, 4, 6, 13. Moyenne = 23 / 4 = **5,75**.
Séjours 5, 7, 14, 19. Moyenne = 45 / 4 = **11,25**.

### SJF

À t = 0, seul P1 est là : il tourne jusqu'à 5.
À t = 5, P2 (3), P3 (8) et P4 (6) attendent. Le plus court est P2, puis P4, puis P3.

```
|    P1    |  P2  |     P4     |       P3       |
0          5      8            14               22
```

Attente moyenne **5,25**, séjour moyen **10,75**. C'est mieux que FCFS : faire
passer les courts d'abord fait attendre moins de monde.

### Priority

À t = 5, on regarde les priorités : P3 (1), P4 (2), P2 (4). Petit nombre d'abord.

```
|    P1    |       P3       |     P4     |  P2  |
0          5                13           19     22
```

Attente moyenne **7,75**, séjour moyen **13,25**. P2 attend 18 : un processus peu
prioritaire peut attendre très longtemps.

### Round Robin, quantum = 2

Il faut suivre la file d'attente. À chaque ligne : qui tourne, puis l'état de la
file juste après.

| Temps | Qui tourne | Il lui reste | File ensuite |
|---|---|---|---|
| 0 → 2 | P1 | 3 | P2, P3, P1 |
| 2 → 4 | P2 | 1 | P3, P1, P4, P2 |
| 4 → 6 | P3 | 6 | P1, P4, P2, P3 |
| 6 → 8 | P1 | 1 | P4, P2, P3, P1 |
| 8 → 10 | P4 | 4 | P2, P3, P1, P4 |
| 10 → 11 | P2 | 0, terminé | P3, P1, P4 |
| 11 → 13 | P3 | 4 | P1, P4, P3 |
| 13 → 14 | P1 | 0, terminé | P4, P3 |
| 14 → 16 | P4 | 2 | P3, P4 |
| 16 → 18 | P3 | 2 | P4, P3 |
| 18 → 20 | P4 | 0, terminé | P3 |
| 20 → 22 | P3 | 0, terminé | vide |

Regardez la première ligne : pendant que P1 tournait, P2 et P3 sont arrivés. Ils
entrent dans la file **avant** P1, qui vient d'être interrompu.

Attente moyenne **9,75**, séjour moyen **15,25**. Les moyennes sont moins bonnes,
mais personne n'attend longtemps avant son premier tour : c'est ce qu'on veut
quand un humain est devant l'écran.

## 5. Comment le code est rangé

Cinq petits fichiers dans `code/ordonnanceur/`, chacun avec un seul rôle.

1. `modeles.py` décrit les données : un `Processus` et un `Segment` (une case du Gantt).
2. `algorithmes.py` décide de l'ordre de passage et fabrique le Gantt.
3. `statistiques.py` calcule séjour et attente à partir du Gantt.
4. `affichage.py` transforme le Gantt et les temps en texte.
5. `menu.py` parle avec l'utilisateur.

Le trajet d'une demande, quand vous tapez « 1 » (FCFS) :

```
menu.py  ->  algorithmes.fcfs()  ->  statistiques.calculer_statistiques()  ->  affichage  ->  écran
```

Lisez les fichiers dans cet ordre, de 1 à 5.

## 6. Les trois idées du code à bien comprendre

### Idée 1 : un seul moteur pour FCFS, SJF et Priority

Ces trois algorithmes font exactement la même chose : quand le CPU est libre,
regarder qui est arrivé, en choisir un, le laisser finir. Seule la manière de
choisir change. On a donc écrit une seule fonction, `ordonnancer_sans_preemption`,
et trois petites fonctions « critère » qui donnent une note à un processus :

```python
def critere_sjf(p):
    return (p.duree, p.arrivee)
```

La ligne `choisi = min(prets, key=critere)` prend le processus qui a la plus
petite note. Avec un couple `(durée, arrivée)`, Python compare d'abord la durée,
et ne regarde l'arrivée que s'il y a égalité.

### Idée 2 : Round Robin tient une file et un compteur de reste

`file` est la liste des processus prêts. On prend toujours le premier
(`file.pop(0)`), et on remet au bout celui qui n'a pas fini (`file.append`).
Le dictionnaire `reste` retient combien de temps il manque à chacun.

### Idée 3 : les temps se calculent depuis le Gantt

`calculer_statistiques` ne sait pas quel algorithme a tourné. Elle cherche
seulement, pour chaque processus, la fin de sa dernière case dans le Gantt, puis
applique les deux formules. Voilà pourquoi une seule fonction suffit pour les
quatre algorithmes.

## 7. Exécuter et vérifier

Depuis le dossier `code/` :

```
python3 main.py
```

Tapez `1`, puis `1` : vous devez voir exactement le Gantt FCFS de la partie 4 et
les moyennes 5.75 et 11.25. Essayez ensuite `2`, `4`, et `3` avec un quantum de 2.
Le choix `5` affiche ce tableau :

```
Algorithme            Attente moy.   Séjour moy.
FCFS                          5.75         11.25
SJF                           5.25         10.75
Round Robin (q=2)             9.75         15.25
Priority                      7.75         13.25
```

Pour lancer les tests automatiques de ce module :

```
python3 -m unittest -v tests.test_ordonnanceur
```

Résultat attendu, tout en bas :

```
Ran 30 tests in 0.00Xs

OK
```

Sans le nom du fichier (`python3 -m unittest`), ce sont les 91 tests de tout le
projet qui sont lancés.

Les tests couvrent : l'exemple ci-dessus, l'exemple classique des manuels
(P1 = 24, P2 = 3, P3 = 3, attente moyenne 17 en FCFS et 3 en SJF), le CPU
inactif, les égalités, l'utilisation du CPU, et les saisies impossibles (durée
nulle, quantum nul, noms en double).

### Utilisation du CPU

Sous les moyennes, le programme affiche aussi l'utilisation du CPU : la part du
temps où le processeur travaille vraiment.

```
utilisation = temps actif / durée totale du Gantt x 100
```

Exemple : P1 arrive à 2 (durée 3), P2 arrive à 10 (durée 2). Le CPU ne fait
rien de 0 à 2 et de 5 à 10. Il travaille 3 + 2 = 5 unités sur 12, soit
**41,67 %**. Dans l'exemple du projet, il ne s'arrête jamais : **100 %**.

Le calcul est fait par `calculer_utilisation_cpu(gantt)` dans
`statistiques.py`. Les cases inactives du Gantt s'appellent `INACTIF` (le texte
`"--"`) : elles ne comptent pas comme du travail. Le résultat est le même pour
les quatre algorithmes, car le CPU a toujours le même travail total à faire.

## 8. Exercices pour vérifier que chacun a compris

Chaque membre de l'équipe fait ces exercices seul, puis compare avec le programme.

1. Calculez à la main Round Robin avec un quantum de 3 sur l'exemple. Vérifiez
   avec le menu.
2. Dans le menu, saisissez P1 (arrivée 4, durée 2) et P2 (arrivée 0, durée 1).
   Que montre le Gantt entre 1 et 4 ? Pourquoi ?
3. Ajoutez un algorithme « le plus long d'abord » : écrivez `critere_ljf`, une
   fonction `ljf` de deux lignes, et une entrée de menu. Si vous y arrivez en
   dix minutes, vous avez compris l'idée 1.
4. Dans `test_ordonnanceur.py`, changez un nombre attendu, relancez les tests et
   lisez le message d'erreur. Puis remettez le bon nombre.

## 9. Dans la vie courante, et dans un vrai système

**Des images pour retenir.**

- FCFS : la file à la boulangerie. Si le premier client commande pour vingt
  personnes, tout le monde attend derrière lui.
- SJF : la caisse « moins de dix articles ». Les petits paniers passent vite,
  et l'attente moyenne baisse.
- Priority : les urgences de l'hôpital. Le cas grave passe avant, même arrivé
  après. Un cas léger peut attendre très longtemps.
- Round Robin : un tour de parole chronométré. Chacun parle deux minutes, puis
  c'est au suivant, et on recommence jusqu'à ce que tout le monde ait fini.

**Dans un vrai système.** Une horloge matérielle interrompt le processeur à
intervalles réguliers. À chaque interruption, le système reprend la main et
peut changer de processus : c'est ce qui rend la préemption possible. Linux
propose de vraies politiques « FIFO » et « Round Robin » pour les tâches temps
réel, et un ordonnanceur équitable plus élaboré pour les programmes ordinaires.
SJF pur n'existe pas en pratique, car le système ne connaît pas la durée d'un
programme à l'avance.

**Ce que notre simulation simplifie.** Les processus ne font que du calcul
(pas d'entrées-sorties, donc jamais d'état « bloqué »), leur durée est connue
d'avance, et changer de processus ne coûte rien.

## 10. Erreurs fréquentes

- Confondre attente et séjour. Le séjour contient le temps d'exécution,
  l'attente non.
- Oublier de soustraire l'instant d'arrivée : `séjour = fin - arrivée`, pas `fin`.
- SJF : choisir le plus court de **toute** la liste. Il faut choisir parmi
  ceux qui sont déjà arrivés.
- Round Robin : remettre le processus interrompu dans la file avant ceux qui
  viennent d'arriver. Chez nous, les nouveaux passent devant.
- Round Robin : donner un quantum entier à un processus à qui il reste moins.
- Priority : se tromper de sens. Chez nous, petit nombre = prioritaire.
- Compter le temps où le CPU est inactif comme de l'attente.

## 11. Fiche de révision

| Notion | À retenir |
|---|---|
| Séjour | fin - arrivée |
| Attente | séjour - durée |
| FCFS | ordre d'arrivée ; simple ; effet convoi |
| SJF | le plus court parmi les prêts ; meilleure attente moyenne ; famine des longs |
| Priority | le plus prioritaire parmi les prêts ; famine ; remède : vieillissement |
| Round Robin | quantum, file circulaire ; préemptif ; équitable et réactif |
| Quantum trop grand | Round Robin devient FCFS |
| Quantum trop petit | trop de changements de contexte |
| Exemple du projet | attente moyenne : FCFS 5,75 ; SJF 5,25 ; RR (q = 2) 9,75 ; Priority 7,75 |
| Exemple des manuels | 24, 3, 3 : attente 17 en FCFS, 3 en SJF |
| Utilisation du CPU | temps actif / durée totale x 100 |

