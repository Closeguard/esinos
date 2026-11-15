"""
interface.py — Petits outils partagés par tous les menus.

Chaque sous-menu (ordonnanceur, mémoire, fichiers) a besoin des mêmes
gestes : afficher un titre, demander un nombre, attendre la touche Entrée.
On les écrit ici une seule fois.

Le programme n'affiche que des lettres, des chiffres et des accents
français : cela s'affiche correctement sur Mac, Windows et Linux.
"""


def titre(texte):
    """Affiche un titre encadré, pour repérer facilement où l'on est."""
    print()
    print("=" * 60)
    print(texte.center(60))
    print("=" * 60)


def pause():
    """Attend que l'utilisateur appuie sur Entrée avant de continuer."""
    input("\n(Appuyez sur Entrée pour continuer) ")


def demander_entier(message, minimum, maximum=None):
    """Repose la question tant que la réponse n'est pas un entier valide.

    La valeur doit être >= minimum, et <= maximum si un maximum est donné.
    """
    while True:
        reponse = input(message).strip()
        try:
            valeur = int(reponse)
        except ValueError:
            print("  Merci de taper un nombre entier.")
            continue
        if valeur < minimum:
            print(f"  La valeur doit être au moins {minimum}.")
            continue
        if maximum is not None and valeur > maximum:
            print(f"  La valeur doit être au plus {maximum}.")
            continue
        return valeur


def demander_liste_entiers(message, minimum=0):
    """Demande plusieurs entiers séparés par des espaces ou des virgules.

    Exemple de saisie acceptée :  7 0 1 2   ou   7,0,1,2
    """
    while True:
        reponse = input(message).replace(",", " ")
        morceaux = reponse.split()
        if len(morceaux) == 0:
            print("  Merci de taper au moins un nombre.")
            continue
        try:
            valeurs = [int(morceau) for morceau in morceaux]
        except ValueError:
            print("  Seulement des nombres entiers, séparés par des espaces.")
            continue
        if min(valeurs) < minimum:
            print(f"  Chaque valeur doit être au moins {minimum}.")
            continue
        return valeurs


def demander_reel(message, minimum, maximum=None):
    """Comme demander_entier, mais accepte les nombres à virgule (0.8 ou 0,8)."""
    while True:
        reponse = input(message).strip().replace(",", ".")
        try:
            valeur = float(reponse)
        except ValueError:
            print("  Merci de taper un nombre, par exemple 0.8")
            continue
        if valeur < minimum:
            print(f"  La valeur doit être au moins {minimum}.")
            continue
        if maximum is not None and valeur > maximum:
            print(f"  La valeur doit être au plus {maximum}.")
            continue
        return valeur


def demander_texte(message):
    """Demande un texte non vide."""
    while True:
        reponse = input(message).strip()
        if reponse == "":
            print("  La réponse ne peut pas être vide.")
            continue
        return reponse
