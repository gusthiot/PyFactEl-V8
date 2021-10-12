from outils import Outils
from traitement import Recap


class UserLabo(Recap):
    """
    Classe pour la création du csv des utilisations des plateformes
    """

    cles = ['year', 'month', 'day', 'week-nbr', 'platf-code', 'platf-op', 'platf-name', 'client-code', 'client-name',
            'client-class', 'user-id', 'user-sciper', 'user-name', 'user-first']

    def __init__(self, edition):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        """
        super().__init__(edition)
        self.nom = "User-labo_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + ".csv"

    def generer(self, trans_vals, paramtexte, dossier_destination, par_plate):
        """
        génération du fichier des usages de labos à partir des transactions
        :param trans_vals: valeurs des transactions générées
        :param paramtexte: paramètres textuels
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param par_plate: tri des transactions par plateforme, par utilisateur, par client, par jour
        """
        ii = 0
        for id_plate in par_plate.keys():
            par_user = par_plate[id_plate]['users']
            for id_user in par_user.keys():
                par_client = par_user[id_user]
                for code in par_client.keys():
                    par_jour = par_client[code]
                    for jour in par_jour.keys():
                        key = par_jour[jour]
                        trans = trans_vals[key]
                        date, info = Outils.est_une_date(trans['transac-date'], "la date de transaction")
                        if info != "":
                            Outils.affiche_message(info)
                        donnee = []
                        for cle in range(2, len(self.cles)):
                            if self.cles[cle] == 'day':
                                donnee.append(date.day)
                            elif self.cles[cle] == 'week-nbr':
                                donnee.append(date.isocalendar()[1])
                            else:
                                donnee.append(trans[self.cles[cle]])
                        self.ajouter_valeur(donnee, ii)
                        ii += 1

        self.csv(dossier_destination, paramtexte)
