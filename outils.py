from tkinter.filedialog import *
from tkinter.scrolledtext import *

from datetime import datetime
import shutil
import errno
import os
import platform
import sys
import re

from erreurs import ErreurConsistance


class Outils(object):
    """
    Classe contenant diverses méthodes utiles
    """
    @staticmethod
    def copier_dossier(source, dossier, destination):
        """
        copier un dossier
        :param source: chemin du dossier à copier
        :param dossier: dossier à copier
        :param destination: chemin de destination de copie
        """
        chemin = destination + "/" + dossier
        if not os.path.exists(chemin):
            try:
                shutil.copytree(source + dossier, chemin)
            except OSError as exc:
                if exc.errno == errno.ENOTDIR:
                    shutil.copy(source, destination)

    if platform.system() in ['Linux', 'Darwin']:
        _interface_graphique = len(os.environ.get('DISPLAY', '')) > 0
    else:
        _interface_graphique = True

    @classmethod
    def interface_graphique(cls, opt_nouvelle_valeur=None):
        """
        enregistre que l'on veut l'interface graphique ou non
        :param opt_nouvelle_valeur: True ou False pour interface graphique
        :return: valeur enregistrée
        """
        if opt_nouvelle_valeur is not None:
            cls._interface_graphique = opt_nouvelle_valeur
        return cls._interface_graphique

    @classmethod
    def affiche_message(cls, message):
        """
        affiche une petite boite de dialogue avec un message et un bouton OK
        :param message: message à afficher
        """
        if cls.interface_graphique():
            fenetre = Tk()
            fenetre.title("Message")
            texte = ScrolledText(fenetre)
            texte.insert(END, message)
            texte.pack()
            button = Button(fenetre, text='OK', command=fenetre.destroy)
            button.pack()
            mainloop()
        else:
            print(message)

    @classmethod
    def fatal(cls, exn, message):
        """
        affiche erreur fatal
        :param exn: erreur
        :param message: message à afficher
        """
        Outils.affiche_message(message + "\n" + str(exn))
        if isinstance(exn, ErreurConsistance) or isinstance(exn, ValueError):
            sys.exit(1)
        else:
            sys.exit(4)            

    @classmethod
    def affiche_message_conditionnel(cls, titre, message):
        """
        affiche une petite boite de dialogue avec un message et 2 boutons OUI/NON, le NON arrête le programme
        :param titre: titre à afficher
        :param message: message à afficher
        """
        if cls.interface_graphique():
            fenetre = Tk()
            fenetre.title(titre)
            texte = ScrolledText(fenetre)
            texte.insert(END, message)
            texte.pack()
            button = Button(fenetre, text='OUI', command=fenetre.destroy)
            button.pack(side="left")
            button = Button(fenetre, text='NON', command=sys.exit)
            button.pack(side="right")
            mainloop()
        else:
            sys.exit("message conditionnel non-autorisé en mode sans graphique")

    @staticmethod
    def choisir_dossier():
        """
        affiche une interface permettant de choisir un dossier
        :return: la position du dossier sélectionné
        """
        fenetre = Tk()
        fenetre.title("Choix du dossier")
        dossier = askdirectory(parent=fenetre, initialdir="/",
                               title='Choisissez un dossier de travail')
        fenetre.destroy()
        if dossier == "":
            Outils.affiche_message("Aucun dossier choisi")
            sys.exit("Aucun dossier choisi")
        return dossier + Outils.separateur_os()

    @staticmethod
    def format_heure(nombre):
        """
        transforme une heure d'un format float à un format hh:mm
        :param nombre: heure en float
        :return: heure en hh:mm
        """
        if nombre == 0:
            return "00:00"
        signe = ""
        if nombre < 0:
            signe = "-"
        nombre = abs(nombre)
        heures = "%d" % (nombre // 60)
        if (nombre // 60) < 10:
            heures = '0' + heures
        minutes = "%d" % (nombre % 60)
        if (nombre % 60) < 10:
            minutes = '0' + minutes
        return signe + heures + ':' + minutes

    @staticmethod
    def mois_string(mois):
        """
        prend un mois comme nombre, et le retourne comme string, avec un '0' devant si plus petit que 10
        :param mois: mois formaté en nombre
        :return: mois formaté en string
        """
        if mois < 10:
            return "0" + str(mois)
        else:
            return str(mois)

    @staticmethod
    def separateur_os():
        """
        retourne le séparateur de chemin logique en fonction de l'OS (si windows ou pas)
        :return: séparateur, string
        """
        if sys.platform == "win32":
            return "\\"
        else:
            return "/"

    @staticmethod
    def separateur_lien(texte, generaux):
        """
        remplace le séparateur de chemin logique en fonction du lien donné dans les paramètres généraux
        :param texte: texte à traiter
        :param generaux: paramètres généraux
        :return: séparateur, string
        """
        if "\\" in generaux.lien:
            if "/" in generaux.lien:
                Outils.affiche_message("'/' et '\\' présents dans le lien des paramètres généraux !!! ")
            texte = texte.replace("/", "\\")
        else:
            texte = texte.replace("\\", "/")
        return texte.replace("//", "/").replace("\\" + "\\", "\\")

    @staticmethod
    def separateur_dossier(texte, generaux):
        """
        remplace le séparateur de chemin logique en fonction du chemin donné dans les paramètres généraux
        :param texte: texte à traiter
        :param generaux: paramètres généraux
        :return: séparateur, string
        """
        if "\\" in generaux.chemin:
            if "/" in generaux.chemin or "/" in generaux.chemin_filigrane:
                Outils.affiche_message("'/' et '\\' présents dans les chemins des paramètres généraux !!! ")
            texte = texte.replace("/", "\\")
            """
            if "\\" != Outils.separateur_os():
                Outils.affiche_message_conditionnel("Le chemin d'enregistrement n'utilise pas le même séparateur que "
                                                    "l'os sur lequel tourne le logiciel. Voulez-vous tout de même "
                                                    "continuer ?")
            """
        else:
            texte = texte.replace("\\", "/")
            """
            if "/" != Outils.separateur_os():
                Outils.affiche_message_conditionnel("Le chemin d'enregistrement n'utilise pas le même séparateur que "
                                                    "l'os sur lequel tourne le logiciel. Voulez-vous tout de même "
                                                    "continuer ?")
            """
        return texte.replace("//", "/").replace("\\" + "\\", "\\")

    @staticmethod
    def eliminer_double_separateur(texte):
        """
        élimine les doubles (back)slashs
        :param texte: texte à nettoyer
        :return: texte nettoyé
        """
        return texte.replace("//", "/").replace("\\" + "\\", "\\")

    @staticmethod
    def chemin(structure, generaux=None):
        """
        construit le chemin pour dossier/fichier
        :param structure: éléments du chemin
        :param generaux: paramètres généraux
        :return: chemin logique complet pour dossier/fichier
        """
        chemin = ""
        first = True
        for element in structure:
            if not first:
                chemin += Outils.separateur_os()
            else:
                first = False
            chemin += str(element)
        if generaux is None:
            return Outils.eliminer_double_separateur(chemin)
        else:
            return Outils.eliminer_double_separateur(Outils.separateur_dossier(chemin, generaux))

    @staticmethod
    def renommer_dossier(ancienne_structure, nouvelle_structure):
        """
        renomme un dossier
        :param ancienne_structure: éléments de l'ancien nom de dossier
        :param nouvelle_structure: éléments du nouveau nom de dossier
        """
        ancien_chemin = ""
        for element in ancienne_structure:
            ancien_chemin += str(element) + Outils.separateur_os()
        nouveau_chemin = ""
        for element in nouvelle_structure:
            nouveau_chemin += str(element) + Outils.separateur_os()
        os.rename(ancien_chemin, nouveau_chemin)

    @staticmethod
    def effacer_fichier(chemin):
        """
        efface un fichier
        :param chemin: chemin du fichier
        """
        titre = "Effacer un fichier"
        message = "Voulez-vous vraiment effacer le fichier ? : " + chemin
        Outils.affiche_message_conditionnel(titre, message)
        os.remove(chemin)

    @staticmethod
    def effacer_dossier(chemin):
        """
        efface un dossier
        :param chemin: chemin du dossier
        """
        titre = "Effacer un dossier et son contenu"
        message = "Voulez-vous vraiment effacer le dossier (et son contenu) ? : " + chemin
        Outils.affiche_message_conditionnel(titre, message)
        shutil.rmtree(chemin)

    @staticmethod
    def existe(chemin, creation=False):
        """
        vérifie si le dossier/fichier existe
        :param chemin: chemin du dossier/fichier
        :param creation: création de l'objet s'il n'existe pas
        :return: True si le dossier/fichier existe, False sinon
        """
        existe = True
        if not os.path.exists(chemin):
            existe = False
            if creation:
                os.makedirs(chemin)
        return existe

    @staticmethod
    def lien_dossier(structure, generaux):
        """
        construit le chemin pour enregistrer les données sans vérifier son existence
        :param structure: éléments du chemin
        :param generaux: paramètres généraux
        :return:chemin logique complet pour dossier
        """
        chemin = ""
        for element in structure:
            chemin += str(element) + Outils.separateur_os()
        return Outils.eliminer_double_separateur(Outils.separateur_lien(chemin, generaux))

    @staticmethod
    def est_un_texte(donnee, colonne, ligne=-1, vide=False):
        """
        vérifie que la donnée est bien un texte
        :param donnee: donnée à vérifier
        :param colonne: colonne contenant la donnée (nom de la variable)
        :param ligne: ligne contenant la donnée (-1 si pas de ligne)
        :param vide: True si la variable peut être vide, False sinon
        :return: la donnée formatée et un string vide si ok, "" et un message d'erreur sinon
        """
        if ligne > -1:
            delaligne = " de la ligne " + str(ligne)
        else:
            delaligne = ""
        try:
            s_d = str(donnee)
            if s_d.startswith('"') and s_d.endswith('"'):
                s_d = s_d[1:-1]
            if s_d == "" and not vide:
                return "", colonne + delaligne + " ne peut être vide\n"
            return s_d, ""
        except ValueError:
            return "", colonne + delaligne + " doit être un texte\n"

    @staticmethod
    def est_une_date(donnee, colonne, ligne=-1, vide=False):
        """
        vérifie que la donnée est bien une date
        :param donnee: donnée à vérifier
        :param colonne: colonne contenant la donnée (nom de la variable)
        :param ligne: ligne contenant la donnée (-1 si pas de ligne)
        :param vide: True si la variable peut être vide, False sinon
        :return: la donnée formatée et un string vide si ok, "" et un message d'erreur sinon
        """
        if ligne > -1:
            delaligne = " de la ligne " + str(ligne)
        else:
            delaligne = ""
        try:
            s_d = str(donnee)
            if s_d.startswith('"') and s_d.endswith('"'):
                s_d = s_d[1:-1]
            if s_d == "":
                if not vide:
                    return "", colonne + delaligne + " ne peut être vide\n"
                else:
                    return "", ""
            date = datetime.strptime(s_d, '%Y-%m-%d %H:%M:%S')
            return date, ""
        except ValueError:
            return "", colonne + delaligne + " doit être une date du bon format : YYYY-MM-DD HH:MM:SS\n"

    @staticmethod
    def est_un_document(donnee, colonne, ligne=-1, vide=False):
        """
        vérifie que la donnée est bien un nom de document
        :param donnee: donnée à vérifier
        :param colonne: colonne contenant la donnée (nom de la variable)
        :param ligne: ligne contenant la donnée (-1 si pas de ligne)
        :param vide: True si la variable peut être vide, False sinon
        :return: la donnée formatée et un string vide si ok, "" et un message d'erreur sinon
        """
        if ligne > -1:
            delaligne = " de la ligne " + str(ligne)
        else:
            delaligne = ""
        try:
            chars = set('\/:*?“<>|')
            s_d = str(donnee)
            if s_d == "" and not vide:
                return "", colonne + delaligne + " ne peut être vide\n"
            if any((c in chars) for c in s_d):
                return "", colonne + delaligne + " n'est pas un nom de document valide\n"
            return s_d, ""
        except:
            return "", colonne + delaligne + " doit être un texte\n"

    @staticmethod
    def est_un_chemin(donnee, colonne, ligne=-1, vide=False):
        """
        vérifie que la donnée est bien un chemin
        :param donnee: donnée à vérifier
        :param colonne: colonne contenant la donnée (nom de la variable)
        :param ligne: ligne contenant la donnée (-1 si pas de ligne)
        :param vide: True si la variable peut être vide, False sinon
        :return: la donnée formatée et un string vide si ok, "" et un message d'erreur sinon
        """
        if ligne > -1:
            delaligne = " de la ligne " + str(ligne)
        else:
            delaligne = ""
        try:
            chars = set('*?"<>|')
            s_d = str(donnee)
            if s_d == "" and not vide:
                return "", colonne + delaligne + " ne peut être vide\n"
            if any((c in chars) for c in s_d):
                return "", colonne + delaligne + " n'est pas un chemin valide\n"
            return s_d, ""
        except:
            return "", colonne + delaligne + " doit être un texte\n"

    @staticmethod
    def est_un_alphanumerique(donnee, colonne, ligne=-1, barres=False, chevrons=False, vide=False):
        """
        vérifie que la donnée est bien un texte
        :param donnee: donnée à vérifier
        :param colonne: colonne contenant la donnée (nom de la variable)
        :param ligne: ligne contenant la donnée (-1 si pas de ligne)
        :param barres: True si la variable peut contenir des barres obliques, False sinon
        :param chevrons: True si la variable peut contenir des < >, False sinon
        :param vide: True si la variable peut être vide, False sinon
        :return: la donnée formatée et un string vide si ok, "" et un message d'erreur sinon
        """
        if ligne > -1:
            delaligne = " de la ligne " + str(ligne)
        else:
            delaligne = ""
        try:
            if barres:
                if chevrons:
                    pattern = '^[a-zA-Z0-9_<>\-./\\\\]+$'
                else:
                    pattern = '^[a-zA-Z0-9_\-./\\\\]+$'
            else:
                if chevrons:
                    pattern = '^[a-zA-Z0-9_<>\-]+$'
                else:
                    pattern = '^[a-zA-Z0-9_\-]+$'
            s_d = str(donnee)
            if s_d == "":
                if not vide:
                    return "", colonne + delaligne + " ne peut être vide\n"
                else:
                    return "", ""
            if not re.match(pattern, s_d):
                return "", colonne + delaligne + " n'est pas un alphanumérique valide\n"
            return s_d, ""
        except:
            return "", colonne + delaligne + " doit être un texte\n"

    @staticmethod
    def est_un_nombre(donnee, colonne, ligne=-1, arrondi=-1, min=None, max=None):
        """
        vérifie que la donnée est bien un nombre
        :param donnee: donnée à vérifier
        :param colonne: colonne contenant la donnée (nom de la variable)
        :param ligne: ligne contenant la donnée (-1 si pas de ligne)
        :param arrondi: arrondi après la virgule (-1 si pas d'arrondi)
        :param min: borne minimale facultative
        :param max: borne maximale facultative
        :return: la donnée formatée en nombre et un string vide si ok, 0 et un message d'erreur sinon
        """
        if ligne > -1:
            delaligne = " de la ligne " + str(ligne)
        else:
            delaligne = ""
        try:
            fl_d = float(donnee)
            if min is not None and fl_d < min:
                return -1, colonne + delaligne + " doit être un nombre >= " + str(min) + "\n"
            if max is not None and fl_d > max:
                return -1, colonne + delaligne + " doit être un nombre <= " + str(max) + "\n"
            if arrondi > -1:
                return round(fl_d, arrondi), ""
            else:
                return fl_d, ""
        except ValueError:
            return -1, colonne + delaligne + " doit être un nombre\n"

    @staticmethod
    def est_un_entier(donnee, colonne, ligne=-1, min=None, max=None):
        """
        vérifie que la donnée est bien un nombre entier dans les bornes éventuelles
        :param donnee: donnée à vérifier
        :param colonne: colonne contenant la donnée (nom de la variable)
        :param ligne: ligne contenant la donnée (-1 si pas de ligne)
        :param min: borne minimale facultative
        :param max: borne maximale facultative
        :return: la donnée formatée en nombre et un string vide si ok, 0 et un message d'erreur sinon
        """
        if ligne > -1:
            delaligne = " de la ligne " + str(ligne)
        else:
            delaligne = ""
        try:
            entier = int(donnee)
            if min is not None and entier < min:
                return -1, colonne + delaligne + " doit être un nombre entier >= " + str(min) + "\n"
            if max is not None and entier > max:
                return -1, colonne + delaligne + " doit être un nombre entier <= " + str(max) + "\n"
            return entier, ""
        except ValueError:
            return -1, colonne + delaligne + " doit être un nombre entier\n"

    @staticmethod
    def format_2_dec(nombre):
        """
        affiche un nombre en float arrondi avec 2 chiffres après la virgule
        :param nombre: nombre à afficher
        :return: nombre arrondi, avec 2 chiffres après la virgule, en string
        """
        try:
            float(nombre)
            return "%.2f" % round(nombre, 2)
        except ValueError:
            return "pas un nombre"

    @staticmethod
    def utilisateurs_in_somme(somme, users):
        """
        création de la liste des utilisateurs présents dans une somme
        :param somme: somme concernée
        :param users: données users
        :return: liste d'utilisateurs triée par nom, puis par prénom
        """
        utilisateurs = {}
        for key in somme:
            prenom = users.donnees[key]['prenom']
            nom = users.donnees[key]['nom']
            if nom not in utilisateurs:
                utilisateurs[nom] = {}
            if prenom not in utilisateurs[nom]:
                utilisateurs[nom][prenom] = []
            utilisateurs[nom][prenom].append(key)

        return utilisateurs

    @staticmethod
    def machines_in_somme(somme, machines, groupes):
        """
        création de la liste des machines présentes dans une somme
        :param somme: somme concernée
        :param machines: données machines
        :param groupes: groupes importés
        :return: liste de machines triée par id_categorie, puis par nom
        """
        machines_utilisees = {}
        for key in somme:
            id_groupe = machines.donnees[key]['id_groupe']
            id_categorie = groupes.donnees[id_groupe]['id_cat_mach']
            nom = machines.donnees[key]['nom']
            if id_categorie not in machines_utilisees:
                machines_utilisees[id_categorie] = {}
            machines_utilisees[id_categorie][nom] = key

        return machines_utilisees

    @staticmethod
    def comptes_in_somme(somme, comptes):
        """
        création de la liste des comptes présents dans une somme
        :param somme: somme concernée
        :param comptes: données comptes
        :return: liste de comptes, triée par numéro
        """
        comptes_utilises = {}
        max_size = 0
        for key in somme:
            numero = comptes.donnees[key]['numero']
            if len(numero) > max_size:
                max_size = len(numero)

        for key in somme:
            numero = comptes.donnees[key]['numero']
            num = numero
            for dif in range(len(numero), max_size):
                num = '0' + num
            if key not in comptes_utilises:
                comptes_utilises[key] = num

        return comptes_utilises
