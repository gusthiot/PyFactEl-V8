from outils import Outils
import math


class BilanUsages(object):
    """
    Classe pour la création du csv de bilan d'usage
    """

    cles = ['invoice-year', 'invoice-month', 'platf-code', 'platf-name', 'item-id', 'item-nbr', 'item-name',
            'item-unit', 'transac-usage', 'transac-runtime', 'runtime-N', 'runtime-avg', 'runtime-stddev']

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
        génération du fichier de bilan des usages à partir des transactions
        :param trans_vals: valeurs des transactions générées
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param par_plate: tri des transactions par plateforme, par item
        """
        pt = self.paramtexte.donnees

        nom = "Bilan-usage_" + str(self.annee) + "_" + Outils.mois_string(self.mois) + ".csv"

        lignes = []
        ii = 0
        for id_plate in par_plate.keys():
            par_item = par_plate[id_plate]['items']
            for item in par_item.keys():
                tbtr = par_item[item]
                base = trans_vals[tbtr[0]]
                if base['item-flag-usage'] == "OUI":
                    ligne = [self.annee, self.mois]
                    for cle in range(2, len(self.cles)-5):
                        ligne.append(base[self.cles[cle]])
                    usage = 0
                    runtime = 0
                    nn = 0
                    avg = 0
                    stddev = 0
                    rts = []
                    for indice in tbtr:
                        use, info = Outils.est_un_nombre(trans_vals[indice]['transac-usage'], "l'usage", arrondi=4)
                        if info != "":
                            Outils.affiche_message(info)
                        usage += use
                        if trans_vals[indice]['transac-runtime'] != "":
                            rti, info = Outils.est_un_nombre(trans_vals[indice]['transac-runtime'], "le runtime",
                                                             arrondi=4)
                            if info != "":
                                Outils.affiche_message(info)
                            runtime += rti
                            nn += 1
                            rts.append(rti)
                    if nn > 0:
                        avg = runtime / nn
                        somme = 0
                        for rt in rts:
                            somme += math.pow(rt-avg, 2)
                        stddev = math.sqrt(1 / nn * somme)
                    ligne += [round(usage, 4), round(runtime, 4), nn, round(avg, 4), round(stddev, 4)]
                    lignes.append(ligne)
                    ii += 1

        with dossier_destination.writer(nom) as fichier_writer:
            ligne = []
            for cle in self.cles:
                ligne.append(pt[cle])
            fichier_writer.writerow(ligne)

            for ligne in lignes:
                fichier_writer.writerow(ligne)
