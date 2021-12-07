from outils import Outils
from traitement import Recap


class Articles(Recap):
    """
    Classe pour la création du listing des articles
    """

    cles = ['invoice-year', 'invoice-month', 'item-id', 'item-nbr', 'item-name', 'item-unit', 'item-idsap',
            'item-codeD', 'item-flag-usage', 'item-flag-conso', 'item-labelcode', 'item-sap', 'platf-code',
            'item-extra']

    def __init__(self, edition):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        """
        super().__init__(edition)
        self.nom = "article_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + ".csv"

    def generer(self, artsap, categories, prestations):
        """
        génération du fichier des articles
        :param artsap: articles SAP importés
        :param categories: catégories importées
        :param prestations: prestations importées
        """
        for key in categories.donnees.keys():
            cat = categories.donnees[key]
            art = artsap.donnees[cat['id_article']]
            donnee = [cat['id_categorie'], cat['no_categorie'], cat['intitule'], cat['unite'], cat['id_article'],
                      art['code_d'], art['flag_usage'], art['flag_conso'], art['intitule_long'], art['code_sap'],
                      cat['id_plateforme'], "FALSE"]
            self.ajouter_valeur(donnee, cat['id_categorie'])

        for key in prestations.donnees.keys():
            prest = prestations.donnees[key]
            art = artsap.donnees[prest['id_article']]
            if prest['id_machine'] == "0":
                extra = "FALSE"
            else:
                extra = "TRUE"
            donnee = [prest['id_prestation'], prest['no_prestation'], prest['designation'],
                      prest['unite_prest'], prest['id_article'], art['code_d'], art['flag_usage'], art['flag_conso'],
                      art['intitule_long'], art['code_sap'], prest['id_plateforme'], extra]
            self.ajouter_valeur(donnee, prest['id_prestation'])
