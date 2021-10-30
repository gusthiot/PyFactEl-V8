from outils import Outils
from erreurs import ErreurConsistance


class Generaux(object):
    """
    Classe pour l'importation des paramètres généraux
    """

    nom_fichier = "paramgen.csv"
    libelle = "Paramètres Généraux"
    cles = ['centre', 'origine', 'code_int', 'code_ext', 'commerciale', 'canal', 'secteur', 'devise', 'financier',
            'fonds', 'poste_reservation', 'lien', 'chemin', 'chemin_filigrane', 'modes', 'min_fact_rese']

    def __init__(self, dossier_source):
        """
        initialisation et importation des données

        :param dossier_source: Une instance de la classe dossier.DossierSource
        """
        self._donnees = {}
        try:
            for ligne in dossier_source.reader(self.nom_fichier):
                cle = ligne.pop(0)
                if cle not in self.cles:
                    Outils.fatal(ErreurConsistance(),
                                 "Clé inconnue dans %s: %s" % (self.nom_fichier, cle))
                while ligne[-1] == "":
                    del ligne[-1]
                self._donnees[cle] = ligne
        except IOError as e:
            Outils.fatal(e, "impossible d'ouvrir le fichier : "+self.nom_fichier)

        erreurs = ""
        for cle in self.cles:
            if cle not in self._donnees:
                erreurs += "\nClé manquante dans %s: %s" % (self.nom_fichier, cle)

        self._donnees['centre'][1], err = Outils.est_un_texte(self._donnees['centre'][1], "le centre")
        erreurs += err
        self._donnees['origine'][1], err = Outils.est_un_alphanumerique(self._donnees['origine'][1], "l'origine")
        erreurs += err
        self._donnees['code_int'][1], err = Outils.est_un_alphanumerique(self._donnees['code_int'][1], "le code INT")
        erreurs += err
        self._donnees['code_ext'][1], err = Outils.est_un_alphanumerique(self._donnees['code_ext'][1], "le code EXT")
        erreurs += err
        self._donnees['commerciale'][1], err = Outils.est_un_alphanumerique(self._donnees['commerciale'][1], "le com.")
        erreurs += err
        self._donnees['canal'][1], err = Outils.est_un_alphanumerique(self._donnees['canal'][1], "le canal")
        erreurs += err
        self._donnees['secteur'][1], err = Outils.est_un_alphanumerique(self._donnees['secteur'][1], "le secteur")
        erreurs += err
        self._donnees['devise'][1], err = Outils.est_un_alphanumerique(self._donnees['devise'][1], "la devise")
        erreurs += err
        self._donnees['financier'][1], err = Outils.est_un_alphanumerique(self._donnees['financier'][1], "le financier")
        erreurs += err
        self._donnees['fonds'][1], err = Outils.est_un_alphanumerique(self._donnees['fonds'][1], "le fonds")
        erreurs += err
        self._donnees['poste_reservation'][1], err = Outils.est_un_entier(self._donnees['poste_reservation'][1],
                                                                          "le poste réservation", min=1, max=9)
        erreurs += err
        self._donnees['lien'][1], err = Outils.est_un_chemin(self._donnees['lien'][1], "le lien")
        erreurs += err
        self._donnees['chemin'][1], err = Outils.est_un_chemin(self._donnees['chemin'][1], "le chemin")
        erreurs += err
        self._donnees['chemin_filigrane'][1], err = Outils.est_un_chemin(self._donnees['chemin_filigrane'][1],
                                                                         "le chemin filigrane")
        erreurs += err

        for modes in self._donnees['modes'][1:]:
            modes, err = Outils.est_un_alphanumerique(modes, "le mode d'envoi", vide=True)
            erreurs += err
        self._donnees['min_fact_rese'][1], err = Outils.est_un_nombre(
            self._donnees['min_fact_rese'][1], "le montant minimum pour des frais de facturation", arrondi=2, min=0)
        erreurs += err

        if len(self._donnees['centre'][1]) > 70:
            erreurs += "le string du paramètre centre est trop long"

        if erreurs != "":
            Outils.fatal(ErreurConsistance(), self.libelle + "\n" + erreurs)

    def obtenir_modes_envoi(self):
        """
        retourne les modes d'envoi
        :return: modes d'envoi
        """
        return self._donnees['modes'][1:]


def ajoute_accesseur_pour_valeur_unique(cls, nom, cle_csv=None):
    if cle_csv is None:
        cle_csv = nom

    def accesseur(self):
        return self._donnees[cle_csv][1]
    setattr(cls, nom, property(accesseur))


ajoute_accesseur_pour_valeur_unique(Generaux, "centre_financier", "financier")

for champ_valeur_unique in ('fonds', 'chemin', 'lien', 'min_fact_rese', 'devise', 'canal', 'secteur', 'origine',
                            'commerciale', 'poste_reservation', 'code_int', 'code_ext', 'centre', 'chemin_filigrane'):
    ajoute_accesseur_pour_valeur_unique(Generaux, champ_valeur_unique)
