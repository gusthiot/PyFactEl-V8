from importes import Fichier
from outils import Outils


class NoShow(Fichier):
    """
    Classe pour l'importation des données de No Show
    """

    cles = ['annee', 'mois', 'date_debut', 'type', 'id_machine', 'id_user', 'id_compte', 'penalite']
    nom_fichier = "noshow.csv"
    libelle = "Pénalités No Show"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.comptes = []
        self.sommes = {}

    def obtenir_comptes(self):
        """
        retourne la liste de tous les comptes clients
        :return: liste des comptes clients présents dans les données noshow importées
        """
        if self.verifie_coherence == 0:
            info = self.libelle + ". vous devez vérifier la cohérence avant de pouvoir obtenir les comptes"
            Outils.affiche_message(info)
            return []
        return self.comptes

    def est_coherent(self, comptes, machines, users):
        """
        vérifie que les données du fichier importé sont cohérentes, et efface les colonnes mois et année
        :param comptes: comptes importés
        :param machines: machines importées
        :param users: users importés
        :return: 1 s'il y a une erreur, 0 sinon
        """
        if self.verifie_date == 0:
            info = self.libelle + ". vous devez vérifier la date avant de vérifier la cohérence"
            Outils.affiche_message(info)
            return 1

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        donnees_list = []

        for donnee in self.donnees:
            if donnee['id_compte'] == "":
                msg += "le id compte de la ligne " + str(ligne) + " ne peut être vide\n"
            elif comptes.contient_id(donnee['id_compte']) == 0:
                msg += "le id compte '" + donnee['id_compte'] + "' de la ligne " + str(ligne) + " n'est pas référencé\n"
            elif donnee['id_compte'] not in self.comptes:
                self.comptes.append(donnee['id_compte'])

            if donnee['id_machine'] == "":
                msg += "le machine id de la ligne " + str(ligne) + " ne peut être vide\n"
            elif machines.contient_id(donnee['id_machine']) == 0:
                msg += "le machine id '" + donnee['id_machine'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            if donnee['id_user'] == "":
                msg += "le user id de la ligne " + str(ligne) + " ne peut être vide\n"
            elif users.contient_id(donnee['id_user']) == 0:
                msg += "le user id '" + donnee['id_user'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            if donnee['type'] == "":
                msg += "HP/HC " + str(ligne) + " ne peut être vide\n"
            elif donnee['type'] != "HP" and donnee['type'] != "HC":
                msg += "HP/HC " + str(ligne) + " doit être égal à HP ou HC\n"

            donnee['penalite'], info = Outils.est_un_nombre(donnee['penalite'], "la pénalité", ligne, 2, 0)
            msg += info

            donnee['date_debut'], info = Outils.est_une_date(donnee['date_debut'], "la date de début", ligne)
            msg += info

            del donnee['annee']
            del donnee['mois']
            donnees_list.append(donnee)

            ligne += 1

        self.donnees = donnees_list
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0

    def calcul_montants(self, machines, categprix, clients, comptes, verification, groupes):
        """
        calcule les sous-totaux nécessaires
        :param machines: machines importées et vérifiées
        :param categprix: catégories prix importés et vérifiés
        :param clients: clients importés et vérifiés
        :param comptes: comptes importés
        :param verification: pour vérifier si les dates et les cohérences sont correctes
        :param groupes: groupes importés
        """
        if verification.a_verifier != 0:
            info = self.libelle + ". vous devez faire les vérifications avant de calculer les montants"
            Outils.affiche_message(info)
            return

        donnees_list = []
        pos = 0
        for donnee in self.donnees:
            id_compte = donnee['id_compte']
            compte = comptes.donnees[id_compte]
            code_client = compte['code_client']
            id_machine = donnee['id_machine']
            id_user = donnee['id_user']

            client = clients.donnees[code_client]
            id_groupe = machines.donnees[id_machine]['id_groupe']
            groupe = groupes.donnees[id_groupe]

            nat = client['nature']
            cat_hp = groupe['id_cat_hp']
            cat_hc = groupe['id_cat_hc']
            pu_hp = round(categprix.donnees[nat + cat_hp]['prix_unit'], 2)
            pu_hc = round(categprix.donnees[nat + cat_hc]['prix_unit'], 2)

            if donnee['type'] == "HP":
                np_hp = round(donnee['penalite'], 1)
                np_hc = 0
            else:
                np_hp = 0
                np_hc = round(donnee['penalite'], 1)
            ok_hp = False
            ok_hc = False
            if np_hp > 0 and pu_hp > 0:
                ok_hp = True
            if np_hc > 0 and pu_hc > 0:
                ok_hc = True

            if ok_hp or ok_hc:
                if code_client not in self.sommes:
                    self.sommes[code_client] = {}
                scl = self.sommes[code_client]

                if id_machine not in scl:
                    scl[id_machine] = {'np_hp': 0, 'np_hc': 0, 'pu_hp': pu_hp, 'pu_hc': pu_hc, 'users': {}}

                scm = scl[id_machine]

                if ok_hp:
                    scm['np_hp'] += np_hp
                if ok_hc:
                    scm['np_hc'] += np_hc

                if id_user not in scm['users']:
                    scm['users'][id_user] = {'np_hp': 0, 'np_hc': 0, 'data': []}
                if ok_hp:
                    scm['users'][id_user]['np_hp'] += np_hp
                if ok_hc:
                    scm['users'][id_user]['np_hc'] += np_hc
                scm['users'][id_user]['data'].append(pos)

            donnees_list.append(donnee)
            pos += 1

        self.donnees = donnees_list
