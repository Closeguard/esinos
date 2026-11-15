"""
affichage.py — Met en forme les résultats du module mémoire.

Comme dans l'ordonnanceur, ces fonctions RENVOIENT du texte et ne font
aucun calcul sur les algorithmes.
"""

from memoire.remplacement import fifo, lru, optimal, compter_defauts


def texte_cadres(cadres):
    """Renvoie par exemple "[7] [0] [-]" (un tiret = cadre vide)."""
    morceaux = []
    for page in cadres:
        if page is None:
            morceaux.append("[-]")
        else:
            morceaux.append(f"[{page}]")
    return " ".join(morceaux)


def formater_etape(etape):
    """Texte détaillé d'UNE étape (utilisé par le mode pas à pas)."""
    texte = f"Étape {etape.numero} : le processus demande la page {etape.page}\n"
    # L'explication contient plusieurs phrases : une par ligne, c'est plus lisible.
    for phrase in etape.explication.split(". "):
        if not phrase.endswith("."):
            phrase = phrase + "."
        texte = texte + f"  {phrase}\n"
    texte = texte + f"  Cadres : {texte_cadres(etape.cadres)}"
    return texte


def formater_tableau(etapes):
    """Tableau récapitulatif : une ligne par page demandée."""
    nb_cadres = len(etapes[0].cadres)

    entete = f"{'Étape':>5} {'Page':>5} |"
    for numero in range(nb_cadres):
        entete = entete + f"{'C' + str(numero):>4}"
    entete = entete + " | Résultat"

    lignes = [entete, "-" * len(entete)]
    for etape in etapes:
        ligne = f"{etape.numero:>5} {etape.page:>5} |"
        for page in etape.cadres:
            contenu = "-" if page is None else str(page)
            ligne = ligne + f"{contenu:>4}"
        if not etape.defaut:
            resultat = "présente"
        elif etape.evincee is None:
            resultat = "DÉFAUT"
        else:
            resultat = f"DÉFAUT, la page {etape.evincee} sort"
        lignes.append(ligne + " | " + resultat)

    total = compter_defauts(etapes)
    lignes.append("")
    lignes.append(f"Défauts de page : {total} sur {len(etapes)} demandes "
                  f"({100 * total / len(etapes):.0f} %)")
    return "\n".join(lignes)


def formater_comparaison(references, nb_cadres):
    """Nombre de défauts de FIFO, LRU et Optimal sur la même suite."""
    resultats = [
        ("FIFO", fifo(references, nb_cadres)),
        ("LRU", lru(references, nb_cadres)),
        ("Optimal", optimal(references, nb_cadres)),
    ]
    lignes = [f"{'Algorithme':<12}{'Défauts':>9}{'Taux':>8}"]
    for nom, etapes in resultats:
        total = compter_defauts(etapes)
        taux = 100 * total / len(etapes)
        lignes.append(f"{nom:<12}{total:>9}{taux:>7.0f}%")
    return "\n".join(lignes)


def formater_tlb(etapes):
    """Tableau de la simulation du TLB."""
    lignes = [f"{'Étape':>5} {'Adresse':>8} {'Page':>5} {'Dépl.':>6}  {'TLB':<7}"
              f"{'Cadre':>6} {'Adr. phys.':>11}  TLB après (page:cadre)"]
    lignes.append("-" * 78)
    for etape in etapes:
        resultat = "succès" if etape.succes else "échec"
        contenu = " ".join(f"{page}:{cadre}" for page, cadre in etape.contenu)
        lignes.append(f"{etape.numero:>5} {etape.adresse:>8} {etape.page:>5} "
                      f"{etape.deplacement:>6}  {resultat:<7}{etape.cadre:>6} "
                      f"{etape.adresse_physique:>11}  {contenu}")
    return "\n".join(lignes)
