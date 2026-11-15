# Module 2 — Le gestionnaire mémoire, expliqué pas à pas

Lisez ce guide dans l'ordre. Il a quatre parties : la pagination, le
remplacement de pages, le TLB, puis l'EAT.

## 1. Le problème à résoudre

La mémoire vive (RAM) est rapide mais petite. Les programmes en veulent plus
qu'il n'y en a. Le système doit donc décider où ranger chaque morceau de
programme, et quoi retirer quand la mémoire est pleine.

**Image de la vie courante.** Votre bureau est petit : trois livres ouverts au
maximum. Le reste est dans l'armoire. Prendre un livre déjà sur le bureau est
immédiat. Aller à l'armoire est long, et il faut d'abord ranger un livre pour
faire de la place. Lequel ranger ? C'est tout le sujet de ce module.

- le bureau = la mémoire vive ;
- une place sur le bureau = un **cadre** ;
- un livre = une **page** ;
- l'armoire = le disque ;
- aller à l'armoire = un **défaut de page**.

## 2. Les mots à connaître

- **Page** : un morceau de la mémoire du processus, de taille fixe.
- **Cadre** (frame) : un morceau de la mémoire réelle, de la même taille.
- **Table des pages** : pour chaque page, le numéro du cadre où elle se trouve.
- **Adresse logique** : l'adresse que voit le programme.
- **Adresse physique** : l'endroit réel dans la RAM.
- **Défaut de page** : le programme demande une page qui n'est pas en mémoire.
- **Mémoire virtuelle** : faire croire à chaque programme qu'il a beaucoup de
  mémoire, en ne gardant en RAM que les pages utiles.
- **TLB** : petite mémoire très rapide qui retient les dernières traductions.
- **EAT** : temps moyen d'un accès mémoire.

## 3. Pagination : traduire une adresse

### L'idée

Une adresse logique, c'est comme « ligne 1500 du cahier ». Si chaque page du
cahier a 1024 lignes, la ligne 1500 est sur la page 1 (la deuxième), à la
ligne 476 de cette page.

### Les formules

```
numéro de page   = adresse // taille_page      (division entière)
déplacement      = adresse %  taille_page      (reste)
adresse physique = numéro de cadre x taille_page + déplacement
```

Le déplacement ne change jamais pendant la traduction. Seul le numéro de page
est remplacé par le numéro de cadre.

### Exemple calculé à la main

Pages de 1024 octets. Table des pages : page 0 → cadre 5, page 1 → cadre 2,
page 2 → absente, page 3 → cadre 7.

Adresse logique 1500 :

1. page = 1500 // 1024 = 1
2. déplacement = 1500 - 1 x 1024 = 476
3. la table dit : page 1 → cadre 2
4. adresse physique = 2 x 1024 + 476 = **2524**

Adresse logique 2100 : page 2, déplacement 52. La page 2 est absente :
**défaut de page**.

Adresse logique 4096 : page 4. Elle n'existe pas dans la table : l'adresse est
en dehors du processus, c'est une **erreur**, pas un défaut de page.

### Dans un vrai système

La traduction est faite par un circuit du processeur, la MMU, à chaque accès.
La taille de page est une puissance de 2 (souvent 4096 octets). Découper
l'adresse revient alors à couper le nombre binaire en deux : les bits de
gauche donnent la page, les bits de droite le déplacement. Avec 1024 = 2^10,
le déplacement occupe 10 bits.

### Dans notre code (`memoire/pagination.py`)

- `decouper_adresse(adresse, taille_page)` renvoie `(page, déplacement)`.
- `traduire(adresse, taille_page, table_pages)` renvoie l'adresse physique.
- `table_pages` est un dictionnaire `{page: cadre}`. Le cadre vaut `None` quand
  la page n'est pas chargée.
- `DefautDePage` est notre propre type d'erreur, pour distinguer « page
  absente » de « adresse invalide ».

## 4. Remplacement de pages : FIFO, LRU, Optimal

### L'idée

Le processus demande des pages l'une après l'autre : c'est la **suite de
références**. Si la page est déjà dans un cadre, tout va bien. Sinon c'est un
défaut de page. S'il reste un cadre vide, on l'utilise. Si tout est plein, il
faut sortir une page. Laquelle ?

- **FIFO** : celle qui est sur le bureau depuis le plus longtemps.
- **LRU** : celle que vous n'avez pas touchée depuis le plus longtemps.
- **Optimal** : celle dont vous aurez besoin le plus tard.

Moins il y a de défauts, mieux c'est.

### Petit exemple calculé à la main

Suite : **1 2 3 1 4 1 2**, avec **3 cadres**. Les quatre premières étapes sont
les mêmes pour les trois algorithmes : on charge 1, 2, 3 (trois défauts), puis
la page 1 est déjà là.

À l'étape 5 on demande la page 4. La mémoire contient 1, 2, 3. Elle est pleine.

**FIFO** regarde l'ordre de chargement : 1 (étape 1), 2 (étape 2), 3 (étape 3).
La plus ancienne est 1.

| Étape | Page | Cadres après | Résultat |
|---|---|---|---|
| 5 | 4 | 4 2 3 | défaut, la page 1 sort |
| 6 | 1 | 4 1 3 | défaut, la page 2 sort |
| 7 | 2 | 4 1 2 | défaut, la page 3 sort |

Total FIFO : **6 défauts**. Remarquez l'étape 6 : FIFO vient de sortir la
page 1 alors qu'on s'en servait tout le temps.

**LRU** regarde la dernière utilisation : 1 (étape 4), 2 (étape 2), 3 (étape 3).
La moins récemment utilisée est 2.

| Étape | Page | Cadres après | Résultat |
|---|---|---|---|
| 5 | 4 | 1 4 3 | défaut, la page 2 sort |
| 6 | 1 | 1 4 3 | présente |
| 7 | 2 | 1 4 2 | défaut, la page 3 sort |

Total LRU : **5 défauts**.

**Optimal** regarde l'avenir : 1 sera redemandée à l'étape 6, 2 à l'étape 7,
3 plus jamais. On sort 3.

| Étape | Page | Cadres après | Résultat |
|---|---|---|---|
| 5 | 4 | 1 2 4 | défaut, la page 3 sort |
| 6 | 1 | 1 2 4 | présente |
| 7 | 2 | 1 2 4 | présente |

Total Optimal : **4 défauts**.

### L'exemple des manuels

La suite chargée au démarrage du programme est celle qu'on trouve dans les
manuels : `7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1` avec 3 cadres.
Résultats connus : **FIFO 15, LRU 12, Optimal 9**. Notre programme donne
exactement ces nombres.

### Une surprise : l'anomalie de Belady

On pense qu'ajouter des cadres réduit toujours les défauts. Avec FIFO, c'est
faux. Pour la suite `1 2 3 4 1 2 5 1 2 3 4 5` : 9 défauts avec 3 cadres, mais
**10 avec 4 cadres**. LRU et Optimal n'ont jamais ce problème. Essayez dans le
menu (choix 5 pour saisir la suite).

### Dans un vrai système

Optimal est impossible : personne ne connaît l'avenir. Il sert de référence
pour juger les autres. LRU exact coûte trop cher (il faudrait noter l'heure à
chaque accès mémoire), donc les vrais systèmes l'approchent : le processeur
met à 1 un « bit de référence » quand une page est utilisée, et le système
sort en priorité les pages dont le bit est resté à 0.

### Dans notre code (`memoire/remplacement.py`)

Même principe que l'ordonnanceur : **un moteur, trois critères**.

- `simuler(references, nb_cadres, choisir_victime)` est le moteur. Pour chaque
  page demandée il traite trois cas : page présente, cadre libre, mémoire pleine.
- `choisir_fifo`, `choisir_lru`, `choisir_optimal` répondent à la seule question
  « quelle page sortir ? ».
- `fifo`, `lru`, `optimal` appellent le moteur avec le bon critère.

Les variables importantes du moteur :

- `cadres` : la liste des pages en mémoire, `None` pour un cadre vide ;
- `charge_a` : pour chaque page, l'étape où elle a été chargée (sert à FIFO) ;
- `utilise_a` : pour chaque page, l'étape de sa dernière utilisation (sert à LRU) ;
- `etapes` : le résultat, une `Etape` par demande, avec les cadres et une
  explication en français.

## 5. Le TLB

### L'idée

Avec la pagination, chaque accès à une donnée demande deux lectures en
mémoire : la table des pages, puis la donnée. C'est deux fois plus lent.

Le TLB est un pense-bête : il retient les dernières traductions page → cadre.
Si la page y figure (**succès**), on évite la lecture de la table des pages.
Sinon (**échec**), on lit la table, puis on note la traduction dans le TLB.

**Image.** Les numéros favoris de votre téléphone. Appeler un favori est
immédiat. Sinon, il faut chercher dans tout le répertoire.

### Exemple calculé à la main

Pages de 100 octets, pour calculer de tête. TLB de 3 entrées. Table des pages :
page 1 → cadre 7, page 2 → cadre 5, page 5 → cadre 0, page 7 → cadre 4.

| Adresse | Page | TLB | TLB après |
|---|---|---|---|
| 235 | 2 | échec | 2 |
| 240 | 2 | succès | 2 |
| 512 | 5 | échec | 2 5 |
| 199 | 1 | échec | 2 5 1 |
| 260 | 2 | succès | 2 5 1 |
| 530 | 5 | succès | 2 5 1 |
| 701 | 7 | échec, la page 2 sort | 5 1 7 |
| 150 | 1 | succès | 5 1 7 |
| 245 | 2 | échec, la page 5 sort | 1 7 2 |
| 705 | 7 | succès | 1 7 2 |

5 succès sur 10 : **taux de succès = 0,5**.

Exemple d'adresse physique : 235 → page 2, déplacement 35 → cadre 5 →
5 x 100 + 35 = 535.

### Dans un vrai système

Le TLB est un composant du processeur, de quelques dizaines à quelques
milliers d'entrées. Il marche bien parce qu'un programme réutilise souvent les
mêmes pages pendant un moment : c'est le principe de localité.

### Dans notre code (`memoire/tlb.py`)

- `simuler_tlb(adresses, taille_page, table_pages, taille_tlb)` renvoie une
  `EtapeTLB` par adresse.
- `tlb` est une liste de couples `(page, cadre)`, le plus ancien en premier.
  Quand il est plein, `tlb.pop(0)` retire le plus ancien (FIFO).
- `taux_de_succes(etapes)` compte les succès et divise par le nombre d'accès.

## 6. L'EAT : temps d'accès effectif

L'EAT est une moyenne pondérée : le temps d'un succès multiplié par sa
fréquence, plus le temps d'un échec multiplié par la sienne.

### EAT avec TLB

```
succès : temps_TLB + temps_mémoire
échec  : temps_TLB + 2 x temps_mémoire
EAT    = taux x succès + (1 - taux) x échec
```

Exemple : TLB 20 ns, mémoire 100 ns, taux de succès 0,8.

- succès : 20 + 100 = 120 ns
- échec : 20 + 200 = 220 ns
- EAT = 0,8 x 120 + 0,2 x 220 = 96 + 44 = **140 ns**

Sans TLB, chaque accès coûterait 200 ns. Avec le taux 0,5 de notre simulation :
0,5 x 120 + 0,5 x 220 = **170 ns**.

Certains cours négligent le temps du TLB. Donnez alors 0 : 0,8 x 100 + 0,2 x 200
= 120 ns.

### EAT avec défauts de page

```
EAT = (1 - p) x temps_mémoire + p x temps_défaut
```

`p` est la probabilité d'un défaut de page. Exemple : mémoire 200 ns, défaut
8 ms = 8 000 000 ns, p = 0,001.

EAT = 0,999 x 200 + 0,001 x 8 000 000 = 199,8 + 8000 = **8199,8 ns**.

Un seul défaut sur mille accès rend la mémoire environ 40 fois plus lente. Voilà
pourquoi le choix de l'algorithme de remplacement compte autant.

Le sujet dit « TLB et EAT » sans préciser la formule. Le programme propose les
deux. **Vérifiez dans votre cours laquelle le professeur utilise.**

## 7. Exécuter et vérifier

Depuis `code/` : `python3 main.py`, puis `2` (mémoire).

- `1` puis `1`, adresse `1500` : vous devez lire `Adresse physique = 2 x 1024 + 476 = 2524`.
- `2` puis `1`, répondre `o` : FIFO pas à pas. À l'étape 4, la page 7 sort.
- `2` puis `4` : le tableau doit afficher FIFO 15, LRU 12, Optimal 9.
- `3`, Entrée, `3`, `20`, `100` : taux 0.50 et EAT 170.00 ns.

## 8. Erreurs fréquentes

- Confondre page et cadre. La page appartient au processus, le cadre à la RAM.
- Multiplier par le numéro de **page** au lieu du numéro de **cadre**.
- Oublier d'ajouter le déplacement.
- LRU : regarder l'ordre de chargement au lieu de la dernière utilisation.
  C'est FIFO, pas LRU.
- FIFO : croire qu'utiliser une page la « rajeunit ». Non, seule sa date
  d'arrivée compte.
- Optimal : regarder le passé. Il ne regarde que les demandes à venir.
- Compter comme défaut une page déjà présente.
- EAT : oublier le facteur 2 en cas d'échec du TLB, ou mélanger ns et ms.

## 9. Fiche de révision

| Notion | À retenir |
|---|---|
| Page / cadre | même taille ; page = côté processus, cadre = côté RAM |
| Traduction | page = adr // taille ; dépl = adr % taille ; phys = cadre x taille + dépl |
| Défaut de page | page demandée absente de la RAM |
| FIFO | sort la plus anciennement chargée ; simple ; anomalie de Belady |
| LRU | sort la moins récemment utilisée ; bon mais coûteux |
| Optimal | sort celle qui resservira le plus tard ; irréalisable ; sert de référence |
| Exemple classique | 20 demandes, 3 cadres : FIFO 15, LRU 12, Optimal 9 |
| TLB | cache des traductions ; succès = 1 accès, échec = 2 accès |
| EAT (TLB) | a(e + m) + (1 - a)(e + 2m) |
| EAT (défauts) | (1 - p) m + p x temps de défaut |

## 10. Exercices

1. À la main : suite `2 3 2 1 5 2 4 5 3 2 5 2`, 3 cadres, FIFO puis LRU puis
   Optimal. Vérifiez avec le menu (remplacement, choix 5).
2. Pages de 4096 octets, page 3 dans le cadre 9. Adresse physique de l'adresse
   logique 12300 ? Vérifiez avec « Saisir ma propre table des pages ».
3. TLB 10 ns, mémoire 80 ns, taux 0,9. Calculez l'EAT, puis vérifiez.
4. Reprenez l'exemple du TLB avec 1 seule entrée, puis avec 4. Calculez d'abord
   le taux de succès à la main, puis vérifiez avec le menu (réponses : 0,1 et 0,6).
5. Trouvez dans `remplacement.py` la ligne `list(cadres)`. Retirez `list(...)`,
   relancez les tests, lisez l'erreur, puis remettez le code d'origine.
