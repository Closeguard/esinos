"""
tlb.py — Le TLB et le temps d'accès effectif (EAT).

Problème : avec la pagination, chaque accès mémoire en coûte deux
(lire la table des pages, puis lire la donnée). C'est deux fois plus lent.

Solution : le TLB (Translation Lookaside Buffer), une toute petite mémoire
très rapide qui retient les dernières traductions page -> cadre.

    page trouvée dans le TLB      -> SUCCÈS : 1 seul accès mémoire
    page absente du TLB           -> ÉCHEC  : 2 accès mémoire, puis on
                                    range la traduction dans le TLB

L'EAT (Effective Access Time) est le temps MOYEN d'un accès, en tenant
compte de la proportion de succès.

Choix du projet : quand le TLB est plein, on retire l'entrée la plus
ancienne (FIFO). On suppose que toutes les pages sont en mémoire : ce
fichier étudie le TLB seul, pas les défauts de page.
"""

from memoire.pagination import decouper_adresse, traduire


class EtapeTLB:
    """Ce qui s'est passé pour un accès mémoire."""

    def __init__(self, numero, adresse, page, deplacement, succes,
                 cadre, adresse_physique, contenu):
        self.numero = numero
        self.adresse = adresse                    # adresse logique demandée
        self.page = page
        self.deplacement = deplacement
        self.succes = succes                      # True = trouvé dans le TLB
        self.cadre = cadre
        self.adresse_physique = adresse_physique
        self.contenu = contenu                    # TLB après l'accès : [(page, cadre), ...]


def simuler_tlb(adresses, taille_page, table_pages, taille_tlb):
    """Traduit une suite d'adresses en passant par un TLB de `taille_tlb` entrées."""
    if len(adresses) == 0:
        raise ValueError("Il faut au moins une adresse.")
    if taille_tlb < 1:
        raise ValueError("Le TLB doit avoir au moins une entrée.")

    tlb = []      # liste de couples (page, cadre), le plus ancien en premier
    etapes = []

    for position in range(len(adresses)):
        adresse = adresses[position]
        page, deplacement = decouper_adresse(adresse, taille_page)

        # 1. On cherche la page dans le TLB.
        cadre = None
        for entree in tlb:
            if entree[0] == page:
                cadre = entree[1]
        succes = cadre is not None

        # 2. Échec : on consulte la table des pages, puis on met à jour le TLB.
        if not succes:
            traduire(adresse, taille_page, table_pages)   # vérifie que la page est valide
            cadre = table_pages[page]
            if len(tlb) == taille_tlb:
                tlb.pop(0)                                # TLB plein : la plus ancienne sort
            tlb.append((page, cadre))

        adresse_physique = cadre * taille_page + deplacement
        etapes.append(EtapeTLB(position + 1, adresse, page, deplacement, succes,
                               cadre, adresse_physique, list(tlb)))

    return etapes


def taux_de_succes(etapes):
    """Proportion d'accès trouvés dans le TLB, entre 0 et 1."""
    succes = 0
    for etape in etapes:
        if etape.succes:
            succes = succes + 1
    return succes / len(etapes)


def eat_tlb(taux_succes, temps_tlb, temps_memoire):
    """Temps d'accès effectif avec un TLB.

        succès : temps_tlb + temps_memoire          (1 accès mémoire)
        échec  : temps_tlb + 2 * temps_memoire      (table des pages + donnée)

        EAT = taux * (succès) + (1 - taux) * (échec)

    Si le cours néglige le temps du TLB, il suffit de donner temps_tlb = 0.
    """
    if taux_succes < 0 or taux_succes > 1:
        raise ValueError("Le taux de succès doit être compris entre 0 et 1.")
    if temps_tlb < 0 or temps_memoire < 0:
        raise ValueError("Un temps ne peut pas être négatif.")

    temps_si_succes = temps_tlb + temps_memoire
    temps_si_echec = temps_tlb + 2 * temps_memoire
    return taux_succes * temps_si_succes + (1 - taux_succes) * temps_si_echec


def eat_defauts(taux_defaut, temps_memoire, temps_defaut):
    """Temps d'accès effectif quand il y a des défauts de page.

        EAT = (1 - p) * temps_memoire + p * temps_defaut

    p est la probabilité d'un défaut de page. temps_defaut est le temps
    total pour traiter un défaut (aller chercher la page sur le disque).
    Tous les temps doivent être dans la même unité.
    """
    if taux_defaut < 0 or taux_defaut > 1:
        raise ValueError("Le taux de défaut doit être compris entre 0 et 1.")
    if temps_memoire < 0 or temps_defaut < 0:
        raise ValueError("Un temps ne peut pas être négatif.")

    return (1 - taux_defaut) * temps_memoire + taux_defaut * temps_defaut
