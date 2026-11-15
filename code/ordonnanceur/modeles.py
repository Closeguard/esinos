"""
modeles.py — Les deux "objets" manipulés par l'ordonnanceur.

- Processus : un programme qui attend d'utiliser le processeur (CPU).
- Segment   : un morceau du diagramme de Gantt ("tel processus a tourné
              de l'instant debut à l'instant fin").

Ce fichier ne contient AUCUN calcul : seulement la description des données.
"""

# Nom utilisé dans le Gantt quand aucun processus n'est prêt (CPU au repos).
INACTIF = "--"


class Processus:
    """Un processus tel que le voit l'ordonnanceur."""

    def __init__(self, nom, arrivee, duree, priorite=0):
        # On refuse tout de suite les valeurs impossibles : mieux vaut une
        # erreur claire ici qu'un résultat faux plus loin.
        if nom == "" or nom == INACTIF:
            raise ValueError("Le nom du processus est vide ou réservé.")
        if arrivee < 0:
            raise ValueError("L'instant d'arrivée doit être positif ou nul.")
        if duree <= 0:
            raise ValueError("La durée d'exécution doit être strictement positive.")

        self.nom = nom            # exemple : "P1"
        self.arrivee = arrivee    # instant où le processus devient prêt
        self.duree = duree        # temps CPU dont il a besoin (burst time)
        self.priorite = priorite  # PETIT nombre = priorité HAUTE (convention du projet)

    def __repr__(self):
        # Texte affiché quand on fait print(processus) : pratique pour déboguer.
        return (f"Processus({self.nom}, arrivee={self.arrivee}, "
                f"duree={self.duree}, priorite={self.priorite})")


class Segment:
    """Une case du diagramme de Gantt : `nom` occupe le CPU de `debut` à `fin`."""

    def __init__(self, nom, debut, fin):
        self.nom = nom
        self.debut = debut
        self.fin = fin

    def __repr__(self):
        return f"Segment({self.nom}, {self.debut}-{self.fin})"


def verifier_processus(liste):
    """Vérifie qu'une liste de processus est utilisable par les algorithmes."""
    if len(liste) == 0:
        raise ValueError("Il faut au moins un processus.")

    noms_vus = []
    for p in liste:
        if p.nom in noms_vus:
            raise ValueError(f"Deux processus portent le même nom : {p.nom}")
        noms_vus.append(p.nom)
