from outils import Outils
from .rabais import Rabais
import math


class Sommes(object):
    """
    Classe contenant les méthodes pour le calcul des sommes par compte, catégorie et client
    """

    cles_somme_compte = ['somme_j_mk', 'somme_j_dhi', 'somme_j_dhi_d', 'somme_j_mm', 'somme_j_mr',
                         'somme_j_mb', 'c1', 'c2']

    cles_somme_client = ['dht', 'somme_t_mm', 'somme_t_mr', 'somme_t_mb', 'mt', 'somme_t', 'nos', 'rm', 'rm_d', 'rr',
                         'r']

    def __init__(self, verification, generaux, artsap):
        """
        initialisation des sommes, et vérification si données utilisées correctes
        :param verification: pour vérifier si les dates et les cohérences sont correctes
        :param generaux: paramètres généraux
        :param artsap: articles SAP importés
        """

        self.verification = verification
        self.sommes_comptes = {}
        self.sco = 0
        self.sommes_clients = {}
        self.calculees = 0
        self.categories = artsap.ids_d3
        self.min_fact_rese = generaux.min_fact_rese

    def calculer_toutes(self, livraisons, acces, clients, noshows):
        """
        calculer toutes les sommes, par compte et par client
        :param livraisons: livraisons importées et vérifiées
        :param acces: accès machines importés et vérifiés
        :param clients: clients importés et vérifiés
        :param noshows: no show importés et vérifiés
        """
        self.somme_par_compte(livraisons, acces, clients)
        self.somme_par_client(clients, acces, noshows)

    def nouveau_somme(self, cles):
        """
        créé un nouveau dictionnaire avec les clés entrées
        :param cles: clés pour le dictionnaire
        :return: dictionnaire indexé par les clés données, avec valeurs à zéro
        """
        somme = {}
        for cle in cles:
            somme[cle] = 0
        somme['sommes_cat_m'] = {}
        somme['sommes_cat_r'] = {}
        somme['tot_cat'] = {}
        for categorie in self.categories:
            somme['sommes_cat_m'][categorie] = 0
            somme['sommes_cat_r'][categorie] = 0
            somme['tot_cat'][categorie] = 0
        return somme

    def somme_par_compte(self, livraisons, acces, clients):
        """
        calcule les sommes par comptes sous forme de dictionnaire : client->compte->clés_sommes
        :param livraisons: livraisons importées et vérifiées
        :param acces: accès machines importés et vérifiés
        :param clients: clients importés et vérifiés
        """

        if self.verification.a_verifier != 0:
            info = "Sommes :  vous devez faire les vérifications avant de calculer les sommes"
            Outils.affiche_message(info)
            return

        spco = {}
        for code_client in acces.sommes:
            if code_client not in spco:
                spco[code_client] = {}
            spco_cl = spco[code_client]
            for id_compte in acces.sommes[code_client]['comptes']:
                if id_compte not in spco_cl:
                    spco_cl[id_compte] = self.nouveau_somme(Sommes.cles_somme_compte)
                somme = spco_cl[id_compte]
                ac_som = acces.sommes[code_client]['comptes']
                if id_compte in ac_som:
                    for id_machine, som in ac_som[id_compte].items():
                        somme['somme_j_dhi'] += som['dhi']
                ac_cat_som = acces.sommes[code_client]['categories']
                if id_compte in ac_cat_som:
                    for t, type_som in ac_cat_som[id_compte].items():
                        for id_categorie, cat_som in type_som.items():
                            somme['somme_j_mk'] += cat_som['mk']

        for code_client in livraisons.sommes:
            if code_client not in spco:
                spco[code_client] = {}
            spco_cl = spco[code_client]
            for id_compte in livraisons.sommes[code_client]:
                if id_compte not in spco_cl:
                    spco_cl[id_compte] = self.nouveau_somme(Sommes.cles_somme_compte)
                somme = spco_cl[id_compte]

                for categorie in livraisons.sommes[code_client][id_compte]:
                    scc = livraisons.sommes[code_client][id_compte][categorie]
                    for prestation in scc:
                        somme['sommes_cat_m'][categorie] += scc[prestation]['montant']
                        somme['sommes_cat_r'][categorie] += scc[prestation]['rabais']

        for code_client in spco:
            for id_compte in spco[code_client]:
                somme = spco[code_client][id_compte]

                dhij = round(2 * somme['somme_j_dhi'], 1) / 2
                somme['somme_j_dhi_d'] = dhij - somme['somme_j_dhi']
                somme['somme_j_dhi'] = dhij

                client = clients.donnees[code_client]
                somme['somme_j_mm'] += somme['somme_j_mk']
                somme['somme_j_mr'] = client['rh'] * somme['somme_j_dhi']
                somme['somme_j_mb'] = client['bh'] * somme['somme_j_dhi']
                somme['mj'] = somme['somme_j_mm'] - somme['somme_j_mr']

                for categorie in self.categories:
                    cat_r = round(2 * somme['sommes_cat_r'][categorie], 1) / 2
                    somme['sommes_cat_r'][categorie] = cat_r

                    somme['tot_cat'][categorie] = somme['sommes_cat_m'][categorie] - somme['sommes_cat_r'][categorie]

                somme['c1'] = somme['somme_j_mm']
                somme['c2'] = somme['mj']
                for categorie in self.categories:
                    somme['c1'] += somme['sommes_cat_m'][categorie]
                    somme['c2'] += somme['tot_cat'][categorie]

        # print("")
        # print("spco")
        # for code in spco:
        #     if code != "220208":
        #         continue
        #     print(code)
        #     spco_cl = spco[code]
        #     for id in spco_cl:
        #         somme = spco_cl[id]

        self.sco = 1
        self.sommes_comptes = spco

    def somme_par_client(self, clients, acces, noshows):
        """
        calcule les sommes par clients sous forme de dictionnaire : client->clés_sommes
        :param clients: clients importés et vérifiés
        :param noshows: no show importés et vérifiés
        :param acces: accès machines importés et vérifiés
        """

        if self.verification.a_verifier != 0:
            info = "Sommes :  vous devez faire les vérifications avant de calculer les sommes"
            Outils.affiche_message(info)
            return

        if self.sco != 0:
            spcl = {}
            for code_client, spco_cl in self.sommes_comptes.items():
                spcl[code_client] = self.nouveau_somme(Sommes.cles_somme_client)
                somme = spcl[code_client]
                somme['nos'] = {}
                somme['rm'] = 0
                somme['rr'] = 0
                somme['r'] = 0
                for id_compte, som_co in spco_cl.items():
                    somme['dht'] += som_co['somme_j_dhi']
                    somme['somme_t_mm'] += som_co['somme_j_mm']
                    somme['somme_t_mr'] += som_co['somme_j_mr']
                    somme['mt'] += som_co['mj']

                    for categorie in self.categories:
                        somme['sommes_cat_m'][categorie] += som_co['sommes_cat_m'][categorie]
                        somme['sommes_cat_r'][categorie] += som_co['sommes_cat_r'][categorie]
                        somme['tot_cat'][categorie] += som_co['tot_cat'][categorie]

            # no show
            for code_client in noshows.sommes:
                if code_client not in spcl:
                    spcl[code_client] = self.nouveau_somme(Sommes.cles_somme_client)
                    spcl[code_client]['nos'] = {}
                somme = spcl[code_client]
                somme_nos = noshows.sommes[code_client]

                for id_machine in somme_nos.keys():
                    np_hp = somme_nos[id_machine]['np_hp']
                    np_hc = somme_nos[id_machine]['np_hc']
                    pu_hp = somme_nos[id_machine]['pu_hp']
                    pu_hc = somme_nos[id_machine]['pu_hc']

                    if np_hp > 0 or np_hc > 0:
                        somme['nos'][id_machine] = {'tot_hp': 0, 'tot_hc': 0, 'users': {}, 'mont_hp': 0,
                                                    'mont_hc': 0}

                        users = somme['nos'][id_machine]['users']
                        for id_user, s_u in somme_nos[id_machine]['users'].items():
                            if id_user not in users:
                                users[id_user] = {'np_hp': s_u['np_hp'],
                                                  'np_hc': s_u['np_hc']}

                        for id_user, s_u in users.items():
                            somme['nos'][id_machine]['tot_hp'] += s_u['np_hp']
                            somme['nos'][id_machine]['tot_hc'] += s_u['np_hc']
                        somme['nos'][id_machine]['tot_hp'] = max(0, somme['nos'][id_machine]['tot_hp'])
                        somme['nos'][id_machine]['tot_hc'] = max(0, somme['nos'][id_machine]['tot_hc'])

                        somme['nos'][id_machine]['mont_hp'] = round(somme['nos'][id_machine]['tot_hp'] * pu_hp, 2)
                        somme['nos'][id_machine]['mont_hc'] = round(somme['nos'][id_machine]['tot_hc'] * pu_hc, 2)
                        somme['rm'] += somme['nos'][id_machine]['mont_hp'] + somme['nos'][id_machine]['mont_hc']

                rm = math.floor(somme['rm'])
                somme['rm_d'] = rm - somme['rm']
                somme['rm'] = rm
                somme['rr'] = Rabais.rabais_reservation_petit_montant(somme['rm'], self.min_fact_rese)
                somme['r'] = somme['rm'] - somme['rr']

            for code_client, somme in spcl.items():
                client = clients.donnees[code_client]

                if code_client in acces.sommes:
                    somme_acces = acces.sommes[code_client]
                    for id_machine, scm in somme_acces['machines'].items():
                        somme['somme_t_mb'] += scm['dhm']
                    somme['somme_t_mb'] *= client['bh']

                somme['somme_t'] = somme['r'] + somme['mt']
                for cat, tt in somme['tot_cat'].items():
                    somme['somme_t'] += tt

            # print("")
            # print("spcl")
            # for code in spcl:
            #     if code != "220208":
            #         continue
            #     somme = spcl[code]

            self.calculees = 1
            self.sommes_clients = spcl

        else:
            info = "Vous devez d'abord faire la somme par catégorie, avant la somme par client"
            Outils.affiche_message(info)
