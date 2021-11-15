from importes import Fichier
from outils import Outils


class UserLabo(Fichier):
    """
    Classe pour l'importation des données des Utilisateurs des  laboratoires
    """

    cles = ['year', 'month', 'day', 'week', 'id_plateforme', 'code_p', 'intitule', 'code_client', 'abrev_labo',
            'id_classe', 'id_user', 'sciper', 'nom', 'prenom']
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
        donnees_dict = {}

        del self.donnees[0]
        for donnee in self.donnees:
            if donnee['id_plateforme'] == "":
                msg += "l'id plateforme de la ligne " + str(ligne) + " ne peut être vide\n"
            elif plateformes.contient_id(donnee['id_plateforme']) == 0:
                msg += "l'id plateforme '" + donnee['id_plateforme'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"
            if donnee['code_client'] == "":
                msg += "le code client de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['code_client'] not in clients.donnees:
                msg += "le code client " + donnee['code_client'] + " de la ligne " + str(ligne) + \
                       " n'est pas référencé\n"
            if donnee['id_user'] == "":
                msg += "le user id de la ligne " + str(ligne) + " ne peut être vide\n"
            elif users.contient_id(donnee['id_user']) == 0:
                msg += "le user id '" + donnee['id_user'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            donnees_dict[donnee['id_plateforme']+donnee['code_client']+donnee['id_user']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
