"""
algorithmes.py — Les quatre algorithmes d'ordonnancement.

Chaque fonction reçoit une liste de Processus et renvoie un diagramme de
Gantt, c'est-à-dire une liste de Segment dans l'ordre du temps.

    fcfs(processus)                  -> premier arrivé, premier servi
    sjf(processus)                   -> le plus court d'abord
    priorite(processus)              -> le plus prioritaire d'abord
    round_robin(processus, quantum)  -> chacun son tour, par tranches

Les trois premiers sont NON préemptifs : un processus qui a commencé va
jusqu'au bout. Seul Round Robin est préemptif : il peut interrompre un
processus pour passer au suivant.

Les fonctions ne modifient jamais les processus reçus.
"""

from ordonnanceur.modeles import INACTIF, Segment, verifier_processus


# ----------------------------------------------------------------------
# Outil commun
# ----------------------------------------------------------------------

def ajouter_segment(gantt, nom, debut, fin):
    """Ajoute une case au Gantt.

    Si la case précédente concerne déjà le même processus et se termine
    exactement à `debut`, on l'allonge au lieu d'en créer une deuxième
    (sinon Round Robin afficherait P3 | P3 au lieu d'un seul bloc P3).
    """
    if gantt and gantt[-1].nom == nom and gantt[-1].fin == debut:
        gantt[-1].fin = fin
    else:
        gantt.append(Segment(nom, debut, fin))


# ----------------------------------------------------------------------
# FCFS, SJF et Priority : même moteur, critère de choix différent
# ----------------------------------------------------------------------
#
# Un "critère" est une petite fonction qui donne une note à un processus.
# Le moteur choisit toujours le processus prêt qui a la PLUS PETITE note.
#
# Quand la note est un couple (a, b), Python compare d'abord a ; il ne
# regarde b que si les deux a sont égaux. Cela sert à départager.
# S'il reste une égalité parfaite, c'est le premier de la liste qui gagne.

def critere_fcfs(p):
    return p.arrivee                # le plus tôt arrivé


def critere_sjf(p):
    return (p.duree, p.arrivee)     # le plus court, puis le plus tôt arrivé


def critere_priorite(p):
    return (p.priorite, p.arrivee)  # le plus petit numéro de priorité


def ordonnancer_sans_preemption(processus, critere):
    """Moteur commun aux algorithmes non préemptifs.

    Idée : à chaque fois que le CPU est libre, on regarde qui est prêt,
    on choisit le meilleur selon `critere`, et on le laisse finir.
    """
    verifier_processus(processus)

    restants = list(processus)  # copie : on ne touche pas à la liste d'origine
    gantt = []
    temps = 0                   # l'horloge de la simulation

    while len(restants) > 0:
        # 1. Qui est déjà arrivé ?
        prets = []
        for p in restants:
            if p.arrivee <= temps:
                prets.append(p)

        # 2. Personne : le CPU attend jusqu'à la prochaine arrivée.
        if len(prets) == 0:
            prochaine_arrivee = min(p.arrivee for p in restants)
            ajouter_segment(gantt, INACTIF, temps, prochaine_arrivee)
            temps = prochaine_arrivee
            continue

        # 3. On choisit le meilleur et on l'exécute en entier.
        choisi = min(prets, key=critere)
        ajouter_segment(gantt, choisi.nom, temps, temps + choisi.duree)
        temps = temps + choisi.duree
        restants.remove(choisi)

    return gantt


def fcfs(processus):
    """First Come, First Served : on sert dans l'ordre d'arrivée."""
    return ordonnancer_sans_preemption(processus, critere_fcfs)


def sjf(processus):
    """Shortest Job First (non préemptif) : le plus court parmi les prêts."""
    return ordonnancer_sans_preemption(processus, critere_sjf)


def priorite(processus):
    """Priority (non préemptif) : petit numéro = priorité haute."""
    return ordonnancer_sans_preemption(processus, critere_priorite)


# ----------------------------------------------------------------------
# Round Robin : le seul algorithme préemptif
# ----------------------------------------------------------------------

def faire_entrer_les_arrives(a_venir, file, temps):
    """Déplace dans la file tous les processus déjà arrivés à l'instant `temps`.

    `a_venir` est trié par instant d'arrivée : il suffit donc de regarder
    le premier élément, encore et encore.
    """
    while len(a_venir) > 0 and a_venir[0].arrivee <= temps:
        file.append(a_venir.pop(0))


def round_robin(processus, quantum):
    """Round Robin : chaque processus reçoit au plus `quantum` unités de temps,
    puis retourne au bout de la file s'il n'a pas terminé.

    Convention (celle des manuels) : si un processus arrive pendant qu'un
    autre tourne, il entre dans la file AVANT le processus interrompu.
    """
    verifier_processus(processus)
    if quantum <= 0:
        raise ValueError("Le quantum doit être strictement positif.")

    # Processus pas encore arrivés, triés par instant d'arrivée.
    a_venir = sorted(processus, key=critere_fcfs)

    # Temps CPU qu'il reste à chaque processus. On le note dans un
    # dictionnaire pour ne pas modifier les objets Processus.
    reste = {}
    for p in processus:
        reste[p.nom] = p.duree

    file = []   # file d'attente des processus prêts (le premier est servi)
    gantt = []
    temps = 0

    while len(a_venir) > 0 or len(file) > 0:
        faire_entrer_les_arrives(a_venir, file, temps)

        # File vide : le CPU attend la prochaine arrivée.
        if len(file) == 0:
            prochaine_arrivee = a_venir[0].arrivee
            ajouter_segment(gantt, INACTIF, temps, prochaine_arrivee)
            temps = prochaine_arrivee
            continue

        # On sert le premier de la file pendant une tranche.
        courant = file.pop(0)
        tranche = min(quantum, reste[courant.nom])
        ajouter_segment(gantt, courant.nom, temps, temps + tranche)
        temps = temps + tranche
        reste[courant.nom] = reste[courant.nom] - tranche

        # Les nouveaux arrivés passent devant le processus interrompu.
        faire_entrer_les_arrives(a_venir, file, temps)
        if reste[courant.nom] > 0:
            file.append(courant)   # pas fini : retour au bout de la file

    return gantt
