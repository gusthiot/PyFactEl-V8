from outils import Outils
from traitement import Recap


class Tarifs(Recap):
    """
    Classe pour la création du listing des tarifs
    """
    
    cles = ['invoice-year', 'invoice-month', 'item-id', 'client-idclass', 'valuation-price']

    def __init__(self, edition):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        """
        super().__init__(edition)
        self.nom = "tarif_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + ".csv"

    def generer(self, classes, categories, prestations, categprix, coefprests):
        """
        génération du fichier des tarifs
        :param classes: classes clients importées
        :param categories: catégories importées
        :param prestations: prestations importées
        :param categprix: catégories de prix importées
        :param coefprests: coefficients prestations importés
        """
        for key in categories.donnees.keys():
            cat = categories.donnees[key]
            for id_classe in classes.donnees.keys():
                unique = id_classe + cat['id_categorie']
                prix_unit = categprix.donnees[unique]['prix_unit']
                donnee = [cat['id_categorie'], id_classe, prix_unit]
                self.ajouter_valeur(donnee, unique)

        for key in prestations.donnees.keys():
            prest = prestations.donnees[key]
            for id_classe in classes.donnees.keys():
                coefprest = coefprests.donnees[id_classe + prest['id_article']]
                prix_unit = round(prest['prix_unit'] * coefprest['coefficient'], 2)
                donnee = [prest['id_prestation'], id_classe, prix_unit]
                self.ajouter_valeur(donnee, id_classe + prest['id_prestation'])
