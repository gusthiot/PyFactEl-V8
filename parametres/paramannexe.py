from outils import Outils
from erreurs import ErreurConsistance


class Paramannexe(object):
    """
    Classe pour la répartition des annexes
    """

    nom_fichier = "paramannex.csv"
    cles = ['nom', 'int', 'ext_postal', 'ext_mail']
    libelle = "Paramètres Annexes"

    dossiers_annexes = {'Annexe-client': "1_Annexes-clients", 'Annexe-projets': "2_Annexes-projets",
                        'Annexe-détails': "3_Annexes-détails", 'Annexe-pièces': "4_Annexes-pièces",
                        'Annexe-interne': "5_Annexes-internes"}

    def __init__(self, dossier_source):
        """
        initialisation et importation des données

        :param dossier_source: Une instance de la classe dossier.DossierSource
        """
        self._chemin = dossier_source.chemin
        try:
            fichier_reader = dossier_source.reader(self.nom_fichier)
            donnees_csv = []
            for ligne in fichier_reader:
                donnees_ligne = self.extraction_ligne(ligne)
                if donnees_ligne == -1:
                    continue
                donnees_csv.append(donnees_ligne)
            self.donnees = donnees_csv
        except IOError as e:
            Outils.fatal(e, "impossible d'ouvrir le fichier : "+self.nom_fichier)
        del self.donnees[0]

        for donnee in self.donnees:
            if donnee['int'] != "" and donnee['int'] != 'X' and donnee['int'] != 'NO':
                Outils.fatal(ErreurConsistance(), self.libelle + ": donnée INT doit être X, NO ou vide ")
            if donnee['ext_postal'] != "" and donnee['ext_postal'] != 'X' and donnee['ext_postal'] != 'NO':
                Outils.fatal(ErreurConsistance(), self.libelle + ": donnée EXT & POSTAL doit être X, NO ou vide ")
            if donnee['ext_mail'] != "" and donnee['ext_mail'] != 'X' and donnee['ext_mail'] != 'NO':
                Outils.fatal(ErreurConsistance(), self.libelle + ": donnée EXT & MAIL doit être X, NO ou vide ")

            if donnee['nom'] in self.dossiers_annexes:
                donnee['dossier'] = self.dossiers_annexes[donnee['nom']]
            else:
                Outils.fatal(ErreurConsistance(),
                             self.libelle + ": nom non-attendu : " + donnee['nom'] + ", pas de nom de dossier ")

    def extraction_ligne(self, ligne):
        """
        extracte une ligne de données du csv
        :param ligne: ligne lue du fichier
        :return: tableau représentant la ligne, indexé par les clés
        """
        num = len(self.cles)
        if len(ligne) != num:
            Outils.fatal(ErreurConsistance(),
                         self.libelle + ": nombre de lignes incorrect : " + str(len(ligne)) + ", attendu : " + str(num))
        donnees_ligne = {}
        for xx in range(0, num):
            donnees_ligne[self.cles[xx]] = ligne[xx]

        return donnees_ligne
