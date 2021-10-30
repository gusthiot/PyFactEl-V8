from outils import Outils
from traitement import Recap
from importes import DossierDestination


class AnnexeDetails(Recap):
    """
    Classe pour la création du csv d'annexe détails
    """

    cles = ['invoice-year', 'invoice-month', 'invoice-ref', 'platf-name', 'client-code', 'client-name', 'oper-name',
            'oper-note', 'staff-note', 'mach-name', 'user-sciper', 'user-name', 'user-first', 'proj-nbr', 'proj-name',
            'item-nbr', 'item-name', 'item-unit', 'transac-date', 'transac-quantity', 'valuation-price',
            'valuation-brut', 'discount-type', 'discount-CHF', 'valuation-net', 'subsid-code','subsid-name',
            'subsid-start', 'subsid-end', 'subsid-ok', 'subsid-pourcent', 'subsid-maxproj', 'subsid-maxmois',
            'subsid-reste', 'subsid-CHF', 'deduct-CHF', 'subsid-deduct', 'total-fact', 'discount-bonus', 'subsid-bonus']

    def __init__(self, edition):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        """
        super().__init__(edition)
        self.version = edition.version
        self.unique = edition.client_unique
        self.nom = ""
        self.dossier = ""
        self.chemin = "./"
        self.prefixe = "Annexe-détails_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + \
            str(edition.version)

    def generer(self, trans_vals, paramtexte, paramannexe, par_client):
        """
        génération des fichiers d'annexes détails à partir des transactions
        :param trans_vals: valeurs des transactions générées
        :param paramtexte: paramètres textuels
        :param paramannexe: paramètres d'annexe
        :param par_client: tri des transactions par client
        """
        for donnee in paramannexe.donnees:
            if donnee['nom'] == 'Annexe-détails':
                self.chemin = donnee['chemin']
                self.dossier = donnee['dossier']
        dossier_destination = DossierDestination(self.chemin)

        for code in par_client.keys():
            if self.version > 0 and self.unique != code:
                continue
            tbtr = par_client[code]['transactions']
            base = trans_vals[tbtr[0]]
            self.nom = self.prefixe + "_" + code + "_" + base['client-name'] + ".csv"
            self.valeurs = {}
            ii = 0
            for indice in tbtr:
                val = trans_vals[indice]
                donnee = []
                for cle in range(2, len(self.cles)):
                    donnee.append(val[self.cles[cle]])
                self.ajouter_valeur(donnee, ii)
                ii += 1
            self.csv(dossier_destination, paramtexte)
