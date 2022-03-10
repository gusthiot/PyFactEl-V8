from latex import Latex
from outils import Outils
import os


class Facture(object):
    """
    Classe contenant les méthodes nécessaires à la génération des factures
    """

    def __init__(self, prod2qual=None):
        """
        Constructeur

        :param prod2qual: Une instance de la classe Prod2Qual
        """

        self.prod2qual = prod2qual

    def factures(self, sommes, destination, edition, generaux, clients, comptes, paramannexe, bilan_trs, artsap,
                 classes, paramtexte):
        """
        génère la facture sous forme de csv
        
        :param sommes: sommes calculées
        :param destination: Une instance de la classe dossier.DossierDestination
        :param edition: paramètres d'édition
        :param generaux: paramètres généraux
        :param clients: clients importés
        :param comptes: comptes importés
        :param paramannexe: paramètres d'annexe
        :param bilan_trs: bilans des transactions
        :param artsap: articles SAP importés
        :param classes: classes clients importés
        :param paramtexte: paramètres textuels
        :return: données du combolist et des sections
        """

        if sommes.calculees == 0:
            info = "Vous devez d'abord faire toutes les sommes avant de pouvoir créer la facture"
            Outils.affiche_message(info)
            return

        nom_facture = "facture_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + \
                      str(edition.version)
        if edition.version > 0:
            nom_facture += "_" + str(edition.client_unique)
        if self.prod2qual:
            nom_facture += "_qualite.csv"
        else:
            nom_facture += ".csv"

        combo_list = {}
        fichier_tab = []

        for code_client in sorted(sommes.sommes_clients.keys()):
            poste = 0
            scl = sommes.sommes_clients[code_client]
            client = clients.donnees[code_client]
            classe = classes.donnees[client['id_classe']]

            if scl['somme_t'] == 0:
                continue

            code_sap = client['code_sap']
            if self.prod2qual and not (self.prod2qual.code_client_existe(code_sap)):
                continue

            if classe['ref_fact'] == "INT":
                genre = generaux.code_int
            else:
                genre = generaux.code_ext
            ref_fact = classe['ref_fact']
            reference = ref_fact + str(edition.annee)[2:] + Outils.mois_string(edition.mois) + "." + code_client
            if edition.version > 0:
                reference += "-" + str(edition.version)

            filtre = classe['filtrer_article']

            pt = paramtexte.donnees
            if client['ref'] != "":
                your_ref = pt['your-ref'] + client['ref']
            else:
                your_ref = ""

            if self.prod2qual:
                code_sap_traduit = self.prod2qual.traduire_code_client(code_sap)
            else:
                code_sap_traduit = code_sap
            dico_contenu = {'code': code_client, 'abrev': client['abrev_labo'], 'nom2': client['nom2'],
                            'nom3': client['nom3'], 'ref': your_ref, 'ref_fact': reference}
            contenu_client = r'''<section id="%(code)s"><div id="entete"> %(code)s <br />
                %(abrev)s <br />
                %(nom2)s <br />
                %(nom3)s <br />
                </div><br />
                %(ref_fact)s <br /><br />
                ''' % dico_contenu

            contenu_client += r'''
                <div id="reference">%(ref)s</div>
                <table id="tableau">
                <tr>
                <td>Item </td><td> Date </td><td> Name </td><td> Description </td><td> Unit </td><td> Quantity </td>
                <td> Unit Price <br /> [CHF] </td><td> Discount </td><td> Net amount <br /> [CHF] </td>
                </tr>
                ''' % dico_contenu

            ligne = [poste, generaux.origine, genre, generaux.commerciale, generaux.canal, generaux.secteur, "", "",
                     code_sap_traduit, client['nom2'], client['nom3'], client['email'], code_sap_traduit,
                     code_sap_traduit, code_sap_traduit, generaux.devise, client['mode'], reference, "", "",
                     your_ref]
            for donnee in paramannexe.donnees:
                nom_annexe = donnee['nom'] + "_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + \
                             "_" + str(edition.version) + "_" + code_client + ".pdf"
                if ref_fact == "INT":
                    code = donnee['int']
                elif client['mode'] == "MAIL":
                    code = donnee['ext_mail']
                else:
                    code = donnee['ext_postal']
                if code != "NO":
                    ligne.append(donnee['lien'] + nom_annexe)
                    ligne.append(code)

            fichier_tab.append(ligne)

            op_centre = classe['code_n'] + str(edition.annee)[2:] + Outils.mois_string(edition.mois)

            if scl['rm'] > 0 and not (filtre == "OUI" and scl['r'] == 0):
                poste = generaux.poste_reservation
                article_d2 = artsap.donnees[artsap.id_d2]
                fichier_tab.append(self.ligne_facture(generaux, article_d2, poste, scl['rm'], scl['rr'], op_centre, "",
                                                      edition))
                contenu_client += self.ligne_tableau(article_d2, poste, scl['rm'], scl['rr'], "", edition)

            inc = 1

            if code_client in sommes.sommes_comptes:
                sclo = sommes.sommes_comptes[code_client]
                comptes_utilises = Outils.comptes_in_somme(sclo, comptes)

                for id_compte, num_compte in sorted(comptes_utilises.items(), key=lambda x: x[1]):
                    sco = sclo[id_compte]
                    compte = comptes.donnees[id_compte]
                    if sco['c1'] > 0 and not (filtre == "OUI" and sco['c2'] == 0):
                        poste = inc*10
                        article_d1 = artsap.donnees[artsap.id_d1]
                        if sco['somme_j_mm'] > 0 and not (filtre == "OUI" and sco['mj'] == 0):
                            fichier_tab.append(
                                self.ligne_facture(generaux, article_d1, poste,
                                                   sco['somme_j_mm'], sco['somme_j_mr'], op_centre,
                                                   compte['numero'] + " - " + compte['intitule'], edition)
                            )
                            contenu_client += self.ligne_tableau(
                                article_d1, poste, sco['somme_j_mm'], sco['somme_j_mr'],
                                compte['numero'] + " - " + compte['intitule'], edition
                            )
                            poste += 1

                        for id_article in artsap.ids_d3:
                            article = artsap.donnees[id_article]
                            if sco['sommes_cat_m'][id_article] > 0 and not (filtre == "OUI"
                                                                            and sco['tot_cat'][id_article] == 0):
                                fichier_tab.append(
                                    self.ligne_facture(generaux, article, poste, sco['sommes_cat_m'][id_article],
                                                       sco['sommes_cat_r'][id_article], op_centre,
                                                       compte['numero'] + " - " + compte['intitule'], edition)
                                )
                                contenu_client += self.ligne_tableau(
                                    article, poste, sco['sommes_cat_m'][id_article],
                                    sco['sommes_cat_r'][id_article], compte['numero'] + " - " + compte['intitule'],
                                    edition
                                )
                                poste += 1
                        inc += 1
            contenu_client += r'''
                <tr><td colspan="8" id="toright">Net amount [CHF] : </td><td id="toright">
                ''' + "%.2f" % scl['somme_t'] + r'''</td></tr>
                </table>
                '''
            contenu_client += r'''<table id="annexes"><tr>'''

            nom_projets = ""
            dossier_projets = ""
            chemin_projets = ""
            for donnee in paramannexe.donnees:
                nom = donnee['nom'] + "_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) \
                             + "_" + str(edition.version) + "_" + code_client
                nom_annexe = nom + ".pdf"
                dossier_annexe = "../" + donnee['dossier'] + "/" + nom_annexe
                chemin_annexe = donnee['chemin'] + "/" + nom_annexe
                if donnee['nom'] == 'Annexe-projets':
                    nom_projets = nom + ".csv"
                    dossier_projets = "../" + donnee['dossier'] + "/" + nom_projets
                    chemin_projets = donnee['chemin'] + "/" + nom_projets

                if not os.path.isfile(chemin_annexe):
                    continue

                contenu_client += r'''<td><a href="''' + dossier_annexe + r'''" target="new">''' + nom_annexe + r'''
                    </a></td>'''

            contenu_client += r'''</tr><tr>'''

            if nom_projets != "" and os.path.isfile(chemin_projets):
                contenu_client += r'''<td><a href="''' + dossier_projets + r'''" target="new">
                    ''' + nom_projets + r'''</a></td>'''

            nom_details = bilan_trs.ann_dets.prefixe + "_" + code_client + "_" + client['abrev_labo'] + ".csv"
            dossier_details = "../" + bilan_trs.ann_dets.dossier + "/" + nom_details
            chemin_details = bilan_trs.ann_dets.chemin + "/" + nom_details
            if os.path.isfile(chemin_details):
                contenu_client += r'''<td><a href="''' + dossier_details + r'''" target="new">
                    ''' + nom_details + r'''</a></td>'''

            nom_subsides = bilan_trs.ann_subs.prefixe + "_" + code_client + "_" + client['abrev_labo'] + ".csv"
            dossier_subsides = "../" + bilan_trs.ann_subs.dossier + "/" + nom_subsides
            chemin_subsides = bilan_trs.ann_subs.chemin + "/" + nom_subsides
            if os.path.isfile(chemin_subsides):
                contenu_client += r'''<td><a href="''' + dossier_subsides + r'''" target="new">
                    ''' + nom_subsides + r'''</a></td>'''

            contenu_client += r'''</tr></table>'''

            contenu_client += r'''</section>'''
            combo_list[client['abrev_labo'] + " (" + code_client + ")"] = contenu_client

        if len(fichier_tab) > 0:
            with destination.writer(nom_facture) as fichier_writer:
                fichier_writer.writerow(["Poste", "Système d'origine", "Type de document de vente",
                                         "Organisation commerciale", "Canal de distribution", "Secteur d'activité", "",
                                         "", "Client", "Nom 2 du client", "Nom 3 du client", "Adresse e-mail du client",
                                         "Client", "Client", "Client", "Devise", "Mode d'envoi",
                                         "Référence de la facture", "", "", "Texte d'entête",
                                         "Lien réseau vers l'annexe client .pdf", "Document interne",
                                         "Lien réseau vers l'annexe projets .pdf", "Document interne",
                                         "Lien réseau vers l'annexe détails .pdf", "Document interne",
                                         "Lien réseau vers l'annexe pièces .pdf", "Document interne",
                                         "Lien réseau vers l'annexe interne .pdf", "Document interne", "Article", "",
                                         "Quantité", "Unité de quantité", "Type de prix", "Prix net du poste",
                                         "Type de rabais", "Valeur rabais du poste", "Date de livraison",
                                         "Centre financier", "", "Fonds à créditer", "", "", "Code opération", "", "",
                                         "", "Texte libre du poste", "Nom"])
                for ligne in fichier_tab:
                    fichier_writer.writerow(ligne)
            self.creer_html(destination, combo_list, edition)
        return combo_list

    @staticmethod
    def ligne_tableau(article, poste, net, rabais, consommateur, edition):
        """
        retourne une ligne de tableau html

        :param article: Une instance de la classe ArticleSap
        :param poste: indice de poste
        :param net: montant net
        :param rabais: rabais sur le montant
        :param consommateur: consommateur
        :param edition: paramètres d'édition
        :return: ligne de tableau html
        """
        montant = net - rabais
        date_livraison = str(edition.dernier_jour) + "." + Outils.mois_string(edition.mois) + "." + str(edition.annee)
        description = article['code_d'] + " : " + str(article['code_sap'])
        dico_tab = {'poste': poste, 'date': date_livraison, 'descr': description,
                    'texte': article['texte_sap'], 'nom': Latex.echappe_caracteres(consommateur),
                    'unit': article['unite'], 'quantity': article['quantite'],
                    'unit_p': "%.2f" % net, 'discount': "%.2f" % rabais, 'net': "%.2f" % montant}
        ligne = r'''<tr>
            <td> %(poste)s </td><td> %(date)s </td><td> %(nom)s </td><td> %(descr)s <br /> %(texte)s </td>
            <td> %(unit)s </td><td id="toright"> %(quantity)s </td><td id="toright"> %(unit_p)s </td>
            <td id="toright"> %(discount)s </td><td id="toright"> %(net)s </td>
            </tr>
            ''' % dico_tab
        return ligne

    @staticmethod
    def ligne_facture(generaux, article, poste, net, rabais, op_centre, consommateur, edition):
        """
        retourne une ligne de facturation formatée

        :param generaux: paramètres généraux
        :param article: Une instance de la classe ArticleSap
        :param poste: indice de poste
        :param net: montant net
        :param rabais: rabais sur le montant
        :param op_centre: centre d'opération
        :param consommateur: consommateur
        :param edition: paramètres d'édition
        :return: ligne de facturation formatée
        """
        net = "%.2f" % net
        rabais = "%.2f" % rabais
        if rabais == 0:
            rabais = ""
        code_op = 'U' + op_centre + article['code_d']
        date_livraison = str(edition.annee) + Outils.mois_string(edition.mois) + str(edition.dernier_jour)

        return [poste, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "", article['code_sap'], "", article['quantite'],
                article['unite'], article['type_prix'], net,
                article['type_rabais'], rabais, date_livraison, generaux.centre_financier, "",
                generaux.fonds, "", "", code_op, "", "", "", article['texte_sap'],
                Latex.echappe_caracteres(consommateur)]

    def creer_html(self, destination, combo_list, edition):
        """
        crée une page html autour d'une liste de sections
        
        :param destination:  Une instance de la classe dossier.DossierDestination
        :param combo_list: liste des clients et leurs sections
        :param edition: paramètres d'édition
        """

        nom = "ticket_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + \
              str(edition.version)
        if edition.version > 0:
            nom += "_" + str(edition.client_unique)
        if self.prod2qual:
            nom += "_qualite.html"
        else:
            nom += ".html"
        with destination.open(nom) as fichier:

            html = r'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
                "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
                <html xmlns="http://www.w3.org/1999/xhtml">
                <head>
                <meta content="text/html; charset=cp1252" http-equiv="content-type" />
                <meta content="EPFL" name="author" />
                <style>
                #entete {
                    margin-left: 600px;
                    text-align:left;
                }
                #tableau {
                    border-collapse: collapse;
                    margin: 20px;
                }
                #tableau tr, #tableau td {
                    border: 1px solid black;
                    vertical-align:middle;
                }
                #tableau td {
                    padding: 3px;
                }
                #annexes tr, #annexes td {
                    border: 0px;
                }
                #annexes td {
                    padding: 3px;
                }
                #toright {
                    text-align:right;
                }
                #combo {
                    margin-top: 10px;
                    margin-left: 50px;
                }
                #reference {
                    text-align:left;
                    margin-left: 20px;
                }
                </style>
                <link rel="stylesheet" href="../css/reveal.css">
                <link rel="stylesheet" href="../css/white.css">
                </head>
                <body>
                <div id="combo">
                <select name="client" onchange="changeClient(this)">
                '''
            i = 0
            for k, v in sorted(combo_list.items()):
                html += r'''<option value="''' + str(i) + r'''">''' + str(k) + r'''</option>'''
                i += 1
            html += r'''
                </select>
                </div>
                <div class="reveal">
                <div class="slides">
                '''
            for k, v in sorted(combo_list.items()):
                html += v
            html += r'''</div></div>
                    <script src="../js/reveal.js"></script>
                    <script>
                        Reveal.initialize();
                    </script>
                    <script>
                    function changeClient(sel) {
                        Reveal.slide(sel.value, 0);
                    }
                    </script>
                    </body>
                </html>'''
            fichier.write(html)
