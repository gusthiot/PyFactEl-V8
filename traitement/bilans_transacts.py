from traitement import AnnexeDetails
from traitement import AnnexeSubsides
from traitement import BilanPlates
from traitement import BilanUsages
from traitement import BilanConsos
from traitement import UserLaboNew
from outils import Outils



class BilansTransacts(object):
    """
    Classe pour la création des csv des bilans des transactions
    """

    def __init__(self, edition):
        """
        initialisation des générateurs de bilans
        :param edition: paramètres d'édition
        """
        self.ann_dets = AnnexeDetails(edition)
        self.ann_subs = AnnexeSubsides(edition)
        self.bil_plat = BilanPlates(edition)
        self.bil_use = BilanUsages(edition)
        self.bil_conso = BilanConsos(edition)
        self.usr_lab = UserLaboNew(edition)

    def generer(self, trans_vals, grants, plafonds, comptes, clients, subsides, paramtexte, paramannexe, artsap,
                dossier_destination):
        """
        tri des transactions et génération des bilans
        :param trans_vals: valeurs des transactions générées
        :param grants: grants importés
        :param plafonds: plafonds importés
        :param comptes: comptes importés
        :param clients: clients importés
        :param subsides: subsides importés
        :param paramtexte: paramètres textuels
        :param paramannexe: paramètres d'annexe
        :param artsap: articles SAP importés
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
            item = transaction['item-id']
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

            par_client[code_client]['transactions'].append(key)

            if type_s != "" and subs > 0:
                pcc = par_client[code_client]['comptes']
                if id_compte not in pcc.keys():
                    pcc[id_compte] = {}
                pcd = pcc[id_compte]
                if id_article not in pcd.keys():
                    pcd[id_article] = [key]
                else:
                    pcd[id_article].append(key)

            if id_plateforme not in par_plate.keys():
                par_plate[id_plateforme] = {'clients': {}, 'items': {}, 'users': {}}

            ppc = par_plate[id_plateforme]['clients']
            if code_client not in ppc.keys():
                ppc[code_client] = {}
            ppd = ppc[code_client]
            if id_article not in ppd.keys():
                ppd[id_article] = [key]
            else:
                ppd[id_article].append(key)

            ppi = par_plate[id_plateforme]['items']
            if item not in ppi.keys():
                ppi[item] = [key]
            else:
                ppi[item].append(key)

            ppu = par_plate[id_plateforme]['users']
            if user_id not in ppu.keys():
                ppu[user_id] = {}
            if code_client not in ppu[user_id].keys():
                ppu[user_id][code_client] = {}
            day = date.day
            ppuc = ppu[user_id][code_client]
            if day not in ppuc.keys():
                ppuc[day] = key

        self.ann_dets.generer(trans_vals, paramtexte, paramannexe, par_client)
        self.ann_subs.generer(trans_vals, grants, plafonds, paramtexte, paramannexe, par_client, comptes, clients,
                              subsides, artsap)
        self.bil_plat.generer(trans_vals, paramtexte, dossier_destination, par_plate)
        self.bil_use.generer(trans_vals, paramtexte, dossier_destination, par_plate)
        self.bil_conso.generer(trans_vals, paramtexte, dossier_destination, par_plate)
        self.usr_lab.generer(trans_vals, paramtexte, dossier_destination, par_plate)
