import customtkinter as ctk
from PIL import Image
import json
import os
from tkcalendar import Calendar
from datetime import datetime

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
            file.seek(0)
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.truncate()
        print("Données sauvegardées avec succès")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")

# -- Fonction pour charger les données depuis un fichier JSON
def load_data():
    global task_lists_data, tasks_data
    try:
        # Charger les données depuis user_data.json
        if os.path.exists("user_data.json"):
            with open("user_data.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                tasks_data = data["users"]["default"]["tasks"]
                task_lists_data = data["users"]["default"]["lists"]
            print("Données chargées avec succès")
        else:
            # Données par défaut si le fichier n'existe pas
            tasks_data = {}

        # Charger les listes
        if os.path.exists("lists_data.json"):
            with open("lists_data.json", "r", encoding="utf-8") as file:
                task_lists_data = json.load(file)
            print("Listes chargées avec succès")
        else:
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

# -- Fonction globale pour gérer la perte de focus des inputs
def handle_focus_out(event):
    # Récupérer le widget qui a actuellement le focus
    focused_widget = root.focus_get()
    
    # Vérifier si on a cliqué sur un widget valide
    if not isinstance(event.widget, str):
        # Si on clique ailleurs que sur un input, on retire le focus
        if isinstance(focused_widget, ctk.CTkEntry) and event.widget != focused_widget:
            focused_widget.master.focus()  # Donner le focus au parent du widget
            
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
        list_btn = ctk.CTkButton(
            sideview_frame, 
            text=list_name, 
            fg_color="transparent" if list_name != selected_list else "cyan",
            hover_color="cyan",
            anchor="w",
            command=lambda name=list_name: select_list(name)
        )
        list_btn.grid(row=index, column=0, padx=10, pady=5, sticky="ew")
    
    current_row = len(default_lists)
    
    # Ajouter le séparateur et le titre "Mes listes"
    separator_frame = ctk.CTkFrame(sideview_frame, fg_color="transparent")
    separator_frame.grid(row=current_row, column=0, sticky="ew", pady=10)
    separator_frame.grid_columnconfigure(1, weight=1)
    
    # Titre "Mes listes"
    mes_listes_label = ctk.CTkLabel(separator_frame, text="Mes listes", font=("Arial", 12, "bold"))
    mes_listes_label.grid(row=0, column=0, sticky="w", padx=10)
    
    # Bouton + pour ajouter une nouvelle liste
    add_btn = ctk.CTkButton(separator_frame, text="+", width=20, height=20, 
                           command=show_add_list_popup)
    add_btn.grid(row=0, column=2, sticky="w", padx=10)
    
    current_row += 1
    
    # Afficher les listes personnalisées
    for index, list_name in enumerate(custom_lists):
        list_btn = ctk.CTkButton(
            sideview_frame,
            text=list_name,
            fg_color="transparent" if list_name != selected_list else "cyan",
            hover_color="cyan",
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
    else:
        # Afficher uniquement les tâches de la liste sélectionnée
        tasks_list = tasks_data.get(selected_list, [])
        for task in tasks_list:
            row_index = display_task(task, row_index)

def display_task(task, row_index):
    task_row_frame = ctk.CTkFrame(tasks_frame)
    task_row_frame.grid(row=row_index, column=0, sticky="ew", pady=2)
    task_row_frame.grid_columnconfigure(0, weight=0)  # checkbox
    task_row_frame.grid_columnconfigure(1, weight=1)  # label de la tâche
    task_row_frame.grid_columnconfigure(2, weight=0)  # horaire

    checkbox = ctk.CTkCheckBox(task_row_frame, text="")
    checkbox.grid(row=0, column=0, sticky="w")

    task_label = ctk.CTkLabel(task_row_frame, text=task["title"])
    task_label.grid(row=0, column=0, sticky="w", padx=(30, 0))

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
    date_label.grid(row=0, column=10, padx=(0, 5), sticky="e")

    time_label = ctk.CTkLabel(task_row_frame, text=task["time"], text_color="gray") 
    time_label.grid(row=0, column=11, padx=(0, 10), sticky="e")

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
    
    list_var = ctk.StringVar(value=task_lists_data[0])  # Valeur par défaut
    list_dropdown = ctk.CTkOptionMenu(popup, values=task_lists_data, variable=list_var, width=300)
    list_dropdown.pack(pady=(0,10))
    
    # Frame pour la date
    date_frame = ctk.CTkFrame(popup, fg_color="transparent")
    date_frame.pack(fill="x", padx=50)
    
    date_label = ctk.CTkLabel(date_frame, text="Date")
    date_label.pack(anchor="w")
    
    date_var = ctk.StringVar()
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
                "time": task_time
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

# -- Création de la fenêtre principale
root = ctk.CTk()
root.title("Liste de Tâches")
root.geometry("900x600")
root.minsize(900, 450)
root.iconbitmap("assets/favicon.ico")

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
try:
    nav_btn1 = ctk.CTkButton(nav_frame, text="", width=40, height=40, fg_color="#808791",
                            image=ctk.CTkImage(light_image=Image.open("assets/circle-user.png"),
                                             dark_image=Image.open("assets/circle-user.png"),
                                             size=(20, 20)))
    nav_btn1.grid(row=0, column=0, padx=10, pady=(10,5))

    nav_btn2 = ctk.CTkButton(nav_frame, text="", width=40, height=40, fg_color="#808791",
                            image=ctk.CTkImage(light_image=Image.open("assets/settings.png"),
                                             dark_image=Image.open("assets/settings.png"), 
                                             size=(20, 20)))
    nav_btn2.grid(row=1, column=0, padx=10, pady=5)

    nav_btn3 = ctk.CTkButton(nav_frame, text="", width=40, height=40, fg_color="#808791",
                            image=ctk.CTkImage(light_image=Image.open("assets/circle-check.png"),
                                             dark_image=Image.open("assets/circle-check.png"),
                                             size=(20, 20)))
    nav_btn3.grid(row=2, column=0, padx=10, pady=5)

    nav_btn4 = ctk.CTkButton(nav_frame, text="", width=40, height=40, fg_color="#808791",
                            image=ctk.CTkImage(light_image=Image.open("assets/calendar.png"),
                                             dark_image=Image.open("assets/calendar.png"),
                                             size=(20, 20)))
    nav_btn4.grid(row=3, column=0, padx=10, pady=5)
except Exception as e:
    print(f"Erreur lors du chargement des images: {e}")
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

# Titre
title_label = ctk.CTkLabel(top_bar_frame, text="7 Prochains Jours", font=("Arial", 18, "bold"), fg_color="transparent")
title_label.grid(row=0, column=0, sticky="w")

# Icône/placeholder à droite (par ex. un bouton "filtre")
filter_btn = ctk.CTkButton(top_bar_frame, text="Filtrer", width=80)
filter_btn.grid(row=0, column=2, sticky="e")

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

# Lier l'événement de clic à la fonction globale
root.bind_all("<Button-1>", handle_focus_out)

# -- Lancement de la boucle principale
root.protocol("WM_DELETE_WINDOW", lambda: (save_data(), root.destroy()))
root.mainloop()