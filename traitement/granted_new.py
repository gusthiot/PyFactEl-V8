from outils import Outils
from traitement import Resumes


class GrantedNew(object):
    """
    Classe pour la création du listing des montants de subsides comptabilisés
    """

    cles = ['id_compte', 'id_plateforme', 'id_article', 'montant']
    noms = ['Id-Compte', 'Id-Plateforme', 'Id-ArticleSAP', 'Montant comptabilisé']

    def __init__(self, edition):
        """
        initialisation des données et stockage des paramètres d'édition
        :param edition: paramètres d'édition
        """
        self.nom = "granted_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + ".csv"
        self.valeurs = {}
        self.edition = edition

    def generer(self, grants, transactions):
        """
        génération des nouveaux fichiers de subventions consommées
        :param grants: grants importés
        :param transactions: transactions générées
        """

        for key in grants.donnees.keys():
            self.valeurs[key] = grants.donnees[key].copy()

        for key in transactions.comptabilises.keys():
            if key in self.valeurs.keys():
                self.valeurs[key]['montant'] = self.valeurs[key]['montant'] + transactions.comptabilises[key]['montant']
            else:
                self.valeurs[key] = transactions.comptabilises[key].copy()

    def csv(self, dossier_destination):
        """
        création du fichier csv
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        """
        with dossier_destination.writer(self.nom) as fichier_writer:
            ligne = []
            for nom in self.noms:
                ligne.append(nom)
            fichier_writer.writerow(ligne)

            for key in self.valeurs.keys():
                valeur = self.valeurs[key]
                ligne = []
                for i in range(0, len(self.cles)):
                    ligne.append(valeur[self.cles[i]])
                fichier_writer.writerow(ligne)

    def mise_a_jour(self, dossier_source, dossier_destination, maj_grants, comptes):
        """
        modification des résumés mensuels au niveau du client dont la facture est modifiée
        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param maj_grants: données modifiées pour le client pour les grants
        :param comptes: comptes importés
        """
        fichier_grant = "granted_" + str(self.edition.annee) + "_" + Outils.mois_string(self.edition.mois) + ".csv"
        donnees_csv = Resumes.ouvrir_csv_sans_comptes_client(dossier_source, fichier_grant, self.edition.client_unique,
                                                             comptes)
        with dossier_destination.writer(fichier_grant) as fichier_writer:
            for ligne in donnees_csv:
                fichier_writer.writerow(ligne)
            for key in maj_grants.valeurs.keys():
                valeur = maj_grants.valeurs[key]
                if comptes.donnees[valeur['id_compte']]['code_client'] == self.edition.client_unique:
                    ligne = []
                    for i in range(0, len(self.cles)):
                        ligne.append(valeur[self.cles[i]])
                    fichier_writer.writerow(ligne)
