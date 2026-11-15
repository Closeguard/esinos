"""
test_fichiers.py — Tests automatiques du module 3 (bonus).

Lancement (depuis le dossier code/) :

    python3 -m unittest -v

Chaque test travaille sur un disque neuf créé dans un dossier temporaire,
supprimé à la fin : les tests ne touchent jamais à votre vrai fichier-disque.
"""

import os
import tempfile
import unittest

from fichiers.disque import Disque, TAILLE_BLOC, NB_BLOCS
from fichiers.systeme_fichiers import SystemeFichiers, ErreurFichier
from fichiers.affichage import formater_liste, formater_inodes, formater_carte


class AvecDisqueTemporaire(unittest.TestCase):
    """Prépare un disque formaté avant chaque test, le supprime après."""

    def setUp(self):
        self.dossier = tempfile.TemporaryDirectory()
        self.chemin = os.path.join(self.dossier.name, "disque_test.img")
        self.sf = SystemeFichiers(self.chemin)
        self.sf.formater()

    def tearDown(self):
        self.dossier.cleanup()


class TestDisque(AvecDisqueTemporaire):

    def test_taille_du_fichier_disque(self):
        self.assertEqual(os.path.getsize(self.chemin), 64 * 64)   # 4096 octets

    def test_lire_ecrire_un_bloc(self):
        disque = Disque(self.chemin)
        disque.ecrire_bloc(20, b"abc")
        bloc = disque.lire_bloc(20)
        self.assertEqual(len(bloc), TAILLE_BLOC)
        self.assertEqual(bloc[0:3], b"abc")
        self.assertEqual(bloc[3:], bytes(TAILLE_BLOC - 3))   # complété par des zéros
        self.assertEqual(disque.lire_bloc(21), bytes(TAILLE_BLOC))   # le voisin est intact

    def test_bloc_inexistant(self):
        disque = Disque(self.chemin)
        with self.assertRaises(ValueError):
            disque.lire_bloc(NB_BLOCS)
        with self.assertRaises(ValueError):
            disque.ecrire_bloc(-1, b"x")
        with self.assertRaises(ValueError):
            disque.ecrire_bloc(20, bytes(TAILLE_BLOC + 1))


class TestFormatage(AvecDisqueTemporaire):

    def test_disque_vide_apres_formatage(self):
        self.assertTrue(self.sf.est_formate())
        self.assertEqual(self.sf.lister(), [])
        self.assertEqual(len(self.sf.blocs_libres()), 54)   # blocs 10 à 63
        self.assertEqual(self.sf.blocs_libres()[0], 10)
        self.assertEqual([i.utilise for i in self.sf.lire_inodes()], [False] * 16)

    def test_disque_non_formate(self):
        autre = SystemeFichiers(os.path.join(self.dossier.name, "absent.img"))
        self.assertFalse(autre.est_formate())
        with self.assertRaises(ErreurFichier):
            autre.lire("a.txt")
        with self.assertRaises(ErreurFichier):
            autre.creer("a.txt", "x")

    def test_fichier_quelconque_n_est_pas_un_disque(self):
        chemin = os.path.join(self.dossier.name, "notes.txt")
        with open(chemin, "w") as fichier:
            fichier.write("ceci n'est pas un disque ESINOS")
        self.assertFalse(SystemeFichiers(chemin).est_formate())


class TestCreerLireSupprimer(AvecDisqueTemporaire):

    def test_creer_puis_lire(self):
        numero = self.sf.creer("a.txt", "Bonjour")
        self.assertEqual(numero, 0)                       # premier inode libre
        self.assertEqual(self.sf.lire("a.txt"), "Bonjour")
        self.assertEqual(self.sf.lister(), [("a.txt", 0, 7, [10])])

    def test_fichier_sur_plusieurs_blocs(self):
        texte = "x" * 150                                 # 150 octets -> 3 blocs de 64
        self.sf.creer("long.txt", texte)
        self.assertEqual(self.sf.lire("long.txt"), texte)
        self.assertEqual(self.sf.lister(), [("long.txt", 0, 150, [10, 11, 12])])
        self.assertEqual(len(self.sf.blocs_libres()), 51)

    def test_nombre_de_blocs_aux_limites(self):
        self.sf.creer("vide", "")
        self.sf.creer("plein", "a" * 64)                  # exactement 1 bloc
        self.sf.creer("deborde", "a" * 65)                # 1 octet de trop -> 2 blocs
        blocs = {nom: b for nom, inode, taille, b in self.sf.lister()}
        self.assertEqual(blocs["vide"], [])
        self.assertEqual(blocs["plein"], [10])
        self.assertEqual(blocs["deborde"], [11, 12])
        self.assertEqual(self.sf.lire("vide"), "")
        self.assertEqual(self.sf.lire("plein"), "a" * 64)

    def test_accents(self):
        self.sf.creer("été.txt", "Système d'exploitation : mémoire, élève")
        self.assertEqual(self.sf.lire("été.txt"), "Système d'exploitation : mémoire, élève")
        # "é" occupe 2 octets en UTF-8 : la taille compte des octets, pas des lettres.
        self.sf.creer("e", "été")
        self.assertEqual(self.sf.trouver_inode("e").taille, 5)

    def test_supprimer_libere_tout(self):
        self.sf.creer("a.txt", "x" * 100)
        self.sf.supprimer("a.txt")
        self.assertEqual(self.sf.lister(), [])
        self.assertEqual(len(self.sf.blocs_libres()), 54)
        self.assertFalse(self.sf.lire_inodes()[0].utilise)
        with self.assertRaises(ErreurFichier):
            self.sf.lire("a.txt")

    def test_reutilisation_et_fragmentation(self):
        self.sf.creer("a", "x" * 150)     # blocs 10 11 12, inode 0
        self.sf.creer("b", "y" * 10)      # bloc 13, inode 1
        self.sf.supprimer("a")            # libère 10 11 12 et l'inode 0
        self.assertEqual(self.sf.creer("c", "z" * 100), 0)    # l'inode 0 est réutilisé
        self.sf.creer("d", "w" * 100)
        blocs = {nom: b for nom, inode, taille, b in self.sf.lister()}
        self.assertEqual(blocs["c"], [10, 11])
        self.assertEqual(blocs["d"], [12, 14])    # blocs non voisins : fragmentation
        self.assertEqual(self.sf.lire("d"), "w" * 100)
        self.assertEqual(self.sf.lire("b"), "y" * 10)

    def test_les_donnees_restent_apres_fermeture(self):
        self.sf.creer("a.txt", "persistant")
        nouveau = SystemeFichiers(self.chemin)    # comme si on relançait le programme
        self.assertEqual(nouveau.lire("a.txt"), "persistant")

    def test_formater_efface_tout(self):
        self.sf.creer("a.txt", "x")
        self.sf.formater()
        self.assertEqual(self.sf.lister(), [])


class TestErreurs(AvecDisqueTemporaire):

    def test_nom_deja_pris(self):
        self.sf.creer("a.txt", "1")
        with self.assertRaises(ErreurFichier):
            self.sf.creer("a.txt", "2")
        self.assertEqual(self.sf.lire("a.txt"), "1")      # l'ancien est intact

    def test_noms_invalides(self):
        with self.assertRaises(ErreurFichier):
            self.sf.creer("", "x")
        with self.assertRaises(ErreurFichier):
            self.sf.creer("nom_beaucoup_trop_long.txt", "x")
        self.sf.creer("quatorze_carac", "x")              # 14 caractères : accepté

    def test_fichier_trop_grand(self):
        self.sf.creer("max", "a" * 384)                   # 6 blocs : la limite
        with self.assertRaises(ErreurFichier):
            self.sf.creer("trop", "a" * 385)

    def test_fichier_introuvable(self):
        with self.assertRaises(ErreurFichier):
            self.sf.lire("fantome")
        with self.assertRaises(ErreurFichier):
            self.sf.supprimer("fantome")

    def test_plus_d_inode(self):
        for numero in range(16):
            self.sf.creer(f"f{numero}", "x")
        with self.assertRaises(ErreurFichier):
            self.sf.creer("f16", "x")

    def test_disque_plein(self):
        for numero in range(9):                           # 9 x 6 blocs = 54 blocs
            self.sf.creer(f"gros{numero}", "a" * 384)
        self.assertEqual(self.sf.blocs_libres(), [])
        with self.assertRaises(ErreurFichier):
            self.sf.creer("petit", "x")
        # Un échec ne doit rien laisser derrière lui.
        self.assertEqual(len(self.sf.lister()), 9)
        self.sf.creer("vide", "")                         # 0 bloc : toujours possible


class TestAffichage(AvecDisqueTemporaire):

    def test_liste(self):
        self.assertEqual(formater_liste(self.sf.lister()), "(aucun fichier)")
        self.sf.creer("a.txt", "x" * 100)
        self.assertIn("a.txt", formater_liste(self.sf.lister()))
        self.assertIn("10 11", formater_liste(self.sf.lister()))

    def test_table_des_inodes(self):
        self.sf.creer("a.txt", "x" * 100)
        lignes = formater_inodes(self.sf.lire_inodes()).split("\n")
        self.assertEqual(len(lignes), 17)                 # en-tête + 16 inodes
        self.assertEqual(lignes[1].split(), ["0", "utilisé", "100", "10", "11"])
        self.assertEqual(lignes[2].split(), ["1", "libre", "-", "-"])
        self.assertNotIn("a.txt", "\n".join(lignes))      # pas de nom dans un inode

    def test_carte_des_blocs(self):
        self.sf.creer("a.txt", "x" * 100)
        lignes = formater_carte(self.sf.lire_carte()).split("\n")
        self.assertTrue(lignes[0].endswith("SCIIIIRRRR##...."))
        self.assertTrue(lignes[1].endswith("................"))


if __name__ == "__main__":
    unittest.main()
