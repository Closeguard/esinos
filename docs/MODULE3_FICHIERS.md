# Module 3 (bonus) — Le système de fichiers, expliqué pas à pas

## 1. Le problème à résoudre

Un disque ne connaît pas les fichiers. Il ne voit qu'une longue suite de
**blocs** numérotés. Le système de fichiers est l'organisation qui permet de
dire : « le fichier `notes.txt` fait 81 octets et se trouve dans les blocs 10
et 11 ».

**Image de la vie courante : une bibliothèque.**

- les étagères = les **blocs** de données ;
- la fiche d'un livre (sa taille, ses étagères) = un **inode** ;
- le catalogue (titre → numéro de fiche) = le **répertoire** ;
- le plan des étagères libres = la **carte des blocs** ;
- le panneau à l'entrée (taille de la bibliothèque) = le **superbloc**.

Point important : le titre du livre est dans le catalogue, **pas sur la fiche**.
De même, le nom d'un fichier est dans le répertoire, pas dans l'inode.

## 2. Les mots à connaître

- **Bloc** : unité de lecture et d'écriture du disque. Ici, 64 octets.
- **Inode** : la fiche d'un fichier. Contient sa taille et les numéros de ses blocs.
- **Pointeur direct** : un numéro de bloc rangé dans l'inode.
- **Répertoire** : table qui associe un nom à un numéro d'inode.
- **Carte des blocs** (bitmap) : dit pour chaque bloc s'il est libre ou occupé.
- **Superbloc** : premier bloc, qui décrit le disque.
- **Formater** : écrire sur le disque une organisation vide.
- **Fichier-disque** : le fichier de votre ordinateur qui joue le rôle du disque.

## 3. Le plan de notre disque

64 blocs de 64 octets, soit un fichier `disque_esinos.img` de 4096 octets.

| Blocs | Contenu |
|---|---|
| 0 | superbloc |
| 1 | carte des blocs : 1 octet par bloc, 0 = libre, 1 = occupé |
| 2 à 5 | table des inodes : 16 inodes de 16 octets |
| 6 à 9 | répertoire : 16 entrées de 16 octets |
| 10 à 63 | données : 54 blocs |

Un inode contient : un indicateur « utilisé », la taille, et 6 numéros de blocs.
Un fichier fait donc au plus 6 x 64 = **384 octets**, et il y a au plus
**16 fichiers**.

## 4. Créer un fichier, étape par étape

On crée `notes.txt` avec un texte de 81 octets sur un disque vide.

1. **Vérifier** : le nom est valide, il n'existe pas déjà, 81 ≤ 384.
2. **Trouver un inode libre** : le premier libre est l'inode 0.
3. **Compter les blocs** : 81 octets dans des blocs de 64. Un bloc ne suffit
   pas, il en faut 2. Formule : `(81 + 63) // 64 = 2`.
4. **Trouver 2 blocs libres** dans la carte : les blocs 10 et 11.
5. **Écrire les données** : les 64 premiers octets dans le bloc 10, les 17
   suivants dans le bloc 11.
6. **Marquer** les blocs 10 et 11 occupés dans la carte.
7. **Remplir l'inode 0** : utilisé, taille 81, blocs 10 et 11.
8. **Ajouter** au répertoire : `notes.txt` → inode 0.

La carte des blocs devient :

```
blocs  0 à 15 : SCIIIIRRRR##....
```

## 5. Lire et supprimer

**Lire** `notes.txt` suit le chemin inverse :

1. répertoire : `notes.txt` → inode 0 ;
2. inode 0 : taille 81, blocs 10 et 11 ;
3. lire les blocs 10 et 11, soit 128 octets ;
4. ne garder que les 81 premiers.

**Supprimer** `notes.txt` :

1. marquer les blocs 10 et 11 libres dans la carte ;
2. marquer l'inode 0 libre ;
3. retirer le nom du répertoire.

Les octets du texte restent dans les blocs 10 et 11 : on ne les efface pas, on
déclare seulement la place libre. Un vrai disque fait pareil, ce qui explique
qu'on puisse parfois récupérer un fichier supprimé.

## 6. La fragmentation, visible dans la démo

Créez `a` (150 octets, blocs 10 11 12), puis `b` (10 octets, bloc 13).
Supprimez `a`. Créez `c` (100 octets) : il prend 10 et 11. Créez `d`
(100 octets) : il prend **12 et 14**, deux blocs qui ne se touchent pas.
Grâce à l'inode, qui liste ses blocs un par un, cela ne pose aucun problème.

## 7. Dans un vrai système

Les systèmes de fichiers de Linux (famille ext) reposent sur les mêmes
pièces : superbloc, cartes des blocs libres, table d'inodes, répertoires.
Les différences avec notre version :

- un vrai inode contient aussi le propriétaire, les permissions et les dates ;
- quand les pointeurs directs ne suffisent pas, un pointeur **indirect**
  désigne un bloc rempli d'autres numéros de blocs, ce qui autorise de très
  gros fichiers ;
- un répertoire est lui-même un fichier, et il peut contenir d'autres
  répertoires ;
- la carte utilise 1 bit par bloc, nous utilisons 1 octet pour rester lisibles.

Sous Linux ou Mac, `ls -i` affiche le numéro d'inode de chaque fichier.

## 8. Dans notre code

Deux fichiers, deux niveaux, comme dans un vrai système.

**`fichiers/disque.py` : le disque.** Il ne sait faire que deux choses :
`lire_bloc(numero)` et `ecrire_bloc(numero, donnees)`. Il ignore tout des
fichiers. La ligne clé est `fichier.seek(numero * TAILLE_BLOC)` : le bloc
numéro n commence à l'octet n x 64.

**`fichiers/systeme_fichiers.py` : l'organisation.** Il ne touche jamais au
fichier-disque directement : il passe toujours par `lire_bloc` et `ecrire_bloc`.

- `formater()` : écrit le superbloc et marque les blocs 0 à 9 occupés.
- `lire_inodes()` / `ecrire_inode(inode)` : lisent et écrivent la table des inodes.
- `lire_repertoire()` / `ecrire_repertoire(d)` : idem pour le répertoire, vu
  comme un dictionnaire `{nom: numéro d'inode}`.
- `blocs_libres()` : lit la carte et renvoie les blocs de données libres.
- `creer(nom, contenu)`, `lire(nom)`, `supprimer(nom)` : les trois opérations
  demandées, écrites exactement comme les étapes des parties 4 et 5.
- `ErreurFichier` : notre type d'erreur pour les cas normaux (fichier
  introuvable, disque plein). Le menu l'attrape et affiche le message.

Deux notions Python nouvelles :

- `bytes` : une suite d'octets. Sur un disque, tout est octets. `texte.encode("utf-8")`
  transforme un texte en octets, `octets.decode("utf-8")` fait l'inverse.
- `nombre.to_bytes(2, "big")` écrit un nombre sur 2 octets, et
  `int.from_bytes(octets, "big")` le relit.

## 9. Exécuter et vérifier

Depuis `code/` : `python3 main.py`, puis `3`. Répondez `o` pour formater.

1. `1`, nom `notes.txt`, un texte de plus de 64 caractères.
2. `4` : le fichier apparaît avec son inode et deux blocs.
3. `5` : la table des inodes. Aucun nom n'y figure.
4. `6` : la carte des blocs, avec `##` aux positions 10 et 11.
5. `2`, `notes.txt` : le texte revient intact.
6. Quittez le programme, relancez-le, relisez le fichier : il est toujours là.
7. `3`, `notes.txt`, puis `6` : les blocs sont redevenus libres.

## 10. Erreurs fréquentes

- Dire que le nom du fichier est dans l'inode. Il est dans le répertoire.
- Confondre taille en octets et nombre de caractères : « é » occupe 2 octets.
- Oublier d'arrondir au bloc supérieur : 65 octets demandent 2 blocs, pas 1.
- Croire que supprimer efface les données.
- Lire tout le dernier bloc au lieu de s'arrêter à la taille du fichier.

## 11. Fiche de révision

| Notion | À retenir |
|---|---|
| Bloc | unité du disque, taille fixe (ici 64 octets) |
| Inode | taille + numéros des blocs ; pas de nom |
| Répertoire | nom → numéro d'inode |
| Carte des blocs | libre ou occupé, pour chaque bloc |
| Superbloc | description du disque, au bloc 0 |
| Créer | inode libre, blocs libres, données, carte, inode, répertoire |
| Lire | répertoire → inode → blocs → couper à la taille |
| Supprimer | libérer blocs et inode, retirer le nom ; données non effacées |
| Limites du projet | 16 fichiers, 384 octets par fichier, un seul répertoire |

## 12. Exercices

1. Combien de blocs pour un fichier de 64 octets ? De 129 octets ? De 0 octet ?
   Vérifiez avec le menu.
2. Créez 16 petits fichiers, puis un 17e. Quel message obtenez-vous, et quelle
   ressource manque ?
3. Refaites le scénario de fragmentation de la partie 6 et montrez la carte.
4. Ouvrez `disque_esinos.img` avec la commande `xxd disque_esinos.img | head`
   (Mac, Linux). Retrouvez les lettres `ESFS` au tout début : c'est le superbloc.
