from outils import Outils
import math


class StatMachine(object):
    """
    Classe pour la création du csv des stats nombre user
    """

    cles = ['invoice-year', 'invoice-month', 'mach-id', 'mach-name', 'item-id', 'item-nbr', 'item-name', 'item-unit',
            'transac-quantity', 'transac-usage', 'transac-runtime', 'runtime-N', 'runtime-avg', 'runtime-stddev']

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
        génération du fichier de stats des users à partir des transactions
        :param trans_vals: valeurs des transactions générées
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param par_plate: tri des transactions par plateforme, par machine
        """
        pt = self.paramtexte.donnees

        prefixe = "Stat-machine_" + str(self.annee) + "_" + Outils.mois_string(self.mois) + ".csv"

        for id_plate in par_plate.keys():
            lignes = []
            plate_name = ""
            par_machine = par_plate[id_plate]['machines']
            for id_machine in par_machine.keys():
                ligne = [self.annee, self.mois]
                tbtr = par_machine[id_machine]
                base = trans_vals[tbtr[0]]
                if plate_name == "":
                    plate_name = base['platf-name']
                for cle in range(2, len(self.cles)-6):
                    ligne.append(base[self.cles[cle]])
                quantity = 0
                usage = 0
                runtime = 0
                nn = 0
                avg = 0
                stddev = 0
                rts = []
                for indice in tbtr:
                    qua, info = Outils.est_un_nombre(trans_vals[indice]['transac-quantity'], "la quantité", arrondi=4)
                    if info != "":
                        Outils.affiche_message(info)
                    quantity += qua
                    use, info = Outils.est_un_nombre(trans_vals[indice]['transac-usage'], "l'usage", arrondi=4)
                    if info != "":
                        Outils.affiche_message(info)
                    usage += use
                    run = trans_vals[indice]['transac-runtime']
                    if run != "":
                        run, info = Outils.est_un_nombre(run, "le runtime", arrondi=4)
                        if info != "":
                            Outils.affiche_message(info)
                        runtime += run
                        nn += 1
                if nn > 0:
                    avg = runtime / nn
                    somme = 0
                    for rt in rts:
                        somme += math.pow(rt-avg, 2)
                    stddev = math.sqrt(1 / nn * somme)
                ligne += [round(quantity, 4), round(usage, 4), round(runtime, 4), nn, round(avg, 4), round(stddev, 4)]
                lignes.append(ligne)

            nom = prefixe + "_" + plate_name + ".csv"
            with dossier_destination.writer(nom) as fichier_writer:
                ligne = []
                for cle in self.cles:
                    ligne.append(pt[cle])
                fichier_writer.writerow(ligne)

                for ligne in lignes:
                    fichier_writer.writerow(ligne)
