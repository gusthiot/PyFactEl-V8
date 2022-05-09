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

    def generer(self, trans_vals, dossier_destination, par_plate, par_plate_ul, clients, classes):
        """
        génération du fichier de stats des clients à partir des transactions
        :param trans_vals: valeurs des transactions générées
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param par_plate: tri des transactions par plateforme, par users, par client
        :param par_plate_ul: tri des users labo par plateforme, par date
        :param clients: clients importés
        :param classes: classes clients importées
        """

        pt = self.paramtexte.donnees
        prefixe = "Stat-client_" + str(self.annee) + "_" + Outils.mois_string(self.mois)

        for id_plateforme in par_plate_ul.keys():
            stats_clients = {}
            pp = par_plate_ul[id_plateforme]
            if self.mois in pp['annees'][self.annee]:
                pm = pp['annees'][self.annee][self.mois]['clients']
                for code in pm:
                    stats_clients[code] = {'1m': len(pm[code]), '3m': pm[code].copy(), '6m': pm[code].copy(),
                                           '12m': pm[code].copy()}
            for gap in range(1, 12):
                if gap < self.mois:
                    mo = self.mois - gap
                    an = self.annee
                else:
                    mo = 12 + self.mois - gap
                    an = self.annee - 1
                if an in pp['annees']:
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
                                if idd not in stats_clients[code]['12m']:
                                    stats_clients[code]['12m'].append(idd)

            lignes = []
            ll = [self.annee, self.mois]
            if id_plateforme in par_plate:
                par_client = par_plate[id_plateforme]['clients']
                for code, stats in stats_clients.items():
                    client = clients.donnees[code]
                    classe = classes.donnees[client['id_classe']]
                    lc = ll + [client['code'], client['code_sap'], client['abrev_labo'], client['id_classe'],
                               classe['code_n'], classe['intitule']]
                    if code in par_client.keys():
                        tbtr = par_plate[id_plateforme]['clients'][code]['transactions']
                        ligne = lc
                        stat_run = 0
                        for indice in tbtr:
                            if str(trans_vals[indice]['transac-runcae']) == "1":
                                stat_run += 1
                        ligne += [len(tbtr), stat_run, stats['1m'], len(stats['3m']), len(stats['6m']),
                                  len(stats['12m'])]
                        lignes.append(ligne)
                    else:
                        lignes.append(lc + [0, 0, stats['1m'], len(stats['3m']), len(stats['6m']), len(stats['12m'])])
            else:
                for code, stats in stats_clients.items():
                    client = clients.donnees[code]
                    classe = classes.donnees[client['id_classe']]
                    lc = ll + [client['code'], client['code_sap'], client['abrev_labo'], client['id_classe'],
                               classe['code_n'], classe['intitule']]
                    lignes.append(lc + [0, 0, stats['1m'], len(stats['3m']), len(stats['6m']), len(stats['12m'])])

            nom = prefixe + "_" + pp['nom'] + ".csv"
            with dossier_destination.writer(nom) as fichier_writer:
                ligne = []
                for cle in self.cles:
                    ligne.append(pt[cle])
                fichier_writer.writerow(ligne)

                for ligne in lignes:
                    fichier_writer.writerow(ligne)
