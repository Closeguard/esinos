"""
test_integration.py — Tests d'intégration : le programme entier, menu compris.

Les tests unitaires vérifient chaque fonction séparément. Ici on vérifie
que tout marche ENSEMBLE : on lance le vrai programme (main.py) et on
"tape" à la place de l'utilisateur.

Comment ça marche : `subprocess.run` démarre main.py comme dans un
terminal. Le texte donné dans `input=` est ce que l'utilisateur aurait
tapé, une ligne par réponse. On récupère tout ce que le programme a
affiché, et on vérifie que les bons résultats y figurent.
"""

import os
import subprocess
import sys
import tempfile
import unittest

# Emplacement de main.py : le dossier parent de tests/.
DOSSIER_CODE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(DOSSIER_CODE, "main.py")


def lancer(reponses, dossier):
    """Lance ESINOS, tape les `reponses`, renvoie (texte affiché, code de retour).

    `dossier` est le dossier de travail : le fichier-disque y sera créé.
    """
    environnement = dict(os.environ)
    environnement["PYTHONIOENCODING"] = "utf-8"    # mêmes accents sur tous les systèmes
    resultat = subprocess.run(
        [sys.executable, MAIN],
        input="\n".join(reponses) + "\n",
        capture_output=True, encoding="utf-8",
        cwd=dossier, env=environnement, timeout=30)
    return resultat.stdout + resultat.stderr, resultat.returncode


class TestProgrammeComplet(unittest.TestCase):

    def setUp(self):
        self.dossier = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.dossier.cleanup()

    def test_ordonnanceur(self):
        sortie, code = lancer([
            "1",            # menu principal -> ordonnanceur
            "1", "",        # FCFS, puis Entrée
            "3", "2", "",   # Round Robin, quantum 2
            "5", "2", "",   # comparaison, quantum 2
            "0", "0",       # retour, quitter
        ], self.dossier.name)
        self.assertEqual(code, 0)
        self.assertIn("|    P1    |  P2  |       P3       |     P4     |", sortie)
        self.assertIn("Temps d'attente moyen : 5.75", sortie)
        self.assertIn("Temps de séjour moyen : 15.25", sortie)
        self.assertIn("Au revoir.", sortie)
        self.assertNotIn("Traceback", sortie)

    def test_memoire(self):
        sortie, code = lancer([
            "2",                    # mémoire
            "1", "1", "1500", "",   # pagination : traduire 1500
            "1", "2100", "",        # 2100 -> défaut de page
            "0",
            "2", "1", "n", "",      # remplacement : FIFO, tout afficher
            "4", "",                # comparaison
            "0",
            "3", "", "3", "20", "100", "",   # TLB : exemple, 3 entrées, 20 ns, 100 ns
            "4", "1", "0.8", "20", "100", "", "0",   # EAT direct
            "0", "0",
        ], self.dossier.name)
        self.assertEqual(code, 0)
        self.assertIn("Adresse physique = 2 x 1024 + 476 = 2524", sortie)
        self.assertIn("Défaut de page : la page 2 n'est pas en mémoire.", sortie)
        self.assertIn("Défauts de page : 15 sur 20 demandes (75 %)", sortie)
        self.assertIn("Taux de succès du TLB : 0.50 (50 %)", sortie)
        self.assertIn("= 170.00 ns", sortie)
        self.assertIn("= 140.00 ns", sortie)
        self.assertNotIn("Traceback", sortie)

    def test_memoire_pas_a_pas(self):
        sortie, code = lancer([
            "2", "2", "1", "o",     # FIFO en mode pas à pas
            "", "", "", "t",        # trois étapes, puis terminer
            "", "0", "0", "0",
        ], self.dossier.name)
        self.assertEqual(code, 0)
        self.assertIn("Étape 1 : le processus demande la page 7", sortie)
        self.assertIn("Étape 4 : le processus demande la page 2", sortie)
        self.assertIn("La plus ancienne en mémoire est la page 7", sortie)
        self.assertNotIn("Étape 5 : le processus demande", sortie)   # arrêté par "t"
        self.assertIn("Récapitulatif", sortie)

    def test_fichiers(self):
        sortie, code = lancer([
            "3", "o",                               # fichiers, formater
            "1", "notes.txt", "Bonjour ESINOS", "", # créer
            "2", "notes.txt", "",                   # lire
            "5", "",                                # table des inodes
            "6", "",                                # carte des blocs
            "3", "notes.txt", "",                   # supprimer
            "4", "",                                # lister
            "2", "notes.txt", "",                   # lire un fichier supprimé
            "0", "0",
        ], self.dossier.name)
        self.assertEqual(code, 0)
        self.assertIn("Fichier 'notes.txt' créé avec l'inode 0.", sortie)
        self.assertIn("Bonjour ESINOS", sortie)
        self.assertIn("SCIIIIRRRR#.....", sortie)
        self.assertIn("(aucun fichier)", sortie)
        self.assertIn("Erreur : Le fichier 'notes.txt' n'existe pas.", sortie)
        self.assertNotIn("Traceback", sortie)
        self.assertTrue(os.path.exists(os.path.join(self.dossier.name, "disque_esinos.img")))

    def test_le_disque_survit_a_la_fermeture(self):
        lancer(["3", "o", "1", "a.txt", "toujours là", "", "0", "0"], self.dossier.name)
        sortie, code = lancer(["3", "2", "a.txt", "", "0", "0"], self.dossier.name)
        self.assertEqual(code, 0)
        self.assertIn("toujours là", sortie)

    def test_saisies_invalides(self):
        sortie, code = lancer([
            "9", "abc",                 # choix inconnus au menu principal
            "1", "3", "zero", "0", "2", "",   # quantum : texte, puis 0, puis 2
            "0",
            "2", "2", "5", "a b", "", "1 2 3", "0", "2",   # suite invalide, cadres = 0
            "0", "0",
            "3", "o", "1", "", "x.txt", "ok", "",          # nom vide refusé
            "0", "0",
        ], self.dossier.name)
        self.assertEqual(code, 0)
        self.assertIn("Choix inconnu", sortie)
        self.assertIn("Merci de taper un nombre entier.", sortie)
        self.assertIn("La valeur doit être au moins 1.", sortie)
        self.assertIn("Seulement des nombres entiers", sortie)
        self.assertIn("La réponse ne peut pas être vide.", sortie)
        self.assertNotIn("Traceback", sortie)

    def test_sortie_propre_si_l_entree_s_arrete(self):
        # L'utilisateur ferme le terminal au milieu d'un sous-menu.
        sortie, code = lancer(["1"], self.dossier.name)
        self.assertEqual(code, 0)
        self.assertIn("Au revoir.", sortie)
        self.assertNotIn("Traceback", sortie)

    def test_les_trois_modules_dans_une_seule_session(self):
        sortie, code = lancer([
            "1", "2", "", "0",                       # SJF
            "2", "2", "2", "n", "", "0", "0",        # LRU
            "3", "o", "1", "f", "abc", "", "4", "", "0",
            "0",
        ], self.dossier.name)
        self.assertEqual(code, 0)
        self.assertIn("===== SJF =====", sortie)
        self.assertIn("Défauts de page : 12 sur 20 demandes (60 %)", sortie)
        self.assertIn("Fichier 'f' créé avec l'inode 0.", sortie)


if __name__ == "__main__":
    unittest.main()
