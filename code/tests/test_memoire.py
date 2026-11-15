"""
test_memoire.py — Tests automatiques du module 2.

Lancement (depuis le dossier code/) :

    python3 -m unittest -v

Les résultats attendus sont calculés à la main dans docs/MODULE2_MEMOIRE.md,
ou sont les résultats connus des exemples classiques des manuels.
"""

import unittest

from memoire.pagination import (decouper_adresse, traduire, bits_deplacement,
                                DefautDePage)
from memoire.remplacement import fifo, lru, optimal, compter_defauts
from memoire.tlb import simuler_tlb, taux_de_succes, eat_tlb, eat_defauts
from memoire.affichage import (formater_tableau, formater_comparaison,
                               formater_etape, formater_tlb, texte_cadres)
from memoire.menu import exemple_references, exemple_pagination, exemple_tlb


def cadres_de(etapes):
    """Contenu des cadres après chaque étape, facile à comparer."""
    return [etape.cadres for etape in etapes]


class TestPagination(unittest.TestCase):

    def setUp(self):
        # Pages de 1024 octets ; table {0: 5, 1: 2, 2: None, 3: 7}
        self.taille_page, self.table = exemple_pagination()

    def test_decoupage(self):
        self.assertEqual(decouper_adresse(1500, 1024), (1, 476))
        self.assertEqual(decouper_adresse(0, 1024), (0, 0))
        self.assertEqual(decouper_adresse(1023, 1024), (0, 1023))   # dernier octet de la page 0
        self.assertEqual(decouper_adresse(1024, 1024), (1, 0))      # premier octet de la page 1
        self.assertEqual(decouper_adresse(235, 100), (2, 35))

    def test_traduction(self):
        # 1500 -> page 1, déplacement 476 -> cadre 2 -> 2 x 1024 + 476 = 2524
        self.assertEqual(traduire(1500, self.taille_page, self.table), 2524)
        self.assertEqual(traduire(0, self.taille_page, self.table), 5120)
        self.assertEqual(traduire(3072, self.taille_page, self.table), 7168)

    def test_defaut_de_page(self):
        # 2100 -> page 2, qui n'est pas en mémoire
        with self.assertRaises(DefautDePage):
            traduire(2100, self.taille_page, self.table)

    def test_adresse_hors_du_processus(self):
        # 4096 -> page 4, qui n'existe pas dans la table
        with self.assertRaises(ValueError):
            traduire(4096, self.taille_page, self.table)

    def test_valeurs_impossibles(self):
        with self.assertRaises(ValueError):
            decouper_adresse(-1, 1024)
        with self.assertRaises(ValueError):
            decouper_adresse(10, 0)

    def test_bits_du_deplacement(self):
        self.assertEqual(bits_deplacement(1024), 10)
        self.assertEqual(bits_deplacement(4096), 12)
        self.assertEqual(bits_deplacement(1), 0)
        self.assertIsNone(bits_deplacement(100))    # 100 n'est pas une puissance de 2


class TestPetitExemple(unittest.TestCase):
    """Suite 1 2 3 1 4 1 2 avec 3 cadres : déroulée à la main dans le guide."""

    REFERENCES = [1, 2, 3, 1, 4, 1, 2]

    def test_fifo(self):
        etapes = fifo(self.REFERENCES, 3)
        self.assertEqual(cadres_de(etapes), [
            [1, None, None], [1, 2, None], [1, 2, 3], [1, 2, 3],
            [4, 2, 3], [4, 1, 3], [4, 1, 2]])
        self.assertEqual([e.defaut for e in etapes],
                         [True, True, True, False, True, True, True])
        self.assertEqual([e.evincee for e in etapes],
                         [None, None, None, None, 1, 2, 3])
        self.assertEqual(compter_defauts(etapes), 6)

    def test_lru(self):
        etapes = lru(self.REFERENCES, 3)
        self.assertEqual(cadres_de(etapes), [
            [1, None, None], [1, 2, None], [1, 2, 3], [1, 2, 3],
            [1, 4, 3], [1, 4, 3], [1, 4, 2]])
        self.assertEqual([e.evincee for e in etapes],
                         [None, None, None, None, 2, None, 3])
        self.assertEqual(compter_defauts(etapes), 5)

    def test_optimal(self):
        etapes = optimal(self.REFERENCES, 3)
        self.assertEqual(cadres_de(etapes), [
            [1, None, None], [1, 2, None], [1, 2, 3], [1, 2, 3],
            [1, 2, 4], [1, 2, 4], [1, 2, 4]])
        self.assertEqual([e.evincee for e in etapes],
                         [None, None, None, None, 3, None, None])
        self.assertEqual(compter_defauts(etapes), 4)

    def test_explications(self):
        etape = fifo(self.REFERENCES, 3)[4]      # étape 5 : la page 4 chasse la page 1
        self.assertIn("La plus ancienne en mémoire est la page 1", etape.explication)
        etape = lru(self.REFERENCES, 3)[4]
        self.assertIn("La moins récemment utilisée est la page 2", etape.explication)
        etape = optimal(self.REFERENCES, 3)[4]
        self.assertIn("page 3 plus jamais demandée", etape.explication)


class TestExemplesClassiques(unittest.TestCase):

    def test_suite_des_manuels_15_12_9(self):
        references, nb_cadres = exemple_references()    # 20 demandes, 3 cadres
        self.assertEqual(compter_defauts(fifo(references, nb_cadres)), 15)
        self.assertEqual(compter_defauts(lru(references, nb_cadres)), 12)
        self.assertEqual(compter_defauts(optimal(references, nb_cadres)), 9)

    def test_anomalie_de_belady(self):
        # Avec FIFO, ajouter un cadre peut AUGMENTER le nombre de défauts.
        references = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
        self.assertEqual(compter_defauts(fifo(references, 3)), 9)
        self.assertEqual(compter_defauts(fifo(references, 4)), 10)
        # LRU et Optimal n'ont pas ce défaut.
        self.assertEqual(compter_defauts(lru(references, 3)), 10)
        self.assertEqual(compter_defauts(lru(references, 4)), 8)
        self.assertEqual(compter_defauts(optimal(references, 3)), 7)
        self.assertEqual(compter_defauts(optimal(references, 4)), 6)


class TestCasParticuliers(unittest.TestCase):

    def test_un_seul_cadre(self):
        # Chaque changement de page est un défaut.
        self.assertEqual(compter_defauts(fifo([1, 1, 2, 2, 1], 1)), 3)

    def test_assez_de_cadres(self):
        # Autant de cadres que de pages différentes : un défaut par page, pas plus.
        for algorithme in (fifo, lru, optimal):
            self.assertEqual(compter_defauts(algorithme([3, 1, 2, 1, 3, 2], 3)), 3)

    def test_optimal_jamais_pire(self):
        references, nb_cadres = exemple_references()
        for cadres in range(1, 6):
            meilleur = compter_defauts(optimal(references, cadres))
            self.assertLessEqual(meilleur, compter_defauts(fifo(references, cadres)))
            self.assertLessEqual(meilleur, compter_defauts(lru(references, cadres)))

    def test_la_liste_n_est_pas_modifiee(self):
        references = [1, 2, 3, 1, 4]
        fifo(references, 2)
        self.assertEqual(references, [1, 2, 3, 1, 4])

    def test_erreurs(self):
        with self.assertRaises(ValueError):
            fifo([], 3)
        with self.assertRaises(ValueError):
            lru([1, 2], 0)
        with self.assertRaises(ValueError):
            optimal([1, -2], 3)


class TestTLB(unittest.TestCase):

    def setUp(self):
        self.adresses, self.taille_page, self.table, self.taille_tlb = exemple_tlb()

    def test_simulation(self):
        etapes = simuler_tlb(self.adresses, self.taille_page, self.table, self.taille_tlb)
        self.assertEqual([e.page for e in etapes], [2, 2, 5, 1, 2, 5, 7, 1, 2, 7])
        self.assertEqual([e.succes for e in etapes],
                         [False, True, False, False, True, True, False, True, False, True])
        self.assertEqual([e.adresse_physique for e in etapes],
                         [535, 540, 12, 799, 560, 30, 401, 750, 545, 405])
        self.assertEqual(etapes[6].contenu, [(5, 0), (1, 7), (7, 4)])   # la page 2 est sortie
        self.assertEqual(etapes[9].contenu, [(1, 7), (7, 4), (2, 5)])
        self.assertEqual(taux_de_succes(etapes), 0.5)

    def test_tlb_plus_grand_plus_de_succes(self):
        petit = simuler_tlb(self.adresses, self.taille_page, self.table, 1)
        grand = simuler_tlb(self.adresses, self.taille_page, self.table, 4)
        self.assertEqual(taux_de_succes(petit), 0.1)
        self.assertEqual(taux_de_succes(grand), 0.6)

    def test_adresse_invalide(self):
        with self.assertRaises(ValueError):
            simuler_tlb([900], self.taille_page, self.table, 2)    # page 9 inexistante
        with self.assertRaises(ValueError):
            simuler_tlb([10], self.taille_page, self.table, 0)


class TestEAT(unittest.TestCase):

    def test_eat_tlb(self):
        # 0.8 x (20 + 100) + 0.2 x (20 + 200) = 96 + 44 = 140
        self.assertAlmostEqual(eat_tlb(0.8, 20, 100), 140)
        # 0.98 x 120 + 0.02 x 220 = 117.6 + 4.4 = 122
        self.assertAlmostEqual(eat_tlb(0.98, 20, 100), 122)
        # Exemple du projet : taux 0.5 -> 0.5 x 120 + 0.5 x 220 = 170
        self.assertAlmostEqual(eat_tlb(0.5, 20, 100), 170)

    def test_eat_tlb_temps_du_tlb_neglige(self):
        # 0.8 x 100 + 0.2 x 200 = 120
        self.assertAlmostEqual(eat_tlb(0.8, 0, 100), 120)

    def test_eat_tlb_cas_extremes(self):
        self.assertAlmostEqual(eat_tlb(1, 20, 100), 120)   # toujours succès
        self.assertAlmostEqual(eat_tlb(0, 20, 100), 220)   # toujours échec

    def test_eat_defauts(self):
        # 0.999 x 200 + 0.001 x 8 000 000 = 199.8 + 8000 = 8199.8 ns
        self.assertAlmostEqual(eat_defauts(0.001, 200, 8000000), 8199.8)
        self.assertAlmostEqual(eat_defauts(0, 200, 8000000), 200)

    def test_erreurs(self):
        with self.assertRaises(ValueError):
            eat_tlb(1.5, 20, 100)
        with self.assertRaises(ValueError):
            eat_tlb(0.8, -1, 100)
        with self.assertRaises(ValueError):
            eat_defauts(-0.1, 200, 8000000)


class TestAffichage(unittest.TestCase):

    def test_texte_cadres(self):
        self.assertEqual(texte_cadres([7, 0, None]), "[7] [0] [-]")

    def test_tableau(self):
        texte = formater_tableau(fifo([1, 2, 3, 1, 4, 1, 2], 3))
        self.assertIn("DÉFAUT, la page 1 sort", texte)
        self.assertIn("présente", texte)
        self.assertIn("Défauts de page : 6 sur 7 demandes (86 %)", texte)

    def test_etape_detaillee(self):
        texte = formater_etape(fifo([1, 2], 3)[1])
        self.assertIn("Étape 2 : le processus demande la page 2", texte)
        self.assertIn("Cadres : [1] [2] [-]", texte)

    def test_comparaison(self):
        references, nb_cadres = exemple_references()
        lignes = formater_comparaison(references, nb_cadres).split("\n")
        self.assertEqual(lignes[1].split(), ["FIFO", "15", "75%"])
        self.assertEqual(lignes[2].split(), ["LRU", "12", "60%"])
        self.assertEqual(lignes[3].split(), ["Optimal", "9", "45%"])

    def test_tableau_tlb(self):
        adresses, taille_page, table, taille_tlb = exemple_tlb()
        texte = formater_tlb(simuler_tlb(adresses, taille_page, table, taille_tlb))
        self.assertIn("succès", texte)
        self.assertIn("5:0 1:7 7:4", texte)


if __name__ == "__main__":
    unittest.main()
