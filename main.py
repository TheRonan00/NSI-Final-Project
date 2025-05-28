import customtkinter as ctk
import json
import os
from tkcalendar import Calendar
from datetime import datetime, timedelta
import tkinter as tk
import tkinter.messagebox as tkmb
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def sauvegarder_donnees():
    try:
        with open("user_data.json", "r+", encoding="utf-8") as fichier:
            donnees = json.load(fichier)
            donnees["users"]["default"]["tasks"] = donnees_taches
            donnees["users"]["default"]["lists"] = donnees_listes_taches
            donnees["users"]["default"]["profile"]["level"] = niveau
            donnees["users"]["default"]["profile"]["xp"] = experience_actuelle
            donnees["users"]["default"]["profile"]["coins"] = pieces
            fichier.seek(0)
            json.dump(donnees, fichier, ensure_ascii=False, indent=4)
            fichier.truncate()
        print("Données sauvegardées avec succès")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")

def charger_donnees():
    global donnees_listes_taches, donnees_taches, niveau, experience_actuelle, pieces, experience_maximale
    try:
        if os.path.exists("user_data.json"):
            with open("user_data.json", "r", encoding="utf-8") as fichier:
                donnees = json.load(fichier)
                donnees_taches = donnees["users"]["default"]["tasks"]
                donnees_listes_taches = donnees["users"]["default"]["lists"]
                profil = donnees["users"]["default"]["profile"]
                niveau = profil.get("level", 1)
                experience_actuelle = profil.get("xp", 0)
                pieces = profil.get("coins", 0)
                experience_maximale = int(round(100 * (1.05 ** (niveau - 1))))
            print("Données chargées avec succès")
        else:
            donnees_taches = {}
            donnees_listes_taches = [
                "📥 Toutes",
                "📅 Aujourd'hui",
                "📆 7 Prochains Jours",
                "⏱️ Tâches Quotidiennes",
                "💼 Tâches Professionnelles",
                "📚 Tâches École",
                "🛒 Courses",
                "✈️ Plans de Voyage",
                "📝 Non Planifié"
            ]
            niveau = 1
            experience_actuelle = 0
            pieces = 0
        
        mettre_a_jour_affichage_taches()
        mettre_a_jour_affichage_listes()
    except Exception as e:
        print(f"Erreur lors du chargement: {e}")
        donnees_taches = {}
        donnees_listes_taches = [                
            "📥 Toutes",
            "📅 Aujourd'hui",
            "📆 7 Prochains Jours",
        ]
        niveau = 1
        experience_actuelle = 0
        pieces = 0
            
liste_selectionnee = "📥 Toutes"

def mettre_a_jour_affichage_listes():
    global liste_selectionnee
    for widget in cadre_vue_laterale.winfo_children():
        if isinstance(widget, ctk.CTkButton) and widget not in [bouton_ajouter_liste]:
            widget.destroy()
    
    listes_defaut = donnees_listes_taches[:3]
    listes_personnalisees = donnees_listes_taches[3:]
    
    for index, nom_liste in enumerate(listes_defaut):
        selectionnee = (nom_liste == liste_selectionnee)
        bouton_liste = ctk.CTkButton(
            cadre_vue_laterale, 
            text=nom_liste, 
            fg_color="#1F6AA5" if selectionnee else "transparent",
            hover_color="#1F6AA5",
            anchor="w",
            command=lambda nom=nom_liste: selectionner_liste(nom)
        )
        bouton_liste.grid(row=index, column=0, padx=10, pady=5, sticky="ew")
    
    ligne_courante = len(listes_defaut)
    
    cadre_separateur = ctk.CTkFrame(cadre_vue_laterale, fg_color="transparent")
    cadre_separateur.grid(row=ligne_courante, column=0, sticky="ew", pady=10)
    cadre_separateur.grid_columnconfigure(0, weight=0)
    cadre_separateur.grid_columnconfigure(1, weight=1)
    cadre_separateur.grid_columnconfigure(2, weight=0)
    
    etiquette_mes_listes = ctk.CTkLabel(cadre_separateur, text="Mes listes", font=("", 14, "bold"))
    etiquette_mes_listes.grid(row=0, column=0, sticky="w", padx=10)
    
    bouton_ajout = ctk.CTkButton(cadre_separateur, text="+", width=20, height=20, command=afficher_popup_ajout_liste)
    bouton_ajout.grid(row=0, column=2, sticky="ew", padx=10)
    
    ligne_courante += 1
    
    for index, nom_liste in enumerate(listes_personnalisees):
        selectionnee = (nom_liste == liste_selectionnee)
        bouton_liste = ctk.CTkButton(
            cadre_vue_laterale,
            text=nom_liste,
            fg_color="#1F6AA5" if selectionnee else "transparent",
            hover_color="#1F6AA5",
            anchor="w",
            command=lambda nom=nom_liste: selectionner_liste(nom)
        )
        bouton_liste.grid(row=ligne_courante + index, column=0, padx=10, pady=5, sticky="ew")

def selectionner_liste(nom_liste):
    global liste_selectionnee, etiquette_titre
    liste_selectionnee = nom_liste
    mettre_a_jour_affichage_listes()
    etiquette_titre.configure(text=nom_liste)
    mettre_a_jour_affichage_taches()

def mettre_a_jour_affichage_taches():
    for widget in cadre_taches.winfo_children():
        widget.destroy()
        
    indice_ligne = 0
    
    if liste_selectionnee == "📥 Toutes":
        for nom_liste, liste_taches in donnees_taches.items():
            if liste_taches:
                etiquette_groupe = ctk.CTkLabel(cadre_taches, text=nom_liste, font=("Arial", 14, "bold"))
                etiquette_groupe.grid(row=indice_ligne, column=0, sticky="w", pady=(10, 5))
                indice_ligne += 1
                
                for tache in liste_taches:
                    indice_ligne = afficher_tache(tache, indice_ligne)
    elif liste_selectionnee == "📅 Aujourd'hui":
        aujourd_hui = datetime.now().date()
        aujourd_hui_str = aujourd_hui.strftime("%Y-%m-%d")
        
        for nom_liste, liste_taches in donnees_taches.items():
            taches_auj = [tache for tache in liste_taches if tache["date"] == aujourd_hui_str]
            if taches_auj:
                etiquette_groupe = ctk.CTkLabel(cadre_taches, text=nom_liste, font=("Arial", 14, "bold"))
                etiquette_groupe.grid(row=indice_ligne, column=0, sticky="w", pady=(10, 5))
                indice_ligne += 1
                
                for tache in taches_auj:
                    indice_ligne = afficher_tache(tache, indice_ligne)
    elif liste_selectionnee == "📆 7 Prochains Jours":
        aujourd_hui = datetime.now().date()
        date_fin = aujourd_hui + timedelta(days=7)
        
        for nom_liste, liste_taches in donnees_taches.items():
            prochaines_taches = []
            for tache in liste_taches:
                date_tache = datetime.strptime(tache["date"], "%Y-%m-%d").date()
                if aujourd_hui <= date_tache <= date_fin:
                    prochaines_taches.append(tache)
            
            if prochaines_taches:
                etiquette_groupe = ctk.CTkLabel(cadre_taches, text=nom_liste, font=("Arial", 14, "bold"))
                etiquette_groupe.grid(row=indice_ligne, column=0, sticky="w", pady=(10, 5))
                indice_ligne += 1
                
                for tache in prochaines_taches:
                    indice_ligne = afficher_tache(tache, indice_ligne)
    else:
        liste_taches = donnees_taches.get(liste_selectionnee, [])
        for tache in liste_taches:
            indice_ligne = afficher_tache(tache, indice_ligne)

experience_maximale = 100
experience_par_tache = 10

def afficher_barre_xp():
    global etiquette_xp, barre_xp, cadre_barre_xp

    cadre_barre_xp = ctk.CTkFrame(cadre_principal)
    cadre_barre_xp.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
    etiquette_xp = ctk.CTkLabel(cadre_barre_xp, text=f"Niveau {niveau} | {pieces} 🪙 | XP : {experience_actuelle}/{experience_maximale}")
    etiquette_xp.pack(side="left", padx=10)
    barre_xp = ctk.CTkProgressBar(cadre_barre_xp, width=250)
    barre_xp.set(experience_actuelle / experience_maximale)
    barre_xp.pack(side="left", padx=10, pady=8)

def gagner_experience_pour_tache():
    global experience_actuelle, experience_maximale, niveau
    experience_actuelle += experience_par_tache
    if experience_actuelle >= experience_maximale:
        experience_actuelle -= experience_maximale
        monter_niveau()
    afficher_barre_xp()

def monter_niveau():
    global niveau, experience_maximale, pieces
    niveau += 1
    experience_maximale = int(round(experience_maximale * 1.1))
    pieces += 10
    tkmb.showinfo("Félicitations !", f"Bravo ! Tu passes au niveau {niveau} 🎉\nTu gagnes 15 🪙 pièces !")
    afficher_barre_xp()

def perdre_experience_pour_tache():
    global experience_actuelle, experience_maximale, niveau, pieces
    experience_actuelle -= experience_par_tache
    if experience_actuelle < 0:
        if niveau > 1:
            niveau -= 1
            experience_maximale = int(round(experience_maximale / 1.1))
            experience_actuelle = experience_maximale + experience_actuelle
            pieces = max(0, pieces - 15)
            tkmb.showwarning("Perte de niveau", f"Tu redescends au niveau {niveau}...\nTu perds 15 🪙 pièces.")
        else:
            experience_actuelle = 0
    afficher_barre_xp()

def afficher_tache(tache, indice_ligne):
    cadre_ligne_tache = ctk.CTkFrame(cadre_taches)
    cadre_ligne_tache.grid(row=indice_ligne, column=0, sticky="ew", pady=2)
    cadre_ligne_tache.grid_columnconfigure(0, weight=1)
    cadre_ligne_tache.grid_columnconfigure(1, weight=0)
    cadre_ligne_tache.grid_columnconfigure(2, weight=0)

    variable_cochee = tk.BooleanVar(value=tache.get("checked", False))

    case_a_cocher = ctk.CTkCheckBox(cadre_ligne_tache, text="", variable=variable_cochee)
    case_a_cocher.grid(row=0, column=0, sticky="w")

    etiquette_tache = ctk.CTkLabel(cadre_ligne_tache, text=tache["title"])
    etiquette_tache.grid(row=0, column=0, sticky="w", padx=(30, 0))

    if variable_cochee.get():
        etiquette_tache.configure(font=("", 0, "overstrike"), text_color=("#888888"))

    def au_clic_case():
        if variable_cochee.get():
            etiquette_tache.configure(font=("", 0, "overstrike"), text_color=("#888888"))
            gagner_experience_pour_tache()
        else:
            etiquette_tache.configure(font=("", 0, "normal"), text_color=("#FFFFFF"))
            perdre_experience_pour_tache()
        
        tache["checked"] = variable_cochee.get()
        sauvegarder_donnees()

    case_a_cocher.configure(command=au_clic_case)

    aujourd_hui = datetime.now().date()
    date_tache = datetime.strptime(tache["date"], "%Y-%m-%d").date()
    
    delta = (date_tache - aujourd_hui).days
    
    if delta == 0:
        affichage_date = "Aujourd'hui"
    elif delta == 1:
        affichage_date = "Demain"
    elif delta == -1:
        affichage_date = "Hier"
    else:
        mois = ["janvier", "février", "mars", "avril", "mai", "juin", 
               "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
        jour = date_tache.day
        mois_str = mois[date_tache.month - 1]
        
        if date_tache.year != aujourd_hui.year:
            affichage_date = f"{jour} {mois_str} {date_tache.year}"
        else:
            affichage_date = f"{jour} {mois_str}"

    etiquette_date = ctk.CTkLabel(cadre_ligne_tache, text=affichage_date, text_color="gray")
    etiquette_date.grid(row=0, column=1, padx=(0, 5), sticky="e")

    etiquette_heure = ctk.CTkLabel(cadre_ligne_tache, text=tache["time"], text_color="gray") 
    etiquette_heure.grid(row=0, column=2, padx=(0, 10), sticky="e")

    return indice_ligne + 1

def ajouter_nouvelle_liste(nom_liste):
    if nom_liste and nom_liste not in donnees_listes_taches:
        donnees_listes_taches.append(nom_liste)
        mettre_a_jour_affichage_listes()
        sauvegarder_donnees()
            
def afficher_popup_ajout_liste():
    popup = ctk.CTkToplevel()
    popup.title("Nouvelle Liste")
    popup.geometry("300x200")
    popup.geometry(f"+{int(popup.winfo_screenwidth()/2 - 150)}+{int(popup.winfo_screenheight()/2 - 100)}")
    etiquette_titre_popup = ctk.CTkLabel(popup, text="Créer une nouvelle liste", font=("Arial", 16, "bold"))
    etiquette_titre_popup.pack(pady=20)
    champ_saisie_liste = ctk.CTkEntry(popup, placeholder_text="Nom de la liste", width=200)
    champ_saisie_liste.pack(pady=10)
    def creer_liste():
        nom_liste = champ_saisie_liste.get()
        if nom_liste and nom_liste not in donnees_listes_taches:
            donnees_listes_taches.append(nom_liste)
            mettre_a_jour_affichage_listes()
            sauvegarder_donnees()
            popup.destroy()
    cadre_boutons = ctk.CTkFrame(popup, fg_color="transparent")
    cadre_boutons.pack(pady=20)
    bouton_annuler = ctk.CTkButton(cadre_boutons, text="Annuler", command=popup.destroy)
    bouton_annuler.pack(side="left", padx=10)
    bouton_creer = ctk.CTkButton(cadre_boutons, text="Créer", command=creer_liste)
    bouton_creer.pack(side="left", padx=10)

def afficher_popup_ajout_tache():
    popup = ctk.CTkToplevel()
    popup.title("Nouvelle Tâche")
    popup.geometry("400x350")
    popup.geometry(f"+{int(popup.winfo_screenwidth()/2 - 200)}+{int(popup.winfo_screenheight()/2 - 175)}")
    etiquette_titre_fenetre = ctk.CTkLabel(popup, text="Créer une nouvelle tâche", font=("Arial", 16, "bold"))
    etiquette_titre_fenetre.pack(pady=20)
    champ_saisie_tache = ctk.CTkEntry(popup, placeholder_text="Nom de la tâche", width=300)
    champ_saisie_tache.pack(pady=10)
    etiquette_liste = ctk.CTkLabel(popup, text="Liste")
    etiquette_liste.pack(anchor="w", padx=50)
    listes_disponibles = [nom_liste for nom_liste in donnees_listes_taches if nom_liste not in ["📥 Toutes", "📅 Aujourd'hui", "📆 7 Prochains Jours"]]
    variable_liste = ctk.StringVar(value=listes_disponibles[0] if listes_disponibles else "")
    menu_deroulant_liste = ctk.CTkOptionMenu(popup, values=listes_disponibles, variable=variable_liste, width=300)
    menu_deroulant_liste.pack(pady=(0,10))
    cadre_date = ctk.CTkFrame(popup, fg_color="transparent")
    cadre_date.pack(fill="x", padx=50)
    etiquette_date = ctk.CTkLabel(cadre_date, text="Date")
    etiquette_date.pack(anchor="w")
    aujourd_hui_str = datetime.now().strftime("%Y-%m-%d")
    variable_date = ctk.StringVar(value=aujourd_hui_str)
    champ_saisie_date = ctk.CTkEntry(cadre_date, textvariable=variable_date, width=250, state="readonly")
    champ_saisie_date.pack(side="left", pady=(0,10))
    def ouvrir_calendrier():
        fenetre_calendrier = ctk.CTkToplevel(popup)
        fenetre_calendrier.title("Sélectionner une date")
        fenetre_calendrier.geometry("300x300")
        fenetre_calendrier.geometry(f"+{int(popup.winfo_x() + popup.winfo_width())}+{int(popup.winfo_y())}")
        calendrier = Calendar(fenetre_calendrier, selectmode='day', date_pattern='yyyy-mm-dd')
        calendrier.pack(expand=True, fill="both", padx=10, pady=10)
        def definir_date():
            variable_date.set(calendrier.get_date())
            fenetre_calendrier.destroy()
        bouton_valider_date = ctk.CTkButton(fenetre_calendrier, text="Sélectionner", command=definir_date)
        bouton_valider_date.pack(pady=10)
    bouton_calendrier = ctk.CTkButton(cadre_date, text="📅", width=40, command=ouvrir_calendrier)
    bouton_calendrier.pack(side="left", padx=(10,0))
    etiquette_heure = ctk.CTkLabel(popup, text="Heure")
    etiquette_heure.pack(anchor="w", padx=50)
    options_heures = [f"{h:02d}:00" for h in range(24)]
    variable_heure = ctk.StringVar(value="09:00")
    menu_deroulant_heure = ctk.CTkOptionMenu(popup, values=options_heures, variable=variable_heure, width=300)
    menu_deroulant_heure.pack(pady=(0,10))
    def ajouter_tache():
        nom_tache = champ_saisie_tache.get()
        date_tache = variable_date.get()
        heure_tache = variable_heure.get()
        liste_choisie = variable_liste.get()
        if nom_tache:
            if not date_tache:
                maintenant = datetime.now()
                date_tache = maintenant.strftime("%Y-%m-%d")
            nouvelle_tache = {
                "title": nom_tache,
                "date": date_tache,
                "time": heure_tache,
                "checked": False
            }
            if liste_choisie not in donnees_taches:
                donnees_taches[liste_choisie] = []
            donnees_taches[liste_choisie].append(nouvelle_tache)
            mettre_a_jour_affichage_taches()
            sauvegarder_donnees()
            popup.destroy()
    cadre_boutons = ctk.CTkFrame(popup, fg_color="transparent")
    cadre_boutons.pack(pady=(0, 10))
    bouton_annuler = ctk.CTkButton(cadre_boutons, text="Annuler", command=popup.destroy)
    bouton_annuler.pack(side="left", padx=(0,5))
    bouton_creer = ctk.CTkButton(cadre_boutons, text="Créer", command=ajouter_tache)
    bouton_creer.pack(side="right", padx=(5,0))

def afficher_boutique():
    try:
        with open("user_data.json", "r", encoding="utf-8") as fichier:
            donnees = json.load(fichier)
            articles_boutique = donnees["users"]["default"]["shop_items"]
    except Exception:
        articles_boutique = []
    fenetre_boutique = ctk.CTkToplevel()
    fenetre_boutique.title("Boutique de Récompenses")
    fenetre_boutique.geometry("500x600")
    fenetre_boutique.geometry(f"+{int(fenetre_boutique.winfo_screenwidth()/2 - 250)}+{int(fenetre_boutique.winfo_screenheight()/2 - 300)}")
    cadre_titre = ctk.CTkFrame(fenetre_boutique, fg_color="transparent")
    cadre_titre.pack(fill="x", padx=20, pady=10)
    etiquette_titre_boutique = ctk.CTkLabel(cadre_titre, text="Boutique de Récompenses", font=("Arial", 24, "bold"))
    etiquette_titre_boutique.pack(side="left")
    etiquette_pieces_boutique = ctk.CTkLabel(cadre_titre, text=f"🪙 {pieces} pièces", font=("Arial", 18))
    etiquette_pieces_boutique.pack(side="right")
    cadre_objets = ctk.CTkFrame(fenetre_boutique)
    cadre_objets.pack(fill="both", expand=True, padx=20, pady=10)
    for article in articles_boutique:
        cadre_objet = ctk.CTkFrame(cadre_objets)
        cadre_objet.pack(fill="x", padx=10, pady=5)
        cadre_infos = ctk.CTkFrame(cadre_objet, fg_color="transparent")
        cadre_infos.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        cadre_entete = ctk.CTkFrame(cadre_infos, fg_color="transparent")
        cadre_entete.pack(fill="x", pady=(0, 5))
        etiquette_icone = ctk.CTkLabel(cadre_entete, text=article["icon"], font=("Arial", 20))
        etiquette_icone.pack(side="left", padx=(0, 10))
        etiquette_nom = ctk.CTkLabel(cadre_entete, text=article["name"], font=("Arial", 16, "bold"))
        etiquette_nom.pack(side="left")
        etiquette_description = ctk.CTkLabel(cadre_infos, text=article["description"], text_color="gray")
        etiquette_description.pack(anchor="w")
        def creer_commande_achat(prix_article, nom_article, icone_article):
            def acheter_article():
                global pieces
                if pieces >= prix_article:
                    pieces -= prix_article
                    etiquette_pieces_boutique.configure(text=f"🪙 {pieces} pièces")
                    afficher_barre_xp()
                    sauvegarder_donnees()
                    tkmb.showinfo(
                        "Achat réussi!",
                        f"Vous avez acheté {icone_article} {nom_article}!\nProfitez bien de votre récompense !"
                    )
                else:
                    tkmb.showwarning(
                        "Erreur",
                        f"Vous n'avez pas assez de pièces !\nIl vous manque {prix_article - pieces} pièces."
                    )
            return acheter_article
        bouton_acheter = ctk.CTkButton(
            cadre_objet,
            text=f"Acheter ({article['price']} 🪙)",
            command=creer_commande_achat(article["price"], article["name"], article["icon"])
        )
        bouton_acheter.pack(side="right", padx=10, pady=5)

def afficher_profil():
    try:
        with open("user_data.json", "r", encoding="utf-8") as fichier:
            donnees = json.load(fichier)
            profil = donnees["users"]["default"]["profile"]
            nom_utilisateur = profil["username"]
            chemin_image_profil = profil["profile_picture"]
    except Exception:
        nom_utilisateur = "Utilisateur"
        chemin_image_profil = "assets/default_profile.png"
    fenetre_profil = ctk.CTkToplevel()
    fenetre_profil.title("Profil Utilisateur")
    fenetre_profil.geometry("400x500")
    fenetre_profil.geometry(f"+{int(fenetre_profil.winfo_screenwidth()/2 - 200)}+{int(fenetre_profil.winfo_screenheight()/2 - 250)}")
    cadre_principal_profil = ctk.CTkFrame(fenetre_profil)
    cadre_principal_profil.pack(fill="both", expand=True, padx=20, pady=20)
    try:
        image_profil = ctk.CTkImage(
            light_image=Image.open(chemin_image_profil),
            dark_image=Image.open(chemin_image_profil),
            size=(150, 150)
        )
        etiquette_image_profil = ctk.CTkLabel(cadre_principal_profil, image=image_profil, text="")
        etiquette_image_profil.pack(pady=20)
    except Exception:
        etiquette_image_profil = ctk.CTkLabel(cadre_principal_profil, text="👤", font=("Arial", 80))
        etiquette_image_profil.pack(pady=20)
    etiquette_nom_utilisateur = ctk.CTkLabel(cadre_principal_profil, text=nom_utilisateur, font=("Arial", 24, "bold"))
    etiquette_nom_utilisateur.pack(pady=10)
    cadre_stats = ctk.CTkFrame(cadre_principal_profil)
    cadre_stats.pack(fill="x", padx=20, pady=20)
    cadre_niveau = ctk.CTkFrame(cadre_stats, fg_color="transparent")
    cadre_niveau.pack(fill="x", pady=5, padx=10)
    etiquette_niveau = ctk.CTkLabel(cadre_niveau, text="Niveau", font=("Arial", 16))
    etiquette_niveau.pack(side="left")
    valeur_niveau = ctk.CTkLabel(cadre_niveau, text=str(niveau), font=("Arial", 16, "bold"))
    valeur_niveau.pack(side="right")
    cadre_xp = ctk.CTkFrame(cadre_stats, fg_color="transparent")
    cadre_xp.pack(fill="x", pady=5, padx=10)
    etiquette_xp_profil = ctk.CTkLabel(cadre_xp, text="XP", font=("Arial", 16))
    etiquette_xp_profil.pack(side="left")
    valeur_xp = ctk.CTkLabel(cadre_xp, text=f"{experience_actuelle}/{experience_maximale}", font=("Arial", 16, "bold"))
    valeur_xp.pack(side="right")
    barre_xp_profil = ctk.CTkProgressBar(cadre_stats)
    barre_xp_profil.set(experience_actuelle / experience_maximale)
    barre_xp_profil.pack(fill="x", pady=10, padx=10)
    cadre_pieces = ctk.CTkFrame(cadre_stats, fg_color="transparent")
    cadre_pieces.pack(fill="x", pady=5, padx=10)
    etiquette_pieces_profil = ctk.CTkLabel(cadre_pieces, text="Pièces", font=("Arial", 16))
    etiquette_pieces_profil.pack(side="left")
    valeur_pieces = ctk.CTkLabel(cadre_pieces, text=f"{pieces} 🪙", font=("Arial", 16, "bold"))
    valeur_pieces.pack(side="right")
    bouton_modifier_profil = ctk.CTkButton(
        cadre_principal_profil,
        text="Modifier le profil",
        command=lambda: tkmb.showinfo("Information", "Cette fonctionnalité sera disponible prochainement !")
    )
    bouton_modifier_profil.pack(pady=20)

racine = ctk.CTk()
racine.title("Liste de Tâches")
racine.geometry("900x600")
racine.minsize(900, 450)

try:
    racine.iconbitmap("assets/favicon.ico")
except Exception:
    pass

racine.grid_columnconfigure(0, weight=1)
racine.grid_rowconfigure(0, weight=1)

conteneur = ctk.CTkFrame(racine)
conteneur.grid(row=0, column=0, sticky="nsew")
conteneur.grid_columnconfigure(0, weight=0)
conteneur.grid_columnconfigure(1, weight=0)
conteneur.grid_columnconfigure(2, weight=1)
conteneur.grid_rowconfigure(0, weight=1)

cadre_navigation = ctk.CTkFrame(conteneur, width=60, corner_radius=0)
cadre_navigation.grid(row=0, column=0, sticky="nsw", padx=(0,10), pady=0)
cadre_navigation.grid_propagate(False)
cadre_navigation.grid_rowconfigure(99, weight=1)

bouton_navigation_1 = ctk.CTkButton(cadre_navigation, text="🏠", width=40, height=40, fg_color="#1F6AA5")
bouton_navigation_1.grid(row=0, column=0, padx=10, pady=(10,5))

bouton_navigation_2 = ctk.CTkButton(cadre_navigation, text="🛒", width=40, height=40, fg_color="#1F6AA5", command=afficher_boutique)
bouton_navigation_2.grid(row=1, column=0, padx=10, pady=5)

bouton_navigation_3 = ctk.CTkButton(cadre_navigation, text="👤", width=40, height=40, fg_color="#1F6AA5", command=afficher_profil)
bouton_navigation_3.grid(row=2, column=0, padx=10, pady=5)

cadre_vue_laterale = ctk.CTkFrame(conteneur, width=220)
cadre_vue_laterale.grid(row=0, column=1, sticky="nsw", pady=10)
cadre_vue_laterale.grid_propagate(False)
cadre_vue_laterale.grid_rowconfigure(99, weight=1)

etiquette_listes_titre = ctk.CTkLabel(cadre_vue_laterale, text="Listes", font=("Arial", 14, "bold"))
etiquette_listes_titre.grid(row=0, column=0, padx=10, pady=(5, 5), sticky="w")

bouton_ajouter_liste = ctk.CTkButton(cadre_vue_laterale, text="+ Nouvelle Liste", command=afficher_popup_ajout_liste,
                            fg_color="transparent", anchor="w")
bouton_ajouter_liste.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

donnees_listes_taches = []

cadre_principal = ctk.CTkFrame(conteneur)
cadre_principal.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
cadre_principal.grid_columnconfigure(0, weight=1)
cadre_principal.grid_rowconfigure(2, weight=1)

cadre_barre_superieure = ctk.CTkFrame(cadre_principal, fg_color="transparent")
cadre_barre_superieure.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
cadre_barre_superieure.grid_columnconfigure(0, weight=1)
cadre_barre_superieure.grid_columnconfigure(1, weight=0)

etiquette_titre = ctk.CTkLabel(cadre_barre_superieure, text=liste_selectionnee, font=("Arial", 18, "bold"), fg_color="transparent")
etiquette_titre.grid(row=0, column=0, sticky="w")

bouton_ajouter_tache = ctk.CTkButton(cadre_principal, text="+ Ajouter une tâche", height=35, command=afficher_popup_ajout_tache)
bouton_ajouter_tache.grid(row=1, column=0, sticky="ew", padx=10, pady=20)

cadre_taches = ctk.CTkFrame(cadre_principal, fg_color="transparent")
cadre_taches.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
cadre_taches.grid_columnconfigure(0, weight=1)

donnees_taches = {}

charger_donnees()
afficher_barre_xp()

racine.protocol("WM_DELETE_WINDOW", lambda: (sauvegarder_donnees(), racine.destroy()))
racine.mainloop()