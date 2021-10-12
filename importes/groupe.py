from importes import Fichier
from outils import Outils


class Groupe(Fichier):
    """
    Classe pour l'importation des données de Machines Cmi
    """

    # K1, K2, K3, K4, K5, K5, K6
    cles = ['id_groupe', 'id_cat_mach', 'id_cat_mo', 'id_cat_plat', 'id_cat_cher', 'id_cat_hp', 'id_cat_hc']
    nom_fichier = "groupe.csv"
    libelle = "Groupes de machines"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def contient_id(self, id_groupe):
        """
        vérifie si un groupe contient l'id donné
        :param id_groupe: id à vérifier
        :return: 1 si id contenu, 0 sinon
        """
        if self.verifie_coherence == 1:
            if id_groupe in self.donnees.keys():
                return 1
        else:
            for groupe in self.donnees:
                if groupe['id_groupe'] == id_groupe:
                    return 1
        return 0

    def est_coherent(self, categories):
        """
        vérifie que les données du fichier importé sont cohérentes
        :param categories: catégories importées
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        ids = []
        donnees_dict = {}

        del self.donnees[0]
        for donnee in self.donnees:
            donnee['id_groupe'], info = Outils.est_un_alphanumerique(donnee['id_groupe'], "l'id groupe", ligne)
            msg += info
            if info == "":
                if donnee['id_groupe'] not in ids:
                    ids.append(donnee['id_groupe'])
                else:
                    msg += "l'id groupe '" + donnee['id_groupe'] + "' de la ligne " + str(ligne) +\
                           " n'est pas unique\n"

            if donnee['id_cat_mach'] == "":
                msg += "l'id catégorie machine de la ligne " + str(ligne) + " ne peut être vide\n"
            elif categories.contient_id(donnee['id_cat_mach']) == 0:
                msg += "l'id catégorie machine '" + donnee['id_cat_mach'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            if donnee['id_cat_mo'] == "":
                msg += "l'id catégorie opérateur de la ligne " + str(ligne) + " ne peut être vide\n"
            elif categories.contient_id(donnee['id_cat_mo']) == 0:
                msg += "l'id catégorie opérateur '" + donnee['id_cat_mo'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            if donnee['id_cat_plat'] == "":
                msg += "l'id catégorie plateforme de la ligne " + str(ligne) + " ne peut être vide\n"
            elif categories.contient_id(donnee['id_cat_plat']) == 0:
                msg += "l'id catégorie plateforme '" + donnee['id_cat_plat'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            if donnee['id_cat_cher'] == "":
                msg += "l'id catégorie onéreux de la ligne " + str(ligne) + " ne peut être vide\n"
            elif categories.contient_id(donnee['id_cat_cher']) == 0:
                msg += "l'id catégorie onéreux '" + donnee['id_cat_cher'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            if donnee['id_cat_hp'] == "":
                msg += "l'id catégorie hp de la ligne " + str(ligne) + " ne peut être vide\n"
            elif categories.contient_id(donnee['id_cat_hp']) == 0:
                msg += "l'id catégorie hp '" + donnee['id_cat_hp'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            if donnee['id_cat_hc'] == "":
                msg += "l'id catégorie hc de la ligne " + str(ligne) + " ne peut être vide\n"
            elif categories.contient_id(donnee['id_cat_hc']) == 0:
                msg += "l'id catégorie hc '" + donnee['id_cat_hc'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            donnees_dict[donnee['id_groupe']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
