import customtkinter as ctk
import json
import os
from tkcalendar import Calendar
from datetime import datetime, timedelta
import tkinter as tk
import tkinter.messagebox as tkmb
from PIL import Image

# -- Configurer CustomTkinter pour un thème sombre et une couleur principale bleue
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# -- Fonction pour sauvegarder les données dans un fichier JSON
def save_data():
    try:
        # Sauvegarder les données dans user_data.json
        with open("user_data.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            data["users"]["default"]["tasks"] = tasks_data
            data["users"]["default"]["lists"] = task_lists_data
            # Sauvegarder les informations du profil
            data["users"]["default"]["profile"]["level"] = level
            data["users"]["default"]["profile"]["xp"] = current_xp
            data["users"]["default"]["profile"]["coins"] = coins
            file.seek(0)
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.truncate()
        print("Données sauvegardées avec succès")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")

# -- Fonction pour charger les données depuis un fichier JSON
def load_data():
    global task_lists_data, tasks_data, level, current_xp, coins, xp_max
    try:
        # Charger les données depuis user_data.json
        if os.path.exists("user_data.json"):
            with open("user_data.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                tasks_data = data["users"]["default"]["tasks"]
                task_lists_data = data["users"]["default"]["lists"]
                # Charger les informations du profil
                profile_data = data["users"]["default"]["profile"]
                level = profile_data.get("level", 1)
                current_xp = profile_data.get("xp", 0)
                coins = profile_data.get("coins", 0)
                xp_max = int(round(100 * (1.05 ** (level - 1))))  # Recalculer xp_max basé sur le niveau
            print("Données chargées avec succès")
        else:
            # Données par défaut si le fichier n'existe pas
            tasks_data = {}
            # Liste par défaut si aucune sauvegarde n'existe
            task_lists_data = [
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
            # Valeurs par défaut pour le profil
            level = 1
            current_xp = 0
            coins = 0
        
        update_tasks_display()
        update_lists_display()
    except Exception as e:
        print(f"Erreur lors du chargement: {e}")
        tasks_data = {}
        task_lists_data = [                
            "📥 Toutes",
            "📅 Aujourd'hui",
            "📆 7 Prochains Jours",
        ]
        level = 1
        current_xp = 0
        coins = 0
            
# Ajouter la variable globale pour la liste sélectionnée
selected_list = "📥 Toutes"

def update_lists_display():
    global selected_list
    # Supprimer les anciens boutons de liste
    for widget in sideview_frame.winfo_children():
        if isinstance(widget, ctk.CTkButton) and widget not in [add_list_btn]:
            widget.destroy()
    
    # Listes par défaut (3 premières listes)
    default_lists = task_lists_data[:3]
    custom_lists = task_lists_data[3:]
    
    # Afficher les listes par défaut
    for index, list_name in enumerate(default_lists):
        is_selected = (list_name == selected_list)
        list_btn = ctk.CTkButton(
            sideview_frame, 
            text=list_name, 
            fg_color="#1F6AA5" if is_selected else "transparent",
            hover_color="#1F6AA5",
            anchor="w",
            command=lambda name=list_name: select_list(name)
        )
        list_btn.grid(row=index, column=0, padx=10, pady=5, sticky="ew")
    
    current_row = len(default_lists)
    
    # Ajouter le séparateur et le titre "Mes listes"
    separator_frame = ctk.CTkFrame(sideview_frame, fg_color="transparent")
    separator_frame.grid(row=current_row, column=0, sticky="ew", pady=10)
    separator_frame.grid_columnconfigure(0, weight=0)
    separator_frame.grid_columnconfigure(1, weight=1)
    separator_frame.grid_columnconfigure(2, weight=0)
    
    # Titre "Mes listes"
    mes_listes_label = ctk.CTkLabel(separator_frame, text="Mes listes", font=("", 14, "bold"))
    mes_listes_label.grid(row=0, column=0, sticky="w", padx=10)
    
    # Bouton + pour ajouter une nouvelle liste
    add_btn = ctk.CTkButton(separator_frame, text="+", width=20, height=20, command=show_add_list_popup)
    add_btn.grid(row=0, column=2, sticky="ew", padx=10)
    
    current_row += 1
    
    # Afficher les listes personnalisées
    for index, list_name in enumerate(custom_lists):
        is_selected = (list_name == selected_list)
        list_btn = ctk.CTkButton(
            sideview_frame,
            text=list_name,
            fg_color="#1F6AA5" if is_selected else "transparent",
            hover_color="#1F6AA5",
            anchor="w",
            command=lambda name=list_name: select_list(name)
        )
        list_btn.grid(row=current_row + index, column=0, padx=10, pady=5, sticky="ew")

def select_list(list_name):
    global selected_list, title_label
    selected_list = list_name
    update_lists_display()  # Mettre à jour l'affichage des listes pour refléter la sélection
    title_label.configure(text=list_name)  # Mettre à jour le titre
    update_tasks_display()  # Mettre à jour l'affichage des tâches

def update_tasks_display():
    # Mettre à jour l'affichage
    for widget in tasks_frame.winfo_children():
        widget.destroy()
        
    row_index = 0
    
    # Si "Toutes" est sélectionné, afficher toutes les tâches
    if selected_list == "📥 Toutes":
        for list_name, tasks_list in tasks_data.items():
            if tasks_list:  # Ne pas afficher les listes vides
                # Titre du groupe
                group_label = ctk.CTkLabel(tasks_frame, text=list_name, font=("Arial", 14, "bold"))
                group_label.grid(row=row_index, column=0, sticky="w", pady=(10, 5))
                row_index += 1
                
                # Afficher les tâches de cette liste
                for task in tasks_list:
                    row_index = display_task(task, row_index)
    # Si "Aujourd'hui" est sélectionné, afficher uniquement les tâches d'aujourd'hui
    elif selected_list == "📅 Aujourd'hui":
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")
        
        # Parcourir toutes les listes pour trouver les tâches d'aujourd'hui
        for list_name, tasks_list in tasks_data.items():
            today_tasks = [task for task in tasks_list if task["date"] == today_str]
            if today_tasks:  # Ne pas afficher les listes vides
                # Titre du groupe
                group_label = ctk.CTkLabel(tasks_frame, text=list_name, font=("Arial", 14, "bold"))
                group_label.grid(row=row_index, column=0, sticky="w", pady=(10, 5))
                row_index += 1
                
                # Afficher les tâches d'aujourd'hui de cette liste
                for task in today_tasks:
                    row_index = display_task(task, row_index)
    # Si "7 Prochains Jours" est sélectionné
    elif selected_list == "📆 7 Prochains Jours":
        today = datetime.now().date()
        # Calculer la date de fin (7 jours après aujourd'hui)
        end_date = today + timedelta(days=7)
        
        # Parcourir toutes les listes pour trouver les tâches des 7 prochains jours
        for list_name, tasks_list in tasks_data.items():
            # Filtrer les tâches qui sont dans la période
            next_week_tasks = []
            for task in tasks_list:
                task_date = datetime.strptime(task["date"], "%Y-%m-%d").date()
                if today <= task_date <= end_date:
                    next_week_tasks.append(task)
            
            if next_week_tasks:  # Ne pas afficher les listes vides
                # Titre du groupe
                group_label = ctk.CTkLabel(tasks_frame, text=list_name, font=("Arial", 14, "bold"))
                group_label.grid(row=row_index, column=0, sticky="w", pady=(10, 5))
                row_index += 1
                
                # Afficher les tâches de la semaine de cette liste
                for task in next_week_tasks:
                    row_index = display_task(task, row_index)
    else:
        # Afficher uniquement les tâches de la liste sélectionnée
        tasks_list = tasks_data.get(selected_list, [])
        for task in tasks_list:
            row_index = display_task(task, row_index)

# === BARRE D'XP - AJOUT ICI ===
xp_max = 100
xp_per_task = 10

def show_xp_bar():
    global xp_label, xp_progress, xp_bar_frame

    # Crée la nouvelle frame en bas du main_frame
    xp_bar_frame = ctk.CTkFrame(main_frame)
    xp_bar_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
    # Label XP
    xp_label = ctk.CTkLabel(xp_bar_frame, text=f"Niveau {level} | {coins} 🪙 | XP : {current_xp}/{xp_max}")
    xp_label.pack(side="left", padx=10)
    # Barre de progression XP
    xp_progress = ctk.CTkProgressBar(xp_bar_frame, width=250)
    xp_progress.set(current_xp / xp_max)
    xp_progress.pack(side="left", padx=10, pady=8)

def gain_xp_for_task():
    global current_xp, xp_max, level
    current_xp += xp_per_task
    if current_xp >= xp_max:
        current_xp -= xp_max
        level_up()
    show_xp_bar()

def level_up():
    global level, xp_max, coins
    level += 1
    xp_max = int(round(xp_max * 1.1))
    coins += 10  # Ajout de 15 coins à chaque level up
    try:
        ctk.CTkMessagebox(title="Félicitations !", message=f"Bravo ! Tu passes au niveau {level} 🎉\nTu gagnes 15 🪙 coins !", icon="info")
    except Exception:
        tkmb.showinfo("Félicitations !", f"Bravo ! Tu passes au niveau {level} 🎉\nTu gagnes 15 🪙 coins !")
    show_xp_bar()

def lose_xp_for_task():
    global current_xp, xp_max, level, coins
    current_xp -= xp_per_task
    if current_xp < 0:
        if level > 1:
            level -= 1
            xp_max = int(round(xp_max / 1.1))
            current_xp = xp_max + current_xp  # current_xp est négatif
            coins = max(0, coins - 15)  # On retire 15 coins, sans descendre sous 0
            try:
                ctk.CTkMessagebox(title="Perte de niveau", message=f"Tu redescends au niveau {level}...\nTu perds 15 🪙 coins.", icon="warning")
            except Exception:
                tkmb.showwarning("Perte de niveau", f"Tu redescends au niveau {level}...\nTu perds 15 🪙 coins.")
        else:
            current_xp = 0
    show_xp_bar()

def display_task(task, row_index):
    task_row_frame = ctk.CTkFrame(tasks_frame)
    task_row_frame.grid(row=row_index, column=0, sticky="ew", pady=2)
    task_row_frame.grid_columnconfigure(0, weight=1)  # checkbox + label
    task_row_frame.grid_columnconfigure(1, weight=0)  # date
    task_row_frame.grid_columnconfigure(2, weight=0)  # heure

    # Variable de contrôle pour la checkbox
    checked_var = tk.BooleanVar(value=task.get("checked", False))

    # Checkbox
    checkbox = ctk.CTkCheckBox(task_row_frame, text="", variable=checked_var)
    checkbox.grid(row=0, column=0, sticky="w")

    # Label de la tâche (dans la même colonne que la checkbox, mais avec un padding)
    task_label = ctk.CTkLabel(task_row_frame, text=task["title"])
    task_label.grid(row=0, column=0, sticky="w", padx=(30, 0))

    # Appliquer le style initial si la tâche est déjà cochée
    if checked_var.get():
        task_label.configure(font=("", 0, "overstrike"), text_color=("#888888"))

    # --- CALLBACK pour la barre d'XP et le style barré ---
    def on_task_checked():
        if checked_var.get():
            # Texte barré et opacité réduite, police par défaut
            task_label.configure(font=("", 0, "overstrike"), text_color=("#888888"))
            gain_xp_for_task()
        else:
            # Texte normal, police par défaut
            task_label.configure(font=("", 0, "normal"), text_color=("#FFFFFF"))
            lose_xp_for_task()
        
        # Mettre à jour l'état de la tâche dans les données
        task["checked"] = checked_var.get()
        save_data()  # Sauvegarder les données après chaque changement d'état

    checkbox.configure(command=on_task_checked)
    # --- FIN XP ---

    # Formatage de la date
    today = datetime.now().date()
    task_datetime = datetime.strptime(task["date"], "%Y-%m-%d").date()
    
    # Calcul de la différence en jours
    delta = (task_datetime - today).days
    
    if delta == 0:
        display_date = "Aujourd'hui"
    elif delta == 1:
        display_date = "Demain"
    elif delta == -1:
        display_date = "Hier"
    else:
        # Conversion de la date en format français
        mois = ["janvier", "février", "mars", "avril", "mai", "juin", 
               "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
        jour = task_datetime.day
        mois_str = mois[task_datetime.month - 1]
        
        # Ajouter l'année si différente de l'année actuelle
        if task_datetime.year != today.year:
            display_date = f"{jour} {mois_str} {task_datetime.year}"
        else:
            display_date = f"{jour} {mois_str}"

    date_label = ctk.CTkLabel(task_row_frame, text=display_date, text_color="gray")
    date_label.grid(row=0, column=1, padx=(0, 5), sticky="e")

    time_label = ctk.CTkLabel(task_row_frame, text=task["time"], text_color="gray") 
    time_label.grid(row=0, column=2, padx=(0, 10), sticky="e")

    return row_index + 1

def add_new_list(list_name):
    if list_name and list_name not in task_lists_data:
        task_lists_data.append(list_name)
        update_lists_display()
        save_data()  # Sauvegarder après l'ajout
            
def show_add_list_popup():
    # Créer une nouvelle fenêtre popup
    popup = ctk.CTkToplevel()
    popup.title("Nouvelle Liste")
    popup.geometry("300x200")
    
    # Centrer la popup
    popup.geometry(f"+{int(popup.winfo_screenwidth()/2 - 150)}+{int(popup.winfo_screenheight()/2 - 100)}")
    
    # Ajouter les widgets dans la popup
    title_label = ctk.CTkLabel(popup, text="Créer une nouvelle liste", font=("Arial", 16, "bold"))
    title_label.pack(pady=20)
    
    list_entry = ctk.CTkEntry(popup, placeholder_text="Nom de la liste", width=200)
    list_entry.pack(pady=10)
    
    def create_list():
        list_name = list_entry.get()
        if list_name and list_name not in task_lists_data:
            task_lists_data.append(list_name)
            update_lists_display()
            save_data()  # Sauvegarder après l'ajout
            popup.destroy()
    
    # Boutons Annuler/Créer
    buttons_frame = ctk.CTkFrame(popup, fg_color="transparent")
    buttons_frame.pack(pady=20)
    
    cancel_btn = ctk.CTkButton(buttons_frame, text="Annuler", command=popup.destroy)
    cancel_btn.pack(side="left", padx=10)
    
    create_btn = ctk.CTkButton(buttons_frame, text="Créer", command=create_list)
    create_btn.pack(side="left", padx=10)
    
def show_add_task_popup():
    # Créer une nouvelle fenêtre popup
    popup = ctk.CTkToplevel()
    popup.title("Nouvelle Tâche")
    popup.geometry("400x350")  # Augmenté la hauteur pour le nouveau champ
    
    # Centrer la popup
    popup.geometry(f"+{int(popup.winfo_screenwidth()/2 - 200)}+{int(popup.winfo_screenheight()/2 - 175)}")
    
    # Ajouter les widgets dans la popup
    title_label = ctk.CTkLabel(popup, text="Créer une nouvelle tâche", font=("Arial", 16, "bold"))
    title_label.pack(pady=20)
    
    task_entry = ctk.CTkEntry(popup, placeholder_text="Nom de la tâche", width=300)
    task_entry.pack(pady=10)
    
    # Menu déroulant pour les listes
    list_label = ctk.CTkLabel(popup, text="Liste")
    list_label.pack(anchor="w", padx=50)
    
    # Filtrer les listes spéciales
    available_lists = [list_name for list_name in task_lists_data 
                      if list_name not in ["📥 Toutes", "📅 Aujourd'hui", "📆 7 Prochains Jours"]]
    
    list_var = ctk.StringVar(value=available_lists[0] if available_lists else "")  # Valeur par défaut
    list_dropdown = ctk.CTkOptionMenu(popup, values=available_lists, variable=list_var, width=300)
    list_dropdown.pack(pady=(0,10))
    
    # Frame pour la date
    date_frame = ctk.CTkFrame(popup, fg_color="transparent")
    date_frame.pack(fill="x", padx=50)
    
    date_label = ctk.CTkLabel(date_frame, text="Date")
    date_label.pack(anchor="w")
    
    # Préremplir la date avec aujourd'hui
    today_str = datetime.now().strftime("%Y-%m-%d")
    date_var = ctk.StringVar(value=today_str)
    date_entry = ctk.CTkEntry(date_frame, textvariable=date_var, width=250, state="readonly")
    date_entry.pack(side="left", pady=(0,10))
    
    def open_calendar():
        # Créer une nouvelle fenêtre pour le calendrier
        cal_window = ctk.CTkToplevel(popup)
        cal_window.title("Sélectionner une date")
        cal_window.geometry("300x300")
        
        # Centrer la fenêtre du calendrier
        cal_window.geometry(f"+{int(popup.winfo_x() + popup.winfo_width())}+{int(popup.winfo_y())}")

        # Créer le calendrier
        cal = Calendar(cal_window, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(expand=True, fill="both", padx=10, pady=10)
        
        def set_date():
            date_var.set(cal.get_date())
            cal_window.destroy()
        
        # Bouton pour valider la sélection
        select_btn = ctk.CTkButton(cal_window, text="Sélectionner", command=set_date)
        select_btn.pack(pady=10)
    
    cal_btn = ctk.CTkButton(date_frame, text="📅", width=40, command=open_calendar)
    cal_btn.pack(side="left", padx=(10,0))
    
    # Menu déroulant pour les heures
    time_label = ctk.CTkLabel(popup, text="Heure")
    time_label.pack(anchor="w", padx=50)
    
    # Générer la liste des heures possibles (00:00 à 23:00)
    time_options = [f"{h:02d}:00" for h in range(24)]
    
    time_var = ctk.StringVar(value="09:00")  # Valeur par défaut 9h
    time_dropdown = ctk.CTkOptionMenu(popup, values=time_options, variable=time_var, width=300)
    time_dropdown.pack(pady=(0,10))
    
    def add_task():
        task_name = task_entry.get()
        task_date = date_var.get()
        task_time = time_var.get()
        selected_list = list_var.get()
        
        if task_name:
            # Si pas de date spécifiée, utiliser aujourd'hui
            if not task_date:
                now = datetime.now()
                task_date = now.strftime("%Y-%m-%d")
                
            # Créer la nouvelle tâche avec la nouvelle structure
            new_task = {
                "title": task_name,
                "date": task_date,
                "time": task_time,
                "checked": False
            }
                
            # Ajouter la tâche à la liste sélectionnée
            if selected_list not in tasks_data:
                tasks_data[selected_list] = []
            tasks_data[selected_list].append(new_task)
                
            update_tasks_display()
            
            # Sauvegarder les données après l'ajout d'une tâche
            save_data()
            
            popup.destroy()
    
    # Boutons Annuler/Créer
    buttons_frame = ctk.CTkFrame(popup, fg_color="transparent")
    buttons_frame.pack(pady=(0, 10))
    
    cancel_btn = ctk.CTkButton(buttons_frame, text="Annuler", command=popup.destroy)
    cancel_btn.pack(side="left", padx=(0,5))
    
    create_btn = ctk.CTkButton(buttons_frame, text="Créer", command=add_task)
    create_btn.pack(side="right", padx=(5,0))

# === SYSTÈME DE COINS ET BOUTIQUE ===
coins = 0  # Ajout du système de coins

def show_shop():
    # Charger les items de la boutique depuis le fichier JSON
    try:
        with open("user_data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            shop_items = data["users"]["default"]["shop_items"]
    except Exception:
        # Items par défaut en cas d'erreur
        shop_items = [
            {
                "name": "Temps de Média",
                "price": 100,
                "description": "30 minutes de temps libre pour regarder des vidéos ou utiliser les réseaux sociaux",
                "icon": "📱"
            },
            {
                "name": "Temps de Repos",
                "price": 50,
                "description": "15 minutes de pause bien méritée",
                "icon": "😴"
            }
        ]

    # Créer une nouvelle fenêtre pour la boutique
    shop_window = ctk.CTkToplevel()
    shop_window.title("Boutique de Récompenses")
    shop_window.geometry("500x600")
    
    # Centrer la fenêtre
    shop_window.geometry(f"+{int(shop_window.winfo_screenwidth()/2 - 250)}+{int(shop_window.winfo_screenheight()/2 - 300)}")
    
    # Titre de la boutique
    title_frame = ctk.CTkFrame(shop_window, fg_color="transparent")
    title_frame.pack(fill="x", padx=20, pady=10)
    
    title_label = ctk.CTkLabel(title_frame, text="Boutique de Récompenses", font=("Arial", 24, "bold"))
    title_label.pack(side="left")
    
    coins_label = ctk.CTkLabel(title_frame, text=f"🪙 {coins} coins", font=("Arial", 18))
    coins_label.pack(side="right")
    
    # Frame pour les articles
    items_frame = ctk.CTkFrame(shop_window)
    items_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Créer les articles dans la boutique
    for item in shop_items:
        item_frame = ctk.CTkFrame(items_frame)
        item_frame.pack(fill="x", padx=10, pady=5)
        
        # Informations de l'article
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        
        # En-tête avec icône et nom
        header_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))
        
        icon_label = ctk.CTkLabel(header_frame, text=item["icon"], font=("Arial", 20))
        icon_label.pack(side="left", padx=(0, 10))
        
        name_label = ctk.CTkLabel(header_frame, text=item["name"], font=("Arial", 16, "bold"))
        name_label.pack(side="left")
        
        desc_label = ctk.CTkLabel(info_frame, text=item["description"], text_color="gray")
        desc_label.pack(anchor="w")
        
        # Bouton d'achat
        def create_buy_command(item_price, item_name, item_icon):
            def buy_item():
                global coins
                if coins >= item_price:
                    coins -= item_price
                    coins_label.configure(text=f"🪙 {coins} coins")
                    show_xp_bar()  # Mettre à jour l'affichage des coins
                    save_data()  # Sauvegarder les données après l'achat
                    ctk.CTkMessagebox(
                        title="Achat réussi!", 
                        message=f"Vous avez acheté {item_icon} {item_name}!\nProfitez bien de votre récompense !", 
                        icon="check"
                    )
                else:
                    ctk.CTkMessagebox(
                        title="Erreur", 
                        message=f"Vous n'avez pas assez de coins !\nIl vous manque {item_price - coins} coins.", 
                        icon="cancel"
                    )
            return buy_item
        
        buy_btn = ctk.CTkButton(
            item_frame, 
            text=f"Acheter ({item['price']} 🪙)", 
            command=create_buy_command(item["price"], item["name"], item["icon"])
        )
        buy_btn.pack(side="right", padx=10, pady=5)

# === SYSTÈME DE PROFIL ===
def show_profile():
    # Charger les données du profil depuis le fichier JSON
    try:
        with open("user_data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            profile_data = data["users"]["default"]["profile"]
            username = profile_data["username"]
            profile_picture = profile_data["profile_picture"]
    except Exception:
        username = "Utilisateur"
        profile_picture = "assets/default_profile.png"

    # Créer une nouvelle fenêtre pour le profil
    profile_window = ctk.CTkToplevel()
    profile_window.title("Profil Utilisateur")
    profile_window.geometry("400x500")
    
    # Centrer la fenêtre
    profile_window.geometry(f"+{int(profile_window.winfo_screenwidth()/2 - 200)}+{int(profile_window.winfo_screenheight()/2 - 250)}")
    
    # Frame principale
    main_frame = ctk.CTkFrame(profile_window)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Photo de profil
    try:
        profile_image = ctk.CTkImage(
            light_image=Image.open(profile_picture),
            dark_image=Image.open(profile_picture),
            size=(150, 150)
        )
        profile_image_label = ctk.CTkLabel(main_frame, image=profile_image, text="")
        profile_image_label.pack(pady=20)
    except Exception:
        # Si l'image n'existe pas, afficher un emoji comme fallback
        profile_image_label = ctk.CTkLabel(main_frame, text="👤", font=("Arial", 80))
        profile_image_label.pack(pady=20)
    
    # Nom d'utilisateur
    username_label = ctk.CTkLabel(main_frame, text=username, font=("Arial", 24, "bold"))
    username_label.pack(pady=10)
    
    # Frame pour les statistiques
    stats_frame = ctk.CTkFrame(main_frame)
    stats_frame.pack(fill="x", padx=20, pady=20)
    
    # Niveau
    level_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
    level_frame.pack(fill="x", pady=5, padx=10)
    level_label = ctk.CTkLabel(level_frame, text="Niveau", font=("Arial", 16))
    level_label.pack(side="left")
    level_value = ctk.CTkLabel(level_frame, text=str(level), font=("Arial", 16, "bold"))
    level_value.pack(side="right")
    
    # XP
    xp_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
    xp_frame.pack(fill="x", pady=5, padx=10)
    xp_label = ctk.CTkLabel(xp_frame, text="XP", font=("Arial", 16))
    xp_label.pack(side="left")
    xp_value = ctk.CTkLabel(xp_frame, text=f"{current_xp}/{xp_max}", font=("Arial", 16, "bold"))
    xp_value.pack(side="right")
    
    # Barre de progression XP
    xp_progress = ctk.CTkProgressBar(stats_frame)
    xp_progress.set(current_xp / xp_max)
    xp_progress.pack(fill="x", pady=10, padx=10)
    
    # Coins
    coins_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
    coins_frame.pack(fill="x", pady=5, padx=10)
    coins_label = ctk.CTkLabel(coins_frame, text="Coins", font=("Arial", 16))
    coins_label.pack(side="left")
    coins_value = ctk.CTkLabel(coins_frame, text=f"{coins} 🪙", font=("Arial", 16, "bold"))
    coins_value.pack(side="right")
    
    # Bouton pour modifier le profil
    edit_profile_btn = ctk.CTkButton(
        main_frame,
        text="Modifier le profil",
        command=lambda: tkmb.showinfo("Information", "Cette fonctionnalité sera disponible prochainement !")
    )
    edit_profile_btn.pack(pady=20)

# -- Création de la fenêtre principale
root = ctk.CTk()
root.title("Liste de Tâches")
root.geometry("900x600")
root.minsize(900, 450)

# Ajouter l'icône de l'application
try:
    root.iconbitmap("assets/favicon.ico")
except Exception:
    pass

# -- Configuration de la grille principale
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

# -- Conteneur principal avec un léger padding
container = ctk.CTkFrame(root)
container.grid(row=0, column=0, sticky="nsew")
# On configure 3 colonnes : 0 pour la sidebar de navigation, 1 pour la side view, 2 pour la main view
container.grid_columnconfigure(0, weight=0)  # Navigation sidebar
container.grid_columnconfigure(1, weight=0)  # Side view (listes de rappels)
container.grid_columnconfigure(2, weight=1)  # Main view
container.grid_rowconfigure(0, weight=1)
# ------------------------------------------------------------------------------
# 1) NAVIGATION SIDEBAR (Colonne 0)
# ------------------------------------------------------------------------------
nav_frame = ctk.CTkFrame(container, width=60, corner_radius=0)
nav_frame.grid(row=0, column=0, sticky="nsw", padx=(0,10), pady=0)
nav_frame.grid_propagate(False)
nav_frame.grid_rowconfigure(99, weight=1)  # Pour pousser les boutons en haut

# Boutons de navigation avec icônes
nav_btn1 = ctk.CTkButton(nav_frame, text="🏠", width=40, height=40, fg_color="#1F6AA5")
nav_btn1.grid(row=0, column=0, padx=10, pady=(10,5))

nav_btn2 = ctk.CTkButton(nav_frame, text="🛒", width=40, height=40, fg_color="#1F6AA5", command=show_shop)
nav_btn2.grid(row=1, column=0, padx=10, pady=5)

nav_btn3 = ctk.CTkButton(nav_frame, text="👤", width=40, height=40, fg_color="#1F6AA5", command=show_profile)
nav_btn3.grid(row=2, column=0, padx=10, pady=5)
# ------------------------------------------------------------------------------
# 2) SIDE VIEW (Colonne 1) : listes de rappels
# ------------------------------------------------------------------------------
sideview_frame = ctk.CTkFrame(container, width=220)
sideview_frame.grid(row=0, column=1, sticky="nsw", pady=10)
sideview_frame.grid_propagate(False)
sideview_frame.grid_rowconfigure(99, weight=1)  # Laisse de la place en bas

# -- Section "Lists"
lbl_lists_title = ctk.CTkLabel(sideview_frame, text="Listes", font=("Arial", 14, "bold"))
lbl_lists_title.grid(row=0, column=0, padx=10, pady=(5, 5), sticky="w")

# Bouton pour ajouter une nouvelle liste
add_list_btn = ctk.CTkButton(sideview_frame, text="+ Nouvelle Liste", command=show_add_list_popup,
                            fg_color="transparent", anchor="w")
add_list_btn.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

# Initialisation de task_lists_data
task_lists_data = []

# ------------------------------------------------------------------------------
# 3) MAIN VIEW (Colonne 2)
# ------------------------------------------------------------------------------
main_frame = ctk.CTkFrame(container)
main_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(2, weight=1)  # la liste des tâches doit s'étendre

# -- Barre supérieure (titre + icône tri/filtre + etc.)
top_bar_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
top_bar_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
top_bar_frame.grid_columnconfigure(0, weight=1)
top_bar_frame.grid_columnconfigure(1, weight=0)

# Titre
title_label = ctk.CTkLabel(top_bar_frame, text=selected_list, font=("Arial", 18, "bold"), fg_color="transparent")
title_label.grid(row=0, column=0, sticky="w")

# -- Bouton "Add Task"
add_task_btn = ctk.CTkButton(main_frame, text="+ Ajouter une tâche", height=35, command=show_add_task_popup)
add_task_btn.grid(row=1, column=0, sticky="ew", padx=10, pady=20)

# -- Cadre pour la liste des tâches
tasks_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
tasks_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
tasks_frame.grid_columnconfigure(0, weight=1)

# Initialisation des données de tâches
tasks_data = {}

# Charger les données après la création de tous les widgets
load_data()

# Afficher la barre d'XP dès le départ
show_xp_bar()

# -- Lancement de la boucle principale
root.protocol("WM_DELETE_WINDOW", lambda: (save_data(), root.destroy()))
root.mainloop()
