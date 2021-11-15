from outils import Outils
from traitement import Recap


class BilanConsos(Recap):
    """
    Classe pour la création du csv de bilan de consommation propre
    """

    cles = ['invoice-year', 'invoice-month', 'platf-code', 'platf-name', 'proj-id', 'proj-nbr', 'proj-name',
            'proj-expl', 'item-id', 'item-nbr', 'item-name', 'item-unit', 'item-codeD', 'item-extra',
            'conso-propre-march-expl', 'conso-propre-extra-expl', 'conso-propre-march-proj', 'conso-propre-extra-proj']

    def __init__(self, edition):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        """
        super().__init__(edition)
        self.nom = "Bilan-conso-propre_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) +  ".csv"

    def generer(self, trans_vals, paramtexte, dossier_destination, par_plate):
        """
        génération du fichier de bilan des consommations à partir des transactions
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
                if base['item-type'] == paramtexte.donnees['item-good']:
                    donnee = []
                    for cle in range(2, len(self.cles) - 4):
                        donnee.append(base[self.cles[cle]])
                    goops = 0
                    extrops = 0
                    goint = 0
                    extrint = 0
                    for indice in tbtr:
                        val = trans_vals[indice]
                        net, info = Outils.est_un_nombre(val['valuation-net'], "le net", arrondi=2)
                        if info != "":
                            Outils.affiche_message(info)
                        if val['client-code'] == val['platf-code']:
                            if val['item-extra'] == "TRUE":
                                if val['proj-expl'] == "TRUE":
                                    extrops += net
                                else:
                                    extrint += net
                            else:
                                if val['proj-expl'] == "TRUE":
                                    goops += net
                                else:
                                    goint += net
                    if goops > 0 or extrops > 0 or goint > 0 or extrint > 0:
                        donnee += [round(goops, 2), round(extrops, 2), round(goint, 2), round(extrint, 2)]
                        self.ajouter_valeur(donnee, ii)
                        ii += 1

        self.csv(dossier_destination, paramtexte)
