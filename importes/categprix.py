from importes import Fichier
from outils import Outils


class CategPrix(Fichier):
    """
    Classe pour l'importation des données de Catégories Prix
    """

    nom_fichier = "categprix.csv"
    cles = ['id_classe', 'id_categorie', 'prix_unit']
    libelle = "Catégories Prix"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def est_coherent(self, classes, categories):
        """
        vérifie que les données du fichier importé sont cohérentes
        :param classes: classes clients importées
        :param categories: catégories importées
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        donnees_dict = {}
        clas = []
        couples = []
        ids = []

        del self.donnees[0]
        for donnee in self.donnees:
            if donnee['id_classe'] == "":
                msg += "l'id de classe client de la ligne " + str(ligne) + " ne peut être vide\n"
            elif not classes.contient_id(donnee['id_classe']):
                msg += "l'id de classe client de la ligne " + str(ligne) + " n'existe pas dans les codes N\n"
            elif donnee['id_classe'] not in clas:
                clas.append(donnee['id_classe'])

            if donnee['id_categorie'] == "":
                msg += "l'id catégorie " + str(ligne) + " ne peut être vide\n"
            elif categories.contient_id(donnee['id_categorie']) == 0:
                msg += "l'id catégorie de la ligne " + str(ligne) + " n'existe pas dans les catégories \n"
            elif donnee['id_categorie'] not in ids:
                ids.append(donnee['id_categorie'])

            if (donnee['id_categorie'] != "") and (donnee['id_classe'] != ""):
                couple = [donnee['id_categorie'], donnee['id_classe']]
                if couple not in couples:
                    couples.append(couple)
                else:
                    msg += "Couple id catégorie '" + donnee['id_categorie'] + "' et id classe '" + \
                           donnee['id_classe'] + "' de la ligne " + str(ligne) + " pas unique\n"

            donnee['prix_unit'], info = Outils.est_un_nombre(donnee['prix_unit'], "le prix unitaire ", ligne, 2)
            msg += info

            donnees_dict[donnee['id_classe'] + donnee['id_categorie']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        for id_classe in classes.donnees.keys():
            if id_classe not in clas:
                msg += "L'id de classe '" + id_classe + "' dans les classes clients n'est pas présent dans " \
                                                         "les catégories prix\n"

        for id_cat in categories.donnees.keys():
            if id_cat not in ids:
                msg += "L'id catégorie '" + id_cat + "' dans les catégories n'est pas présent dans " \
                                                         "les catégories prix\n"
        for id_cat in ids:
            for classe in clas:
                couple = [id_cat, classe]
                if couple not in couples:
                    msg += "Couple id catégorie '" + id_cat + "' et id classe client '" + \
                           classe + "' n'existe pas\n"

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
