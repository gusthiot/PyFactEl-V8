from outils import Outils


class UserLaboNew(object):
    """
    Classe pour la création du csv des utilisations des plateformes
    """

    cles = ['year', 'month', 'day', 'week-nbr', 'platf-code', 'platf-op', 'platf-name', 'client-code', 'client-name',
            'client-class', 'user-id', 'user-sciper', 'user-name', 'user-first']

    def __init__(self, edition, paramtexte):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        :param paramtexte: paramètres textuels
        """
        self.annee = edition.annee
        self.mois = edition.mois
        self.paramtexte = paramtexte

    def generer(self, trans_vals, dossier_destination, par_plate, userlabs):
        """
        génération du fichier des usages de labos à partir des transactions
        :param trans_vals: valeurs des transactions générées
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param par_plate: tri des transactions par plateforme, par utilisateur, par client, par jour
        :param userlabs: users labo importés
        """
        pt = self.paramtexte.donnees

        nom = "User-labo_" + str(self.annee) + "_" + Outils.mois_string(self.mois) + ".csv"

        lignes = []
        for donnee in userlabs.donnees:
            year, info = Outils.est_un_entier(donnee['year'], "l'année", min=2000, max=2099)
            if info != "":
                Outils.affiche_message(info)
            month, info = Outils.est_un_entier(donnee['month'], "le mois", min=1, max=12)
            if info != "":
                Outils.affiche_message(info)

            if self.annee - year > 1:
                Outils.affiche_message("Comment peut-on avoir des user-labo de plus d'1 année d'écart ?")
                continue
            if self.annee - year == 1:
                if self.mois - month > -1:
                    continue
            ligne = []
            for i in range(0, len(self.cles)):
                ligne.append(donnee[self.cles[i]])
            lignes.append(ligne)

        for id_plate in par_plate.keys():
            par_user = par_plate[id_plate]['users']
            for id_user in par_user.keys():
                par_client = par_user[id_user]
                for code in par_client.keys():
                    par_jour = par_client[code]['days']
                    for jour in par_jour.keys():
                        key = par_jour[jour]
                        trans = trans_vals[key]
                        date, info = Outils.est_une_date(trans['transac-date'], "la date de transaction")
                        if info != "":
                            Outils.affiche_message(info)
                        ligne = [self.annee, self.mois]
                        for cle in range(2, len(self.cles)):
                            if self.cles[cle] == 'day':
                                ligne.append(date.day)
                            elif self.cles[cle] == 'week-nbr':
                                ligne.append(date.isocalendar()[1])
                            else:
                                ligne.append(trans[self.cles[cle]])
                        lignes.append(ligne)

        with dossier_destination.writer(nom) as fichier_writer:
            ligne = []
            for cle in self.cles:
                ligne.append(pt[cle])
            fichier_writer.writerow(ligne)

            for ligne in lignes:
                fichier_writer.writerow(ligne)
