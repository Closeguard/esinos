"""
remplacement.py — Remplacement de pages : FIFO, LRU et Optimal.

Situation : la mémoire a peu de cadres, et le processus demande des pages
les unes après les autres (la "suite de références"). Quand la page
demandée n'est pas en mémoire, c'est un DÉFAUT DE PAGE : il faut la
charger. Si tous les cadres sont pleins, il faut d'abord en vider un.
Quelle page sortir ? C'est la seule question où les trois algorithmes
diffèrent :

    FIFO    -> la page chargée depuis le plus longtemps
    LRU     -> la page utilisée il y a le plus longtemps
    Optimal -> la page qui resservira le plus tard (ou jamais)

Comme pour l'ordonnanceur : un seul moteur (`simuler`), et une petite
fonction de choix par algorithme.

Chaque simulation renvoie une liste d'Etape, une par page demandée, qui
contient le contenu des cadres et une explication en français.
"""


class Etape:
    """Ce qui s'est passé quand le processus a demandé une page."""

    def __init__(self, numero, page, cadres, defaut, evincee, explication):
        self.numero = numero            # 1, 2, 3...
        self.page = page                # la page demandée
        self.cadres = cadres            # contenu des cadres APRÈS l'étape (None = vide)
        self.defaut = defaut            # True s'il y a eu un défaut de page
        self.evincee = evincee          # la page sortie de la mémoire, ou None
        self.explication = explication  # pourquoi, en français


# ----------------------------------------------------------------------
# Les trois façons de choisir la page à sortir (la "victime")
# ----------------------------------------------------------------------
#
# Chaque fonction reçoit les mêmes informations et renvoie :
#     (la page victime, une phrase d'explication)
#
#   cadres      : les pages actuellement en mémoire
#   charge_a    : dictionnaire page -> étape où elle a été chargée
#   utilise_a   : dictionnaire page -> étape de sa dernière utilisation
#   references  : la suite complète des pages demandées
#   position    : l'indice (à partir de 0) de la demande en cours

def choisir_fifo(cadres, charge_a, utilise_a, references, position):
    """FIFO : sort la page présente en mémoire depuis le plus longtemps."""
    victime = cadres[0]
    for page in cadres:
        if charge_a[page] < charge_a[victime]:
            victime = page

    details = []
    for page in cadres:
        details.append(f"page {page} chargée à l'étape {charge_a[page]}")
    explication = ("FIFO : " + ", ".join(details) +
                   f". La plus ancienne en mémoire est la page {victime}.")
    return victime, explication


def choisir_lru(cadres, charge_a, utilise_a, references, position):
    """LRU : sort la page qui n'a pas servi depuis le plus longtemps."""
    victime = cadres[0]
    for page in cadres:
        if utilise_a[page] < utilise_a[victime]:
            victime = page

    details = []
    for page in cadres:
        details.append(f"page {page} utilisée à l'étape {utilise_a[page]}")
    explication = ("LRU : " + ", ".join(details) +
                   f". La moins récemment utilisée est la page {victime}.")
    return victime, explication


def prochaine_utilisation(page, references, position):
    """Étape de la prochaine demande de `page` après `position`, ou None."""
    for indice in range(position + 1, len(references)):
        if references[indice] == page:
            return indice + 1      # les étapes sont numérotées à partir de 1
    return None                    # la page ne sera plus jamais demandée


def choisir_optimal(cadres, charge_a, utilise_a, references, position):
    """Optimal : sort la page dont la prochaine utilisation est la plus lointaine.

    Il faut connaître l'avenir : impossible dans un vrai système. Cet
    algorithme sert de référence pour juger les autres.
    En cas d'égalité (plusieurs pages jamais réutilisées), on prend celle
    du cadre de plus petit numéro.
    """
    jamais = len(references) + 1   # plus loin que n'importe quelle étape

    victime = None
    plus_loin = -1
    details = []
    for page in cadres:
        prochaine = prochaine_utilisation(page, references, position)
        if prochaine is None:
            distance = jamais
            details.append(f"page {page} plus jamais demandée")
        else:
            distance = prochaine
            details.append(f"page {page} redemandée à l'étape {prochaine}")
        if distance > plus_loin:
            plus_loin = distance
            victime = page

    explication = ("Optimal : " + ", ".join(details) +
                   f". Celle qui resservira le plus tard est la page {victime}.")
    return victime, explication


# ----------------------------------------------------------------------
# Le moteur commun
# ----------------------------------------------------------------------

def simuler(references, nb_cadres, choisir_victime):
    """Déroule la suite de références et renvoie la liste des Etape."""
    if len(references) == 0:
        raise ValueError("La suite de références est vide.")
    if min(references) < 0:
        raise ValueError("Un numéro de page ne peut pas être négatif.")
    if nb_cadres < 1:
        raise ValueError("Il faut au moins un cadre.")

    cadres = [None] * nb_cadres   # None = cadre vide
    charge_a = {}                 # page -> étape de chargement
    utilise_a = {}                # page -> étape de dernière utilisation
    etapes = []

    for position in range(len(references)):
        page = references[position]
        numero = position + 1
        evincee = None

        if page in cadres:
            # Cas 1 : la page est déjà en mémoire. Rien à charger.
            defaut = False
            explication = (f"La page {page} est déjà dans le cadre "
                           f"{cadres.index(page)} : pas de défaut.")

        elif None in cadres:
            # Cas 2 : défaut de page, mais il reste un cadre vide.
            defaut = True
            libre = cadres.index(None)
            cadres[libre] = page
            charge_a[page] = numero
            explication = (f"Défaut de page. Le cadre {libre} est libre : "
                           f"on y charge la page {page}.")

        else:
            # Cas 3 : défaut de page et mémoire pleine. Il faut une victime.
            defaut = True
            evincee, raison = choisir_victime(cadres, charge_a, utilise_a,
                                              references, position)
            indice = cadres.index(evincee)
            cadres[indice] = page
            del charge_a[evincee]
            del utilise_a[evincee]
            charge_a[page] = numero
            explication = (f"Défaut de page, mémoire pleine. {raison} "
                           f"La page {page} prend sa place dans le cadre {indice}.")

        utilise_a[page] = numero   # dans tous les cas, la page vient de servir

        # list(cadres) fait une COPIE : sans elle, toutes les étapes
        # pointeraient vers la même liste et afficheraient l'état final.
        etapes.append(Etape(numero, page, list(cadres), defaut, evincee, explication))

    return etapes


def fifo(references, nb_cadres):
    """First In, First Out."""
    return simuler(references, nb_cadres, choisir_fifo)


def lru(references, nb_cadres):
    """Least Recently Used."""
    return simuler(references, nb_cadres, choisir_lru)


def optimal(references, nb_cadres):
    """Algorithme optimal (Belady)."""
    return simuler(references, nb_cadres, choisir_optimal)


def compter_defauts(etapes):
    """Nombre de défauts de page dans une simulation."""
    total = 0
    for etape in etapes:
        if etape.defaut:
            total = total + 1
    return total
