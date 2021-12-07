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
                      UserLabo,
                      PlafSubside,
                      Plateforme,
                      Service,
                      Subside,
                      CleSubside,
                      DossierSource,
                      DossierDestination)
from outils import Outils
from parametres import (Edition,
                        DocPdf,
                        Paramannexe,
                        Paramtexte,
                        Generaux)
from traitement import (Annexes,
                        Articles,
                        Tarifs,
                        Transactions,
                        GrantedNew,
                        BilansTransacts,
                        BilanMensuel,
                        Facture,
                        Sommes,
                        Verification,
                        Resumes)
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
    userlabs = UserLabo(dossier_source, edition)
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
    services = Service(dossier_source)

    if Outils.existe(Outils.chemin([dossier_data, DocPdf.nom_fichier])):
        docpdf = DocPdf(dossier_source)
    else:
        docpdf = None

    ## vérification de la cohérence

    verification = Verification()
    if verification.verification_date(edition, acces, clients, comptes, livraisons, machines, noshows, prestations,
                                      users, services) > 0:
        sys.exit("Erreur dans les dates")

    if verification.verification_coherence(generaux, edition, acces, categories, categprix, clients, coefprests,
                                           comptes, grants, livraisons, machines, noshows, plafonds, plateformes,
                                           prestations, subsides, users, docpdf, groupes, cles, classes, artsap,
                                           userlabs, services) > 0:
        sys.exit("Erreur dans la cohérence")

    ## génération du dossier destination

    if edition.filigrane != "":
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

        if Outils.existe(dossier_csv, True):
            msg = "La version " + str(edition.version) + " du client " + edition.client_unique + " existe déjà !"
            Outils.affiche_message(msg)
            sys.exit("Erreur sur le répértoire")

    dossier_destination = DossierDestination(dossier_csv)

    ## copie des fichiers bruts

    for fichier in [acces, clients, coefprests, comptes,
                    livraisons, machines, prestations, categories,
                    users, generaux, grants, edition,
                    categprix, paramannexe, noshows, plafonds,
                    plateformes, subsides, paramtexte, groupes,
                    cles, artsap, classes, userlabs, services]:
        dossier_destination.ecrire(fichier.nom_fichier, dossier_source.lire(fichier.nom_fichier))
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
    articles.generer(artsap, categories, prestations)
    articles.csv(dossier_destination, paramtexte)
    tarifs = Tarifs(edition)
    tarifs.generer(classes, categories, prestations, categprix, coefprests)
    tarifs.csv(dossier_destination, paramtexte)
    transactions = Transactions(edition)
    transactions.generer(acces, noshows, livraisons, services, prestations, machines, categprix, comptes, clients,
                         users, plateformes, classes, articles, tarifs, subsides, plafonds, grants, groupes, cles,
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

    bilan_trs = BilansTransacts(edition, paramtexte, paramannexe)
    bilan_trs.generer(trans_vals, grants, plafonds, comptes, clients, subsides, artsap, userlabs,
                      DossierDestination(dossier_enregistrement))

    # faire les annexes avant la facture, que le ticket puisse vérifier leur existence
    if Latex.possibles():
        Annexes.annexes(sommes, clients, edition, livraisons, acces, machines, comptes, paramannexe, generaux, users,
                        categories, noshows, docpdf, groupes, artsap, classes)

    Outils.copier_dossier("./reveal.js/", "js", dossier_enregistrement)
    Outils.copier_dossier("./reveal.js/", "css", dossier_enregistrement)
    facture_prod = Facture()
    f_html_sections = facture_prod.factures(sommes, dossier_destination, edition, generaux, clients, comptes,
                                            paramannexe, bilan_trs, artsap, classes, paramtexte)

    prod2qual = Prod2Qual(dossier_source)
    if prod2qual.actif:
        facture_qual = Facture(prod2qual)
        facture_qual.factures(sommes, dossier_destination, edition, generaux, clients, comptes, paramannexe, bilan_trs,
                              artsap, classes, paramtexte)

    bm_lignes = BilanMensuel.creation_lignes(edition, sommes, clients, classes)
    BilanMensuel.bilan(dossier_destination, edition, bm_lignes)

    if edition.filigrane == "":
        if edition.version == 0:
            Resumes.base(edition, DossierSource(dossier_csv), DossierDestination(dossier_enregistrement))
        elif Outils.existe(Outils.chemin([dossier_enregistrement, "csv_0"])):
            maj = [bm_lignes]
            Resumes.mise_a_jour(edition, clients, DossierSource(dossier_enregistrement),
                                DossierDestination(dossier_enregistrement), maj, f_html_sections)

    Outils.affiche_message("OK !!! (" + str(datetime.timedelta(seconds=(time.time() - start_time))).split(".")[0] + ")")

except Exception as e:
    Outils.fatal(traceback.format_exc(), "Erreur imprévue :\n")
