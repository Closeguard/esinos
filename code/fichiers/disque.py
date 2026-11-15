"""
disque.py — Le disque simulé.

Un vrai disque est une longue suite de BLOCS de taille fixe, numérotés
0, 1, 2... On ne peut lire ou écrire qu'un bloc entier à la fois.

Ici, le disque est un simple fichier de l'ordinateur (le "fichier-disque").
Le bloc numéro n commence à l'octet n * TAILLE_BLOC de ce fichier.

Ce fichier ne sait RIEN des fichiers, des noms ou des inodes : il sait
seulement lire et écrire un bloc. Tout le reste est dans systeme_fichiers.py.
"""

import os

TAILLE_BLOC = 64   # octets par bloc (petit exprès : un texte court occupe plusieurs blocs)
NB_BLOCS = 64      # nombre de blocs du disque -> disque de 64 x 64 = 4096 octets


class Disque:

    def __init__(self, chemin):
        self.chemin = chemin   # emplacement du fichier-disque sur l'ordinateur

    def existe(self):
        return os.path.exists(self.chemin)

    def creer(self):
        """Crée un disque vierge : NB_BLOCS blocs remplis de zéros."""
        with open(self.chemin, "wb") as fichier:
            fichier.write(bytes(TAILLE_BLOC * NB_BLOCS))

    def verifier_numero(self, numero):
        if numero < 0 or numero >= NB_BLOCS:
            raise ValueError(f"Bloc {numero} inexistant (le disque a {NB_BLOCS} blocs).")

    def lire_bloc(self, numero):
        """Renvoie les TAILLE_BLOC octets du bloc demandé."""
        self.verifier_numero(numero)
        with open(self.chemin, "rb") as fichier:
            fichier.seek(numero * TAILLE_BLOC)   # se placer au début du bloc
            return fichier.read(TAILLE_BLOC)

    def ecrire_bloc(self, numero, donnees):
        """Écrit un bloc. Si `donnees` est plus court, on complète avec des zéros."""
        self.verifier_numero(numero)
        if len(donnees) > TAILLE_BLOC:
            raise ValueError("Trop de données pour un seul bloc.")
        donnees = donnees + bytes(TAILLE_BLOC - len(donnees))
        # "r+b" : ouvrir un fichier existant pour le modifier, sans l'effacer.
        with open(self.chemin, "r+b") as fichier:
            fichier.seek(numero * TAILLE_BLOC)
            fichier.write(donnees)
