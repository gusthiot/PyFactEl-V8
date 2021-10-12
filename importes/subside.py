from importes import Fichier
from outils import Outils


class Subside(Fichier):
    """
    Classe pour l'importation des données de Subsides
    """

    nom_fichier = "subside.csv"
    cles = ['type', 'intitule', 'debut', 'fin']
    libelle = "Subsides"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def contient_type(self, ty):
        """
        vérifie si un subside contient le type donné
        :param ty: type à vérifier
        :return: 1 si id contenu, 0 sinon
        """
        if self.verifie_coherence == 1:
            if ty in self.donnees.keys():
                return 1
        else:
            for subside in self.donnees:
                if subside['type'] == ty:
                    return 1
        return 0

    def est_coherent(self):
        """
        vérifie que les données du fichier importé sont cohérentes
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        donnees_dict = {}
        types = []

        del self.donnees[0]
        for donnee in self.donnees:
            donnee['type'], info = Outils.est_un_alphanumerique(donnee['type'], "le type subside", ligne)
            msg += info
            if info == "":
                if donnee['type'] not in types:
                    types.append(donnee['type'])
                else:
                    msg += "le type de la ligne " + str(ligne) + " n'est pas unique\n"
            donnee['intitule'], info = Outils.est_un_texte(donnee['intitule'], "l'intitulé", ligne)
            msg += info

            if donnee['debut'] != 'NULL':
                donnee['debut'], info = Outils.est_une_date(donnee['debut'], "la date de début", ligne)
                msg += info
            if donnee['fin'] != 'NULL':
                donnee['fin'], info = Outils.est_une_date(donnee['fin'], "la date de fin", ligne)
                msg += info
            if donnee['debut'] != 'NULL' and donnee['fin'] != 'NULL':
                if donnee['debut'] > donnee['fin']:
                    msg += "la date de fin de la ligne " + str(ligne) + " doit être postérieure à la date de début"

            donnees_dict[donnee['type']] = donnee

            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
