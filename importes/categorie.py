from importes import Fichier
from outils import Outils


class Categorie(Fichier):
    """
    Classe pour l'importation des données de Catégories
    """

    cles = ['id_categorie', 'no_categorie', 'intitule', 'unite', 'id_plateforme', 'id_article']
    nom_fichier = "categorie.csv"
    libelle = "Catégories"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def contient_id(self, id_cat):
        """
        vérifie si une catégorie contient l'id donné
        :param id_cat: id à vérifier
        :return: 1 si id contenu, 0 sinon
        """
        if self.verifie_coherence == 1:
            if id_cat in self.donnees.keys():
                return 1
        else:
            for cat in self.donnees:
                if cat['id_categorie'] == id_cat:
                    return 1
        return 0

    def est_coherent(self, artsap, plateformes):
        """
        vérifie que les données du fichier importé sont cohérentes
        :param artsap: articles SAP importés
        :param plateformes: plateformes importées
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        donnees_dict = {}
        ids = []

        del self.donnees[0]
        for donnee in self.donnees:
            donnee['id_categorie'], info = Outils.est_un_alphanumerique(donnee['id_categorie'], "l'id catégorie", ligne)
            msg += info
            if info == "":
                if donnee['id_categorie'] not in ids:
                    ids.append(donnee['id_categorie'])
                else:
                    msg += "l'id catégorie '" + donnee['id_categorie'] + "' de la ligne " + str(ligne) +\
                           " n'est pas unique\n"

            if donnee['id_article'] == "":
                msg += "l'id d'article SAP de la ligne " + str(ligne) + " ne peut être vide\n"
            elif not artsap.contient_id(donnee['id_article'], ['cae', 'noshow']):
                msg += "l'id d'article SAP de la ligne " + str(ligne) + " n'est pas un code D1 ou D2\n"

            if donnee['id_plateforme'] == "":
                msg += "l'id plateforme de la ligne " + str(ligne) + " ne peut être vide\n"
            elif plateformes.contient_id(donnee['id_plateforme']) == 0:
                msg += "l'id plateforme '" + donnee['id_plateforme'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            donnee['no_categorie'], info = Outils.est_un_alphanumerique(donnee['no_categorie'], "le no catégorie",
                                                                        ligne)
            msg += info
            donnee['intitule'], info = Outils.est_un_texte(donnee['intitule'], "l'intitulé", ligne)
            msg += info
            donnee['unite'], info = Outils.est_un_texte(donnee['unite'], "l'unité", ligne)
            msg += info

            donnees_dict[donnee['id_categorie']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
