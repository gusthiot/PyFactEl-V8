from outils import Outils


class StatNbUser(object):
    """
    Classe pour la création du csv des stats nombre user
    """

    cles = ['year', 'month', 'day', 'week-nbr', 'stat-nbuser-d', 'stat-nbuser-w', 'stat-nbuser-m', 'stat-nbuser-3m',
            'stat-nbuser-6m', 'stat-nbuser-12m']

    def __init__(self, edition, paramtexte):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        :param paramtexte: paramètres textuels
        """
        self.annee = edition.annee
        self.mois = edition.mois
        self.paramtexte = paramtexte

    def generer(self, trans_vals, dossier_destination):
        self.prefixe = "Stat-nbre-user_" + str(self.annee) + "_" + Outils.mois_string(self.mois) + ".csv"