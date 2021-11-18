from outils import Outils
from importes import DossierDestination


class AnnexeDetails(object):
    """
    Classe pour la création du csv d'annexe détails
    """

    cles = ['invoice-year', 'invoice-month', 'invoice-ref', 'platf-name', 'client-code', 'client-name', 'oper-name',
            'oper-note', 'staff-note', 'mach-name', 'user-sciper', 'user-name', 'user-first', 'proj-nbr', 'proj-name',
            'item-nbr', 'item-name', 'item-unit', 'transac-date', 'transac-quantity', 'valuation-price',
            'valuation-brut', 'discount-type', 'discount-CHF', 'valuation-net', 'subsid-code', 'subsid-name',
            'subsid-start', 'subsid-end', 'subsid-ok', 'subsid-pourcent', 'subsid-maxproj', 'subsid-maxmois',
            'subsid-reste', 'subsid-CHF', 'deduct-CHF', 'subsid-deduct', 'total-fact', 'discount-bonus', 'subsid-bonus']

    def __init__(self, edition, paramtexte, paramannexe):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        :param paramtexte: paramètres textuels
        :param paramannexe: paramètres d'annexe
        """
        self.annee = edition.annee
        self.mois = edition.mois
        self.version = edition.version
        self.unique = edition.client_unique
        self.paramtexte = paramtexte
        self.paramannexe = paramannexe
        self.dossier = ""
        self.chemin = "./"
        self.prefixe = "Annexe-détails_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + \
            str(edition.version)

    def generer(self, trans_vals, par_client):
        """
        génération des fichiers d'annexes détails à partir des transactions
        :param trans_vals: valeurs des transactions générées
        :param par_client: tri des transactions par client
        """
        pt = self.paramtexte.donnees

        for donnee in self.paramannexe.donnees:
            if donnee['nom'] == 'Annexe-détails':
                self.chemin = donnee['chemin']
                self.dossier = donnee['dossier']
        dossier_destination = DossierDestination(self.chemin)

        for code in par_client.keys():
            if self.version > 0 and self.unique != code:
                continue
            tbtr = par_client[code]['transactions']
            base = trans_vals[tbtr[0]]
            nom = self.prefixe + "_" + code + "_" + base['client-name'] + ".csv"
            ii = 0
            lignes = []
            for indice in tbtr:
                val = trans_vals[indice]
                ligne = [self.annee, self.mois]
                for cle in range(2, len(self.cles)):
                    ligne.append(val[self.cles[cle]])
                lignes.append(ligne)
                ii += 1
            with dossier_destination.writer(nom) as fichier_writer:
                ligne = []
                for cle in self.cles:
                    ligne.append(pt[cle])
                fichier_writer.writerow(ligne)

                for ligne in lignes:
                    fichier_writer.writerow(ligne)
