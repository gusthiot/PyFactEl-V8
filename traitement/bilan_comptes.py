from outils import Outils


class BilanComptes(object):
    """
    Classe pour la création du bilan des comptes
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

        nom = "bilan-comptes_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + \
              str(edition.version)
        if edition.version > 0:
            nom += "_" + str(edition.client_unique)
        nom += ".csv"

        with dossier_destination.writer(nom) as fichier_writer:

            ligne = ["année", "mois", "référence", "code client", "code client sap", "abrév. labo", "type client",
                     "nature client", "id-compte", "numéro compte", "intitulé compte", "code type compte", "-", "-",
                     "rabais", "mj"]
            for id_article in artsap.ids_d3:
                article = artsap.donnees[id_article]
                ligne.append(article['code_d'] + "j")
            ligne += ["somme-j", "bonus"]
            fichier_writer.writerow(ligne)

            for ligne in lignes:
                fichier_writer.writerow(ligne)

    @staticmethod
    def creation_lignes(edition, sommes, clients, comptes, artsap, classes):
        """
        génération des lignes de données du bilan
        :param edition: paramètres d'édition
        :param sommes: sommes calculées
        :param clients: clients importés
        :param comptes: comptes importés
        :param artsap: articles SAP importés
        :param classes: classes clients importées
        :return: lignes de données du bilan
        """
        if sommes.calculees == 0:
            info = "Vous devez d'abord faire toutes les sommes avant de pouvoir créer le bilan des comptes"
            Outils.affiche_message(info)
            return None

        lignes = []
        for code_client in sorted(sommes.sommes_clients.keys()):
            if code_client in sommes.sommes_comptes:
                client = clients.donnees[code_client]
                classe = classes.donnees[client['id_classe']]
                ref_fact = classe['ref_fact']
                reference = ref_fact + str(edition.annee)[2:] + Outils.mois_string(edition.mois) + "." + code_client
                if edition.version > 0:
                    reference += "-" + str(edition.version)

                comptes_utilises = Outils.comptes_in_somme(sommes.sommes_comptes[code_client], comptes)
                for id_compte, num_compte in sorted(comptes_utilises.items(), key=lambda x: x[1]):
                    compte = comptes.donnees[id_compte]
                    sco = sommes.sommes_comptes[code_client][id_compte]
                    ligne = [edition.annee, edition.mois, reference, code_client, client['code_sap'],
                             client['abrev_labo'], 'U', classe['code_n'], id_compte, num_compte, compte['intitule'],
                             compte['type_subside'], 0, 0, Outils.format_2_dec(client['rh'] * sco['somme_j_dhi']),
                             Outils.format_2_dec(sco['mj'])]
                    total = sco['mj']
                    for id_article in artsap.ids_d3:
                        total += sco['tot_cat'][id_article]
                        ligne.append(Outils.format_2_dec(sco['tot_cat'][id_article]))
                    ligne += [Outils.format_2_dec(total), Outils.format_2_dec(client['bh'] * sco['somme_j_dhi'])]
                    lignes.append(ligne)
        return lignes
