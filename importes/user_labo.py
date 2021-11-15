from importes import Fichier
from outils import Outils


class UserLabo(Fichier):
    """
    Classe pour l'importation des données des Utilisateurs des  laboratoires
    """

    cles = ['year', 'month', 'day', 'week-nbr', 'platf-code', 'platf-op', 'platf-name', 'client-code', 'client-name',
            'client-class', 'user-id', 'user-sciper', 'user-name', 'user-first']
    libelle = "User labo"

    def __init__(self, dossier_source, edition):
        self.nom_fichier = "User-labo_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois-1) + ".csv"
        super().__init__(dossier_source)

    def est_coherent(self, plateformes, clients, users):
        """
        vérifie que les données du fichier importé sont cohérentes
        :param plateformes: plateformes importées
        :param clients: clients importés
        :param users: users importés
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        donnees_list = []

        del self.donnees[0]
        for donnee in self.donnees:
            if donnee['platf-code'] == "":
                msg += "l'id plateforme de la ligne " + str(ligne) + " ne peut être vide\n"
            elif plateformes.contient_id(donnee['platf-code']) == 0:
                msg += "l'id plateforme '" + donnee['platf-code'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"
            if donnee['client-code'] == "":
                msg += "le code client de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['client-code'] not in clients.donnees:
                msg += "le code client " + donnee['client-code'] + " de la ligne " + str(ligne) + \
                       " n'est pas référencé\n"
            if donnee['user-id'] == "":
                msg += "le user id de la ligne " + str(ligne) + " ne peut être vide\n"
            elif users.contient_id(donnee['user-id']) == 0:
                msg += "le user id '" + donnee['user-id'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            donnees_list.append(donnee)
            ligne += 1

        self.donnees = donnees_list
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
