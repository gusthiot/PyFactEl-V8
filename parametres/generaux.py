from outils import Outils
from erreurs import ErreurConsistance
from collections import namedtuple

_champs_article = ["code_d", "code_sap", "quantite", "unite", "type_prix", "type_rabais", "texte_sap", "intitule_long",
                   "intitule_court"]
Article = namedtuple("Article", _champs_article)


class Generaux(object):
    """
    Classe pour l'importation des paramètres généraux
    """

    nom_fichier = "paramgen.csv"
    libelle = "Paramètres Généraux"
    cles_obligatoires = ['centre', 'code_cfact_centre', 'origine', 'code_int', 'code_ext', 'commerciale', 'canal',
                         'secteur', 'devise', 'financier', 'fonds', 'entete', 'poste_reservation', 'lien', 'chemin',
                         'chemin_propre', 'chemin_filigrane', 'code_t', 'code_n', 'intitule_n', 'code_ref_fact',
                         'avantage_HC', 'subsides', 'rabais_excep', 'filtrer_article_nul', 'code_d', 'code_sap',
                         'quantite', 'unite', 'type_prix', 'type_rabais', 'texte_sap', 'intitule_long',
                         'intitule_court', 'modes', 'min_fact_rese']
    cles_autorisees = cles_obligatoires + ['code_sap_qas']

    def __init__(self, dossier_source, prod2qual=None):
        """
        initialisation et importation des données

        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param prod2qual: Une instance de la classe Prod2Qual si on souhaite éditer
                          des factures et annexes avec les codes d'articles de
                          qualification
        """
        self._donnees = {}
        self.verifie_coherence = 0
        try:
            for ligne in dossier_source.reader(self.nom_fichier):
                cle = ligne.pop(0)
                if cle not in self.cles_autorisees:
                    Outils.fatal(ErreurConsistance(),
                                 "Clé inconnue dans %s: %s" % (self.nom_fichier, cle))
                if cle != "texte_sap":
                    while ligne[-1] == "":
                        del ligne[-1]
                self._donnees[cle] = ligne
        except IOError as e:
            Outils.fatal(e, "impossible d'ouvrir le fichier : "+self.nom_fichier)
        if prod2qual and 'code_sap_qas' in self._donnees:
            self._donnees['code_sap'] = self._donnees['code_sap_qas']

        erreurs = ""
        for cle in self.cles_obligatoires:
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
        self._donnees['entete'][1], err = Outils.est_un_texte(self._donnees['entete'][1], "l'entête", vide=True)
        erreurs += err
        self._donnees['poste_reservation'][1], err = Outils.est_un_entier(self._donnees['poste_reservation'][1],
                                                                          "le poste réservation", min=1, max=9)
        erreurs += err
        self._donnees['lien'][1], err = Outils.est_un_chemin(self._donnees['lien'][1], "le lien")
        erreurs += err
        self._donnees['chemin'][1], err = Outils.est_un_chemin(self._donnees['chemin'][1], "le chemin")
        erreurs += err
        self._donnees['chemin_propre'][1], err = Outils.est_un_chemin(self._donnees['chemin_propre'][1],
                                                                      "le chemin propre")
        erreurs += err
        self._donnees['chemin_filigrane'][1], err = Outils.est_un_chemin(self._donnees['chemin_filigrane'][1],
                                                                         "le chemin filigrane")
        erreurs += err
        for intitule in self._donnees['intitule_n'][1:]:
            intitule, err = Outils.est_un_texte(intitule, "l'intitulé N")
            erreurs += err
        for code_s in self._donnees['code_sap'][1:]:
            code_s, err = Outils.est_un_entier(code_s, "le code sap", min=1)
            erreurs += err
        for code_sq in self._donnees['code_sap_qas'][1:]:
            code_sq, err = Outils.est_un_entier(code_sq, "le code sap qas", min=1)
            erreurs += err
        for quantite in self._donnees['quantite'][1:]:
            quantite, err = Outils.est_un_nombre(quantite, "la quantité", arrondi=3, min=0)
            erreurs += err
        for unite in self._donnees['unite'][1:]:
            unite, err = Outils.est_un_texte(unite, "l'unité")
            erreurs += err
        for type_prix in self._donnees['type_prix'][1:]:
            type_prix, err = Outils.est_un_alphanumerique(type_prix, "le type de prix")
            erreurs += err
        for type_rabais in self._donnees['type_rabais'][1:]:
            type_rabais, err = Outils.est_un_alphanumerique(type_rabais, "le type de rabais")
            erreurs += err
        for texte_sap in self._donnees['texte_sap'][1:]:
            texte_sap, err = Outils.est_un_texte(texte_sap, "le texte sap", vide=True)
            erreurs += err
        for intitule_long in self._donnees['intitule_long'][1:]:
            intitule_long, err = Outils.est_un_texte(intitule_long, "l'intitulé long")
            erreurs += err
        for intitule_court in self._donnees['intitule_court'][1:]:
            intitule_court, err = Outils.est_un_texte(intitule_court, "l'intitulé court")
            erreurs += err
        for modes in self._donnees['modes'][1:]:
            modes, err = Outils.est_un_alphanumerique(modes, "le mode d'envoi", vide=True)
            erreurs += err
        self._donnees['min_fact_rese'][1], err = Outils.est_un_nombre(
            self._donnees['min_fact_rese'][1], "le montant minimum pour des frais de facturation", arrondi=2, min=0)
        erreurs += err

        codes_n = []
        for nn in self._donnees['code_n'][1:]:
            nn, err = Outils.est_un_alphanumerique(nn, "le code N")
            erreurs += err
            if nn not in codes_n:
                codes_n.append(nn)
            else:
                erreurs += "le code N '" + nn + "' n'est pas unique\n"
        codes_d = []
        for dd in self._donnees['code_d'][1:]:
            dd, err = Outils.est_un_alphanumerique(dd, "le code D")
            erreurs += err
            if dd not in codes_d:
                codes_d.append(dd)
            else:
                erreurs += "le code D '" + dd + "' n'est pas unique\n"

        len_ok = True
        if len(self._donnees['code_n']) != len(self._donnees['intitule_n']) or \
                len(self._donnees['code_n']) != len(self._donnees['code_ref_fact']) or \
                len(self._donnees['code_n']) != len(self._donnees['avantage_HC']) or \
                len(self._donnees['code_n']) != len(self._donnees['subsides']) or \
                len(self._donnees['code_n']) != len(self._donnees['rabais_excep']) or \
                len(self._donnees['code_n']) != len(self._donnees['filtrer_article_nul']):
            len_ok = False
            erreurs += "le nombre de colonees doit être le même pour le code N, l'intitulé N, " \
                       "le code référence du client, l'avantage HC, le mode subsides, le mode rabais exceptionnel et " \
                       "le filtre articles nuls\n"

        if len_ok:
            for i in range(1, len(self._donnees['code_n'])):
                if self._donnees['code_ref_fact'][i] != 'INT' and self._donnees['code_ref_fact'][i] != 'EXT':
                    erreurs += "le code référence client doit être INT ou EXT\n"
                if self._donnees['avantage_HC'][i] != 'BONUS' and self._donnees['avantage_HC'][i] != 'RABAIS':
                    erreurs += "l'avantage HC doit être BONUS ou RABAIS\n"
                if self._donnees['subsides'][i] != 'BONUS' and self._donnees['subsides'][i] != 'RABAIS':
                    erreurs += "le mode subsides doit être BONUS ou RABAIS\n"
                if self._donnees['rabais_excep'][i] != 'BONUS' and self._donnees['rabais_excep'][i] != 'RABAIS':
                    erreurs += "le mode rabais exceptionnel doit être BONUS ou RABAIS\n"
                if self._donnees['filtrer_article_nul'][i] != 'OUI' and self._donnees['filtrer_article_nul'][i] != 'NON':
                    erreurs += "le filtre articles nuls doit être OUI ou NON\n"

        if len(self._donnees['code_d']) != len(self._donnees['code_sap']) or \
                len(self._donnees['code_d']) != len(self._donnees['quantite']) or \
                len(self._donnees['code_d']) != len(self._donnees['unite']) or \
                len(self._donnees['code_d']) != len(self._donnees['type_prix']) or \
                len(self._donnees['code_d']) != len(self._donnees['intitule_long']) or \
                len(self._donnees['code_d']) != len(self._donnees['intitule_court']) or \
                len(self._donnees['code_d']) != len(self._donnees['type_rabais']) or \
                len(self._donnees['code_d']) != len(self._donnees['texte_sap']):
            erreurs += "le nombre de colonnes doit être le même pour le code D, le code SAP, la quantité, l'unité, " \
                       "le type de prix, le type de rabais, le texte SAP, l'intitulé long et l'intitulé court\n"

        if len(self._donnees['centre'][1]) > 70:
            erreurs += "le string du paramètre centre est trop long"

        if erreurs != "":
            Outils.fatal(ErreurConsistance(), self.libelle + "\n" + erreurs)

    def est_coherent(self, clients):
        """
        vérifie que les données du fichier importé sont cohérentes
        :param clients: clients importés
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        self.verifie_coherence = 1
        if self._donnees['code_cfact_centre'][1] == "":
            Outils.affiche_message(self.libelle + "\n" + "le code client du centre de facturation ne peut être vide\n")
            return 1
        elif self._donnees['code_cfact_centre'][1] not in clients.donnees:
            Outils.affiche_message(self.libelle + "\n" + "le code client du centre de facturation " +
                                   self._donnees['code_cfact_centre'][1] + " n'est pas référencé\n")
            return 1
        return 0

    def obtenir_code_n(self):
        """
        retourne les codes N
        :return: codes N
        """
        return self._donnees['code_n'][1:]

    def obtenir_code_d(self):
        """
        retourne les codes D
        :return: codes D
        """
        return self._donnees['code_d'][1:]

    def obtenir_modes_envoi(self):
        """
        retourne les modes d'envoi
        :return: modes d'envoi
        """
        return self._donnees['modes'][1:]

    @property
    def articles(self):
        """renvoie la liste des articles de facturation.

        Le premier (frais de réservation) s'appelle "D1"; le second (coûts procédés machines)
        s'appellent "D2"; les suivants (en nombre variable) s'appellent "D3".

        :return: une liste ordonnée d'objets Article
        """
        if not hasattr(self, "_articles"):
            self._articles = []
            for i in range(1, len(self._donnees['code_d'])):
                kw = dict((k, self._donnees[k][i]) for k in _champs_article)
                self._articles.append(Article(**kw))
        return self._articles

    @property
    def article_d1(self):
        """
        retourne uniquement l'article D1

        :return: un objet Article
        """
        return self.articles[0]

    @property
    def article_d2(self):
        """
        retourne uniquement l'article D2

        :return: un objet Article
        """
        return self.articles[1]

    @property
    def articles_d3(self):
        """
        retourne uniquement les articles D3

        :return: une liste ordonnée d'objets Article
        """
        return self.articles[2:]

    def codes_d3(self):
        return [a.code_d for a in self.articles_d3]

    def code_ref_par_code_n(self, code_n):
        return self._donnees['code_ref_fact'][
            self._donnees['code_n'].index(code_n)]

    def avantage_hc_par_code_n(self, code_n):
        return self._donnees['avantage_HC'][
            self._donnees['code_n'].index(code_n)]

    def subsides_par_code_n(self, code_n):
        return self._donnees['subsides'][
            self._donnees['code_n'].index(code_n)]

    def rabais_excep_par_code_n(self, code_n):
        return self._donnees['rabais_excep'][
            self._donnees['code_n'].index(code_n)]

    def intitule_n_par_code_n(self, code_n):
        return self._donnees['intitule_n'][
            self._donnees['code_n'].index(code_n)]

    def filtrer_article_nul_par_code_n(self, code_n):
        return self._donnees['filtrer_article_nul'][
            self._donnees['code_n'].index(code_n)]

    def intitule_long_par_code_d(self, code_d):
        return self._donnees['intitule_long'][
            self._donnees['code_d'].index(code_d)]

    def code_sap_par_code_d(self, code_d):
        return self._donnees['code_sap'][
            self._donnees['code_d'].index(code_d)]


def ajoute_accesseur_pour_valeur_unique(cls, nom, cle_csv=None):
    if cle_csv is None:
        cle_csv = nom

    def accesseur(self):
        return self._donnees[cle_csv][1]
    setattr(cls, nom, property(accesseur))


ajoute_accesseur_pour_valeur_unique(Generaux, "centre_financier", "financier")

for champ_valeur_unique in ('fonds', 'entete', 'chemin', 'lien', 'min_fact_rese', 'devise', 'canal', 'secteur',
                            'origine', 'commerciale', 'poste_reservation', 'code_int', 'code_ext', 'code_t',
                            'centre', 'code_cfact_centre', 'chemin_propre', 'chemin_filigrane'):
    ajoute_accesseur_pour_valeur_unique(Generaux, champ_valeur_unique)
