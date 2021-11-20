from traitement import (AnnexeDetails,
                        AnnexeSubsides,
                        BilanPlates,
                        BilanUsages,
                        BilanConsos,
                        UserLaboNew,
                        StatUser,
                        StatNbUser,
                        StatMachine,
                        StatClient)
from outils import Outils


class BilansTransacts(object):
    """
    Classe pour la création des csv des bilans des transactions
    """

    def __init__(self, edition, paramtexte, paramannexe):
        """
        initialisation des générateurs de bilans
        :param edition: paramètres d'édition
        :param paramtexte: paramètres textuels
        :param paramannexe: paramètres d'annexe
        """
        self.ann_dets = AnnexeDetails(edition, paramtexte, paramannexe)
        self.ann_subs = AnnexeSubsides(edition, paramtexte, paramannexe)
        self.bil_plat = BilanPlates(edition, paramtexte)
        self.bil_use = BilanUsages(edition, paramtexte)
        self.bil_conso = BilanConsos(edition, paramtexte)
        self.usr_lab = UserLaboNew(edition, paramtexte)
        self.stat_user = StatUser(edition, paramtexte)
        self.stat_nb_user = StatNbUser(edition, paramtexte)
        self.stat_cli = StatClient(edition, paramtexte)
        self.stat_mach = StatMachine(edition, paramtexte)

    def generer(self, trans_vals, grants, plafonds, comptes, clients, subsides, artsap, userlabs, dossier_destination):
        """
        tri des transactions et génération des bilans
        :param trans_vals: valeurs des transactions générées
        :param grants: grants importés
        :param plafonds: plafonds importés
        :param comptes: comptes importés
        :param clients: clients importés
        :param subsides: subsides importés
        :param artsap: articles SAP importés
        :param userlabs: users labo importés
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        """
        par_client = {}
        par_plate = {}
        for key in trans_vals.keys():
            transaction = trans_vals[key]
            code_client = transaction['client-code']
            id_compte = transaction['proj-id']
            id_plateforme = transaction['platf-code']
            id_article = transaction['item-idsap']
            id_projet = transaction['proj-id']
            item = transaction['item-id']
            id_machine = transaction['mach-id']
            user_id = transaction['user-id']
            date, info = Outils.est_une_date(transaction['transac-date'], "la date de transaction")
            if info != "":
                Outils.affiche_message(info)
            type_s = transaction['subsid-code']
            subs, info = Outils.est_un_nombre(transaction['subsid-maxproj'], "le subside projet", min=0, arrondi=2)
            if info != "":
                Outils.affiche_message(info)

            if code_client not in par_client.keys():
                par_client[code_client] = {'transactions': [], 'comptes': {}}

            par_client[code_client]['transactions'].append(key)  # => annexe details

            if type_s != "" and subs > 0:
                pcc = par_client[code_client]['comptes']
                if id_compte not in pcc.keys():
                    pcc[id_compte] = {}
                pccd = pcc[id_compte]
                if id_article not in pccd.keys():
                    pccd[id_article] = [key]  # => annexe subsides
                else:
                    pccd[id_article].append(key)

            if id_plateforme not in par_plate.keys():
                par_plate[id_plateforme] = {'clients': {}, 'items': {}, 'users': {}, 'machines': {}, 'projets': {}}

            ppc = par_plate[id_plateforme]['clients']
            if code_client not in ppc.keys():
                ppc[code_client] = {'articles': {}, 'transactions': []}
            ppc[code_client]['transactions'].append(key)
            ppcd = ppc[code_client]['articles']
            if id_article not in ppcd.keys():
                ppcd[id_article] = [key]
            else:
                ppcd[id_article].append(key)  # => bilan plates

            ppi = par_plate[id_plateforme]['items']
            if item not in ppi.keys():
                ppi[item] = [key]
            else:
                ppi[item].append(key)  # => bilan usage

            ppp = par_plate[id_plateforme]['projets']
            if id_projet not in ppp.keys():
                ppp[id_projet] = {}
            pppi = ppp[id_projet]
            if item not in pppi.keys():
                pppi[item] = [key]
            else:
                pppi[item].append(key)  # => bilan conso

            ppm = par_plate[id_plateforme]['machines']
            if id_machine not in ppm.keys():
                ppm[id_machine] = {}
            if item not in ppm[id_machine].keys():
                ppm[id_machine][item] = [key]
            else:
                ppm[id_machine][item].append(key)  # => stat machine

            ppu = par_plate[id_plateforme]['users']
            if user_id not in ppu.keys():
                ppu[user_id] = {}
            if code_client not in ppu[user_id].keys():
                ppu[user_id][code_client] = {'days': {}, 'transactions': []}
            ppuc = ppu[user_id][code_client]
            ppuc['transactions'].append(key)  # => stat user
            day = date.day
            if day not in ppuc['days'].keys():
                ppuc['days'][day] = key  # => user labo

        self.ann_dets.generer(trans_vals, par_client)
        self.ann_subs.generer(trans_vals, grants, plafonds, par_client, comptes, clients, subsides, artsap)
        self.bil_plat.generer(trans_vals, dossier_destination, par_plate)
        self.bil_use.generer(trans_vals, dossier_destination, par_plate)
        self.bil_conso.generer(trans_vals, dossier_destination, par_plate)
        self.stat_user.generer(trans_vals, dossier_destination, par_plate)
        self.stat_mach.generer(trans_vals, dossier_destination, par_plate)
        self.usr_lab.generer(trans_vals, dossier_destination, par_plate, userlabs)

        par_plate_ul = {}
        for jour in self.usr_lab.valeurs.keys():
            valeur = self.usr_lab.valeurs[jour]
            id_plateforme = valeur['platf-code']
            if id_plateforme not in par_plate_ul.keys():
                par_plate_ul[id_plateforme] = {'annees': {}, 'semaines': {}, 'nom': valeur['platf-name']}
            pp = par_plate_ul[id_plateforme]
            if pp['nom'] == "" and valeur['platf-name'] != "":
                pp['nom'] = valeur['platf-name']
            annee, info = Outils.est_un_entier(valeur['year'], "l'année", min=2000, max=2099)
            if info != "":
                Outils.affiche_message(info)
            mois, info = Outils.est_un_entier(valeur['month'], "le mois", min=1, max=12)
            if info != "":
                Outils.affiche_message(info)
            if annee not in pp['annees']:
                pp['annees'][annee] = {}
            if mois not in pp['annees'][annee]:
                pp['annees'][annee][mois] = {'users': [], 'jours': {}, 'clients': {}}
            pm = pp['annees'][annee][mois]
            jour = valeur['day']
            if jour not in pm['jours']:
                pm['jours'][jour] = []
            code = valeur['client-code']
            if code not in pm['clients']:
                pm['clients'][code] = []

            semaine = valeur['week-nbr']
            if semaine not in pp['semaines']:
                pp['semaines'][semaine] = []

            user = valeur['user-id']
            if id_plateforme != valeur['client-code']:
                if user not in pm['jours'][jour]:
                    pm['jours'][jour].append(user)
                if user not in pm['users']:
                    pm['users'].append(user)
                if user not in pp['semaines'][semaine]:
                    pp['semaines'][semaine].append(user)
            if user not in pm['clients'][code]:
                pm['clients'][code].append(user)

        self.stat_nb_user.generer(dossier_destination, par_plate_ul)
        self.stat_cli.generer(trans_vals, dossier_destination, par_plate, par_plate_ul)
