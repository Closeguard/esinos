# ESINOS — Mini-noyau de système d'exploitation simulé

Projet semestriel du module Systèmes d'Exploitation (UIR / ESIN), projet 4.
Enseignant : Pr. Ilias Tougui.

ESINOS est un programme Python qui simule, dans un terminal, trois parties d'un
système d'exploitation :

1. **l'ordonnanceur** : qui utilise le processeur, et quand ;
2. **le gestionnaire mémoire** : où sont rangées les pages, et laquelle sortir
   quand la mémoire est pleine ;
3. **le système de fichiers** (bonus) : comment des fichiers sont rangés sur
   un disque avec des inodes.

**Équipe :**

- Mohamed Amine El Guandafi
- Ziad El Gazzar
- Yasmina Saidi
- Ziad Bakraoui

Groupe de TP : TPF, section 1

## Fonctionnalités

| Module | Contenu |
|---|---|
| Ordonnanceur | FCFS, SJF, Round Robin, Priority ; diagramme de Gantt ; temps d'attente et de séjour par processus et en moyenne ; utilisation du CPU ; comparaison des quatre algorithmes |
| Mémoire | Pagination et traduction d'adresse logique → physique ; FIFO, LRU, Optimal avec affichage des cadres étape par étape ; comptage des défauts de page ; simulation d'un TLB ; calcul de l'EAT |
| Fichiers (bonus) | Disque simulé dans un fichier ; allocation de blocs ; inodes ; créer, lire, supprimer ; table des inodes ; carte des blocs |
| Interface | Menu principal, un sous-menu par module, saisies vérifiées, retour au menu précédent, sortie propre |

## Ce qu'il faut pour l'exécuter

Python 3.8 ou plus récent (testé avec Python 3.11, 3.12 et 3.13). **Aucune bibliothèque à installer.**

Vérifier sa version :

```
python3 --version
```

Sous Windows, remplacez `python3` par `python` dans toutes les commandes.

## Lancer le programme

```
cd code
python3 main.py
```

Le menu principal s'affiche :

```
1. Ordonnanceur de processus
2. Gestionnaire mémoire
3. Système de fichiers (bonus)
0. Quitter
```

Chaque module démarre avec un exemple déjà chargé : il suffit de choisir un
algorithme. `0` revient toujours au menu précédent. `Ctrl+C` quitte proprement.

## Exemple d'exécution

Ordonnanceur, choix `1` (FCFS) sur l'exemple :

```
===== FCFS =====
+----------+------+----------------+------------+
|    P1    |  P2  |       P3       |     P4     |
+----------+------+----------------+------------+
0          5      8                16           22

Processus  Arrivée  Durée   Fin  Séjour  Attente
P1               0      5     5       5        0
P2               1      3     8       7        4
P3               2      8    16      14        6
P4               3      6    22      19       13
Temps d'attente moyen : 5.75
Temps de séjour moyen : 11.25
```

Mémoire, remplacement de pages, FIFO en mode pas à pas :

```
Étape 4 : le processus demande la page 2
  Défaut de page, mémoire pleine.
  FIFO : page 7 chargée à l'étape 1, page 0 chargée à l'étape 2, page 1 chargée à l'étape 3.
  La plus ancienne en mémoire est la page 7.
  La page 2 prend sa place dans le cadre 0.
  Cadres : [2] [0] [1]
```

Système de fichiers, carte des blocs après la création d'un fichier de deux blocs :

```
blocs  0 à 15 : SCIIIIRRRR##....
```

## Lancer les tests

```
cd code
python3 -m unittest
```

Résultat attendu :

```
Ran 91 tests in 0.XXXs

OK
```

Ajoutez `-v` pour voir le nom de chaque test. Pour un seul module :
`python3 -m unittest tests.test_memoire`.

Les tests comparent le programme à des résultats calculés à la main et aux
exemples classiques des manuels. Les tests d'intégration lancent le programme
entier et tapent à la place de l'utilisateur.

## Organisation du code

```
code/
  main.py                  menu principal
  interface.py             outils communs des menus (titres, saisies)
  ordonnanceur/            modeles, algorithmes, statistiques, affichage, menu
  memoire/                 pagination, remplacement, tlb, affichage, menu
  fichiers/                disque, systeme_fichiers, affichage, menu
  tests/                   un fichier de tests par module + test_integration
docs/
  MODULE1_ORDONNANCEUR.md  guide pas à pas de l'ordonnanceur
  MODULE2_MEMOIRE.md       guide pas à pas du gestionnaire mémoire
  MODULE3_FICHIERS.md      guide pas à pas du système de fichiers
```

Règles suivies partout : un fichier = un rôle ; les calculs n'affichent rien ;
l'affichage ne calcule rien.

## Conventions choisies

- Priorité : un **petit** nombre signifie une priorité **haute**.
- SJF et Priority sont **non préemptifs**. Round Robin est préemptif.
- Round Robin : un processus qui arrive au moment où un autre est interrompu
  entre dans la file avant lui.
- En cas d'égalité parfaite, l'ordre de saisie décide.
- TLB : quand il est plein, l'entrée la plus ancienne sort.
- EAT avec TLB : `taux x (tlb + mem) + (1 - taux) x (tlb + 2 x mem)`.
- Disque : 64 blocs de 64 octets, 16 inodes, 6 pointeurs directs par inode
  (fichier de 384 octets au plus), un seul répertoire.

## Fichier créé par le programme

Le module fichiers crée `disque_esinos.img` (4096 octets) dans le dossier d'où
le programme est lancé. Vous pouvez le supprimer : il sera recréé.
