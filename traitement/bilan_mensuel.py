from outils import Outils


class BilanMensuel(object):
    """
    Classe pour la création du bilan mensuel
    """

    @staticmethod
    def bilan(dossier_destination, edition, artsap, lignes):
        """
        création du bilan
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param edition: paramètres d'édition
        :param artsap: articles SAP importés
        :param lignes: lignes de données du bilan
        """

        nom = "bilan_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + str(edition.version)
        if edition.version > 0:
            nom += "_" + str(edition.client_unique)
        nom += ".csv"

        with dossier_destination.writer(nom) as fichier_writer:

            ligne = ["année", "mois", "référence", "code client", "code client sap", "abrév. labo", "type client",
                     "nature client", "", "", "", "", "-", "-", "DHt", "", "Rt", "Mt"]
            for id_article in artsap.ids_d3:
                article = artsap.donnees[id_article]
                ligne.append(article['code_d'] + "t")
            ligne += ["total facturé HT", "Bonus Ht"]
            fichier_writer.writerow(ligne)

            for ligne in lignes:
                fichier_writer.writerow(ligne)

    @staticmethod
    def creation_lignes(edition, sommes, clients, artsap, classes):
        """
        génération des lignes de données du bilan
        :param edition: paramètres d'édition
        :param sommes: sommes calculées
        :param clients: clients importés
        :param artsap: articles SAP importés
        :param classes: classes clients importées
        :return: lignes de données du bilan
        """
        if sommes.calculees == 0:
            info = "Vous devez d'abord faire toutes les sommes avant de pouvoir créer le bilan mensuel"
            Outils.affiche_message(info)
            return None

        lignes = []

        for code_client in sorted(sommes.sommes_clients.keys()):
            scl = sommes.sommes_clients[code_client]
            client = clients.donnees[code_client]
            classe = classes.donnees[client['id_classe']]
            ref_fact = classe['ref_fact']
            reference = ref_fact + str(edition.annee)[2:] + Outils.mois_string(edition.mois) + "." + code_client
            if edition.version > 0:
                reference += "-" + str(edition.version)
            rht = client['rh'] * scl['dht']

            ligne = [edition.annee, edition.mois, reference, code_client, client['code_sap'], client['abrev_labo'], 'U',
                     classe['code_n'], 0, 0, 0, 0, 0, 0, Outils.format_2_dec(rht), 0, Outils.format_2_dec(scl['r']),
                     Outils.format_2_dec(scl['mt'])]
            for id_article in artsap.ids_d3:
                ligne.append(Outils.format_2_dec(scl['tot_cat'][id_article]))
            ligne += [Outils.format_2_dec(scl['somme_t']), Outils.format_2_dec(scl['somme_t_mb'])]
            lignes.append(ligne)
        return lignes
