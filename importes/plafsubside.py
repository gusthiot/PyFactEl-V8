from importes import Fichier
from outils import Outils


class PlafSubside(Fichier):
    """
    Classe pour l'importation des données ded Plafonds de Subsides
    """

    nom_fichier = "plafsubside.csv"
    cles = ['type', 'id_plateforme', 'id_article', 'pourcentage', 'max_mois', 'max_compte']
    libelle = "Plafonds Subsides"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def est_coherent(self, subsides, artsap, plateformes):
        """
        vérifie que les données du fichier importé sont cohérentes
        :param subsides: subsides importés
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
        triplets = []

        del self.donnees[0]
        for donnee in self.donnees:
            if donnee['type'] == "":
                msg += "le type de la ligne " + str(ligne) + " ne peut être vide\n"
            elif subsides.contient_type(donnee['type']) == 0:
                msg += "le type '" + donnee['type'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"
            if donnee['id_article'] == "":
                msg += "l'id article SAP de la ligne " + str(ligne) + " ne peut être vide\n"
            elif not artsap.contient_id(donnee['id_article']):
                msg += "l'id article SAP de la ligne " + str(ligne) + " n'existe pas dans les codes D\n"

            if donnee['id_plateforme'] == "":
                msg += "l'id plateforme de la ligne " + str(ligne) + " ne peut être vide\n"
            elif plateformes.contient_id(donnee['id_plateforme']) == 0:
                msg += "l'id plateforme '" + donnee['id_plateforme'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            triplet = [donnee['type'], donnee['id_plateforme'], donnee['id_article']]
            if triplet not in triplets:
                triplets.append(triplet)
            else:
                msg += "Triplet type '" + donnee['type'] + "' id plateforme '" + donnee['id_plateforme'] + \
                       "' et id article SAP '" + donnee['id_article'] + "' de la ligne " + str(ligne) + " pas unique\n"

            donnee['pourcentage'], info = Outils.est_un_nombre(donnee['pourcentage'], "le pourcentage", ligne, 2, 0,
                                                               100)
            msg += info

            donnee['max_mois'], info = Outils.est_un_nombre(donnee['max_mois'], "le max mensuel", ligne, 2, 0)
            msg += info

            donnee['max_compte'], info = Outils.est_un_nombre(donnee['max_compte'], "le max compte", ligne, 2, 0)
            msg += info

            donnees_dict[donnee['type'] + donnee['id_article']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
