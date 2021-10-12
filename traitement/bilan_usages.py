from outils import Outils
from traitement import Recap


class BilanUsages(Recap):
    """
    Classe pour la création du csv de bilan d'usage
    """

    cles = ['invoice-year', 'invoice-month', 'platf-code', 'platf-name', 'item-id', 'item-nbr', 'item-name',
            'item-unit', 'transac-usage']

    def __init__(self, edition):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        """
        super().__init__(edition)
        self.nom = "Bilan-usage_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + ".csv"

    def generer(self, trans_vals, paramtexte, dossier_destination, par_plate):
        """
        génération du fichier de bilan des usages à partir des transactions
        :param trans_vals: valeurs des transactions générées
        :param paramtexte: paramètres textuels
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param par_plate: tri des transactions par plateforme, par item
        """
        ii = 0
        for id_plate in par_plate.keys():
            par_item = par_plate[id_plate]['items']
            for item in par_item.keys():
                tbtr = par_item[item]
                base = trans_vals[tbtr[0]]
                if base['item-type'] == paramtexte.donnees['item-service']:
                    donnee = []
                    for cle in range(2, len(self.cles)-1):
                        donnee.append(base[self.cles[cle]])
                    usage = 0
                    for indice in tbtr:
                        val, info = Outils.est_un_nombre(trans_vals[indice]['transac-usage'], "l'usage", arrondi=4)
                        if info != "":
                            Outils.affiche_message(info)
                        usage += val
                    donnee += [round(usage, 4)]
                    self.ajouter_valeur(donnee, ii)
                    ii += 1

        self.csv(dossier_destination, paramtexte)
