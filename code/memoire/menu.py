"""
menu.py — Le sous-menu du gestionnaire mémoire.

Aucun calcul ici : on pose des questions, on appelle les fonctions des
autres fichiers, on affiche leurs résultats.
"""

from interface import (titre, pause, demander_entier, demander_liste_entiers,
                       demander_reel)
from memoire.pagination import (decouper_adresse, traduire, bits_deplacement,
                                DefautDePage)
from memoire.remplacement import fifo, lru, optimal
from memoire.tlb import simuler_tlb, taux_de_succes, eat_tlb, eat_defauts
from memoire.affichage import (formater_etape, formater_tableau,
                               formater_comparaison, formater_tlb)


# ----------------------------------------------------------------------
# Exemples chargés au démarrage (les mêmes que dans le guide et les tests)
# ----------------------------------------------------------------------

def exemple_references():
    """La suite de références classique des manuels, avec 3 cadres."""
    return [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1], 3


def exemple_pagination():
    """Pages de 1024 octets ; la page 2 n'est pas chargée (None)."""
    return 1024, {0: 5, 1: 2, 2: None, 3: 7}


def exemple_tlb():
    """Pages de 100 octets pour calculer de tête : l'adresse 235 = page 2, dépl. 35."""
    taille_page = 100
    table_pages = {0: 3, 1: 7, 2: 5, 3: 1, 4: 6, 5: 0, 6: 2, 7: 4}
    adresses = [235, 240, 512, 199, 260, 530, 701, 150, 245, 705]
    taille_tlb = 3
    return adresses, taille_page, table_pages, taille_tlb


# ----------------------------------------------------------------------
# Pagination
# ----------------------------------------------------------------------

def afficher_table_pages(taille_page, table_pages):
    print(f"Taille d'une page : {taille_page} octets")
    bits = bits_deplacement(taille_page)
    if bits is not None:
        print(f"({taille_page} = 2 puissance {bits} : le déplacement tient sur {bits} bits)")
    print(f"{'Page':>6}{'Cadre':>8}")
    for page in sorted(table_pages):
        cadre = table_pages[page]
        print(f"{page:>6}{'absente' if cadre is None else cadre:>8}")


def saisir_table_pages():
    taille_page = demander_entier("Taille d'une page (en octets) : ", 1)
    nombre = demander_entier("Nombre de pages du processus : ", 1)
    table_pages = {}
    for page in range(nombre):
        cadre = demander_entier(f"  Cadre de la page {page} (-1 si elle n'est pas en mémoire) : ", -1)
        table_pages[page] = None if cadre == -1 else cadre
    return taille_page, table_pages


def menu_pagination():
    taille_page, table_pages = exemple_pagination()
    while True:
        titre("MÉMOIRE - Traduction d'adresse")
        afficher_table_pages(taille_page, table_pages)
        print()
        print("1. Traduire une adresse logique")
        print("2. Saisir ma propre table des pages")
        print("3. Revenir à l'exemple")
        print("0. Retour")
        choix = input("Votre choix : ").strip()

        if choix == "1":
            adresse = demander_entier("Adresse logique : ", 0)
            page, deplacement = decouper_adresse(adresse, taille_page)
            print(f"  Page        = {adresse} // {taille_page} = {page}")
            print(f"  Déplacement = {adresse} %  {taille_page} = {deplacement}")
            try:
                physique = traduire(adresse, taille_page, table_pages)
                cadre = table_pages[page]
                print(f"  La page {page} est dans le cadre {cadre}.")
                print(f"  Adresse physique = {cadre} x {taille_page} + {deplacement} = {physique}")
            except DefautDePage as erreur:
                print(f"  {erreur}")
                print("  Un vrai système chargerait la page depuis le disque, puis recommencerait.")
            except ValueError as erreur:
                print(f"  Erreur : {erreur}")
            pause()
        elif choix == "2":
            taille_page, table_pages = saisir_table_pages()
        elif choix == "3":
            taille_page, table_pages = exemple_pagination()
        elif choix == "0":
            return
        else:
            print("Choix inconnu.")


# ----------------------------------------------------------------------
# Remplacement de pages
# ----------------------------------------------------------------------

def derouler(nom, etapes):
    """Affiche une simulation, étape par étape ou d'un seul coup."""
    titre(f"{nom} - {len(etapes[0].cadres)} cadres")
    reponse = input("Pas à pas ? (o = oui, autre touche = tout afficher) : ").strip().lower()

    if reponse == "o":
        print("À chaque étape : Entrée = suivante, t = terminer d'un coup.")
        for etape in etapes:
            print()
            print(formater_etape(etape))
            if input("").strip().lower() == "t":
                break
        print()
        print("Récapitulatif :")

    print(formater_tableau(etapes))
    pause()


def menu_remplacement():
    references, nb_cadres = exemple_references()
    while True:
        titre("MÉMOIRE - Remplacement de pages")
        print("Suite de références : " + " ".join(str(page) for page in references))
        print(f"Nombre de cadres    : {nb_cadres}")
        print()
        print("1. FIFO")
        print("2. LRU")
        print("3. Optimal")
        print("4. Comparer les trois algorithmes")
        print("5. Saisir ma suite de références et mon nombre de cadres")
        print("6. Revenir à l'exemple")
        print("0. Retour")
        choix = input("Votre choix : ").strip()

        if choix == "1":
            derouler("FIFO", fifo(references, nb_cadres))
        elif choix == "2":
            derouler("LRU", lru(references, nb_cadres))
        elif choix == "3":
            derouler("Optimal", optimal(references, nb_cadres))
        elif choix == "4":
            print()
            print(formater_comparaison(references, nb_cadres))
            pause()
        elif choix == "5":
            references = demander_liste_entiers(
                "Pages demandées, séparées par des espaces : ", 0)
            nb_cadres = demander_entier("Nombre de cadres : ", 1)
        elif choix == "6":
            references, nb_cadres = exemple_references()
        elif choix == "0":
            return
        else:
            print("Choix inconnu.")


# ----------------------------------------------------------------------
# TLB et EAT
# ----------------------------------------------------------------------

def lancer_tlb():
    adresses, taille_page, table_pages, taille_tlb = exemple_tlb()
    titre("MÉMOIRE - Simulation du TLB")
    print(f"Exemple : pages de {taille_page} octets, "
          f"{len(table_pages)} pages toutes en mémoire.")
    print("Adresses par défaut : " + " ".join(str(a) for a in adresses))

    if input("Saisir mes propres adresses ? (o = oui) : ").strip().lower() == "o":
        maximum = taille_page * len(table_pages) - 1
        print(f"Adresses autorisées : de 0 à {maximum}.")
        adresses = demander_liste_entiers("Adresses, séparées par des espaces : ", 0)
    taille_tlb = demander_entier(f"Nombre d'entrées du TLB (exemple : {taille_tlb}) : ", 1)

    try:
        etapes = simuler_tlb(adresses, taille_page, table_pages, taille_tlb)
    except ValueError as erreur:
        print(f"Erreur : {erreur}")
        pause()
        return

    print()
    print(formater_tlb(etapes))
    taux = taux_de_succes(etapes)
    print()
    print(f"Taux de succès du TLB : {taux:.2f} ({100 * taux:.0f} %)")

    print()
    print("Calcul de l'EAT avec ce taux :")
    temps_tlb = demander_reel("  Temps de consultation du TLB, en ns (exemple : 20) : ", 0)
    temps_memoire = demander_reel("  Temps d'un accès mémoire, en ns (exemple : 100) : ", 0)
    afficher_eat_tlb(taux, temps_tlb, temps_memoire)
    pause()


def nombre(valeur):
    """Écrit 100.0 sous la forme "100", et laisse 0.8 tel quel."""
    if valeur == int(valeur):
        return str(int(valeur))
    return f"{valeur:g}"


def afficher_eat_tlb(taux, temps_tlb, temps_memoire):
    """Affiche le calcul de l'EAT ligne par ligne, comme on l'écrirait à la main."""
    succes = temps_tlb + temps_memoire
    echec = temps_tlb + 2 * temps_memoire
    eat = eat_tlb(taux, temps_tlb, temps_memoire)
    print(f"  Succès : {nombre(temps_tlb)} + {nombre(temps_memoire)} = {nombre(succes)} ns")
    print(f"  Échec  : {nombre(temps_tlb)} + 2 x {nombre(temps_memoire)} = {nombre(echec)} ns")
    print(f"  EAT = {taux:g} x {nombre(succes)} + {1 - taux:g} x {nombre(echec)}"
          f" = {eat:.2f} ns")


def menu_eat():
    while True:
        titre("MÉMOIRE - Calcul d'un EAT")
        print("1. EAT avec TLB (taux de succès)")
        print("2. EAT avec défauts de page (taux de défaut)")
        print("0. Retour")
        choix = input("Votre choix : ").strip()

        if choix == "1":
            taux = demander_reel("Taux de succès du TLB, entre 0 et 1 (exemple : 0.8) : ", 0, 1)
            temps_tlb = demander_reel("Temps de consultation du TLB, en ns (exemple : 20) : ", 0)
            temps_memoire = demander_reel("Temps d'un accès mémoire, en ns (exemple : 100) : ", 0)
            afficher_eat_tlb(taux, temps_tlb, temps_memoire)
            pause()
        elif choix == "2":
            taux = demander_reel("Taux de défaut de page, entre 0 et 1 (exemple : 0.001) : ", 0, 1)
            temps_memoire = demander_reel("Temps d'un accès mémoire, en ns (exemple : 200) : ", 0)
            temps_defaut = demander_reel(
                "Temps de traitement d'un défaut, en ns (exemple : 8000000) : ", 0)
            eat = eat_defauts(taux, temps_memoire, temps_defaut)
            print(f"  EAT = {1 - taux:g} x {nombre(temps_memoire)} + {taux:g} x "
                  f"{nombre(temps_defaut)} = {eat:.2f} ns")
            pause()
        elif choix == "0":
            return
        else:
            print("Choix inconnu.")


# ----------------------------------------------------------------------
# Menu du module
# ----------------------------------------------------------------------

def menu_memoire():
    while True:
        titre("GESTIONNAIRE MÉMOIRE")
        print("1. Traduction d'adresse (pagination)")
        print("2. Remplacement de pages (FIFO, LRU, Optimal)")
        print("3. Simulation du TLB, puis EAT")
        print("4. Calculer un EAT avec mes valeurs")
        print("0. Retour au menu principal")
        choix = input("Votre choix : ").strip()

        if choix == "1":
            menu_pagination()
        elif choix == "2":
            menu_remplacement()
        elif choix == "3":
            lancer_tlb()
        elif choix == "4":
            menu_eat()
        elif choix == "0":
            return
        else:
            print("Choix inconnu.")
