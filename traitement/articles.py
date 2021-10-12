from outils import Outils
from traitement import Recap


class Articles(Recap):
    """
    Classe pour la création du listing des articles
    """

    cles = ['invoice-year', 'invoice-month', 'item-id', 'item-type', 'item-nbr', 'item-name', 'item-unit', 'item-codeD',
            'item-labelcode', 'item-sap', 'platf-code', 'item-extra']

    def __init__(self, edition):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        """
        super().__init__(edition)
        self.nom = "article_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + ".csv"

    def generer(self, generaux, categories, prestations, paramtexte):
        """
        génération du fichier des articles
        :param generaux: paramètres généraux
        :param categories: catégories importées
        :param prestations: prestations importées
        :param paramtexte: paramètres textuels
        """
        pt = paramtexte.donnees
        for key in categories.donnees.keys():
            cat = categories.donnees[key]
            if cat['code_d'] == generaux.obtenir_code_d()[0]:
                type = pt['item-penalty']
            elif cat['code_d'] == generaux.obtenir_code_d()[1]:
                type = pt['item-service']
            else:
                type = ""
                Outils.fatal("Erreur code D", "Une catégorie devrait avoir un code D1 ou D2")
            donnee = [cat['id_categorie'], type, cat['no_categorie'], cat['intitule'], cat['unite'],
                      cat['code_d'], generaux.intitule_long_par_code_d(cat['code_d']),
                      generaux.code_sap_par_code_d(cat['code_d']), cat['id_plateforme'], "FALSE"]
            self.ajouter_valeur(donnee, cat['id_categorie'])

        for key in prestations.donnees.keys():
            prest = prestations.donnees[key]
            if prest['id_machine'] == "0":
                extra = "FALSE"
            else:
                extra = "TRUE"
            donnee = [prest['id_prestation'], pt['item-good'], prest['no_prestation'], prest['designation'],
                      prest['unite_prest'], prest['categorie'], generaux.intitule_long_par_code_d(prest['categorie']),
                      generaux.code_sap_par_code_d(prest['categorie']), prest['id_plateforme'], extra]
            self.ajouter_valeur(donnee, prest['id_prestation'])
