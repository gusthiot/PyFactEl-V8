from importes import Fichier
from outils import Outils


class ArticleSap(Fichier):
    """
    Classe pour l'importation des données des Articles SAP
    """

    cles = ['id_article', 'flux', 'code_d', 'intitule_long', 'intitule_court', 'code_sap', 'code_sap_qas', 'quantite',
            'unite', 'type_prix', 'type_rabais', 'texte_sap']
    nom_fichier = "articlesap.csv"
    libelle = "Articles SAP"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_d1 = None
        self.id_d2 = None
        self.ids_d3 = []
        self.ids = []

    def contient_id(self, id_article, flux=None):
        """
        vérifie si un article contient l'id donné, voire s'il est dans le(s) flux donné(s)
        :param id_article: id à vérifier
        :param flux: tableau de flux, facultatif
        :return: 1 si id contenu, 0 sinon
        """
        if self.verifie_coherence == 1:
            if id_article in self.donnees.keys():
                if flux is not None and self.donnees[id_article]['flux'] not in flux:
                    return 0
                return 1
        else:
            for article in self.donnees:
                if article['id_article'] == id_article:
                    if flux is not None and article['flux'] not in flux:
                        return 0
                    return 1
        return None

    def est_coherent(self):
        """
        vérifie que les données du fichier importé sont cohérentes
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        del self.donnees[0]
        msg = ""
        ligne = 1
        donnees_dict = {}

        for donnee in self.donnees:
            donnee['id_article'], info = Outils.est_un_alphanumerique(donnee['id_article'], "l'id de l'article", ligne)
            msg += info
            if info == "":
                if donnee['id_article'] not in self.ids:
                    self.ids.append(donnee['id_article'])
                else:
                    msg += "l'id de l'article '" + donnee['id_article'] + "' de la ligne " + str(ligne) +\
                           " n'est pas unique\n"

            donnee['code_d'], info = Outils.est_un_alphanumerique(donnee['code_d'], "le code D", ligne)
            msg += info
            donnee['intitule_long'], info = Outils.est_un_texte(donnee['intitule_long'], "l'intitulé long", ligne)
            msg += info
            donnee['intitule_court'], info = Outils.est_un_texte(donnee['intitule_court'], "l'intitulé court", ligne)
            msg += info
            donnee['code_sap'], info = Outils.est_un_entier(donnee['code_sap'], "le code sap", ligne, 1)
            msg += info
            donnee['code_sap_qas'], info = Outils.est_un_entier(donnee['code_sap_qas'], "le code sap qas", ligne, 1)
            msg += info
            donnee['quantite'], info = Outils.est_un_nombre(donnee['quantite'], "la quantité", ligne, 3, 0)
            msg += info
            donnee['unite'], info = Outils.est_un_texte(donnee['unite'], "l'unité", ligne)
            msg += info
            donnee['type_prix'], info = Outils.est_un_alphanumerique(donnee['type_prix'], "le type de prix", ligne)
            msg += info
            donnee['type_rabais'], info = Outils.est_un_alphanumerique(donnee['type_rabais'], "le type de rabais",
                                                                       ligne)
            msg += info
            donnee['texte_sap'], info = Outils.est_un_texte(donnee['texte_sap'], "le texte sap", ligne, True)
            msg += info

            if donnee['flux'] == 'lvr':
                self.ids_d3.append(donnee['id_article'])
            elif donnee['flux'] == 'cae':
                self.id_d1 = donnee['id_article']
            elif donnee['flux'] == 'noshow':
                self.id_d2 = donnee['id_article']
            else:
                msg += "le flux de la ligne " + str(ligne) + " doit être cae, noshow ou lvr\n"

            donnees_dict[donnee['id_article']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
