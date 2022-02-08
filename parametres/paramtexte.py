from outils import Outils
from erreurs import ErreurConsistance


class Paramtexte(object):
    """
     Classe pour les labels
     """

    cles = ['invoice-year', 'invoice-month', 'invoice-ref', 'platf-code', 'platf-op', 'platf-sap',
            'platf-name', 'platf-cf', 'platf-fund', 'client-code', 'client-sap', 'client-name',
            'client-idclass', 'client-class', 'client-labelclass', 'oper-id', 'oper-name', 'oper-note', 'oper-PO',
            'staff-note', 'mach-id', 'mach-name', 'mach-extra', 'user-id', 'user-sciper', 'user-name', 'user-first',
            'proj-id', 'proj-nbr', 'proj-name', 'proj-expl', 'flow-type', 'flow-cae', 'flow-noshow', 'flow-lvr',
            'flow-srv', 'item-id', 'item-idsap', 'item-codeK', 'item-textK', 'item-text2K', 'item-K1', 'item-K1a',
            'item-K1b', 'item-K2', 'item-K2a', 'item-K3', 'item-K3a', 'item-K4', 'item-K4a', 'item-K5', 'item-K5a',
            'item-K6', 'item-K6a', 'item-K7', 'item-K7a', 'item-nbr', 'item-name', 'item-unit', 'item-codeD',
            'item-flag-usage', 'item-flag-conso', 'item-labelcode', 'item-sap', 'item-extra', 'transac-date',
            'transac-quantity', 'transac-usage', 'transac-runtime', 'transac-runcae', 'valuation-price',
            'valuation-brut', 'discount-type', 'discount-HC', 'discount-LVR', 'discount-CHF', 'deduct-CHF',
            'valuation-net', 'subsid-code', 'subsid-name', 'subsid-start', 'subsid-end', 'subsid-ok', 'subsid-pourcent',
            'subsid-maxproj', 'subsid-maxmois', 'subsid-reste', 'subsid-CHF', 'subsid-deduct', 'discount-bonus',
            'subsid-bonus', 'total-fact', 'OP-code', 'runtime-N', 'runtime-avg', 'runtime-stddev',
            'conso-propre-march-expl', 'conso-propre-extra-expl', 'conso-propre-march-proj', 'conso-propre-extra-proj',
            'year', 'month', 'day', 'week-nbr', 'subsid-alrdygrant', 'your-ref', 'stat-nbuser-d', 'stat-nbuser-w',
            'stat-nbuser-m', 'stat-nbuser-3m', 'stat-nbuser-6m', 'stat-nbuser-12m', 'stat-trans', 'stat-run',
            'stat-hmach']
    nom_fichier = "paramtext.csv"
    libelle = "Paramètres de Texte"

    def __init__(self, dossier_source):
        """
        initialisation et importation des données

        :param dossier_source: Une instance de la classe dossier.DossierSource
        """
        fichier_reader = dossier_source.reader(self.nom_fichier)
        self.donnees = {}
        labels = []
        try:
            for ligne in fichier_reader:
                if len(ligne) != 2:
                    Outils.fatal(ErreurConsistance(),
                                 self.libelle + ": nombre de colonnes incorrect : " + str(len(ligne)) + ", attendu : 2")
                if ligne[0] in labels:
                    Outils.fatal(ErreurConsistance(), self.libelle + "le label '" + ligne[0] + " n'est pas unique\n")

                ligne[0], err = Outils.est_un_alphanumerique(ligne[0], "le label", chevrons=True)
                if err != "":
                    Outils.fatal(ErreurConsistance(), self.libelle + err)
                ligne[1], err = Outils.est_un_texte(ligne[1], "l'entête")
                if err != "":
                    Outils.fatal(ErreurConsistance(), self.libelle + err)

                labels.append(ligne[0])
                self.donnees[ligne[0]] = ligne[1]

            for cle in self.cles:
                if cle not in labels:
                    Outils.fatal(ErreurConsistance(),
                                 self.libelle + ": la clé " + cle + " n'est pas présente dans paramtext.csv")

        except IOError as e:
            Outils.fatal(e, "impossible d'ouvrir le fichier : "+self.nom_fichier)
