"""
statistiques.py — Temps de séjour et temps d'attente.

Les deux formules à connaître par cœur :

    temps de séjour  = instant de fin - instant d'arrivée
    temps d'attente  = temps de séjour - durée d'exécution

Le calcul part du diagramme de Gantt. Il marche donc pour n'importe quel
algorithme, sans rien changer.
"""


def calculer_statistiques(processus, gantt):
    """Renvoie (lignes, attente_moyenne, sejour_moyen).

    `lignes` contient un dictionnaire par processus, avec les clés :
    nom, arrivee, duree, fin, sejour, attente.
    """
    lignes = []

    for p in processus:
        # L'instant de fin d'un processus = la fin de sa DERNIÈRE case
        # dans le Gantt (avec Round Robin il peut en avoir plusieurs).
        fin = 0
        for segment in gantt:
            if segment.nom == p.nom and segment.fin > fin:
                fin = segment.fin

        sejour = fin - p.arrivee
        attente = sejour - p.duree

        lignes.append({
            "nom": p.nom,
            "arrivee": p.arrivee,
            "duree": p.duree,
            "fin": fin,
            "sejour": sejour,
            "attente": attente,
        })

    nombre = len(lignes)
    attente_moyenne = sum(ligne["attente"] for ligne in lignes) / nombre
    sejour_moyen = sum(ligne["sejour"] for ligne in lignes) / nombre

    return lignes, attente_moyenne, sejour_moyen
def calculer_utilisation_cpu(gantt):
        if not gantt:
            return 0

        temps_actif = sum(
            segment.fin - segment.debut
            for segment in gantt
            if segment.nom != "INACTIF"
        )

        duree_totale = gantt[-1].fin - gantt[0].debut

        if duree_totale == 0:
            return 0

        return (temps_actif / duree_totale) * 100
