from outils import Outils


class StatClient(object):
    """
    Classe pour la création du csv des stats nombre user
    """

    cles = ['invoice-year', 'invoice-month', 'client-code', 'client-sap', 'client-name', 'client-idclass',
            'client-class', 'client-labelclass', 'stat-trans', 'stat-run', 'stat-nbuser-m', 'stat-nbuser-3m',
            'stat-nbuser-6m', 'stat-nbuser-12m']

    def __init__(self, edition, paramtexte):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        """
        self.annee = edition.annee
        self.mois = edition.mois
        self.paramtexte = paramtexte

    def generer(self, trans_vals, dossier_destination):
        prefixe = "Stat-client_" + str(self.annee) + "_" + Outils.mois_string(self.mois) + ".csv"