from importes import Fichier
from outils import Outils
import re


class Client(Fichier):
    """
    Classe pour l'importation des données de Clients Cmi
    """

    cles = ['annee', 'mois', 'code', 'code_sap', 'abrev_labo', 'nom_labo', 'ref', 'dest', 'email', 'mode', 'nature']
    nom_fichier = "client.csv"
    libelle = "Clients"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.codes = []

    def obtenir_codes(self):
        """
        retourne les codes de tous les clients
        :return: codes de tous les clients
        """
        if self.verifie_coherence == 0:
            info = self.libelle + ". vous devez vérifier la cohérence avant de pouvoir obtenir les codes"
            Outils.affiche_message(info)
            return []
        return self.codes

    def est_coherent(self, generaux):
        """
        vérifie que les données du fichier importé sont cohérentes, et efface les colonnes mois et année
        :param generaux: paramètres généraux
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
        donnees_dict = {}

        for donnee in self.donnees:
            donnee['code_sap'], info = Outils.est_un_alphanumerique(donnee['code_sap'], "le code client sap", ligne)
            msg += info

            donnee['code'], info = Outils.est_un_alphanumerique(donnee['code'], "le code client", ligne)
            msg += info
            if info == "":
                if donnee['code'] not in self.codes:
                    self.codes.append(donnee['code'])
                else:
                    msg += "le code client '" + donnee['code'] + "' de la ligne " + str(ligne) +\
                           " n'est pas unique\n"

            donnee['abrev_labo'], info = Outils.est_un_alphanumerique(donnee['abrev_labo'], "l'abrev. labo", ligne)
            msg += info
            donnee['nom_labo'], info = Outils.est_un_texte(donnee['nom_labo'], "le nom labo", ligne, True)
            msg += info
            donnee['ref'], info = Outils.est_un_texte(donnee['ref'], "la référence", ligne, True)
            msg += info
            donnee['dest'], info = Outils.est_un_texte(donnee['dest'], "le destinataire", ligne, True)
            msg += info

            if donnee['nature'] == "":
                msg += "le type de labo de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['nature'] not in generaux.obtenir_code_n():
                msg += "le type de labo '" + donnee['nature'] + "' de la ligne " + str(ligne) +\
                    " n'existe pas dans les types N\n"
            else:
                av_hc = generaux.avantage_hc_par_code_n(donnee['nature'])
                donnee['rh'] = 1
                donnee['bh'] = 0
                if av_hc == 'BONUS':
                    donnee['bh'] = 1
                    donnee['rh'] = 0

            if (donnee['mode'] != "") and (donnee['mode'] not in generaux.obtenir_modes_envoi()):
                msg += "le mode d'envoi '" + donnee['mode'] + "' de la ligne " + str(ligne) +\
                    " n'existe pas dans les modes d'envoi généraux\n"

            if (donnee['mode'] == "MAIL") and (not re.match("[^@]+@[^@]+\.[^@]+", donnee['email'])):
                msg += "le format de l'e-mail '" + donnee['email'] + "' de la ligne " + str(ligne) +\
                    " n'est pas correct\n"

            del donnee['annee']
            del donnee['mois']
            donnees_dict[donnee['code']] = donnee

            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
