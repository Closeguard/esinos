"""
systeme_fichiers.py — Le mini système de fichiers à inodes.

Organisation du disque (64 blocs de 64 octets) :

    bloc  0        superbloc : la "carte d'identité" du disque
    bloc  1        carte des blocs : 1 octet par bloc, 0 = libre, 1 = occupé
    blocs 2 à 5    table des inodes : 16 inodes de 16 octets
    blocs 6 à 9    répertoire : 16 entrées (nom du fichier -> numéro d'inode)
    blocs 10 à 63  données : le contenu des fichiers

Les trois idées à retenir :
- un INODE décrit un fichier : sa taille et les numéros de ses blocs.
  Il ne contient PAS le nom du fichier ;
- le RÉPERTOIRE fait le lien entre un nom et un numéro d'inode ;
- la CARTE DES BLOCS dit quels blocs sont libres.

Simplifications assumées : un seul répertoire, pas de sous-dossiers, et
6 pointeurs directs par inode, donc un fichier fait au plus 6 x 64 = 384 octets.
"""

from fichiers.disque import Disque, TAILLE_BLOC, NB_BLOCS

# --- Plan du disque ----------------------------------------------------
BLOC_SUPERBLOC = 0
BLOC_CARTE = 1
PREMIER_BLOC_INODES = 2
NB_BLOCS_INODES = 4
PREMIER_BLOC_REPERTOIRE = 6
NB_BLOCS_REPERTOIRE = 4
PREMIER_BLOC_DONNEES = 10

# --- Inodes --------------------------------------------------------------
NB_INODES = 16
TAILLE_INODE = 16        # 2 octets "utilisé" + 2 octets taille + 6 x 2 octets de pointeurs
NB_POINTEURS = 6         # nombre maximal de blocs par fichier
TAILLE_MAX_FICHIER = NB_POINTEURS * TAILLE_BLOC

# --- Répertoire ----------------------------------------------------------
TAILLE_ENTREE = 16       # 14 octets pour le nom + 2 octets pour le numéro d'inode
TAILLE_NOM = 14

SIGNATURE = b"ESFS"      # 4 octets écrits au début du disque pour le reconnaître


class ErreurFichier(Exception):
    """Erreur normale d'utilisation : fichier introuvable, disque plein..."""


class Inode:
    """La fiche d'un fichier : sa taille et la liste de ses blocs."""

    def __init__(self, numero, utilise, taille, blocs):
        self.numero = numero
        self.utilise = utilise   # True si cet inode décrit un fichier
        self.taille = taille     # taille du fichier en octets
        self.blocs = blocs       # numéros des blocs de données, dans l'ordre


# --- Conversion nombre <-> octets ---------------------------------------
# Sur le disque tout est octets. Chaque nombre est écrit sur 2 octets.

def en_octets(nombre):
    return nombre.to_bytes(2, "big")


def en_nombre(octets):
    return int.from_bytes(octets, "big")


class SystemeFichiers:

    def __init__(self, chemin):
        self.disque = Disque(chemin)

    # ------------------------------------------------------------------
    # Lecture / écriture d'une zone de plusieurs blocs
    # ------------------------------------------------------------------

    def lire_zone(self, premier_bloc, nb_blocs):
        """Lit plusieurs blocs à la suite et les renvoie collés ensemble.

        bytearray = suite d'octets MODIFIABLE (bytes ne l'est pas).
        """
        zone = bytearray()
        for numero in range(premier_bloc, premier_bloc + nb_blocs):
            zone = zone + self.disque.lire_bloc(numero)
        return zone

    def ecrire_zone(self, premier_bloc, zone):
        """Recoupe la zone en blocs et les écrit sur le disque."""
        nb_blocs = len(zone) // TAILLE_BLOC
        for indice in range(nb_blocs):
            morceau = zone[indice * TAILLE_BLOC:(indice + 1) * TAILLE_BLOC]
            self.disque.ecrire_bloc(premier_bloc + indice, bytes(morceau))

    # ------------------------------------------------------------------
    # Formatage
    # ------------------------------------------------------------------

    def formater(self):
        """Crée un disque vierge et y installe un système de fichiers vide."""
        self.disque.creer()

        superbloc = (SIGNATURE + en_octets(NB_BLOCS) + en_octets(TAILLE_BLOC) +
                     en_octets(NB_INODES) + en_octets(PREMIER_BLOC_DONNEES))
        self.disque.ecrire_bloc(BLOC_SUPERBLOC, superbloc)

        # Les blocs 0 à 9 servent au système : on les marque occupés.
        carte = bytearray(NB_BLOCS)
        for numero in range(PREMIER_BLOC_DONNEES):
            carte[numero] = 1
        self.disque.ecrire_bloc(BLOC_CARTE, bytes(carte))
        # La table des inodes et le répertoire sont déjà remplis de zéros.

    def est_formate(self):
        """True si le fichier-disque existe et contient notre système de fichiers."""
        if not self.disque.existe():
            return False
        try:
            superbloc = self.disque.lire_bloc(BLOC_SUPERBLOC)
        except OSError:
            return False
        return (superbloc[0:4] == SIGNATURE and
                en_nombre(superbloc[4:6]) == NB_BLOCS and
                en_nombre(superbloc[6:8]) == TAILLE_BLOC)

    def verifier_formate(self):
        if not self.est_formate():
            raise ErreurFichier("Le disque n'est pas formaté.")

    # ------------------------------------------------------------------
    # Carte des blocs
    # ------------------------------------------------------------------

    def lire_carte(self):
        return bytearray(self.disque.lire_bloc(BLOC_CARTE))

    def blocs_libres(self):
        """Liste des numéros de blocs de données libres, du plus petit au plus grand."""
        carte = self.lire_carte()
        libres = []
        for numero in range(PREMIER_BLOC_DONNEES, NB_BLOCS):
            if carte[numero] == 0:
                libres.append(numero)
        return libres

    # ------------------------------------------------------------------
    # Inodes
    # ------------------------------------------------------------------

    def lire_inodes(self):
        """Renvoie la liste des NB_INODES inodes du disque."""
        zone = self.lire_zone(PREMIER_BLOC_INODES, NB_BLOCS_INODES)
        inodes = []
        for numero in range(NB_INODES):
            debut = numero * TAILLE_INODE
            brut = zone[debut:debut + TAILLE_INODE]

            utilise = en_nombre(brut[0:2]) == 1
            taille = en_nombre(brut[2:4])
            blocs = []
            for indice in range(NB_POINTEURS):
                pointeur = en_nombre(brut[4 + 2 * indice:6 + 2 * indice])
                if pointeur != 0:          # 0 = "pas de bloc" (le bloc 0 est le superbloc)
                    blocs.append(pointeur)
            inodes.append(Inode(numero, utilise, taille, blocs))
        return inodes

    def ecrire_inode(self, inode):
        """Écrit un inode à sa place dans la table des inodes."""
        brut = en_octets(1 if inode.utilise else 0) + en_octets(inode.taille)
        for indice in range(NB_POINTEURS):
            if indice < len(inode.blocs):
                brut = brut + en_octets(inode.blocs[indice])
            else:
                brut = brut + en_octets(0)

        zone = self.lire_zone(PREMIER_BLOC_INODES, NB_BLOCS_INODES)
        debut = inode.numero * TAILLE_INODE
        zone[debut:debut + TAILLE_INODE] = brut
        self.ecrire_zone(PREMIER_BLOC_INODES, zone)

    # ------------------------------------------------------------------
    # Répertoire
    # ------------------------------------------------------------------

    def lire_repertoire(self):
        """Renvoie un dictionnaire {nom du fichier: numéro d'inode}."""
        zone = self.lire_zone(PREMIER_BLOC_REPERTOIRE, NB_BLOCS_REPERTOIRE)
        repertoire = {}
        for indice in range(NB_INODES):
            debut = indice * TAILLE_ENTREE
            nom_brut = bytes(zone[debut:debut + TAILLE_NOM]).rstrip(b"\x00")
            if len(nom_brut) > 0:          # nom vide = entrée libre
                numero_inode = en_nombre(zone[debut + TAILLE_NOM:debut + TAILLE_ENTREE])
                repertoire[nom_brut.decode("utf-8")] = numero_inode
        return repertoire

    def ecrire_repertoire(self, repertoire):
        """Réécrit tout le répertoire à partir du dictionnaire."""
        zone = bytearray(NB_BLOCS_REPERTOIRE * TAILLE_BLOC)
        indice = 0
        for nom in repertoire:
            debut = indice * TAILLE_ENTREE
            nom_brut = nom.encode("utf-8")
            zone[debut:debut + len(nom_brut)] = nom_brut
            zone[debut + TAILLE_NOM:debut + TAILLE_ENTREE] = en_octets(repertoire[nom])
            indice = indice + 1
        self.ecrire_zone(PREMIER_BLOC_REPERTOIRE, zone)

    # ------------------------------------------------------------------
    # Les trois opérations demandées : créer, lire, supprimer
    # ------------------------------------------------------------------

    def creer(self, nom, contenu):
        """Crée le fichier `nom` contenant le texte `contenu`.

        Renvoie le numéro de l'inode utilisé.
        """
        self.verifier_formate()
        donnees = contenu.encode("utf-8")     # texte -> octets
        repertoire = self.lire_repertoire()

        # 1. Vérifications : on refuse AVANT d'avoir écrit quoi que ce soit.
        if nom == "" or "\x00" in nom:
            raise ErreurFichier("Nom de fichier invalide.")
        if len(nom.encode("utf-8")) > TAILLE_NOM:
            raise ErreurFichier(f"Nom trop long ({TAILLE_NOM} octets maximum).")
        if nom in repertoire:
            raise ErreurFichier(f"Le fichier '{nom}' existe déjà.")
        if len(donnees) > TAILLE_MAX_FICHIER:
            raise ErreurFichier(f"Fichier trop grand : {len(donnees)} octets, "
                                f"maximum {TAILLE_MAX_FICHIER}.")

        # 2. Trouver un inode libre.
        inode_libre = None
        for inode in self.lire_inodes():
            if not inode.utilise:
                inode_libre = inode
                break
        if inode_libre is None:
            raise ErreurFichier("Plus d'inode libre : nombre maximal de fichiers atteint.")

        # 3. Trouver assez de blocs libres.
        #    Arrondi au bloc supérieur : 65 octets demandent 2 blocs.
        nb_blocs = (len(donnees) + TAILLE_BLOC - 1) // TAILLE_BLOC
        libres = self.blocs_libres()
        if nb_blocs > len(libres):
            raise ErreurFichier(f"Disque plein : il faut {nb_blocs} blocs, "
                                f"il en reste {len(libres)}.")
        blocs = libres[0:nb_blocs]            # les premiers blocs libres

        # 4. Écrire les données, bloc par bloc.
        for indice in range(nb_blocs):
            morceau = donnees[indice * TAILLE_BLOC:(indice + 1) * TAILLE_BLOC]
            self.disque.ecrire_bloc(blocs[indice], morceau)

        # 5. Marquer les blocs occupés dans la carte.
        carte = self.lire_carte()
        for numero in blocs:
            carte[numero] = 1
        self.disque.ecrire_bloc(BLOC_CARTE, bytes(carte))

        # 6. Remplir l'inode.
        inode_libre.utilise = True
        inode_libre.taille = len(donnees)
        inode_libre.blocs = blocs
        self.ecrire_inode(inode_libre)

        # 7. Ajouter le nom dans le répertoire.
        repertoire[nom] = inode_libre.numero
        self.ecrire_repertoire(repertoire)

        return inode_libre.numero

    def trouver_inode(self, nom):
        """Renvoie l'inode du fichier `nom`, ou lève ErreurFichier."""
        self.verifier_formate()
        repertoire = self.lire_repertoire()
        if nom not in repertoire:
            raise ErreurFichier(f"Le fichier '{nom}' n'existe pas.")
        return self.lire_inodes()[repertoire[nom]]

    def lire(self, nom):
        """Renvoie le texte contenu dans le fichier `nom`."""
        inode = self.trouver_inode(nom)       # nom -> inode
        donnees = b""
        for numero in inode.blocs:            # inode -> blocs
            donnees = donnees + self.disque.lire_bloc(numero)
        donnees = donnees[0:inode.taille]     # le dernier bloc n'est pas forcément plein
        return donnees.decode("utf-8")

    def supprimer(self, nom):
        """Supprime le fichier `nom` et libère son inode et ses blocs.

        Comme sur un vrai disque, les octets du contenu ne sont pas effacés :
        les blocs sont seulement déclarés libres et seront réécrits plus tard.
        """
        inode = self.trouver_inode(nom)

        # 1. Libérer les blocs dans la carte.
        carte = self.lire_carte()
        for numero in inode.blocs:
            carte[numero] = 0
        self.disque.ecrire_bloc(BLOC_CARTE, bytes(carte))

        # 2. Libérer l'inode.
        inode.utilise = False
        inode.taille = 0
        inode.blocs = []
        self.ecrire_inode(inode)

        # 3. Retirer le nom du répertoire.
        repertoire = self.lire_repertoire()
        del repertoire[nom]
        self.ecrire_repertoire(repertoire)

    def lister(self):
        """Renvoie la liste des fichiers : (nom, numéro d'inode, taille, blocs)."""
        self.verifier_formate()
        inodes = self.lire_inodes()
        repertoire = self.lire_repertoire()
        fichiers = []
        for nom in sorted(repertoire):
            inode = inodes[repertoire[nom]]
            fichiers.append((nom, inode.numero, inode.taille, inode.blocs))
        return fichiers
