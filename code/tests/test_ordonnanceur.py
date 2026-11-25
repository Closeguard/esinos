"""
test_ordonnanceur.py — Tests automatiques du module 1.

Lancement (depuis le dossier code/) :

    python3 -m unittest -v

Principe : chaque test compare ce que le programme calcule avec un résultat
calculé À LA MAIN (détaillé dans docs/MODULE1_ORDONNANCEUR.md). Si un seul
nombre diffère, le test échoue et dit lequel.
"""

import unittest

from ordonnanceur.modeles import Processus, Segment
from ordonnanceur.algorithmes import (fcfs, sjf, priorite, round_robin,
                                      ajouter_segment)
from ordonnanceur.statistiques import calculer_statistiques, calculer_utilisation_cpu
from ordonnanceur.affichage import dessiner_gantt, formater_statistiques
from ordonnanceur.menu import exemple


def en_tuples(gantt):
    """Transforme le Gantt en liste de (nom, debut, fin), facile à comparer."""
    return [(s.nom, s.debut, s.fin) for s in gantt]


def moyennes(processus, gantt):
    """Renvoie (attente moyenne, séjour moyen)."""
    lignes, attente_moyenne, sejour_moyen = calculer_statistiques(processus, gantt)
    return attente_moyenne, sejour_moyen


class TestExempleDuProjet(unittest.TestCase):
    """P1(arr 0, durée 5, prio 3)  P2(1, 3, 4)  P3(2, 8, 1)  P4(3, 6, 2)"""

    def setUp(self):
        # setUp est exécutée avant chaque test : on repart d'une liste neuve.
        self.processus = exemple()

    def test_fcfs(self):
        gantt = fcfs(self.processus)
        self.assertEqual(en_tuples(gantt), [
            ("P1", 0, 5), ("P2", 5, 8), ("P3", 8, 16), ("P4", 16, 22)])
        self.assertEqual(moyennes(self.processus, gantt), (5.75, 11.25))

    def test_sjf(self):
        gantt = sjf(self.processus)
        self.assertEqual(en_tuples(gantt), [
            ("P1", 0, 5), ("P2", 5, 8), ("P4", 8, 14), ("P3", 14, 22)])
        self.assertEqual(moyennes(self.processus, gantt), (5.25, 10.75))

    def test_priorite(self):
        gantt = priorite(self.processus)
        self.assertEqual(en_tuples(gantt), [
            ("P1", 0, 5), ("P3", 5, 13), ("P4", 13, 19), ("P2", 19, 22)])
        self.assertEqual(moyennes(self.processus, gantt), (7.75, 13.25))

    def test_round_robin_quantum_2(self):
        gantt = round_robin(self.processus, 2)
        self.assertEqual(en_tuples(gantt), [
            ("P1", 0, 2), ("P2", 2, 4), ("P3", 4, 6), ("P1", 6, 8),
            ("P4", 8, 10), ("P2", 10, 11), ("P3", 11, 13), ("P1", 13, 14),
            ("P4", 14, 16), ("P3", 16, 18), ("P4", 18, 20), ("P3", 20, 22)])
        self.assertEqual(moyennes(self.processus, gantt), (9.75, 15.25))

    def test_detail_des_temps_fcfs(self):
        lignes, _, _ = calculer_statistiques(self.processus, fcfs(self.processus))
        self.assertEqual([l["fin"] for l in lignes], [5, 8, 16, 22])
        self.assertEqual([l["sejour"] for l in lignes], [5, 7, 14, 19])
        self.assertEqual([l["attente"] for l in lignes], [0, 4, 6, 13])

    def test_les_processus_ne_sont_pas_modifies(self):
        round_robin(self.processus, 2)
        sjf(self.processus)
        self.assertEqual([p.nom for p in self.processus], ["P1", "P2", "P3", "P4"])
        self.assertEqual([p.duree for p in self.processus], [5, 3, 8, 6])


class TestExempleClassique(unittest.TestCase):
    """L'exemple des manuels : P1=24, P2=3, P3=3, tous arrivés à t=0."""

    def setUp(self):
        self.processus = [Processus("P1", 0, 24), Processus("P2", 0, 3),
                          Processus("P3", 0, 3)]

    def test_fcfs_attente_17(self):
        gantt = fcfs(self.processus)
        self.assertEqual(en_tuples(gantt), [("P1", 0, 24), ("P2", 24, 27), ("P3", 27, 30)])
        self.assertEqual(moyennes(self.processus, gantt)[0], 17)

    def test_sjf_attente_3(self):
        gantt = sjf(self.processus)
        self.assertEqual(en_tuples(gantt), [("P2", 0, 3), ("P3", 3, 6), ("P1", 6, 30)])
        self.assertEqual(moyennes(self.processus, gantt)[0], 3)

    def test_round_robin_quantum_4(self):
        gantt = round_robin(self.processus, 4)
        # P1 tourne de 10 à 30 d'un seul bloc : les tranches qui se suivent
        # sont fusionnées en une seule case.
        self.assertEqual(en_tuples(gantt), [
            ("P1", 0, 4), ("P2", 4, 7), ("P3", 7, 10), ("P1", 10, 30)])
        self.assertAlmostEqual(moyennes(self.processus, gantt)[0], 17 / 3)


class TestCasParticuliers(unittest.TestCase):

    def test_cpu_inactif(self):
        processus = [Processus("P1", 2, 3), Processus("P2", 10, 2)]
        attendu = [("--", 0, 2), ("P1", 2, 5), ("--", 5, 10), ("P2", 10, 12)]
        self.assertEqual(en_tuples(fcfs(processus)), attendu)
        self.assertEqual(en_tuples(sjf(processus)), attendu)
        self.assertEqual(en_tuples(priorite(processus)), attendu)
        self.assertEqual(en_tuples(round_robin(processus, 2)), attendu)
        # Le temps d'inactivité ne compte pas comme de l'attente.
        self.assertEqual(moyennes(processus, fcfs(processus)), (0, 2.5))

    def test_un_seul_processus(self):
        processus = [Processus("P1", 0, 4)]
        self.assertEqual(en_tuples(fcfs(processus)), [("P1", 0, 4)])
        self.assertEqual(en_tuples(round_robin(processus, 1)), [("P1", 0, 4)])

    def test_egalite_ordre_de_la_liste(self):
        # Même arrivée, même durée, même priorité : l'ordre de saisie décide.
        processus = [Processus("A", 0, 2, 1), Processus("B", 0, 2, 1)]
        attendu = [("A", 0, 2), ("B", 2, 4)]
        self.assertEqual(en_tuples(fcfs(processus)), attendu)
        self.assertEqual(en_tuples(sjf(processus)), attendu)
        self.assertEqual(en_tuples(priorite(processus)), attendu)

    def test_sjf_ne_choisit_que_parmi_les_arrives(self):
        # B est plus court, mais il n'est pas encore là quand le CPU se libère.
        processus = [Processus("A", 0, 5), Processus("B", 1, 1)]
        self.assertEqual(en_tuples(sjf(processus)), [("A", 0, 5), ("B", 5, 6)])

    def test_priorite_petit_nombre_gagne(self):
        processus = [Processus("A", 0, 2, 5), Processus("B", 0, 2, 1)]
        self.assertEqual(en_tuples(priorite(processus)), [("B", 0, 2), ("A", 2, 4)])

    def test_grand_quantum_donne_fcfs(self):
        processus = exemple()
        self.assertEqual(en_tuples(round_robin(processus, 100)),
                         en_tuples(fcfs(processus)))

    def test_round_robin_nouvel_arrive_avant_interrompu(self):
        # À t=2, A est interrompu et B arrive : B passe devant A.
        processus = [Processus("A", 0, 4), Processus("B", 2, 2)]
        self.assertEqual(en_tuples(round_robin(processus, 2)), [
            ("A", 0, 2), ("B", 2, 4), ("A", 4, 6)])

    def test_liste_donnee_dans_le_desordre(self):
        processus = [Processus("B", 3, 2), Processus("A", 0, 2)]
        attendu = [("A", 0, 2), ("--", 2, 3), ("B", 3, 5)]
        self.assertEqual(en_tuples(fcfs(processus)), attendu)
        self.assertEqual(en_tuples(round_robin(processus, 5)), attendu)


class TestUtilisationCPU(unittest.TestCase):

    def test_cpu_toujours_occupe(self):
        # Dans l'exemple du projet, le CPU ne s'arrête jamais : 22 sur 22.
        self.assertEqual(calculer_utilisation_cpu(fcfs(exemple())), 100)

    def test_cpu_inactif(self):
        # CPU inactif de 0 à 2 et de 5 à 10 : il travaille 5 unités sur 12.
        processus = [Processus("P1", 2, 3), Processus("P2", 10, 2)]
        self.assertAlmostEqual(calculer_utilisation_cpu(fcfs(processus)), 500 / 12)

    def test_meme_resultat_pour_tous_les_algorithmes(self):
        # Le CPU travaille autant au total, quel que soit l'ordre de passage.
        processus = [Processus("P1", 2, 3), Processus("P2", 10, 2)]
        for gantt in (sjf(processus), priorite(processus), round_robin(processus, 2)):
            self.assertAlmostEqual(calculer_utilisation_cpu(gantt), 500 / 12)

    def test_gantt_vide(self):
        self.assertEqual(calculer_utilisation_cpu([]), 0)


class TestErreurs(unittest.TestCase):
    """Les valeurs impossibles doivent être refusées avec un message clair."""

    def test_duree_nulle(self):
        with self.assertRaises(ValueError):
            Processus("P1", 0, 0)

    def test_arrivee_negative(self):
        with self.assertRaises(ValueError):
            Processus("P1", -1, 3)

    def test_nom_vide(self):
        with self.assertRaises(ValueError):
            Processus("", 0, 3)

    def test_liste_vide(self):
        with self.assertRaises(ValueError):
            fcfs([])

    def test_noms_en_double(self):
        with self.assertRaises(ValueError):
            sjf([Processus("P1", 0, 3), Processus("P1", 1, 2)])

    def test_quantum_nul(self):
        with self.assertRaises(ValueError):
            round_robin([Processus("P1", 0, 3)], 0)


class TestAffichage(unittest.TestCase):

    def test_fusion_des_segments(self):
        gantt = []
        ajouter_segment(gantt, "P1", 0, 2)
        ajouter_segment(gantt, "P1", 2, 4)   # même processus, à la suite
        ajouter_segment(gantt, "P2", 4, 5)
        self.assertEqual(en_tuples(gantt), [("P1", 0, 4), ("P2", 4, 5)])

    def test_dessin_du_gantt(self):
        gantt = [Segment("P1", 0, 5), Segment("P2", 5, 8)]
        attendu = ("+----------+------+\n"
                   "|    P1    |  P2  |\n"
                   "+----------+------+\n"
                   "0          5      8")
        self.assertEqual(dessiner_gantt(gantt, echelle=2), attendu)

    def test_tableau_contient_les_moyennes(self):
        processus = exemple()
        lignes, attente, sejour = calculer_statistiques(processus, fcfs(processus))
        texte = formater_statistiques(lignes, attente, sejour)
        self.assertIn("Temps d'attente moyen : 5.75", texte)
        self.assertIn("Temps de séjour moyen : 11.25", texte)


if __name__ == "__main__":
    unittest.main()
