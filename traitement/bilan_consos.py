from outils import Outils


class BilanConsos(object):
    """
    Classe pour la création du csv de bilan de consommation propre
    """

    cles = ['invoice-year', 'invoice-month', 'platf-code', 'platf-name', 'proj-id', 'proj-nbr', 'proj-name',
            'proj-expl', 'item-id', 'item-nbr', 'item-name', 'item-unit', 'item-idsap', 'item-codeD', 'item-extra',
            'mach-extra', 'conso-propre-march-expl', 'conso-propre-extra-expl', 'conso-propre-march-proj',
            'conso-propre-extra-proj']

    def __init__(self, edition, paramtexte):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        :param paramtexte: paramètres textuels
        """
        self.annee = edition.annee
        self.mois = edition.mois
        self.paramtexte = paramtexte

    def generer(self, trans_vals, dossier_destination, par_plate):
        """
        génération du fichier de bilan des consommations à partir des transactions
        :param trans_vals: valeurs des transactions générées
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param par_plate: tri des transactions par plateforme, par item
        """
        pt = self.paramtexte.donnees

        nom = "Bilan-conso-propre_" + str(self.annee) + "_" + Outils.mois_string(self.mois) + ".csv"

        lignes = []
        ii = 0
        for id_plate in par_plate.keys():
            par_proj = par_plate[id_plate]['projets']
            for id_projet in par_proj.keys():
                par_item = par_proj[id_projet]
                for item in par_item.keys():
                    tbtr = par_item[item]
                    base = trans_vals[tbtr[0]]
                    if base['item-flag-conso'] == "OUI":
                        ligne = [self.annee, self.mois]
                        for cle in range(2, len(self.cles) - 4):
                            ligne.append(base[self.cles[cle]])
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
                            ligne += [round(goops, 2), round(extrops, 2), round(goint, 2), round(extrint, 2)]
                            lignes.append(ligne)
                            ii += 1

        with dossier_destination.writer(nom) as fichier_writer:
            ligne = []
            for cle in self.cles:
                ligne.append(pt[cle])
            fichier_writer.writerow(ligne)

            for ligne in lignes:
                fichier_writer.writerow(ligne)
