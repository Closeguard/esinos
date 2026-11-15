"""
pagination.py — Traduire une adresse logique en adresse physique.

Idée de la pagination :
- la mémoire du PROCESSUS est découpée en morceaux égaux, les PAGES ;
- la mémoire RÉELLE (RAM) est découpée en morceaux de même taille, les CADRES ;
- la TABLE DES PAGES dit dans quel cadre se trouve chaque page.

Une adresse logique se découpe en deux nombres :

    numéro de page = adresse // taille_page     (division entière)
    déplacement    = adresse %  taille_page     (reste de la division)

Puis :

    adresse physique = numéro de cadre * taille_page + déplacement

Dans ce projet, la table des pages est un dictionnaire Python :
    {numéro de page: numéro de cadre}
et le cadre vaut None quand la page n'est pas chargée en mémoire.
"""


class DefautDePage(Exception):
    """Levée quand la page demandée existe mais n'est pas en mémoire."""


def decouper_adresse(adresse, taille_page):
    """Renvoie (numéro de page, déplacement) pour une adresse logique."""
    if taille_page <= 0:
        raise ValueError("La taille de page doit être strictement positive.")
    if adresse < 0:
        raise ValueError("Une adresse ne peut pas être négative.")

    numero_page = adresse // taille_page
    deplacement = adresse % taille_page
    return numero_page, deplacement


def traduire(adresse, taille_page, table_pages):
    """Renvoie l'adresse physique correspondant à une adresse logique.

    Deux problèmes possibles, à ne pas confondre :
    - la page n'existe pas dans la table : l'adresse est en dehors de la
      mémoire du processus, c'est une erreur (ValueError) ;
    - la page existe mais son cadre vaut None : elle n'est pas chargée,
      c'est un défaut de page (DefautDePage).
    """
    numero_page, deplacement = decouper_adresse(adresse, taille_page)

    if numero_page not in table_pages:
        raise ValueError(f"Adresse {adresse} invalide : la page {numero_page} "
                         f"n'appartient pas au processus.")

    numero_cadre = table_pages[numero_page]
    if numero_cadre is None:
        raise DefautDePage(f"Défaut de page : la page {numero_page} "
                           f"n'est pas en mémoire.")

    return numero_cadre * taille_page + deplacement


def bits_deplacement(taille_page):
    """Nombre de bits du déplacement, si la taille de page est une puissance de 2.

    Exemple : 1024 = 2 puissance 10, donc 10 bits. Renvoie None sinon.
    Dans un vrai système la taille de page est toujours une puissance de 2 :
    le découpage se fait alors en coupant simplement l'adresse binaire en deux.
    """
    bits = 0
    valeur = taille_page
    while valeur > 1:
        if valeur % 2 != 0:
            return None      # pas une puissance de 2
        valeur = valeur // 2
        bits = bits + 1
    return bits
