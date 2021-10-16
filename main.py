# This Python file uses the following encoding: utf-8

"""
Fichier principal à lancer pour faire tourner le logiciel

Usage:
  main.py [options]

Options:

  -h   --help              Affiche le présent message
  --entrees <chemin>       Chemin des fichiers d'entrée
  --sansgraphiques         Pas d'interface graphique
"""
import datetime
import sys
import time
import traceback
from docopt import docopt

from importes import (Client,
                      Acces,
                      ArticleSap,
                      ClasseClient,
                      CoefPrest,
                      CategPrix,
                      Compte,
                      Livraison,
                      Machine,
                      Groupe,
                      Prestation,
                      Categorie,
                      User,
                      NoShow,
                      Granted,
                      PlafSubside,
                      Plateforme,
                      Subside,
                      CleSubside,
                      DossierSource,
                      DossierDestination)
from outils import Outils
from parametres import (Edition,
                        DocPdf,
                        Paramannexe,
                        Paramtexte,
                        SuppressionFacture,
                        AnnulationVersion,
                        AnnulationSuppression,
                        Generaux)
from traitement import (Annexes,
                        Articles,
                        Tarifs,
                        Transactions,
                        GrantedNew,
                        BilansTransacts,
                        BilanMensuel,
                        BilanComptes,
                        Facture,
                        Sommes,
                        Verification,
                        Detail,
                        Resumes,
                        Recapitulatifs)
from prod2qual import Prod2Qual
from latex import Latex

arguments = docopt(__doc__)

if arguments["--sansgraphiques"]:
    Outils.interface_graphique(False)

if arguments["--entrees"]:
    dossier_data = arguments["--entrees"]
else:
    dossier_data = Outils.choisir_dossier()
dossier_source = DossierSource(dossier_data)
try:
    start_time = time.time()
    generaux = Generaux(dossier_source)

    pe_present = Outils.existe(Outils.chemin([dossier_data, Edition.nom_fichier]))
    sup_present = Outils.existe(Outils.chemin([dossier_data, SuppressionFacture.nom_fichier]))
    ann_present = Outils.existe(Outils.chemin([dossier_data, AnnulationVersion.nom_fichier]))
    ann_sup_present = Outils.existe(Outils.chemin([dossier_data, AnnulationSuppression.nom_fichier]))

    if pe_present and sup_present:
        msg = "Deux fichiers bruts incompatibles dans le répertoire : supprfact.csv et paramedit.csv"
        Outils.affiche_message(msg)
        sys.exit("Erreur sur les fichiers")

    if pe_present and ann_present:
        msg = "Deux fichiers bruts incompatibles dans le répertoire : paramedit.csv et annulversion.csv"
        Outils.affiche_message(msg)
        sys.exit("Erreur sur les fichiers")

    if ann_present and sup_present:
        msg = "Deux fichiers bruts incompatibles dans le répertoire : supprfact.csv et annulversion.csv"
        Outils.affiche_message(msg)
        sys.exit("Erreur sur les fichiers")

    if pe_present and ann_sup_present:
        msg = "Deux fichiers bruts incompatibles dans le répertoire : annulsuppr.csv et paramedit.csv"
        Outils.affiche_message(msg)
        sys.exit("Erreur sur les fichiers")

    if ann_sup_present and ann_present:
        msg = "Deux fichiers bruts incompatibles dans le répertoire : annulsuppr.csv et annulversion.csv"
        Outils.affiche_message(msg)
        sys.exit("Erreur sur les fichiers")

    if ann_sup_present and sup_present:
        msg = "Deux fichiers bruts incompatibles dans le répertoire : annulsuppr.csv et annulversion.csv"
        Outils.affiche_message(msg)
        sys.exit("Erreur sur les fichiers")

    if not ann_present and not sup_present and not pe_present and not ann_sup_present:
        msg = "Ni supprfact.csv, ni paramedit.csv, ni annulversion.csv , ni annulsuppr.csv " \
              "dans le répértoire, rien ne sera fait !"
        Outils.affiche_message(msg)
        sys.exit("Erreur sur les fichiers")

    if pe_present:
        ## importation des bruts

        edition = Edition(dossier_source)
        paramannexe = Paramannexe(dossier_source)
        paramtexte = Paramtexte(dossier_source)

        acces = Acces(dossier_source)
        categories = Categorie(dossier_source)
        categprix = CategPrix(dossier_source)
        clients = Client(dossier_source)
        coefprests = CoefPrest(dossier_source)
        comptes = Compte(dossier_source)
        grants = Granted(dossier_source, edition)
        livraisons = Livraison(dossier_source)
        machines = Machine(dossier_source)
        groupes = Groupe(dossier_source)
        noshows = NoShow(dossier_source)
        plafonds = PlafSubside(dossier_source)
        plateformes = Plateforme(dossier_source)
        prestations = Prestation(dossier_source)
        subsides = Subside(dossier_source)
        cles = CleSubside(dossier_source)
        users = User(dossier_source)
        classes = ClasseClient(dossier_source)
        artsap = ArticleSap(dossier_source)

        if Outils.existe(Outils.chemin([dossier_data, DocPdf.nom_fichier])):
            docpdf = DocPdf(dossier_source)
        else:
            docpdf = None

        ## vérification de la cohérence

        verification = Verification()
        if verification.verification_date(edition, acces, clients, comptes, livraisons, machines, noshows,
                                          prestations, users) > 0:
            sys.exit("Erreur dans les dates")

        if verification.verification_coherence(generaux, edition, acces, categories, categprix, clients, coefprests,
                                               comptes, grants, livraisons, machines, noshows, plafonds,
                                               plateformes, prestations, subsides, users, docpdf, groupes, cles,
                                               classes, artsap) > 0:
            sys.exit("Erreur dans la cohérence")

        ## génération du dossier destination

        if edition.version > 0 and edition.client_unique == generaux.code_cfact_centre:
            chemin = generaux.chemin_propre
        elif edition.filigrane != "":
            chemin = generaux.chemin_filigrane
        else:
            chemin = generaux.chemin
        dossier_enregistrement = Outils.chemin([chemin, edition.annee, Outils.mois_string(edition.mois)], generaux)
        existe = Outils.existe(dossier_enregistrement, True)
        dossier_lien = Outils.lien_dossier([generaux.lien, edition.annee, Outils.mois_string(edition.mois)], generaux)

        if edition.version == 0:
            if existe:
                msg = "Le répertoire " + dossier_enregistrement + " existe déjà !"
                Outils.affiche_message(msg)
                sys.exit("Erreur sur le répértoire")
            dossier_csv = Outils.chemin([dossier_enregistrement, "csv_0"], generaux)
            Outils.existe(dossier_csv, True)
        else:
            dossier_csv = Outils.chemin([dossier_enregistrement, "csv_" + str(edition.version) + "_" +
                                         edition.client_unique])

            w = edition.version - 1
            dossier_w = Outils.chemin([dossier_enregistrement, "suppr_" + str(w) + "_" + edition.client_unique])
            if Outils.existe(dossier_w) and not Outils.existe(Outils.chemin([dossier_w, "copernic.csv"])):
                msg = "La suppression de la version " + str(w) + " du client " + edition.client_unique + \
                      " n'a pas été confirmée !"
                Outils.affiche_message(msg)
                sys.exit("Erreur sur le répértoire")

            if Outils.existe(dossier_csv, True):
                msg = "La version " + str(edition.version) + " du client " + edition.client_unique + " existe déjà !"
                Outils.affiche_message(msg)
                sys.exit("Erreur sur le répértoire")

        dossier_destination = DossierDestination(dossier_csv)

        ## copie des fichiers bruts

        for fichier in [acces.nom_fichier, clients.nom_fichier, coefprests.nom_fichier, comptes.nom_fichier,
                        livraisons.nom_fichier, machines.nom_fichier, prestations.nom_fichier, categories.nom_fichier,
                        users.nom_fichier, generaux.nom_fichier, grants.nom_fichier, edition.nom_fichier,
                        categprix.nom_fichier, paramannexe.nom_fichier, noshows.nom_fichier, plafonds.nom_fichier,
                        plateformes.nom_fichier, subsides.nom_fichier, paramtexte.nom_fichier, groupes.nom_fichier,
                        cles.nom_fichier, artsap.nom_fichier, classes.nom_fichier]:
            dossier_destination.ecrire(fichier, dossier_source.lire(fichier))
        if docpdf is not None:
            dossier_destination.ecrire(docpdf.nom_fichier, dossier_source.lire(docpdf.nom_fichier))

        ## calcul des sommes intermédiaires

        livraisons.calcul_montants(prestations, coefprests, clients, verification, comptes)
        acces.calcul_montants(machines, categprix, clients, verification, comptes, groupes)
        noshows.calcul_montants(machines, categprix, clients, comptes, verification, groupes)

        sommes = Sommes(verification, generaux, artsap)
        sommes.calculer_toutes(livraisons, acces, clients, noshows)

        for donnee in paramannexe.donnees:
            donnee['chemin'] = Outils.chemin([dossier_enregistrement, donnee['dossier']], generaux)
            Outils.existe(donnee['chemin'], True)
            donnee['dossier_pdf'] = DossierDestination(donnee['chemin'])
            donnee['lien'] = Outils.lien_dossier([dossier_lien, donnee['dossier']], generaux)

        ## traitement

        articles = Articles(edition)
        articles.generer(artsap, categories, prestations, paramtexte)
        articles.csv(dossier_destination, paramtexte)
        tarifs = Tarifs(edition)
        tarifs.generer(classes, categories, prestations, categprix, coefprests)
        tarifs.csv(dossier_destination, paramtexte)
        transactions = Transactions(edition)
        transactions.generer(acces, noshows, livraisons, prestations, machines, categprix, comptes, clients, users,
                             plateformes, classes, articles, tarifs, subsides, plafonds, grants, groupes, cles,
                             paramtexte)
        transactions.csv(dossier_destination, paramtexte)

        new_grants = GrantedNew(edition)
        new_grants.generer(grants, transactions)

        trans_vals = transactions.valeurs
        if edition.filigrane == "" and edition.version > 0 and \
                Outils.existe(Outils.chemin([dossier_enregistrement, "csv_0"])):
            transactions.mise_a_jour(edition, DossierSource(dossier_enregistrement),
                                     DossierDestination(dossier_enregistrement), transactions)
            trans_fichier = "Transaction_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + ".csv"
            trans_vals = transactions.recuperer_valeurs_de_fichier(DossierSource(dossier_enregistrement), trans_fichier)
            new_grants.mise_a_jour(DossierSource(dossier_enregistrement), DossierDestination(dossier_enregistrement),
                                   new_grants, comptes)
        else:
            new_grants.csv(DossierDestination(dossier_enregistrement))

        bilan_trs = BilansTransacts(edition)
        bilan_trs.generer(trans_vals, grants, plafonds, comptes, clients, subsides, paramtexte, paramannexe, artsap,
                          DossierDestination(dossier_enregistrement))

        # faire les annexes avant la facture, que le ticket puisse vérifier leur existence
        if Latex.possibles():
            Annexes.annexes(sommes, clients, edition, livraisons, acces, machines, comptes, paramannexe,
                            generaux, users, categories, noshows, docpdf, groupes, artsap, classes)

        Outils.copier_dossier("./reveal.js/", "js", dossier_enregistrement)
        Outils.copier_dossier("./reveal.js/", "css", dossier_enregistrement)
        facture_prod = Facture()
        f_html_sections = facture_prod.factures(sommes, dossier_destination, edition, generaux, clients, comptes,
                                                paramannexe, bilan_trs, artsap, classes)

        prod2qual = Prod2Qual(dossier_source)
        if prod2qual.actif:
            facture_qual = Facture(prod2qual)
            facture_qual.factures(sommes, dossier_destination, edition, generaux, clients, comptes, paramannexe,
                                  bilan_trs, artsap, classes)

        bm_lignes = BilanMensuel.creation_lignes(edition, sommes, clients, artsap, classes)
        BilanMensuel.bilan(dossier_destination, edition, artsap, bm_lignes)
        bc_lignes = BilanComptes.creation_lignes(edition, sommes, clients, comptes, artsap, classes)
        BilanComptes.bilan(dossier_destination, edition, artsap, bc_lignes)
        det_lignes = Detail.creation_lignes(edition, sommes, clients, artsap, acces, livraisons, comptes, categories,
                                            classes)
        Detail.detail(dossier_destination, edition, det_lignes)

        cae_lignes = Recapitulatifs.cae_lignes(edition, acces, comptes, clients, users, machines, categories, groupes)
        Recapitulatifs.cae(dossier_destination, edition, cae_lignes)
        lvr_lignes = Recapitulatifs.lvr_lignes(edition, livraisons, comptes, clients, users, prestations)
        Recapitulatifs.lvr(dossier_destination, edition, lvr_lignes)
        nos_lignes = Recapitulatifs.nos_lignes(edition, noshows, comptes, clients, users, machines, categories, groupes)
        Recapitulatifs.nos(dossier_destination, edition, nos_lignes)

        if edition.filigrane == "":
            if edition.version == 0:
                Resumes.base(edition, DossierSource(dossier_csv), DossierDestination(dossier_enregistrement))
                Resumes.supprimer(generaux.code_cfact_centre, edition.mois, edition.annee,
                                  DossierSource(dossier_enregistrement), DossierDestination(dossier_enregistrement))
            elif Outils.existe(Outils.chemin([dossier_enregistrement, "csv_0"])):
                maj = [bm_lignes, bc_lignes, det_lignes, cae_lignes, lvr_lignes, nos_lignes]
                Resumes.mise_a_jour(edition, clients, DossierSource(dossier_enregistrement),
                                    DossierDestination(dossier_enregistrement), maj, f_html_sections)

    if sup_present:
        suppression = SuppressionFacture(dossier_source)
        dossier_enregistrement = Outils.chemin([generaux.chemin, suppression.annee,
                                                Outils.mois_string(suppression.mois)])
        suffixe = str(suppression.version) + "_" + suppression.client_unique

        if suppression.version == 0:
            if not Outils.existe(Outils.chemin([dossier_enregistrement, "csv_0"])):
                msg = "La version 0 n'existe pas dans " + dossier_enregistrement + ", impossible " \
                                                                                   "de supprimer une facture !"
                Outils.affiche_message(msg)
                sys.exit("Erreur sur la version")

            dossier_copernic = "csv_0"
        else:
            if not Outils.existe(Outils.chemin([dossier_enregistrement, "csv_" + suffixe])):
                msg = "La version " + str(suppression.version) + " du client " + suppression.client_unique + \
                      " n'existe pas dans " + dossier_enregistrement + ", impossible de supprimer une facture !"
                Outils.affiche_message(msg)
                sys.exit("Erreur sur la version")
            dossier_copernic = "csv_" + suffixe

        if not Outils.existe(Outils.chemin([dossier_enregistrement, dossier_copernic, "copernic.csv"])):
            msg = "La version " + str(suppression.version) + " n’a pas été émise dans SAP, " \
                                                             "impossible de supprimer une facture !"
            Outils.affiche_message(msg)
            sys.exit("Erreur sur la version")

        dossier_suppr = Outils.chemin([dossier_enregistrement, "suppr_" + suffixe])
        if Outils.existe(dossier_suppr):
            msg = "La suppression de la version " + str(suppression.version) + " du client " + \
                  suppression.client_unique + " existe déjà!"
            Outils.affiche_message(msg)
            sys.exit("Erreur sur la version")

        Outils.existe(dossier_suppr, True)

        DossierDestination(dossier_suppr).ecrire(suppression.nom_fichier, dossier_source.lire(suppression.nom_fichier))

        Resumes.suppression(
            suppression, DossierSource(dossier_enregistrement), DossierDestination(dossier_enregistrement))

    if ann_sup_present:
        annsupp = AnnulationSuppression(dossier_source)
        dossier_enregistrement = Outils.chemin([generaux.chemin, annsupp.annee,
                                                Outils.mois_string(annsupp.mois)])
        suffixe = str(annsupp.version) + "_" + annsupp.client_unique
        dossier_suppr = Outils.chemin([dossier_enregistrement, "suppr_" + suffixe])

        if not Outils.existe(dossier_suppr):
            msg = "Annulation de suppression impossible!"
            Outils.affiche_message(msg)
            sys.exit("Erreur sur la version")

        if Outils.existe(Outils.chemin([dossier_suppr, "copernic.csv"])):
            msg = "Impossible d’annuler l’opération de suppression de la version " + str(annsupp.version) + \
                  " car l’opération a été confirmée!"
            Outils.affiche_message(msg)
            sys.exit("Erreur sur la version")

        if annsupp.version == 0:
            dossier_csv = Outils.chemin([dossier_enregistrement, "csv_0"])
            if not Outils.existe(dossier_csv):
                msg = "La version 0 à recharger pour le client " + annsupp.client_unique + " n’existe pas !"
                Outils.affiche_message(msg)
                sys.exit("Erreur sur la version")
        else:
            dossier_csv = Outils.chemin([dossier_enregistrement, "csv_" + suffixe])
            if not Outils.existe(dossier_csv):
                msg = "La version " + str(annsupp.version) + " du client " + annsupp.client_unique + \
                      " à recharger n'existe pas !"
                Outils.affiche_message(msg)
                sys.exit("Erreur sur la version")

        DossierDestination(dossier_suppr).ecrire(annsupp.nom_fichier, dossier_source.lire(annsupp.nom_fichier))
        now = datetime.datetime.now()
        Outils.renommer_dossier([dossier_enregistrement, "suppr_" + suffixe],
                                [dossier_enregistrement, "old_" + suffixe + "_" + now.strftime("%Y%m%d_%H%M")])
        Resumes.annulation_suppression(annsupp, DossierSource(dossier_enregistrement),
                                       DossierDestination(dossier_enregistrement), DossierSource(dossier_csv))

    if ann_present:
        annulation = AnnulationVersion(dossier_source)
        if annulation.client_unique == generaux.code_cfact_centre:
            chemin = generaux.chemin_propre
        else:
            chemin = generaux.chemin
        dossier_enregistrement = Outils.chemin([chemin, annulation.annee, Outils.mois_string(annulation.mois)])
        if annulation.annule_version == 0:
            chemin_copernic = Outils.chemin([dossier_enregistrement, "csv_0", "copernic.csv"])
            if Outils.existe(chemin_copernic):
                msg = "La version 0 a déjà été émise et ne peut plus être annulée !"
                Outils.affiche_message(msg)
                sys.exit("Erreur sur la version")
            else:
                Outils.effacer_dossier(Outils.chemin([chemin, annulation.annee, Outils.mois_string(annulation.mois)]))
        else:
            chemin = Outils.chemin([dossier_enregistrement, "csv_" + str(annulation.annule_version) + "_" +
                                    annulation.client_unique])
            if not Outils.existe(chemin):
                msg = "La version " + str(annulation.annule_version) + " à annuler pour le client " +\
                      annulation.client_unique + " n’existe pas !"
                Outils.affiche_message(msg)
                sys.exit("Erreur sur la version")

            chemin_copernic = Outils.chemin([dossier_enregistrement, "csv_" + str(annulation.annule_version) + "_" +
                                             annulation.client_unique, "copernic.csv"])
            if Outils.existe(chemin_copernic):
                msg = "La version " + str(annulation.annule_version) + " à annuler pour le client " + \
                      annulation.client_unique + " a déjà été émise et ne peut plus être annulée !"
                Outils.affiche_message(msg)
                sys.exit("Erreur sur la version")

            if annulation.recharge_version == 0:
                dossier_csv = Outils.chemin([dossier_enregistrement, "csv_0"])
                if not Outils.existe(dossier_csv):
                    msg = "La version 0 à recharger n'existe pas !"
                    Outils.affiche_message(msg)
                    sys.exit("Erreur sur la version")
            else:
                dossier_csv = Outils.chemin([dossier_enregistrement, "csv_" + str(annulation.recharge_version) + "_" +
                                             annulation.client_unique])
                if not Outils.existe(dossier_csv):
                    msg = "La version " + str(annulation.recharge_version) + " à recharger pour le client " + \
                          annulation.client_unique + " n'existe pas !"
                    Outils.affiche_message(msg)
                    sys.exit("Erreur sur la version")

            DossierDestination(chemin).ecrire(annulation.nom_fichier, dossier_source.lire(annulation.nom_fichier))
            now = datetime.datetime.now()
            Outils.renommer_dossier([dossier_enregistrement, "csv_" + str(annulation.annule_version) + "_" +
                                    annulation.client_unique],
                                    [dossier_enregistrement, "old_" + str(annulation.annule_version) + "_" +
                                     annulation.client_unique + "_" + now.strftime("%Y%m%d_%H%M")])

            Resumes.annulation(annulation, DossierSource(dossier_enregistrement),
                               DossierDestination(dossier_enregistrement), DossierSource(dossier_csv))

    Outils.affiche_message("OK !!! (" + str(datetime.timedelta(seconds=(time.time() - start_time))).split(".")[0] + ")")

except Exception as e:
    Outils.fatal(traceback.format_exc(), "Erreur imprévue :\n")
