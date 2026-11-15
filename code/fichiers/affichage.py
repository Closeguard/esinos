"""
affichage.py — Met en forme l'état du système de fichiers (renvoie du texte).
"""

from fichiers.disque import NB_BLOCS
from fichiers.systeme_fichiers import (BLOC_SUPERBLOC, BLOC_CARTE,
                                       PREMIER_BLOC_INODES,
                                       PREMIER_BLOC_REPERTOIRE,
                                       PREMIER_BLOC_DONNEES)


def formater_liste(fichiers):
    """Liste des fichiers : nom, inode, taille, blocs."""
    if len(fichiers) == 0:
        return "(aucun fichier)"
    lignes = [f"{'Nom':<16}{'Inode':>6}{'Taille':>8}  Blocs"]
    for nom, numero_inode, taille, blocs in fichiers:
        texte_blocs = " ".join(str(b) for b in blocs) if blocs else "-"
        lignes.append(f"{nom:<16}{numero_inode:>6}{taille:>8}  {texte_blocs}")
    return "\n".join(lignes)


def formater_inodes(inodes):
    """Table des inodes. Remarquez qu'aucun nom de fichier n'y figure."""
    lignes = [f"{'Inode':>5}  {'État':<8}{'Taille':>7}  Blocs de données"]
    for inode in inodes:
        if inode.utilise:
            texte_blocs = " ".join(str(b) for b in inode.blocs) if inode.blocs else "-"
            lignes.append(f"{inode.numero:>5}  {'utilisé':<8}{inode.taille:>7}  {texte_blocs}")
        else:
            lignes.append(f"{inode.numero:>5}  {'libre':<8}{'-':>7}  -")
    return "\n".join(lignes)


def formater_carte(carte):
    """Dessine les 64 blocs du disque, 16 par ligne.

    S = superbloc, C = carte des blocs, I = inodes, R = répertoire,
    # = bloc de données occupé, . = bloc de données libre
    """
    symboles = ""
    for numero in range(NB_BLOCS):
        if numero == BLOC_SUPERBLOC:
            symboles = symboles + "S"
        elif numero == BLOC_CARTE:
            symboles = symboles + "C"
        elif numero < PREMIER_BLOC_REPERTOIRE and numero >= PREMIER_BLOC_INODES:
            symboles = symboles + "I"
        elif numero < PREMIER_BLOC_DONNEES:
            symboles = symboles + "R"
        elif carte[numero] == 1:
            symboles = symboles + "#"
        else:
            symboles = symboles + "."

    lignes = []
    for debut in range(0, NB_BLOCS, 16):
        lignes.append(f"blocs {debut:>2} à {debut + 15:>2} : {symboles[debut:debut + 16]}")
    lignes.append("S superbloc, C carte, I inodes, R répertoire, # occupé, . libre")
    return "\n".join(lignes)
