from importes import Fichier
from outils import Outils


class CleSubside(Fichier):
    """
    Classe pour l'importation des données de Subsides
    """

    nom_fichier = "clesubside.csv"
    cles = ['type', 'id_plateforme', 'id_classe', 'code_client', 'id_machine']
    libelle = "Clés Subsides"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def est_coherent(self, plateformes, clients, machines, classes, subsides):
        """
        vérifie que les données du fichier importé sont cohérentes
        :param plateformes: plateformes importées
        :param clients: clients importés
        :param machines: machines importées
        :param classes: classes clients importées
        :param subsides: subsides importés
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        donnees_dict = {}
        quintuplets = []

        del self.donnees[0]
        for donnee in self.donnees:
            if donnee['type'] == "":
                msg += "le type de la ligne " + str(ligne) + " ne peut être vide\n"
            elif subsides.contient_type(donnee['type']) == 0:
                msg += "le type '" + donnee['type'] + "' de la ligne " + str(ligne) + " n'est pas référencé\n"

            if donnee['id_plateforme'] == "":
                msg += "l'id plateforme de la ligne " + str(ligne) + " ne peut être vide\n"
            elif plateformes.contient_id(donnee['id_plateforme']) == 0:
                msg += "l'id plateforme '" + donnee['id_plateforme'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            if donnee['id_classe'] != "0" and not classes.contient_id(donnee['id_classe']):
                msg += "l'id classe client de la ligne " + str(ligne) + " n'existe pas\n"

            if donnee['code_client'] != "0" and donnee['code_client'] not in clients.donnees:
                msg += "le code client " + donnee['code_client'] + " de la ligne " + str(ligne) + \
                       " n'est pas référencé\n"

            if donnee['id_machine'] != "0" and machines.contient_id(donnee['id_machine']) == 0:
                msg += "le machine id '" + donnee['id_machine'] + "' de la ligne " + str(ligne)\
                       + " n'est pas référencé\n"

            quintuplet = donnee['type'] + donnee['id_plateforme'] + donnee['id_classe'] + donnee['code_client'] + \
                donnee['id_machine']

            if quintuplet not in quintuplets:
                quintuplets.append(quintuplet)
            else:
                msg += "le quintuplet de la ligne " + str(ligne) + \
                       " n'est pas unique\n"

            if donnee['type'] not in donnees_dict:
                donnees_dict[donnee['type']] = {}
            dict_t = donnees_dict[donnee['type']]
            if donnee['id_plateforme'] not in dict_t:
                dict_t[donnee['id_plateforme']] = {}
            dict_p = dict_t[donnee['id_plateforme']]
            if donnee['id_classe'] not in dict_p:
                dict_p[donnee['id_classe']] = {}
            dict_n = dict_p[donnee['id_classe']]
            if donnee['code_client'] not in dict_n:
                dict_n[donnee['code_client']] = {}
            dict_c = dict_n[donnee['code_client']]
            if donnee['id_machine'] not in dict_c:
                dict_c[donnee['id_machine']] = donnee

            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
