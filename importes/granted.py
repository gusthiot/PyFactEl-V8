from importes import Fichier
from outils import Outils


class Granted(Fichier):
    """
    Classe pour l'importation des données de Subsides comptabilisés
    """

    cles = ['id_compte', 'code_d', 'montant']
    libelle = "Subsides comptabilisés"

    def __init__(self, dossier_source, edition):
        self.nom_fichier = "granted_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois-1) + ".csv"
        super().__init__(dossier_source)

    def est_coherent(self, comptes, generaux):
        """
        vérifie que les données du fichier importé sont cohérentes
        :param comptes: comptes importés
        :param generaux: paramètres généraux
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        donnees_dict = {}
        couples = []

        del self.donnees[0]
        for donnee in self.donnees:
            if donnee['id_compte'] == "":
                msg += "l'id compte de la ligne " + str(ligne) + " ne peut être vide\n"
            elif comptes.contient_id(donnee['id_compte']) == 0:
                msg += "l'id compte '" + donnee['id_compte'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"
            if donnee['code_d'] == "":
                msg += "la code D de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['code_d'] not in generaux.obtenir_code_d():
                msg += "la code D de la ligne " + str(ligne) + " n'existe pas dans les codes D\n"

            couple = [donnee['id_compte'], donnee['code_d']]
            if couple not in couples:
                couples.append(couple)
            else:
                msg += "Couple id compte '" + donnee['id_compte'] + "' et code D '" + \
                       donnee['code_d'] + "' de la ligne " + str(ligne) + " pas unique\n"

            donnee['montant'], info = Outils.est_un_nombre(donnee['montant'], "le montant comptabilisé", ligne, 2, 0)
            msg += info

            donnees_dict[donnee['id_compte']+donnee['code_d']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
