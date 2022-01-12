from outils import Outils
from importes import DossierDestination
from datetime import datetime
import calendar


class AnnexeSubsides(object):
    """
    Classe pour la création du csv d'annexe subsides
    """

    cles = ['invoice-year', 'invoice-month', 'platf-name', 'client-code', 'client-name', 'proj-id', 'proj-name',
            'item-codeD', 'item-labelcode', 'subsid-code', 'subsid-name', 'subsid-start', 'subsid-end',
            'subsid-pourcent', 'subsid-maxproj', 'subsid-maxmois', 'subsid-alrdygrant', 'subsid-CHF', 'subsid-reste']

    def __init__(self, edition, paramtexte, paramannexe):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        :param paramtexte: paramètres textuels
        :param paramannexe: paramètres d'annexe
        """
        self.annee = edition.annee
        self.mois = edition.mois
        self.version = edition.version
        self.unique = edition.client_unique
        self.paramtexte = paramtexte
        self.paramannexe = paramannexe
        self.dossier = ""
        self.chemin = "./"
        self.prefixe = "Annexe-subsides_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + \
            str(edition.version)

    def generer(self, trans_vals, grants, plafonds, par_client, comptes, clients, subsides, artsap, plateformes):
        """
        génération des fichiers d'annexes subsides à partir des transactions
        :param trans_vals: valeurs des transactions générées
        :param grants: grants importés
        :param plafonds: plafonds importés
        :param par_client: tri des transactions par client, par compte, par code D
        :param comptes: comptes importés
        :param clients: clients importés
        :param subsides: subsides importés
        :param artsap: articles SAP importés
        :param plateformes: plateformes importées
        """
        pt = self.paramtexte.donnees

        for donnee in self.paramannexe.donnees:
            if donnee['nom'] == 'Annexe-détails':
                self.chemin = donnee['chemin']
                self.dossier = donnee['dossier']
        dossier_destination = DossierDestination(self.chemin)

        clients_comptes = {}
        for id_compte in comptes.donnees.keys():
            compte = comptes.donnees[id_compte]
            if self.version > 0 and self.unique != compte['code_client']:
                continue
            type_s = compte['type_subside']
            if type_s != "":
                if type_s in subsides.donnees.keys():
                    subside = subsides.donnees[type_s]
                    if subside['debut'] != 'NULL':
                        debut, info = Outils.est_une_date(subside['debut'], "la date de début")
                        if info != "":
                            Outils.affiche_message(info)
                    else:
                        debut = 'NULL'
                    if subside['fin'] != 'NULL':
                        fin, info = Outils.est_une_date(subside['fin'], "la date de fin")
                        if info != "":
                            Outils.affiche_message(info)
                    else:
                        fin = 'NULL'

                    premier, dernier = calendar.monthrange(self.annee, self.mois)
                    if debut == "NULL" or debut <= datetime(self.annee, self.mois, dernier):
                        if fin == "NULL" or fin >= datetime(self.annee, self.mois, 1):
                            code_client = compte['code_client']
                            if code_client not in clients_comptes:
                                clients_comptes[code_client] = []
                            clients_comptes[code_client].append(id_compte)

        for code in clients_comptes.keys():
            cc = clients_comptes[code]
            ii = 0
            lignes = []
            client = clients.donnees[code]
            nom = self.prefixe + "_" + code + "_" + client['abrev_labo'] + ".csv"
            for id_compte in cc:
                compte = comptes.donnees[id_compte]
                type_s = compte['type_subside']
                subside = subsides.donnees[type_s]
                for id_plateforme in plateformes.ids:
                    for id_article in artsap.ids:
                        plaf = type_s + id_plateforme + id_article
                        if plaf in plafonds.donnees.keys():
                            plafond = plafonds.donnees[plaf]
                            ligne = [self.annee, self.mois, id_plateforme, client['code'], client['abrev_labo'],
                                     compte['id_compte'], compte['intitule'], id_article,
                                     artsap.donnees[id_article]['intitule_long'], subside['type'], subside['intitule'],
                                     subside['debut'], subside['fin'], plafond['pourcentage'], plafond['max_compte'],
                                     plafond['max_mois']]
                            subs = 0
                            g_id = id_compte + id_plateforme + id_article
                            if g_id in grants.donnees.keys():
                                grant, info = Outils.est_un_nombre(grants.donnees[g_id]['montant'],
                                                                   "le montant de grant", min=0, arrondi=2)
                                if info != "":
                                    Outils.affiche_message(info)
                            else:
                                grant = 0
                            if code in par_client and id_compte in par_client[code]['comptes']:
                                par_code = par_client[code]['comptes'][id_compte]
                                if id_plateforme in par_code.keys():
                                    par_plate = par_code[id_plateforme]
                                    if id_article in par_plate.keys():
                                        tbtr = par_plate[id_article]
                                        for indice in tbtr:
                                            val, info = Outils.est_un_nombre(trans_vals[indice]['subsid-CHF'],
                                                                             "le subside CHF", arrondi=2)
                                            subs += val

                            reste = plafond['max_compte'] - grant - subs
                            ligne += [round(grant, 2), round(subs, 2), round(reste, 2)]
                            lignes.append(ligne)
                            ii += 1
            with dossier_destination.writer(nom) as fichier_writer:
                ligne = []
                for cle in self.cles:
                    ligne.append(pt[cle])
                fichier_writer.writerow(ligne)

                for ligne in lignes:
                    fichier_writer.writerow(ligne)
