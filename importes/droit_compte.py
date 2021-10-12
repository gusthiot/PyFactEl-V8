from importes import Fichier
from outils import Outils


class DroitCompte(Fichier):
    """
    Classe pour l'importation des données de Droits des Comptes
    """

    cles = ['annee', 'mois', 'id_user', 'id_compte', 'debut', 'fin']
    nom_fichier = "droitcompte.csv"
    libelle = "Droits des Comptes"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def est_coherent(self, comptes, users):
        """
        vérifie que les données du fichier importé sont cohérentes, et efface les colonnes mois et année
        :param comptes: comptes importés
        :param users: users importés
        :return: 1 s'il y a une erreur, 0 sinon
        """
        if self.verifie_date == 0:
            info = self.libelle + ". vous devez vérifier la date avant de vérifier la cohérence"
            Outils.affiche_message(info)
            return 1

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        couples = []
        donnees_dict = {}

        for donnee in self.donnees:
            if donnee['id_compte'] == "":
                msg += "le compte id de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['id_compte'] not in comptes.donnees:
                msg += "le compte id " + donnee['id_compte'] + " de la ligne " + str(ligne) + \
                       " n'est pas référencé\n"
            if donnee['id_user'] == "":
                msg += "le user id de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['id_user'] not in users.donnees:
                msg += "le user id " + donnee['id_user'] + " de la ligne " + str(ligne) + \
                       " n'est pas référencé\n"

            couple = [donnee['id_user'], donnee['id_compte']]
            if couple not in couples:
                couples.append(couple)
            else:
                msg += "Couple user id '" + donnee['id_user'] + "' et compte id '" + \
                       donnee['id_compte'] + "' de la ligne " + str(ligne) + " pas unique\n"

            if donnee['debut'] != 'NULL':
                donnee['debut'], info = Outils.est_une_date(donnee['debut'], "la date de début", ligne)
                msg += info
            if donnee['fin'] != 'NULL':
                donnee['fin'], info = Outils.est_une_date(donnee['fin'], "la date de fin", ligne)
                msg += info

            del donnee['annee']
            del donnee['mois']
            donnees_dict[donnee['id_user'] + donnee['id_compte']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
