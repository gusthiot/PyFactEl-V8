from outils import Outils


class Detail(object):
    """
    Classe pour la création du détail des coûts
    """

    @staticmethod
    def detail(dossier_destination, edition, lignes):
        """
        création du détail des coûts
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param edition: paramètres d'édition
        :param lignes: lignes de données du détail
        """

        nom = "detail_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + str(edition.version)
        if edition.version > 0:
            nom += "_" + str(edition.client_unique)
        nom += ".csv"

        with dossier_destination.writer(nom) as fichier_writer:

            ligne = ["Année", "Mois", "Code Client Facture", "Code Client SAP", "Abrev. Labo", "type client",
                     "nature client", "Id-Compte", "Numéro de compte", "Intitulé compte", "Code Type Compte", "code_d",
                     "Id-categorie", "Intitulé catégorie", "Durée machines (min)", "Durée main d'oeuvre (min)",
                     "-", "-", "-", "-", "intitule_court", "N. prestation", "Intitulé", "Montant", "Rabais",
                     "Catégorie Stock", "Affiliation"]
            fichier_writer.writerow(ligne)

            for ligne in lignes:
                fichier_writer.writerow(ligne)

    @staticmethod
    def creation_lignes(edition, sommes, clients, artsap, acces, livraisons, comptes, categories, classes):
        """
        génération des lignes de données du détail
        :param edition: paramètres d'édition
        :param sommes: sommes calculées
        :param clients: clients importés
        :param artsap: articles SAP importés
        :param acces: accès importés
        :param livraisons: livraisons importées
        :param comptes: comptes importés
        :param categories: catégories importées
        :param classes: classes clients importées
        :return: lignes de données du détail
        """
        if sommes.calculees == 0:
            info = "Vous devez d'abord faire toutes les sommes avant de pouvoir créer le détail des coûts"
            Outils.affiche_message(info)
            return None

        lignes = []

        for code_client in sorted(sommes.sommes_clients.keys()):
            client = clients.donnees[code_client]

            if code_client in sommes.sommes_comptes:
                sclo = sommes.sommes_comptes[code_client]
                comptes_utilises = Outils.comptes_in_somme(sclo, comptes)
                base_client = [edition.annee, edition.mois, code_client, client['code_sap'], client['abrev_labo'],
                               'U', classes.donnees[client['id_classe']]['code_n']]

                for id_compte, num_compte in sorted(comptes_utilises.items(), key=lambda x: x[1]):
                    compte = comptes.donnees[id_compte]
                    base_compte = base_client + [id_compte, num_compte, compte['intitule'], compte['type_subside']]

                    if code_client in acces.sommes and id_compte in acces.sommes[code_client]['categories']:
                        som_cats = acces.sommes[code_client]['categories'][id_compte]['machine']
                        for id_categorie, som_cat in sorted(som_cats.items()):
                            duree = som_cat['duree_hp'] + som_cat['duree_hc']
                            ligne = base_compte + ['M', id_categorie, categories.donnees[id_categorie]['intitule'],
                                                   duree, som_cat['mo'], 0, 0, 0, 0, "", "", "", "", "", "", ""]
                            lignes.append(ligne)

                    if code_client in livraisons.sommes and id_compte in livraisons.sommes[code_client]:
                        somme = livraisons.sommes[code_client][id_compte]

                        for id_article in artsap.ids_d3:
                            article = artsap.donnees[id_article]
                            if id_article in somme:
                                for no_prestation, sip in sorted(somme[id_article].items()):
                                    ligne = base_compte + [id_article, "", "", "", "", "", "", "", "",
                                                           article['intitule_court'], no_prestation, sip['nom'],
                                                           Outils.format_2_dec(sip['montantx']),
                                                           Outils.format_2_dec(sip['rabais']), "-", "-"]
                                    lignes.append(ligne)

        return lignes
