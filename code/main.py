"""
main.py — Point d'entrée d'ESINOS, le mini-noyau simulé.

Lancement (depuis le dossier code/) :

    python3 main.py          (Mac, Linux)
    python main.py           (Windows)

Ce fichier ne contient que le menu principal. Chaque module vit dans son
propre dossier et fournit son sous-menu :

    ordonnanceur/   FCFS, SJF, Round Robin, Priority
    memoire/        pagination, FIFO, LRU, Optimal, TLB, EAT
    fichiers/       mini système de fichiers à inodes (bonus)
"""

from interface import titre
from ordonnanceur.menu import menu_ordonnanceur
from memoire.menu import menu_memoire
from fichiers.menu import menu_fichiers


def menu_principal():
    while True:
        titre("ESINOS - Mini-noyau simulé")
        print("1. Ordonnanceur de processus")
        print("2. Gestionnaire mémoire")
        print("3. Système de fichiers (bonus)")
        print("0. Quitter")
        choix = input("Votre choix : ").strip()

        if choix == "1":
            menu_ordonnanceur()
        elif choix == "2":
            menu_memoire()
        elif choix == "3":
            menu_fichiers()
        elif choix == "0":
            print("Au revoir.")
            return
        else:
            print("Choix inconnu : tapez 1, 2, 3 ou 0.")


if __name__ == "__main__":
    try:
        menu_principal()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C ou fin de l'entrée : on quitte proprement, sans message d'erreur.
        print("\nAu revoir.")
