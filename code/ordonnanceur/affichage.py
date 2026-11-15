"""
affichage.py — Transforme les résultats en texte lisible dans le terminal.

Les fonctions RENVOIENT du texte (elles ne font pas print). Cela permet de
les tester facilement et de réutiliser le texte ailleurs (rapport, fichier).
"""


def dessiner_gantt(gantt, echelle=None):
    """Renvoie le diagramme de Gantt sous forme de texte.

    Exemple :
        +----------+------+
        |    P1    |  P2  |
        +----------+------+
        0          5      8

    `echelle` = nombre de caractères par unité de temps.
    """
    if len(gantt) == 0:
        return "(diagramme vide)"

    # Sans précision, on choisit 2 caractères par unité de temps, ou 1 seul
    # si le diagramme est long, pour qu'il tienne dans la largeur du terminal.
    if echelle is None:
        duree_totale = gantt[-1].fin - gantt[0].debut
        echelle = 2 if duree_totale <= 30 else 1

    bordure = "+"
    cases = "|"
    temps = str(gantt[0].debut)

    for segment in gantt:
        # Largeur proportionnelle à la durée, mais assez grande pour
        # contenir le nom du processus et le nombre écrit en dessous.
        largeur = (segment.fin - segment.debut) * echelle
        largeur = max(largeur, len(segment.nom) + 2, len(str(segment.fin)) + 1)

        bordure = bordure + "-" * largeur + "+"
        cases = cases + segment.nom.center(largeur) + "|"

        # On complète la ligne des temps avec des espaces pour que le
        # nombre tombe juste sous la barre verticale de fin de case.
        temps = temps.ljust(len(cases) - 1) + str(segment.fin)

    return bordure + "\n" + cases + "\n" + bordure + "\n" + temps


def formater_statistiques(lignes, attente_moyenne, sejour_moyen):
    """Renvoie le tableau des temps (une ligne par processus) + les moyennes."""
    texte = (f"{'Processus':<10}{'Arrivée':>8}{'Durée':>7}{'Fin':>6}"
             f"{'Séjour':>8}{'Attente':>9}\n")

    for ligne in lignes:
        texte = texte + (f"{ligne['nom']:<10}{ligne['arrivee']:>8}{ligne['duree']:>7}"
                         f"{ligne['fin']:>6}{ligne['sejour']:>8}{ligne['attente']:>9}\n")

    texte = texte + f"Temps d'attente moyen : {attente_moyenne:.2f}\n"
    texte = texte + f"Temps de séjour moyen : {sejour_moyen:.2f}"
    return texte
