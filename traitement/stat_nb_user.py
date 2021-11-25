from outils import Outils
from calendar import monthrange
from datetime import datetime


class StatNbUser(object):
    """
    Classe pour la création du csv des stats nombre user
    """

    cles = ['year', 'month', 'day', 'week-nbr', 'stat-nbuser-d', 'stat-nbuser-w', 'stat-nbuser-m', 'stat-nbuser-3m',
            'stat-nbuser-6m', 'stat-nbuser-12m']

    def __init__(self, edition, paramtexte):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        :param paramtexte: paramètres textuels
        """
        self.annee = edition.annee
        self.mois = edition.mois
        self.paramtexte = paramtexte

    def generer(self, dossier_destination, par_plate_ul):
        """
        génération du fichier de stats de nombre de users à partir des users labo
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param par_plate_ul: tri des users labo par plateforme, par date
        """

        pt = self.paramtexte.donnees

        prefixe = "Stat-nbre-user_" + str(self.annee) + "_" + Outils.mois_string(self.mois)

        for id_plateforme in par_plate_ul:
            lignes = []
            pp = par_plate_ul[id_plateforme]
            jour_de_semaine, nb_de_jours = monthrange(self.annee, self.mois)
            for jour in range(1, nb_de_jours+1):
                nb_user_d = 0
                nb_user_m = ""
                nb_user_3m = ""
                nb_user_6m = ""
                nb_user_12m = ""
                pmu = []
                if self.mois in pp['annees'][self.annee]:
                    pm = pp['annees'][self.annee][self.mois]
                    pmu = pm['users']
                    if jour in pm['jours']:
                        nb_user_d = len(pm['jours'][jour])
                if jour == nb_de_jours:
                    nb_user_m = len(pmu)
                    user_3m = pmu.copy()
                    user_6m = pmu.copy()
                    user_12m = pmu.copy()
                    for gap in range(1, 12):
                        if gap < self.mois:
                            mo = self.mois - gap
                            an = self.annee
                        else:
                            mo = 12 + self.mois - gap
                            an = self.annee - 1
                        if mo in pp['annees'][an]:
                            ids = pp['annees'][an][mo]['users']
                            for idd in ids:
                                if gap < 3 and idd not in user_3m:
                                    user_3m.append(idd)
                                if gap < 6 and idd not in user_6m:
                                    user_6m.append(idd)
                                if idd not in user_12m:
                                    user_12m.append(idd)

                    nb_user_3m = len(user_3m)
                    nb_user_6m = len(user_6m)
                    nb_user_12m = len(user_12m)
                date = datetime(self.annee, self.mois, jour)
                semaine = date.isocalendar()[1]
                nb_user_w = ""
                if date.weekday() == 6 and semaine in pp['semaines']:
                    nb_user_w = len(pp['semaines'][semaine])
                ligne = [self.annee, self.mois, jour, semaine, nb_user_d, nb_user_w, nb_user_m, nb_user_3m, nb_user_6m,
                         nb_user_12m]
                lignes.append(ligne)

            nom = prefixe + "_" + pp['nom'] + ".csv"
            with dossier_destination.writer(nom) as fichier_writer:
                ligne = []
                for cle in self.cles:
                    ligne.append(pt[cle])
                fichier_writer.writerow(ligne)

                for ligne in lignes:
                    fichier_writer.writerow(ligne)
