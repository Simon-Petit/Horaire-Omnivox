
from pprint import pprint
def scraper():
    
    import requests
    from bs4 import BeautifulSoup as bs
    import re
    from html import unescape

    # Creation d'un dictionnaire avec user-agent puisque omnivox ne donne pas l'acces au site sans cela.
    headers = {"user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}

    # nom du cegep dans l'url. Exemple : https://MonCegep.omnivox.ca/
    nom_url_cegep = "cegepsth"

    #NoDA = input("Entrer votre numéro de DA : ")
    #PasswordEtu = input("Entrer votre mot de passe : ")
    NoDA = "2269161"
    PasswordEtu = "optimus31"

    print("oui")

    # Creation d'un dictionnaire avec le parametre isModeVueParJour a true pour s'assurer que le scraper va bien marcher .
    isModeVueParJour = {"isModeVueParJour":"true"}

    # Boucle pour que le scraper se reconnecte a omnivox 2 fois car changer les préférences d'affichage ne fonctionne pas a la premiere connexion.
    for _ in range(2):

        # Creation d'une instance de la class Session du module requests pour conserver les coockies de connection. 
        s = requests.Session()

        # Connexion a la page de connexion d'omnivox.
        r = s.get(f"https://{nom_url_cegep}.omnivox.ca/Login/Account/Login?isLogout=1", headers=headers)

        # Creation d'un objet BeautifulSoup avec le code html de r.
        soup = bs(r.text, features="html.parser")

        # Recherche de la valeur de la variable k dans le code html de la page de connexion. Omnivox demande cette valeur pour le login.
        k = soup.find("input",id="k")["value"]

        # Creation d'une variable avec le payload pour la connexion.
        data = {'k': k, 'NoDA': NoDA, 'PasswordEtu': PasswordEtu, "TypeLogin" : "PostSolutionLogin" , "TypeIdentification" : "Etudiant"}

        # Connexion a la page principal.
        r = s.post(f"https://{nom_url_cegep}.omnivox.ca/intr/Module/Identification/Login/Login.aspx", headers=headers, data=data)

        # Requete pour mettre la variable isModeVueParJour a true.
        s.post(f"https://{nom_url_cegep}.omnivox.ca/intr/UI/WebParts/Intraflex_CalendrierScolaire/Webpart_Affichage_Selector.ashx", headers=headers, data=isModeVueParJour)

        # Requete pour s'assurer que les seuls type d'evenement charger son les cours et les examens (desactive Lea, Communaute, Calendrier scolaire et Rendez-Vous).
        s.get(f"https://{nom_url_cegep}.omnivox.ca/intr/UI/WebParts/Intraflex_CalendrierScolaire/WebPart_Affichage3.ashx?filtre-categorie=CalScolaire&filtre-etat=O",headers=headers)
        s.get(f"https://{nom_url_cegep}.omnivox.ca/intr/UI/WebParts/Intraflex_CalendrierScolaire/WebPart_Affichage3.ashx?filtre-categorie=Lea&filtre-etat=N",headers=headers)
        s.get(f"https://{nom_url_cegep}.omnivox.ca/intr/UI/WebParts/Intraflex_CalendrierScolaire/WebPart_Affichage3.ashx?filtre-categorie=Communaute&filtre-etat=N", headers=headers)
        s.get(f"https://{nom_url_cegep}.omnivox.ca/intr/UI/WebParts/Intraflex_CalendrierScolaire/WebPart_Affichage3.ashx?filtre-categorie=RendezVous&filtre-etat=N", headers=headers)
        s.get(f"https://{nom_url_cegep}.omnivox.ca/intr/UI/WebParts/Intraflex_CalendrierScolaire/WebPart_Affichage3.ashx?filtre-categorie=Examen&filtre-etat=O", headers=headers)
        s.get(f"https://{nom_url_cegep}.omnivox.ca/intr/UI/WebParts/Intraflex_CalendrierScolaire/WebPart_Affichage3.ashx?filtre-categorie=Cours&filtre-etat=O", headers=headers)

        # Requete pour recuperer les premiers evenements et les tranformer en str. 
        r2 = s.get(f"https://{nom_url_cegep}.omnivox.ca/intr/UI/WebParts/Intraflex_CalendrierScolaire/WebService/EvenementsWebService.asmx/GetFirstLoad?isMobile=false",headers=headers)

    text = r2.text

    # Creation d'une liste avec chaque evenement comme valeur.
    liste_evenement = text.split("carte-portail carte-evenement")
    t_info = {}
    counter  = 0

    # Boucle pour .pour éviter de faire trop de requetes a omnivox.
    while counter < 50:

        # Boucle sur tous les elements de la liste
        for element in liste_evenement:
            info = {}
            
            # Trouve l'id de l'evenement sur lequel on boucle. Cette valeur est utile pour faire la requete des prochains evenements. Il s'agit d'une chaine de caractere en base 64
            id = re.findall(r"\bdata\-idunifie+\b={1}\\?'{1}[a-zA-Z0-9\/\+\=]+",element)
            
            # Permet de retirer les elements de la liste qui ne sont pas des evenements (puisque qu'il n'ont pas d'id)
            if id == []:
                continue
            else:
                print(id)
            # Fomatage du str id pour enlever les éléments inutile (l'id est une suite d'information encrypter en base 64)
            id = "".join(id)
            id = id.replace("data-idunifie='","")
            info["id"] = id
            
            # Recherche le nom du cours
            titre = re.findall(r"\bdata\-titre\b={1}\\{1}\"{1}[a-zA-Z0-9, &#;:.]+",element)
            titre = "".join(titre)
            titre = titre.replace("data-titre=\\\"","")
            titre = unescape(titre)
            info["titre"] = titre

            # Recherche l'heures de debut et fin du cours
            heure = re.findall(r"\bdata\-heure\b={1}\\{1}\"{1}[a-zA-Z0-9, &#;:]+",element)
            heure = "".join(heure)
            heure = heure.replace("data-heure=\\\"","")
            heure = unescape(heure)
            info["heure"] = heure
            
            # Recherche le type du cours (T = Theorie, L = Laboratoire, A = Activite)
            type_cours = re.findall(r"\bCOURS  \- \b[TLA]|EXAMEN",element)
            type_cours = "".join(type_cours)
            type_cours = type_cours.replace("COURS  - ","")
            info["type_cours"] = type_cours

            # Adapte le re car le local n'est pas a la meme place si il s'agit d'un examen
            if type_cours == "EXAMEN":
                local = re.findall(r'\bcouleur_ZZEX\b[">\\rnt]+[A-Z0-9-]+',element)
                lettre_couleur = "EX"
            else:
                local = re.findall(r'\bcouleur_ZZCR\b[">\\rnt]+[A-Z0-9-]+',element)
                lettre_couleur = "CR"

            # Recherche le numero du local
            local = "".join(local)
            local = local.replace(f"couleur_ZZ{lettre_couleur}\\\">","")
            for i in ["\\","n","t","r"]:
                local = local.replace(i,"")
            info["local"] = local
            
            # Recherche la date du cours
            date = re.findall(r"\bdata\-date\b={1}\\{1}\"{1}[a-zA-Z0-9 &#;]+",element)
            date = "".join(date)
            date = date.replace("data-date=\\\"","")
            date = unescape(date)
            info["date"] = date
            
            counter += 1
            print(counter)

            # Ajout des information du cours au dictionnaire contenant tous les cours 
            t_info[str(counter)] = info

        # Envoie une requete au serveur opur avoir le code HTML des prochains evenement
        next_id = t_info[str(counter)]["id"]
        new_url = f"https://{nom_url_cegep}.omnivox.ca/intr/UI/WebParts/Intraflex_CalendrierScolaire/WebService/EvenementsWebService.asmx/GetLoadMore?direction=Futur&idEvenementReference={next_id}&isMobile=false"
        response = s.get(new_url, headers=headers)

        # Formate les information pour le traitement 
        text = response.text
        liste_evenement = text.split("carte-portail carte-evenement")

        # Sort de la boucle while lorsque le dernier evenement a ete ajouter a t_info
        if liste_evenement == ['{"html":""}']:
            print("break")
            break

    pprint(t_info)
    Mois={'janvier':1,'février':2,'mars':3,'avril':4,'mai':5,'juin':6,'juillet':7,'août':8,'septembre':9,'octobre':10,'novembre':11,'décembre':12}
    for cle in t_info.keys():
        liste_date = t_info[cle]["date"].split()
        liste_heure = t_info[cle]["heure"].split()
        if len(liste_date[1]) == 1:
            liste_date[1] = "0" + liste_date[1]
        if len(liste_heure[0]) == 4:
            liste_heure[0] = "0" + liste_heure[0]
        if len(liste_heure[2]) == 4:
            liste_heure[2] = "0" + liste_heure[2]
        date_time_debut = ''.join(['-'.join([liste_date[3], str(Mois[liste_date[2]]), liste_date[1]]), "T", liste_heure[0], ":00-05:00"])
        date_time_fin = ''.join(['-'.join([liste_date[3], str(Mois[liste_date[2]]), liste_date[1]]), "T", liste_heure[2], ":00-05:00"])
        t_info[cle]["date_time_debut"] = date_time_debut
        t_info[cle]["date_time_fin"] = date_time_fin
        
        if t_info[cle]["type_cours"] == "L":
            t_info[cle]["type_cours"] = "Laboratoire"
        elif t_info[cle]["type_cours"] == "T":
            t_info[cle]["type_cours"] = "Théorie"
        elif t_info[cle]["type_cours"] == "A":
            t_info[cle]["type_cours"] = "Activité"
        del t_info[cle]["date"]
        del t_info[cle]["heure"]
        del t_info[cle]["id"]
        
    return t_info

#pprint(scraper())
scraper()
