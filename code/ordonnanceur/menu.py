"""
menu.py — Le sous-menu de l'ordonnanceur (ce que l'utilisateur voit).

Ce fichier ne fait aucun calcul : il pose des questions, appelle les
fonctions des autres fichiers et affiche leurs résultats.
"""

from interface import titre, pause, demander_entier
from ordonnanceur.modeles import Processus
from ordonnanceur.algorithmes import fcfs, sjf, priorite, round_robin
from ordonnanceur.statistiques import calculer_statistiques
from ordonnanceur.affichage import dessiner_gantt, formater_statistiques


def exemple():
    """Le jeu de processus utilisé dans le guide, les tests et la démo."""
    return [
        Processus("P1", arrivee=0, duree=5, priorite=3),
        Processus("P2", arrivee=1, duree=3, priorite=4),
        Processus("P3", arrivee=2, duree=8, priorite=1),
        Processus("P4", arrivee=3, duree=6, priorite=2),
    ]


def saisir_processus():
    """Demande les processus un par un au clavier."""
    nombre = demander_entier("Combien de processus ? ", 1)
    liste = []
    for numero in range(1, nombre + 1):
        nom = f"P{numero}"
        print(f"--- {nom} ---")
        arrivee = demander_entier("  Instant d'arrivée : ", 0)
        duree = demander_entier("  Durée d'exécution : ", 1)
        prio = demander_entier("  Priorité (petit nombre = prioritaire) : ", 0)
        liste.append(Processus(nom, arrivee, duree, prio))
    return liste


def afficher_processus(liste):
    print(f"{'Processus':<10}{'Arrivée':>8}{'Durée':>7}{'Priorité':>10}")
    for p in liste:
        print(f"{p.nom:<10}{p.arrivee:>8}{p.duree:>7}{p.priorite:>10}")


def afficher_resultat(titre, processus, gantt):
    """Affiche le Gantt puis le tableau des temps pour un algorithme."""
    lignes, attente_moyenne, sejour_moyen = calculer_statistiques(processus, gantt)
    print()
    titre("Ordonnanceur")
    print(formater_statistiques(lignes, attente_moyenne, sejour_moyen))
    print(f"Utilisation CPU : {calculer_utilisation_cpu(gantt):.2f}%")

def comparer(processus, quantum):
    """Lance les quatre algorithmes et affiche seulement les moyennes."""
    resultats = [
        ("FCFS", fcfs(processus)),
        ("SJF", sjf(processus)),
        (f"Round Robin (q={quantum})", round_robin(processus, quantum)),
        ("Priority", priorite(processus)),
    ]
    print()
    print(f"{'Algorithme':<20}{'Attente moy.':>14}{'Séjour moy.':>14}")
    for nom, gantt in resultats:
        lignes, attente_moyenne, sejour_moyen = calculer_statistiques(processus, gantt)
        print(f"{nom:<20}{attente_moyenne:>14.2f}{sejour_moyen:>14.2f}")


def menu_ordonnanceur():
    processus = exemple()   # on démarre avec l'exemple, prêt pour la démo

    while True:
        titre("ORDONNANCEUR DE PROCESSUS")
        afficher_processus(processus)
        print()
        print("1. FCFS")
        print("2. SJF")
        print("3. Round Robin")
        print("4. Priority")
        print("5. Comparer les quatre algorithmes")
        print("6. Saisir mes propres processus")
        print("7. Revenir à l'exemple")
        print("0. Retour au menu principal")
        choix = input("Votre choix : ").strip()

        if choix == "1":
            afficher_resultat("FCFS", processus, fcfs(processus))
            pause()
        elif choix == "2":
            afficher_resultat("SJF", processus, sjf(processus))
            pause()
        elif choix == "3":
            quantum = demander_entier("Quantum : ", 1)
            afficher_resultat(f"Round Robin (quantum = {quantum})",
                              processus, round_robin(processus, quantum))
            pause()
        elif choix == "4":
            afficher_resultat("Priority", processus, priorite(processus))
            pause()
        elif choix == "5":
            quantum = demander_entier("Quantum pour Round Robin : ", 1)
            comparer(processus, quantum)
            pause()
        elif choix == "6":
            processus = saisir_processus()
        elif choix == "7":
            processus = exemple()
        elif choix == "0":
            return
        else:
            print("Choix inconnu.")
