from outils import Outils
from erreurs import ErreurConsistance


class Paramtexte(object):
    """
     Classe pour les labels
     """

    nom_fichier = "paramtext.csv"
    libelle = "Paramètres de Texte"

    def __init__(self, dossier_source):
        """
        initialisation et importation des données

        :param dossier_source: Une instance de la classe dossier.DossierSource
        """
        fichier_reader = dossier_source.reader(self.nom_fichier)
        self.donnees = {}
        labels = []
        try:
            for ligne in fichier_reader:
                if len(ligne) != 2:
                    Outils.fatal(ErreurConsistance(),
                                 self.libelle + ": nombre de colonnes incorrect : " + str(len(ligne)) + ", attendu : 2")
                if ligne[0] in labels:
                    Outils.fatal(ErreurConsistance(),self.libelle + "le label '" + ligne[0] + " n'est pas unique\n")

                ligne[0], err = Outils.est_un_alphanumerique(ligne[0], "le label", chevrons=True)
                if err != "":
                    Outils.fatal(ErreurConsistance(), self.libelle + err)
                ligne[1], err = Outils.est_un_texte(ligne[1], "l'entête")
                if err != "":
                    Outils.fatal(ErreurConsistance(), self.libelle + err)

                labels.append(ligne[0])
                self.donnees[ligne[0]] = ligne[1]

        except IOError as e:
            Outils.fatal(e, "impossible d'ouvrir le fichier : "+self.nom_fichier)
