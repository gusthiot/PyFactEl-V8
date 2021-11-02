from outils import Outils
from latex import Latex
from .tables_annexes import TablesAnnexes
from .recaprojet import RecaProjet
import os


class Annexes(object):
    """
    Classe pour la création des annexes
    """
    @staticmethod
    def annexes(sommes, clients, edition, livraisons, acces, machines, comptes, paramannexe, generaux,
                users, categories, noshows, docpdf, groupes, artsap, classes):
        """
        création des annexes
        :param sommes: sommes calculées
        :param clients: clients importés
        :param edition: paramètres d'édition
        :param livraisons: livraisons importées
        :param acces: accès importés
        :param machines: machines importées
        :param comptes: comptes importés
        :param paramannexe: paramètres d'annexe
        :param generaux: paramètres généraux
        :param users: users importés
        :param categories: catégories importées
        :param noshows: no show importés
        :param docpdf: paramètres d'ajout de document pdf
        :param groupes: groupes importés
        :param artsap: articles SAP importés
        :param classes: classes clients importées
        """

        if sommes.calculees == 0:
            info = "Vous devez d'abord faire toutes les sommes avant de pouvoir créer les annexes"
            Outils.affiche_message(info)
            return

        for code_client, scl in sommes.sommes_clients.items():
            code_client = Latex.echappe_caracteres(code_client)
            client = clients.donnees[code_client]
            ref_fact = Latex.echappe_caracteres(classes.donnees[client['id_classe']]['ref_fact'])
            av_hc = Latex.echappe_caracteres(classes.donnees[client['id_classe']]['avantage_HC'])
            reference = ref_fact + str(edition.annee)[2:] + Outils.mois_string(edition.mois) + "." + code_client
            if edition.version > 0:
                reference += "-" + str(edition.version)

            filtre = classes.donnees[client['id_classe']]['filtrer_article']

            contenu_prix_xaj = ""
            contenu_prix_xf = ""
            inc_fact = 1

            contenu_prix_lvr_xdj_tab = {}
            for id_article in artsap.ids_d3:
                contenu_prix_lvr_xdj_tab[id_article] = ""

            contenu_projets = ""
            contenu_details = ""

            todo = {}
            for donnee in paramannexe.donnees:
                if classes.donnees[client['id_classe']]['ref_fact'] == "INT":
                    todo[donnee['nom']] = donnee['int']
                elif client['mode'] == "MAIL":
                    todo[donnee['nom']] = donnee['ext_mail']
                else:
                    todo[donnee['nom']] = donnee['ext_postal']

            if code_client in sommes.sommes_comptes:
                comptes_utilises = Outils.comptes_in_somme(sommes.sommes_comptes[code_client], comptes)

                for id_compte, num_compte in sorted(comptes_utilises.items(), key=lambda x: x[1]):
                    id_compte = Latex.echappe_caracteres(id_compte)

                    # ## COMPTE

                    sco = sommes.sommes_comptes[code_client][id_compte]
                    compte = comptes.donnees[id_compte]
                    intitule_compte = Latex.echappe_caracteres(compte['numero'] + " - " + compte['intitule'])

                    # ## ligne Prix XF - Table Client Récap Postes de la facture

                    if sco['c1'] > 0 and not (filtre == "OUI" and sco['c2'] == 0):
                        poste = inc_fact * 10
                        intitule = Latex.echappe_caracteres(intitule_compte + " - " +
                                                            artsap.donnees[artsap.id_d1]['intitule_long'])

                        if sco['somme_j_mm'] > 0 and not (filtre == "OUI" and sco['mj'] == 0):
                            dico_prix_xf = {'intitule': intitule, 'poste': str(poste),
                                            'mm': Outils.format_2_dec(sco['somme_j_mm']),
                                            'mr': Outils.format_2_dec(sco['somme_j_mr']),
                                            'mj': Outils.format_2_dec(sco['mj'])}
                            contenu_prix_xf += r'''
                                %(poste)s & %(intitule)s & %(mm)s  & %(mr)s & %(mj)s \\
                                \hline
                                ''' % dico_prix_xf
                            poste += 1

                        for id_article in artsap.ids_d3:
                            if sco['sommes_cat_m'][id_article] > 0 and not (filtre == "OUI"
                                                                            and sco['tot_cat'][id_article] == 0):
                                intitule = Latex.echappe_caracteres(intitule_compte + " - " +
                                                                    artsap.donnees[id_article]['intitule_long'])
                                dico_prix_xf = {'intitule': intitule, 'poste': str(poste),
                                                'mm': Outils.format_2_dec(sco['sommes_cat_m'][id_article]),
                                                'mr': Outils.format_2_dec(sco['sommes_cat_r'][id_article]),
                                                'mj': Outils.format_2_dec(sco['tot_cat'][id_article])}
                                contenu_prix_xf += r'''
                                    %(poste)s & %(intitule)s & %(mm)s  & %(mr)s & %(mj)s \\
                                    \hline
                                    ''' % dico_prix_xf
                                poste += 1

                        inc_fact += 1

                    # ## ligne Prix XA/J - Table Client Récap Articles/Compte

                    total = sco['mj']
                    dico_prix_xaj = {'compte': intitule_compte,
                                     'type': Latex.echappe_caracteres(compte['type_subside']),
                                     'procede': Outils.format_2_dec(sco['mj'])}

                    ligne = r'''%(compte)s & %(type)s & %(procede)s ''' % dico_prix_xaj

                    for id_article in artsap.ids_d3:
                        total += sco['tot_cat'][id_article]
                        ligne += r''' & ''' + Outils.format_2_dec(sco['tot_cat'][id_article])

                    if total > 0:
                        dico_prix_xaj['total'] = Outils.format_2_dec(total)
                        ligne += r'''& %(total)s \\
                            \hline
                            ''' % dico_prix_xaj
                        contenu_prix_xaj += ligne

                    # ## ligne Prix LVR X/D/J - Table Client Récap Prestations livr./code D/Compte

                    if code_client in livraisons.sommes and id_compte in livraisons.sommes[code_client]:
                        for id_article in artsap.ids_d3:
                            if id_article in livraisons.sommes[code_client][id_compte]:
                                article = artsap.donnees[id_article]
                                if contenu_prix_lvr_xdj_tab[id_article] == "":
                                    contenu_prix_lvr_xdj_tab[id_article] = r'''
                                        \cline{2-4}
                                        \multicolumn{1}{c}{} & \multicolumn{3}{|c|}{
                                        ''' + Latex.echappe_caracteres(article['intitule_long']) + r'''} \\
                                        \hline
                                        Compte & Montant & Rabais & Montant net \\
                                        \hline
                                        '''
                                dico_prest_client = {'intitule': intitule_compte,
                                                     'cmj': Outils.format_2_dec(sco['sommes_cat_m'][id_article]),
                                                     'crj': Outils.format_2_dec(sco['sommes_cat_r'][id_article]),
                                                     'cj': Outils.format_2_dec(sco['tot_cat'][id_article])}
                                contenu_prix_lvr_xdj_tab[id_article] += r'''
                                %(intitule)s & %(cmj)s & %(crj)s & %(cj)s \\
                                \hline
                                ''' % dico_prest_client

                    # ##

                    ann_pro_titre = "Récapitulatif du projet : " + intitule_compte
                    contenu_projets += Annexes.titre_annexe(client, edition, generaux, reference, ann_pro_titre,
                                                            "Annexe facture")
                    contenu_projets += Annexes.section(client, generaux, reference, ann_pro_titre)

                    contenu_projets += TablesAnnexes.table_prix_ja(sco, artsap)
                    contenu_projets += TablesAnnexes.table_prix_cae_jk(code_client, id_compte, intitule_compte, sco,
                                                                       acces.sommes, categories)
                    contenu_projets += TablesAnnexes.table_prix_lvr_jd(code_client, id_compte, intitule_compte, sco,
                                                                       livraisons.sommes, artsap)
                    if av_hc == "RABAIS":
                        contenu_projets += TablesAnnexes.table_prix_jdmu(code_client, id_compte, intitule_compte, sco,
                                                                         acces.sommes, machines, users, groupes)
                    contenu_projets += r'''\clearpage'''

                    ann_det_titre = "Annexe détaillée du projet : " + intitule_compte
                    contenu_details += Annexes.titre_annexe(client, edition, generaux, reference, ann_det_titre,
                                                            "Annexe facture")
                    contenu_details += Annexes.section(client, generaux, reference, ann_det_titre)
                    contenu_details += TablesAnnexes.table_tps_cae_jkmu(code_client, id_compte, intitule_compte, users,
                                                                        machines, categories, acces, groupes)
                    if code_client in livraisons.sommes and id_compte in livraisons.sommes[code_client]:
                        contenu_details += TablesAnnexes.table_qte_lvr_jdu(code_client, id_compte, intitule_compte,
                                                                           artsap, livraisons, users)
                    contenu_details += r'''\clearpage'''

                    # ## compte

            suffixe = "_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_"
            suffixe += str(edition.version) + "_" + code_client

            # ## Début des tableaux

            pdfs_annexes = {}

            if scl['somme_t'] > 0:
                if todo['Annexe-client'] != "NO":
                    contenu_annexe_client = Annexes.entete(edition)
                    contenu_annexe_client += Annexes.titre_annexe(client, edition, generaux, reference,
                                                                  "Récapitulatif pour le client", "Annexe facture")
                    contenu_annexe_client += Annexes.section(client, generaux, reference,
                                                             "Récapitulatif pour le client")

                    contenu_annexe_client += TablesAnnexes.table_prix_xf(scl, generaux, filtre, contenu_prix_xf, artsap)
                    contenu_annexe_client += TablesAnnexes.table_prix_xaj(scl, artsap, contenu_prix_xaj)
                    if av_hc == "BONUS":
                        contenu_annexe_client += TablesAnnexes.table_points_xbmu(code_client, scl, acces.sommes,
                                                                                 machines, users, groupes)
                    contenu_annexe_client += TablesAnnexes.table_prix_xrmu(code_client, scl, noshows.sommes,
                                                                           machines, users, groupes)
                    contenu_annexe_client += r'''\end{document}'''
                    Latex.creer_latex_pdf('Annexe-client' + suffixe, contenu_annexe_client)
                    pdfs_annexes['Annexe-client'] = ['Annexe-client' + suffixe + ".pdf"]

                if not contenu_projets == "" and todo['Annexe-projets'] != "NO":
                    contenu_annexe_projets = Annexes.entete(edition)
                    contenu_annexe_projets += contenu_projets
                    contenu_annexe_projets += r'''\end{document}'''
                    Latex.creer_latex_pdf('Annexe-projets' + suffixe, contenu_annexe_projets)
                    pdfs_annexes['Annexe-projets'] = ['Annexe-projets' + suffixe + ".pdf"]

                if todo['Annexe-détails'] != "NO":
                    contenu_details_2 = ""
                    if code_client in noshows.sommes:
                        contenu_details_2 += Annexes.titre_annexe(client, edition, generaux, reference,
                                                                  "Annexe détaillée des pénalités de réservation",
                                                                  "Annexe facture")
                        contenu_details_2 += Annexes.section(client, generaux, reference,
                                                             "Annexe détaillée des pénalités de réservation")
                        contenu_details_2 += TablesAnnexes.table_no_show_xmu(code_client, noshows, machines, users,
                                                                             groupes)
                    if not contenu_details == "" or not contenu_details_2 == "":
                        contenu_annexe_details = Annexes.entete(edition)
                        contenu_annexe_details += contenu_details
                        contenu_annexe_details += contenu_details_2
                        contenu_annexe_details += r'''\end{document}'''
                        Latex.creer_latex_pdf('Annexe-détails' + suffixe, contenu_annexe_details)
                        pdfs_annexes['Annexe-détails'] = ['Annexe-détails' + suffixe + ".pdf"]

                if docpdf is not None and todo['Annexe-pièces'] != "NO":
                    pdfs = docpdf.pdfs_pour_client(client, 'Annexe-pièces')
                    if pdfs is not None and len(pdfs) > 0:
                        nom_pdf = 'Annexe-pièces' + suffixe
                        pieces = [nom_pdf + '.pdf']
                        texte = ""
                        for pos, docs in sorted(pdfs.items()):
                            for doc in docs:
                                texte += str(pos) + r''' \hspace*{5cm} 
                                    ''' + Latex.echappe_caracteres(doc['nom']) + r'''
                                     \\ 
                                    '''
                                pieces.append(doc['chemin'])
                        contenu_annexe_pieces = Annexes.entete(edition)
                        contenu_annexe_pieces += Annexes.titre_annexe(client, edition, generaux, reference,
                                                                      "Documents contractuels et informatifs",
                                                                      "Annexe facture")
                        contenu_annexe_pieces += Annexes.section(client, generaux, reference,
                                                                 "Documents contractuels et informatifs")
                        contenu_annexe_pieces += texte
                        contenu_annexe_pieces += r'''\end{document}'''
                        Latex.creer_latex_pdf(nom_pdf, contenu_annexe_pieces)
                        pdfs_annexes['Annexe-pièces'] = pieces

            if docpdf is not None and todo['Annexe-interne'] != "NO":
                pdfs = docpdf.pdfs_pour_client(client, 'Annexe-interne')
                if pdfs is not None and len(pdfs) > 0:
                    nom_pdf = 'Annexe-interne-anntemp'
                    pieces = [nom_pdf + '.pdf']
                    texte = ""
                    for pos, docs in sorted(pdfs.items()):
                        for doc in docs:
                            texte += str(pos) + r''' \hspace*{5cm} 
                                ''' + Latex.echappe_caracteres(doc['nom']) + r'''
                                 \\ 
                                '''
                            pieces.append(doc['chemin'])
                    contenu_annexe_interne_a = Annexes.entete(edition)
                    contenu_annexe_interne_a += Annexes.titre_annexe(client, edition, generaux, reference,
                                                                     "Documents contractuels et informatifs",
                                                                     "Annexe interne")
                    contenu_annexe_interne_a += Annexes.section(
                        client, generaux, reference, "Annexe interne / Documents contractuels et informatifs"
                    )
                    contenu_annexe_interne_a += texte
                    contenu_annexe_interne_a += r'''\end{document}'''
                    Latex.creer_latex_pdf(nom_pdf, contenu_annexe_interne_a)
                    pdfs_annexes['Annexe-interne'] = pieces

            for donnee in paramannexe.donnees:
                if donnee['nom'] in pdfs_annexes:
                    if len(pdfs_annexes[donnee['nom']]) > 1:
                        Latex.concatenation_pdfs(donnee['nom'] + suffixe, pdfs_annexes[donnee['nom']])
                    Latex.finaliser_pdf(donnee['nom'] + suffixe, donnee['chemin'])
                    if donnee['nom'] == 'Annexe-projets':
                        lignes = RecaProjet.creation_lignes(edition, sommes.sommes_comptes[code_client], client,
                                                            generaux, acces, livraisons, comptes, categories, artsap,
                                                            classes)
                        RecaProjet.recap(donnee['dossier_pdf'], donnee['nom'] + suffixe, lignes)

            files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for f in files:
                if f.endswith('anntemp.pdf'):
                    os.unlink(f)

    @staticmethod
    def titre_annexe(client, edition, generaux, reference, titre, annexe):
        """
        création d'un titre d'annexe
        :param client: données du client concerné
        :param edition: paramètres d'édition
        :param generaux: paramètres généraux
        :param reference: référence de la facture
        :param titre: titre de l'annexe
        :param annexe: nom de l'annexe
        :return: page de titre latex de l'annexe
        """
        dic_titre = {'code_sap': Latex.echappe_caracteres(client['code_sap']), 'ref': reference, 'titre': titre,
                     'nom': Latex.echappe_caracteres(client['abrev_labo']), 'annexe': annexe,
                     'date': edition.mois_txt + " " + str(edition.annee),
                     'centre': Latex.echappe_caracteres(generaux.centre)}

        contenu = r'''
            \thispagestyle{empty}
            \begin{adjustwidth}{0cm}{}
            %(centre)s \hspace*{\fill} \thepage \\
            %(ref)s \\
            \hspace*{\fill} %(nom)s \\
            \hspace*{\fill} %(code_sap)s \\
            \end{adjustwidth}
            \begin{center}
            \Large\textsc{%(annexe)s %(date)s} \\
            \Large\textsc{%(titre)s}
            \end{center}
            \rule{\linewidth}{1pt}
             \vspace*{5mm}
            ''' % dic_titre

        return contenu

    @staticmethod
    def section(client, generaux, reference, titre):
        """
        création d'un début de section non-visible
        :param client: données du client concerné
        :param generaux: paramètres généraux
        :param reference: référence de la facture
        :param titre: titre de la section
        :return: section latex
        """
        dic_section = {'code_sap': Latex.echappe_caracteres(client['code_sap']),
                       'nom': Latex.echappe_caracteres(client['abrev_labo']), 'ref': reference, 'titre': titre,
                       'centre': Latex.echappe_caracteres(generaux.centre)}

        section = r'''
            \fakesection{%(centre)s \\ %(ref)s \\ %(titre)s}
            {%(code_sap)s - %(nom)s \\}
            ''' % dic_section

        return section

    @staticmethod
    def entete(edition):
        """
        création de l'entête latex
        :param edition: paramètres d'édition
        :return: entête latex
        """

        entete = Latex.entete()
        entete += r'''
            \usepackage[margin=12mm, includehead, includefoot]{geometry}
            \usepackage{multirow}
            \usepackage{graphicx}
            \usepackage{longtable}
            \usepackage{dcolumn}
            \usepackage{changepage}
            \usepackage[scriptsize]{caption}
            \captionsetup[table]{position=bottom}
            \usepackage{fancyhdr}\usepackage{float}
            \restylefloat{table}

            '''

        if edition.filigrane != "":
            entete += r'''
                \usepackage{draftwatermark}
                \SetWatermarkLightness{0.8}
                \SetWatermarkAngle{45}
                \SetWatermarkScale{2}
                \SetWatermarkFontSize{2cm}
                \SetWatermarkText{''' + edition.filigrane[:15] + r'''}
                '''

        entete += r'''
            \pagestyle{fancy}

            \fancyhead{}
            \fancyfoot{}

            \renewcommand{\headrulewidth}{0pt}
            \renewcommand{\footrulewidth}{0pt}
            \renewcommand{\arraystretch}{1.5}

            \fancyhead[L]{\leftmark}
            \fancyhead[R]{\thepage \\ \rightmark}

            \newcommand{\fakesection}[2]{
                \markboth{#1}{#2}
            }

            \begin{document}
            '''

        return entete
