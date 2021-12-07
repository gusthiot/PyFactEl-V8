from importes import Fichier
from outils import Outils


class CoefPrest(Fichier):
    """
    Classe pour l'importation des données de Coefficients Prestations
    """

    cles = ['id_classe', 'id_article', 'coefficient']
    nom_fichier = "coeffprestation.csv"
    libelle = "Coefficients Prestations"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def contient_article(self, id_article):
        """
        vérifie si l'id de l'article SAP est présent
        :param id_article: l'id article à vérifier
        :return: 1 si présente, 0 sinon
        """
        if self.verifie_coherence == 1:
            for cle, coefprest in self.donnees.items():
                if coefprest['id_article'] == id_article:
                    return 1
        else:
            for coefprest in self.donnees:
                if coefprest['id_article'] == id_article:
                    return 1
        return 0

    def est_coherent(self, classes, artsap):
        """
        vérifie que les données du fichier importé sont cohérentes (si couple catégorie - classe de tarif est unique),
        et efface les colonnes mois et année
        :param classes: classes clients importées
        :param artsap: articles SAP importés
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        articles = []
        couples = []
        donnees_dict = {}
        clas = []

        del self.donnees[0]
        for donnee in self.donnees:
            if donnee['id_classe'] == "":
                msg += "l'id classe client de la ligne " + str(ligne) + " ne peut être vide\n"
            elif not classes.contient_id(donnee['id_classe']):
                msg += "l'id classe client de la ligne " + str(ligne) + " n'existe pas dans les codes N\n"
            elif donnee['id_classe'] not in clas:
                if donnee['id_classe'] not in clas:
                    clas.append(donnee['id_classe'])

            if donnee['id_article'] == "":
                msg += "l'id article SAP de la ligne " + str(ligne) + " ne peut être vide\n"
            elif not artsap.contient_id(donnee['id_article']):
                msg += "l'id article SAP de la ligne " + str(ligne) + " n'existe pas dans les codes D\n"
            elif donnee['id_article'] not in articles:
                articles.append(donnee['id_article'])

            couple = [donnee['id_article'], donnee['id_classe']]
            if couple not in couples:
                couples.append(couple)
            else:
                msg += "Couple id article SAP '" + donnee['id_article'] + "' et id classe client '" + \
                       donnee['id_classe'] + "' de la ligne " + str(ligne) + " pas unique\n"

            donnee['coefficient'], info = Outils.est_un_nombre(donnee['coefficient'], "le coefficient", ligne, 2, 0)
            msg += info

            donnees_dict[donnee['id_classe'] + donnee['id_article']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        for id_article in artsap.ids_d3:
            if id_article not in articles:
                msg += "L'id article SAP D3 '" + id_article + "' n'est pas présent dans "\
                                                         "les coefficients de prestations\n"

        for id_classe in classes.donnees.keys():
            if id_classe not in clas:
                msg += "L'id de classe '" + id_classe + "' dans les classes clients n'est pas présent dans " \
                                                         "les coefficients de prestations\n"

        for id_article in articles:
            for id_classe in clas:
                couple = [id_article, id_classe]
                if couple not in couples:
                    msg += "Couple id article SAP '" + id_article + "' et id classe client '" + \
                           id_classe + "' n'existe pas\n"

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
