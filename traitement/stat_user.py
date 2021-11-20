from outils import Outils


class StatUser(object):
    """
    Classe pour la création du csv des stats nombre user
    """

    cles = ['invoice-year', 'invoice-month', 'user-id', 'user-sciper', 'user-name', 'user-first', 'client-code',
            'client-sap', 'client-name', 'client-idclass', 'client-class', 'client-labelclass', 'stat-trans',
            'stat-run']

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
        :param par_plate: tri des transactions par plateforme, par users, par client
        """
        pt = self.paramtexte.donnees

        prefixe = "Stat-user_" + str(self.annee) + "_" + Outils.mois_string(self.mois)

        for id_plate in par_plate.keys():
            lignes = []
            plate_name = ""
            par_user = par_plate[id_plate]['users']
            for id_user in par_user.keys():
                par_client = par_user[id_user]
                for code in par_client.keys():
                    tbtr = par_client[code]['transactions']
                    ligne = [self.annee, self.mois]
                    stat_trans = 0
                    stat_run = 0
                    base = trans_vals[tbtr[0]]
                    if plate_name == "":
                        plate_name = base['platf-name']
                    for cle in range(2, len(self.cles)-2):
                        ligne.append(base[self.cles[cle]])
                    for indice in tbtr:
                        trans = trans_vals[indice]
                        stat_trans += 1
                        if str(trans['transac-runcae']) == "1":
                            stat_run += 1
                    ligne += [stat_trans, stat_run]
                    lignes.append(ligne)

            nom = prefixe + "_" + plate_name + ".csv"
            with dossier_destination.writer(nom) as fichier_writer:
                ligne = []
                for cle in self.cles:
                    ligne.append(pt[cle])
                fichier_writer.writerow(ligne)

                for ligne in lignes:
                    fichier_writer.writerow(ligne)
