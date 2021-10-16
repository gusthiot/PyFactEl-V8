from importes import Fichier
from outils import Outils


class ClasseClient(Fichier):
    """
    Classe pour l'importation des données de Classes Clients
    """

    cles = ['id_classe', 'code_n', 'intitule', 'ref_fact', 'avantage_HC', 'subsides', 'rabais_excep', 'filtrer_article']
    nom_fichier = "classeclient.csv"
    libelle = "Classes Clients"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def contient_id(self, id_classe):
        """
        vérifie si une classe contient l'id donné
        :param id_classe: id à vérifier
        :return: la classe si id contenu, None sinon
        """
        if self.verifie_coherence == 1:
            if id_classe in self.donnees.keys():
                return self.donnees[id_classe]
        else:
            for classe in self.donnees:
                if classe['id_classe'] == id_classe:
                    return classe
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
        ids = []

        for donnee in self.donnees:
            donnee['id_classe'], info = Outils.est_un_alphanumerique(donnee['id_classe'], "l'id de classe", ligne)
            msg += info
            if info == "":
                if donnee['id_classe'] not in ids:
                    ids.append(donnee['id_classe'])
                else:
                    msg += "l'id de classe '" + donnee['id_classe'] + "' de la ligne " + str(ligne) +\
                           " n'est pas unique\n"

            donnee['code_n'], info = Outils.est_un_alphanumerique(donnee['code_n'], "le code N", ligne)
            msg += info
            donnee['intitule'], info = Outils.est_un_texte(donnee['intitule'], "l'intitulé", ligne)
            msg += info
            if donnee['ref_fact'] != 'INT' and donnee['ref_fact'] != 'EXT':
                msg += "le code référence client de la ligne " + str(ligne) + " doit être INT ou EXT\n"
            if donnee['avantage_HC'] != 'BONUS' and donnee['avantage_HC'] != 'RABAIS':
                msg += "l'avantage HC de la ligne " + str(ligne) + " doit être BONUS ou RABAIS\n"
            if donnee['subsides'] != 'BONUS' and donnee['subsides'] != 'RABAIS':
                msg += "le mode subsides de la ligne " + str(ligne) + " doit être BONUS ou RABAIS\n"
            if donnee['rabais_excep'] != 'BONUS' and donnee['rabais_excep'] != 'RABAIS':
                msg += "le mode rabais exceptionnel de la ligne " + str(ligne) + " doit être BONUS ou RABAIS\n"
            if donnee['filtrer_article'] != 'OUI' and donnee['filtrer_article'] != 'NON':
                msg += "le filtre articles nuls de la ligne " + str(ligne) + " doit être OUI ou NON\n"

            donnees_dict[donnee['id_classe']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
