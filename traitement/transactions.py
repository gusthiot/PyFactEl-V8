from outils import Outils
from traitement import Recap, Resumes


class Transactions(Recap):
    """
    Classe pour la création des transactions
    """

    cles = ['invoice-year', 'invoice-month', 'invoice-ref', 'client-code', 'client-sap', 'client-name',
            'client-idclass', 'client-class', 'client-labelclass', 'oper-id', 'oper-name', 'oper-note', 'staff-note',
            'mach-id', 'mach-name', 'mach-extra', 'user-id', 'user-sciper', 'user-name', 'user-first', 'proj-id',
            'proj-nbr', 'proj-name', 'proj-expl', 'item-id', 'item-type', 'item-nbr', 'item-name', 'item-unit',
            'item-idsap', 'item-codeD', 'item-labelcode', 'item-sap', 'item-extra', 'platf-code', 'platf-op',
            'platf-sap', 'platf-name', 'platf-cf', 'platf-fund', 'transac-date', 'transac-quantity', 'transac-usage',
            'transac-runtime', 'transac-runcae', 'valuation-price', 'valuation-brut', 'discount-type', 'discount-CHF',
            'valuation-net', 'subsid-code', 'subsid-name', 'subsid-start', 'subsid-end', 'subsid-ok', 'subsid-pourcent',
            'subsid-maxproj', 'subsid-maxmois', 'subsid-reste', 'subsid-CHF', 'deduct-CHF', 'subsid-deduct',
            'total-fact', 'discount-bonus', 'subsid-bonus']
    
    def __init__(self, edition):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        """
        super().__init__(edition)
        self.version = edition.version
        self.nom = "Transaction_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + \
            str(edition.version)
        if edition.version > 0:
            self.nom += "_" + str(edition.client_unique)
        self.nom += ".csv"
        self.comptabilises = {}

    def generer(self, acces, noshows, livraisons, prestations, machines, categprix, comptes, clients, users,
                plateformes, classes, articles, tarifs, subsides, plafonds, grants, groupes, cles, paramtexte):
        """
        génération du fichier des transactions
        :param acces: accès importés
        :param noshows: no show importés
        :param livraisons: livraisons importées
        :param prestations: prestations importées
        :param machines: machines importées
        :param categprix: catégories de prix importées
        :param comptes: comptes importés
        :param clients: clients importés
        :param users: users importés
        :param plateformes: plateformes importées
        :param classes: classes clients importées
        :param articles: articles générés
        :param tarifs: tarifs générés
        :param subsides: subsides importés
        :param plafonds: plafonds importés
        :param grants: grants importés
        :param groupes: groupes importés
        :param cles: clés subsides importées
        :param paramtexte: paramètres textuels
        """

        pt = paramtexte.donnees
        transacts = {}

        for entree in acces.donnees:
            compte = comptes.donnees[entree['id_compte']]
            client = clients.donnees[compte['code_client']]
            id_classe = client['id_classe']
            classe = classes.donnees[id_classe]
            id_machine = entree['id_machine']
            machine = machines.donnees[id_machine]
            groupe = groupes.donnees[machine['id_groupe']]
            ref_client = self.ref_client(classe, client)
            operateur = users.donnees[entree['id_op']]
            ope = [entree['id_op'], operateur['prenom'] + " " + operateur['nom'], entree['remarque_op'],
                   entree['remarque_staff'], id_machine, machine['nom'], ""]
            util_proj = self.util_proj(entree['id_user'], users, compte)
            counted = False

            # K3 CAE-run #
            if entree['duree_machine_hp'] > 0 or entree['duree_machine_hc'] > 0:
                article = articles.valeurs[groupe['id_cat_plat']]
                tarif = tarifs.valeurs[id_classe + groupe['id_cat_plat']]
                art = self.art_plate(article, plateformes, clients)
                if article['platf-code'] == compte['code_client']:
                    usage = 0
                    if compte['exploitation'] == "TRUE":
                        runcae = ""
                    else:
                        runcae = 1
                        counted = True
                else:
                    usage = 1
                    runcae = 1
                    counted = True
                trans = [entree['date_login'], 1, usage, "", runcae]
                val = [tarif['valuation-price'], tarif['valuation-price'], "", 0, tarif['valuation-price']]
                self.put_in_transacts(transacts, ref_client, ope, util_proj, art, trans, val)

            # K7 CAE-runf #
            if entree['duree_machine_hp'] > 0 or entree['duree_machine_hc'] > 0:
                article = articles.valeurs[groupe['id_cat_fixe']]
                tarif = tarifs.valeurs[id_classe + groupe['id_cat_fixe']]
                art = self.art_plate(article, plateformes, clients)
                if article['platf-code'] == compte['code_client'] and compte['exploitation'] == "TRUE":
                    usage = 0
                    runcae = ""
                else:
                    usage = 1
                    if counted:
                        runcae = ""
                    else:
                        runcae = 1
                        counted = True
                trans = [entree['date_login'], 1, usage, "", runcae]
                val = [tarif['valuation-price'], tarif['valuation-price'], "", 0, tarif['valuation-price']]
                self.put_in_transacts(transacts, ref_client, ope, util_proj, art, trans, val)

            # K1 CAE-HP #
            duree_hp = round(entree['duree_machine_hp']/60, 4)
            if duree_hp > 0:
                article = articles.valeurs[groupe['id_cat_mach']]
                art = self.art_plate(article, plateformes, clients)
                if article['platf-code'] == compte['code_client'] and compte['exploitation'] == "TRUE":
                    usage = 0
                    runtime = ""
                    runcae = ""
                else:
                    usage = duree_hp
                    runtime = entree['duree_run']
                    if counted:
                        runcae = ""
                    else:
                        runcae = 1
                        counted = True
                trans = [entree['date_login'], duree_hp, usage, runtime, runcae]
                tarif = tarifs.valeurs[id_classe + groupe['id_cat_mach']]
                prix = round(duree_hp * tarif['valuation-price'], 2)
                val = [tarif['valuation-price'], prix, "", 0, prix]
                self.put_in_transacts(transacts, ref_client, ope, util_proj, art, trans, val)

            # K1 CAE-HC #
            duree_hc = round(entree['duree_machine_hc']/60, 4)
            if duree_hc > 0:
                article = articles.valeurs[groupe['id_cat_mach']]
                art = self.art_plate(article, plateformes, clients)
                if article['platf-code'] == compte['code_client'] and compte['exploitation'] == "TRUE":
                    usage = 0
                    runtime = ""
                    runcae = ""
                else:
                    usage = duree_hc
                    if duree_hp > 0:
                        runtime = ""
                    else:
                        runtime = entree['duree_run']
                    if counted:
                        runcae = ""
                    else:
                        runcae = 1
                        counted = True
                trans = [entree['date_login'], duree_hc, usage, runtime, runcae]
                tarif = tarifs.valeurs[id_classe + groupe['id_cat_mach']]
                prix = round(duree_hc * tarif['valuation-price'], 2)
                reduc = round(tarif['valuation-price'] * machine['tx_rabais_hc']/100 * duree_hc, 2)
                val = [tarif['valuation-price'], prix, pt['discount-HC'] + " -" + str(machine['tx_rabais_hc']) + "%",
                       reduc, prix-reduc]
                self.put_in_transacts(transacts, ref_client, ope, util_proj, art, trans, val)

            # K2 CAE-MO #
            duree_op = round(entree['duree_operateur']/60, 4)
            if duree_op > 0:
                article = articles.valeurs[groupe['id_cat_mo']]
                art = self.art_plate(article, plateformes, clients)
                if article['platf-code'] == compte['code_client']:
                    usage = 0
                    if compte['exploitation'] == "TRUE":
                        runcae = ""
                    else:
                        if counted:
                            runcae = ""
                        else:
                            runcae = 1
                            counted = True
                else:
                    usage = duree_op
                    if counted:
                        runcae = ""
                    else:
                        runcae = 1
                        counted = True
                trans = [entree['date_login'], duree_op, usage, "", runcae]
                tarif = tarifs.valeurs[id_classe + groupe['id_cat_mo']]
                prix = round(duree_op * tarif['valuation-price'], 2)
                val = [tarif['valuation-price'], prix, "", 0, prix]
                self.put_in_transacts(transacts, ref_client, ope, util_proj, art, trans, val)

            # K4 CAE-Extra #
            prix_extra = categprix.donnees[id_classe + groupe['id_cat_cher']]['prix_unit']
            if prix_extra > 0:
                article = articles.valeurs[groupe['id_cat_cher']]
                duree = duree_hp + duree_hc
                if article['platf-code'] == compte['code_client'] and compte['exploitation'] == "TRUE":
                    usage = 0
                    runcae = ""
                else:
                    usage = duree
                    if counted:
                        runcae = ""
                    else:
                        runcae = 1
                trans = [entree['date_login'], duree, usage, "", runcae]
                art = self.art_plate(article, plateformes, clients)
                tarif = tarifs.valeurs[id_classe + groupe['id_cat_cher']]
                prix = round(duree * tarif['valuation-price'], 2)
                val = [tarif['valuation-price'], prix, "", 0, prix]
                self.put_in_transacts(transacts, ref_client, ope, util_proj, art, trans, val)

        for entree in noshows.donnees:
            compte = comptes.donnees[entree['id_compte']]
            client = clients.donnees[compte['code_client']]
            id_classe = client['id_classe']
            classe = classes.donnees[id_classe]
            ref_client = self.ref_client(classe, client)
            id_machine = entree['id_machine']
            machine = machines.donnees[id_machine]
            groupe = groupes.donnees[machine['id_groupe']]
            if entree['type'] == 'HP':
                # K5 NoShow-HP #
                article = articles.valeurs[groupe['id_cat_hp']]
                tarif = tarifs.valeurs[id_classe + groupe['id_cat_hp']]
            else:
                # K6 NoShow-HC #
                article = articles.valeurs[groupe['id_cat_hc']]
                tarif = tarifs.valeurs[id_classe + groupe['id_cat_hc']]
            ope = ["", "", "", "", id_machine, machine['nom'], ""]
            art = self.art_plate(article, plateformes, clients)
            util_proj = self.util_proj(entree['id_user'], users, compte)
            trans = [entree['date_debut'], entree['penalite'], 0, "", ""]
            prix = round(entree['penalite'] * tarif['valuation-price'], 2)
            val = [tarif['valuation-price'], prix, "", 0, prix]
            self.put_in_transacts(transacts, ref_client, ope, util_proj, art, trans, val)

        for entree in livraisons.donnees:
            compte = comptes.donnees[entree['id_compte']]
            client = clients.donnees[compte['code_client']]
            id_classe = client['id_classe']
            classe = classes.donnees[id_classe]
            ref_client = self.ref_client(classe, client)
            id_prestation = entree['id_prestation']
            prestation = prestations.donnees[id_prestation]
            operateur = users.donnees[entree['id_operateur']]
            id_machine = prestation['id_machine']
            article = articles.valeurs[id_prestation]
            art = self.art_plate(article, plateformes, clients)
            if id_machine == "0":
                # LVR-mag #
                idm = ""
                nm = ""
                extra = ""
            else:
                # LVR-mach #
                idm = id_machine
                machine = machines.donnees[id_machine]
                groupe = groupes.donnees[machine['id_groupe']]
                nm = machine['nom']
                extra = groupe['id_cat_mach']
            ope = [entree['id_operateur'], operateur['prenom'] + " " + operateur['nom'],
                   pt['oper-PO'] + " " + str(entree['date_commande']), entree['remarque'], idm, nm, extra]
            util_proj = self.util_proj(entree['id_user'], users, compte)
            trans = [entree['date_livraison'], entree['quantite'], 0, "", ""]
            tarif = tarifs.valeurs[id_classe + id_prestation]
            if entree['rabais'] > 0:
                discount = pt['discount-LVR']
            else:
                discount = ""
            prix = round(entree['quantite'] * tarif['valuation-price'], 2)
            val = [tarif['valuation-price'], prix, discount, entree['rabais'], prix-entree['rabais']]
            self.put_in_transacts(transacts, ref_client, ope, util_proj, art, trans, val)

        i = 0
        for tr in sorted(transacts.keys()):
            tarray = transacts[tr]
            for transact in tarray:
                id_compte = transact['up'][4]
                compte = comptes.donnees[id_compte]
                article = articles.valeurs[transact['art'][0]]
                id_classe = transact['rc'][4]
                montant = transact['val'][4]
                id_mach = transact['ope'][4]
                date = transact['trans'][0]
                subs = self.subsides(subsides, cles, plafonds, grants, compte, id_classe, article, date, montant,
                                     id_mach)
                if classes.donnees[id_classe]['subsides'] == "BONUS":
                    ded_bon = transact['val'][3]
                    ded_rab = 0
                    sub_bon = subs[8]
                    sub_rab = 0
                else:
                    ded_bon = 0
                    ded_rab = transact['val'][3]
                    sub_bon = 0
                    sub_rab = subs[8]
                if article['platf-code'] == compte['code_client']:
                    tot = 0
                else:
                    tot = transact['val'][1] - ded_rab - sub_rab
                mont = [ded_rab, sub_rab, tot, ded_bon, sub_bon]
                donnee = transact['rc'] + transact['ope'] + transact['up'] + transact['art'] + transact['trans'] + \
                    transact['val'] + subs + mont
                self.ajouter_valeur(donnee, i)
                i = i + 1

    def ref_client(self, classe, client):
        """
        ajout de la référence et des valeurs issues du client
        :param classe: classe de la transaction
        :param client: client de la transaction
        :return tableau contenant la référence et les valeurs du client
        """
        code_ref = classe['ref_fact']
        reference = code_ref + str(self.annee)[2:] + Outils.mois_string(self.mois) + "." + client['code']
        if self.version > 0:
            reference += "-" + str(self.version)
        return [reference, client['code'], client['code_sap'], client['abrev_labo'], client['id_classe'],
                classe['code_n'], classe['intitule']]

    @staticmethod
    def util_proj(id_user, users, compte):
        """
        ajout des valeurs issues de l'utilisateur et du projet (compte)
        :param id_user: id de l'utilisateur de la transaction
        :param users: users importés
        :param compte: compte de la transaction
        :return tableau contenant les valeurs de l'utilisateur et du projet
        """
        user = users.donnees[id_user]
        return [user['id_user'], user['sciper'], user['nom'], user['prenom'], compte['id_compte'], compte['numero'],
                compte['intitule'], compte['exploitation']]

    @staticmethod
    def art_plate(article, plateformes, clients):
        """
        ajout des valeurs issues de l'article et de la plateforme
        :param article: article de la transaction
        :param plateformes: plateformes importées
        :param clients: clients importés
        :return tableau contenant les valeurs de l'article et de la plateforme
        """
        plateforme = plateformes.donnees[article['platf-code']]
        client = clients.donnees[plateforme['id_plateforme']]
        return [article['item-id'], article['item-type'], article['item-nbr'], article['item-name'],
                article['item-unit'], article['item-idsap'], article['item-codeD'], article['item-labelcode'],
                article['item-sap'], article['item-extra'], article['platf-code'], plateforme['code_p'],
                client['code_sap'], plateforme['intitule'], plateforme['centre'], plateforme['fonds']]

    def subsides(self, subsides, cles, plafonds, grants, compte, id_classe, article, date, montant, id_machine):
        """
        ajout des valeurs issues des subsides
        :param subsides: subsides importés
        :param cles: clés subsides importées
        :param plafonds: plafonds importés
        :param grants: grants importés
        :param compte: compte de la transaction
        :param id_classe: id classe de la transaction
        :param article: article de la transaction
        :param date: date dela transaction
        :param montant: montant de la transaction
        :param id_machine: id_machine de la transaction
        :return tableau contenant les valeurs de subsides
        """
        type_s = compte['type_subside']
        result = ["", "", "", "", "", 0, 0, 0, 0, 0]
        if type_s != "":
            if type_s in subsides.donnees.keys():
                subside = subsides.donnees[type_s]
                result[0] = subside['type']
                result[1] = subside['intitule']
                result[2] = subside['debut']
                result[3] = subside['fin']
                result[4] = "NO"
                plaf = type_s + article['item-codeD']
                if plaf in plafonds.donnees.keys():
                    plafond = plafonds.donnees[plaf]
                    result[5] = plafond['pourcentage']
                    result[6] = plafond['max_compte']
                    result[7] = plafond['max_mois']
                    if subside['debut'] == "NULL" or subside['debut'] <= date:
                        if subside['fin'] == "NULL" or subside['fin'] >= date:
                            if type_s in cles.donnees.keys():
                                dict_s = cles.donnees[type_s]
                                if self.check_plateforme(dict_s, article['platf-code'], id_classe,
                                                         compte['code_client'], id_machine):
                                    result[4] = "YES"
                                    cg_id = compte['id_compte'] + article['item-codeD']
                                    if cg_id in grants.donnees.keys():
                                        grant = grants.donnees[cg_id]['montant']
                                    else:
                                        grant = 0
                                    if cg_id in self.comptabilises.keys():
                                        comptabilise = self.comptabilises[cg_id]['montant']
                                    else:
                                        comptabilise = 0
                                    res_compte = plafond['max_compte'] - (grant + comptabilise)
                                    res_mois = plafond['max_mois'] - comptabilise
                                    res = max(min(res_compte, res_mois), 0)
                                    max_mo = montant * plafond['pourcentage'] / 100
                                    mo = min(max_mo, res)
                                    if cg_id not in self.comptabilises.keys():
                                        self.comptabilises[cg_id] = {'id_compte': compte['id_compte'],
                                                                     'code_d': article['item-codeD'],
                                                                     'montant': mo}
                                    else:
                                        self.comptabilises[cg_id]['montant'] = self.comptabilises[cg_id]['montant'] + mo
                                    result[8] = res
                                    result[9] = mo
        return result

    @staticmethod
    def check_plateforme(dict_s, plateforme, id_classe, code_client, id_machine):
        """
        vérifie si les clés subsides contiennent la plateforme, ou 0
        :param dict_s: dict pour le type
        :param plateforme: plateforme à vérifier
        :param id_classe: id_classe à vérifier
        :param code_client: code client à vérifier
        :param id_machine: machine à vérifier

        """
        if "0" in dict_s:
            if Transactions.check_id_classe(dict_s, "0", id_classe, code_client, id_machine):
                return True
        if plateforme in dict_s:
            if Transactions.check_id_classe(dict_s, plateforme, id_classe, code_client, id_machine):
                return True
        return False

    @staticmethod
    def check_id_classe(dict_s, plateforme, id_classe, code_client, id_machine):
        """
        vérifie si les clés subsides contiennent le code N, ou 0
        :param dict_s: dict pour le type
        :param plateforme: plateforme sélectionnée ou 0
        :param id_classe: id_classe à vérifier
        :param code_client: code client à vérifier
        :param id_machine: machine à vérifier

        """
        dict_p = dict_s[plateforme]
        if "0" in dict_p:
            if Transactions.check_client(dict_p, "0", code_client, id_machine):
                return True
        if id_classe in dict_p:
            if Transactions.check_client(dict_p, id_classe, code_client, id_machine):
                return True
        return False

    @staticmethod
    def check_client(dict_p, id_classe, code_client, id_machine):
        """
        vérifie si les clés subsides contiennent le code client, ou 0
        :param dict_p: dict pour la plateforme
        :param id_classe: id classe sélectionné ou 0
        :param code_client: code client à vérifier
        :param id_machine: machine à vérifier
        """
        dict_n = dict_p[id_classe]
        if "0" in dict_n:
            if Transactions.check_machine(dict_n, "0", id_machine):
                return True
        if code_client in dict_n:
            if Transactions.check_machine(dict_n, code_client, id_machine):
                return True
        return False

    @staticmethod
    def check_machine(dict_n, client, id_machine):
        """
        vérifie si les clés subsides contiennent l'id machine, ou 0
        :param dict_n: dict pour le code N
        :param client: client sélectionné ou 0
        :param id_machine: machine à vérifier
        """
        dict_c = dict_n[client]
        if "0" in dict_c:
            return True
        if id_machine in dict_c:
            return True
        return False

    @staticmethod
    def put_in_transacts(transacts, ref_client, ope, util_proj, art, trans, val):
        """
        rajoute une ligne de transaction (avant tri chronologique et traitement des subsides)
        :param transacts: tableau des transactions
        :param ref_client: référence et valeurs issues du client
        :param ope: valeurs issues de l'opérateur
        :param util_proj: valeurs issues de l'utilisateur et du projet
        :param art: valeurs issues de l'article et de la plateforme
        :param trans: valeurs de transaction
        :param val: valeurs d'évaluation
        """
        if trans[0] not in transacts.keys():
            transacts[trans[0]] = []
        transacts[trans[0]].append({'rc': ref_client, 'ope': ope, 'up': util_proj, 'art': art, 'trans': trans,
                                    'val': val})

    @staticmethod
    def ouvrir_csv(dossier_source, fichier):
        """
        ouverture d'un csv comme string
        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param fichier: nom du fichier csv
        :return: donnees du csv modifiées en tant que string
        """
        donnees_csv = []
        try:
            fichier_reader = dossier_source.reader(fichier)
            for ligne in fichier_reader:
                if ligne == -1:
                    continue
                donnees_csv.append(ligne)
        except IOError as e:
            Outils.fatal(e, "impossible d'ouvrir le fichier : " + fichier)
        return donnees_csv

    def recuperer_valeurs_de_fichier(self, dossier_source, fichier):
        valeurs = {}
        trans_tab = self.ouvrir_csv(dossier_source, fichier)
        for j in range(1, len(trans_tab)):
            valeur = {}
            ligne = trans_tab[j]
            for i in range(2, len(ligne)):
                valeur[self.cles[i]] = ligne[i]
            valeurs[j] = valeur
        return valeurs

    def mise_a_jour(self, edition, dossier_source, dossier_destination, maj_trans):
        """
        modification des résumés mensuels au niveau du client dont la facture est modifiée
        :param edition: paramètres d'édition
        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param maj_trans: données modifiées pour le client pour les transactions
        """
        fichier_trans = "Transaction_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + ".csv"
        donnees_csv = Resumes.ouvrir_csv_sans_client(dossier_source, fichier_trans, edition.client_unique, 3)
        with dossier_destination.writer(fichier_trans) as fichier_writer:
            for ligne in donnees_csv:
                fichier_writer.writerow(ligne)

            for key in maj_trans.valeurs.keys():
                valeur = maj_trans.valeurs[key]
                ligne = [self.annee, self.mois]
                for i in range(2, len(self.cles)):
                    ligne.append(valeur[self.cles[i]])
                fichier_writer.writerow(ligne)
