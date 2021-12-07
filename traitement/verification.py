import sys
from outils import Outils


class Verification(object):
    """
    Classe servant à vérifier les dates et la cohérence de toutes les données importées
    """

    def __init__(self):
        """
        initialisation à 2 séries de vérification (date et cohérence)
        """
        self.a_verifier = 2

    def verification_date(self, edition, acces, clients, comptes, livraisons, machines, noshows, prestations, users,
                          services):
        """
        vérifie les dates de toutes les données importées
        :param edition: paramètres d'édition
        :param acces: accès importés
        :param clients: clients importés
        :param comptes: comptes importés
        :param livraisons: livraisons importées
        :param machines: machines importées
        :param noshows: no show importés
        :param prestations: prestations importées
        :param users: users importés
        :param services: services importés
        :return: 0 si ok, sinon le nombre d'échecs à la vérification
        """
        verif = 0
        verif += acces.verification_date(edition.annee, edition.mois)
        verif += clients.verification_date(edition.annee, edition.mois)
        verif += comptes.verification_date(edition.annee, edition.mois)
        verif += livraisons.verification_date(edition.annee, edition.mois)
        verif += machines.verification_date(edition.annee, edition.mois)
        verif += prestations.verification_date(edition.annee, edition.mois)
        verif += users.verification_date(edition.annee, edition.mois)
        verif += noshows.verification_date(edition.annee, edition.mois)
        verif += services.verification_date(edition.annee, edition.mois)
        self.a_verifier = 1
        return verif

    def verification_coherence(self, generaux, edition, acces, categories, categprix, clients, coefprests, comptes,
                               grants, livraisons, machines, noshows, plafonds, plateformes, prestations, subsides,
                               users, docpdf, groupes, cles, classes, artsap, userlabs, services):
        """
        vérifie la cohérence des données importées
        :param generaux: paramètres généraux
        :param edition: paramètres d'édition
        :param acces: accès importés
        :param categories: catégories importées
        :param categprix: catégories prix importées
        :param clients: clients importés
        :param coefprests: coefficients prestations importés
        :param comptes: comptes importés
        :param grants: subsides comptabilisés importés
        :param livraisons: livraisons importées
        :param machines: machines importées
        :param noshows: no show importés
        :param plafonds: plafonds de subsides importés
        :param plateformes: plateformes importées
        :param prestations: prestations importées
        :param subsides: subsides importés
        :param users: users importés
        :param docpdf: paramètres d'ajout de document pdf
        :param groupes: groupes importés
        :param cles: clés subsides importées
        :param classes: classes clients importées
        :param artsap: articles sap importés
        :param userlabs: users labo importés
        :param services: services importés
        :return: 0 si ok, sinon le nombre d'échecs à la vérification
        """
        verif = 0
        verif += artsap.est_coherent()
        verif += classes.est_coherent()
        verif += clients.est_coherent(generaux, classes)
        verif += edition.est_coherent(clients)
        verif += docpdf.est_coherent(classes, clients)
        verif += users.est_coherent()
        verif += plateformes.est_coherent(clients)
        verif += categories.est_coherent(artsap, plateformes)
        verif += groupes.est_coherent(categories)
        verif += machines.est_coherent(groupes)
        verif += categprix.est_coherent(classes, categories)
        verif += coefprests.est_coherent(classes, artsap)
        verif += prestations.est_coherent(artsap, coefprests, plateformes, machines)
        verif += subsides.est_coherent()
        verif += plafonds.est_coherent(subsides, artsap)
        verif += cles.est_coherent(plateformes, clients, machines, classes, subsides)
        verif += comptes.est_coherent(clients, subsides)
        verif += grants.est_coherent(comptes, artsap)
        verif += userlabs.est_coherent(plateformes, clients, users)
        verif += acces.est_coherent(comptes, machines, users)
        verif += noshows.est_coherent(comptes, machines, users)
        verif += livraisons.est_coherent(comptes, prestations, users)
        verif += services.est_coherent(comptes, categories, users)

        if verif > 0:
            return verif

        comptes_actifs = Verification.obtenir_comptes_actifs(acces, livraisons, noshows, services)
        clients_actifs = Verification.obtenir_clients_actifs(comptes_actifs, comptes)

        if edition.version > 0 and len(clients_actifs) > 0:
            if len(clients_actifs) > 1:
                Outils.affiche_message("Si version différente de 0, un seul client autorisé")
                sys.exit("Trop de clients pour version > 0")
            if edition.client_unique != clients_actifs[0]:
                Outils.affiche_message("Le client unique des paramètres d'édition n'est pas le même que "
                                       "celui présent dans les transactions")
                sys.exit("clients non-correspondants pour version > 0")
        self.a_verifier = 0
        return verif

    @staticmethod
    def obtenir_comptes_actifs(acces, livraisons, noshows, services):
        """
        retourne la liste des comptes utilisés, pour les accès et les livraisons
        :param acces: accès importés
        :param livraisons: livraisons importées
        :param noshows: noshows importés
        :param services: services importés
        :return: comptes utilisés mappés par clients
        """
        comptes_actifs = []
        for id_compte in livraisons.obtenir_comptes():
            if id_compte not in comptes_actifs:
                comptes_actifs.append(id_compte)
        for id_compte in acces.obtenir_comptes():
            if id_compte not in comptes_actifs:
                comptes_actifs.append(id_compte)
        for id_compte in noshows.obtenir_comptes():
            if id_compte not in comptes_actifs:
                comptes_actifs.append(id_compte)
        for id_compte in services.obtenir_comptes():
            if id_compte not in comptes_actifs:
                comptes_actifs.append(id_compte)

        return comptes_actifs

    @staticmethod
    def obtenir_clients_actifs(comptes_actifs, comptes):
        """
        retourne la liste des clients des comptes actifs
        :param comptes_actifs: comptes actifs
        :param comptes: comptes importés
        :return: comptes utilisés mappés par clients
        """
        clients_actifs = []
        for id_compte in comptes_actifs:
            code_client = comptes.donnees[id_compte]['code_client']
            if code_client not in clients_actifs:
                clients_actifs.append(code_client)
        return clients_actifs
