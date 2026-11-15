"""
menu.py — Le sous-menu du système de fichiers (bonus).
"""

from interface import titre, pause, demander_texte
from fichiers.systeme_fichiers import (SystemeFichiers, ErreurFichier,
                                       TAILLE_MAX_FICHIER, TAILLE_NOM)
from fichiers.affichage import formater_liste, formater_inodes, formater_carte

# Le fichier-disque est créé dans le dossier d'où l'on lance le programme.
CHEMIN_DISQUE = "disque_esinos.img"


def menu_fichiers(chemin=CHEMIN_DISQUE):
    sf = SystemeFichiers(chemin)

    while True:
        titre("SYSTÈME DE FICHIERS (bonus)")
        print(f"Fichier-disque : {chemin}")

        # Tant que le disque n'est pas formaté, on ne peut rien faire d'autre.
        if not sf.est_formate():
            print("Ce disque n'existe pas encore ou n'est pas formaté.")
            reponse = input("Le créer et le formater maintenant ? (o = oui) : ").strip().lower()
            if reponse != "o":
                return
            try:
                sf.formater()
            except OSError as erreur:
                print(f"Impossible de créer le fichier-disque : {erreur}")
                pause()
                return
            print("Disque formaté : 64 blocs de 64 octets, 16 inodes.")
            continue

        print(f"Blocs de données libres : {len(sf.blocs_libres())}")
        print()
        print("1. Créer un fichier")
        print("2. Lire un fichier")
        print("3. Supprimer un fichier")
        print("4. Lister les fichiers")
        print("5. Afficher la table des inodes")
        print("6. Afficher la carte des blocs")
        print("7. Formater le disque (efface tout)")
        print("0. Retour au menu principal")
        choix = input("Votre choix : ").strip()

        # Une seule gestion d'erreur pour toutes les opérations : le menu
        # affiche le message et continue, il ne plante jamais.
        try:
            if choix == "1":
                nom = demander_texte(f"Nom du fichier ({TAILLE_NOM} caractères maximum) : ")
                contenu = input(f"Contenu ({TAILLE_MAX_FICHIER} octets maximum) : ")
                numero = sf.creer(nom, contenu)
                print(f"Fichier '{nom}' créé avec l'inode {numero}.")
                pause()
            elif choix == "2":
                nom = demander_texte("Nom du fichier à lire : ")
                contenu = sf.lire(nom)
                print(f"--- Contenu de '{nom}' ---")
                print(contenu)
                print("--- fin ---")
                pause()
            elif choix == "3":
                nom = demander_texte("Nom du fichier à supprimer : ")
                sf.supprimer(nom)
                print(f"Fichier '{nom}' supprimé : son inode et ses blocs sont libérés.")
                pause()
            elif choix == "4":
                print()
                print(formater_liste(sf.lister()))
                pause()
            elif choix == "5":
                print()
                print(formater_inodes(sf.lire_inodes()))
                pause()
            elif choix == "6":
                print()
                print(formater_carte(sf.lire_carte()))
                pause()
            elif choix == "7":
                reponse = input("Tout effacer ? Tapez oui pour confirmer : ").strip().lower()
                if reponse == "oui":
                    sf.formater()
                    print("Disque formaté.")
                else:
                    print("Formatage annulé.")
                pause()
            elif choix == "0":
                return
            else:
                print("Choix inconnu.")
        except ErreurFichier as erreur:
            print(f"Erreur : {erreur}")
            pause()
        except OSError as erreur:
            # Problème venant de l'ordinateur lui-même (dossier protégé, disque plein...).
            print(f"Impossible d'accéder au fichier-disque : {erreur}")
            pause()
