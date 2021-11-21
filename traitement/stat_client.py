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

    def generer(self, trans_vals, dossier_destination, par_plate, par_plate_ul):
        """
        génération du fichier de stats des clients à partir des transactions
        :param trans_vals: valeurs des transactions générées
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param par_plate: tri des transactions par plateforme, par users, par client
        :param par_plate_ul: tri des users labo par plateforme, par date
        """

        pt = self.paramtexte.donnees
        prefixe = "Stat-client_" + str(self.annee) + "_" + Outils.mois_string(self.mois)

        for id_plateforme in par_plate_ul.keys():
            stats_clients = {}
            pp = par_plate_ul[id_plateforme]
            if self.mois in pp['annees'][self.annee]:
                pm = pp['annees'][self.annee][self.mois]['clients']
                for code in pm:
                    stats_clients[code] = {'1m': len(pm[code]), '3m': pm[code], '6m': pm[code], '12m': pm[code]}
            for gap in range(1, 12):
                if gap < self.mois:
                    mo = self.mois - gap
                    an = self.annee
                else:
                    mo = 12 + self.mois - gap
                    an = self.annee - 1
                if mo in pp['annees'][an]:
                    pm = pp['annees'][an][mo]['clients']
                    for code in pm:
                        if code not in stats_clients:
                            stats_clients[code] = {'1m': 0, '3m': [], '6m': [], '12m': []}
                        for idd in pm[code]:
                            if gap < 3 and idd not in stats_clients[code]['3m']:
                                stats_clients[code]['3m'].append(idd)
                            if gap < 6 and idd not in stats_clients[code]['6m']:
                                stats_clients[code]['6m'].append(idd)
                            if id not in stats_clients[code]['12m']:
                                stats_clients[code]['12m'].append(idd)

            lignes = []
            plate_name = ""
            for code in par_plate[id_plateforme]['clients'].keys():
                tbtr = par_plate[id_plateforme]['clients'][code]['transactions']
                base = trans_vals[tbtr[0]]
                if plate_name == "":
                    plate_name = base['platf-name']
                ligne = [self.annee, self.mois]
                for cle in range(2, len(self.cles)-6):
                    ligne.append(base[self.cles[cle]])
                stat_run = 0
                for indice in tbtr:
                    if str(trans_vals[indice]['transac-runcae']) == "1":
                        stat_run += 1
                stats = stats_clients[code]
                ligne += [len(tbtr), stat_run, stats['1m'], len(stats['3m']), len(stats['6m']), len(stats['12m'])]
                lignes.append(ligne)

            nom = prefixe + "_" + plate_name + ".csv"
            with dossier_destination.writer(nom) as fichier_writer:
                ligne = []
                for cle in self.cles:
                    ligne.append(pt[cle])
                fichier_writer.writerow(ligne)

                for ligne in lignes:
                    fichier_writer.writerow(ligne)