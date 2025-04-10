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
def save_tasks_data():
    try:
        with open("tasks_data.json", "w", encoding="utf-8") as file:
            json.dump(tasks_data, file, ensure_ascii=False, indent=4)
        print("Données sauvegardées avec succès")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")

# -- Fonction pour charger les données depuis un fichier JSON
def load_tasks_data():
    global tasks_data
    try:
        if os.path.exists("tasks_data.json"):
            with open("tasks_data.json", "r", encoding="utf-8") as file:
                tasks_data = json.load(file)
            print("Données chargées avec succès")
            update_tasks_display()
        else:
            print("Aucun fichier de sauvegarde trouvé")
    except Exception as e:
        print(f"Erreur lors du chargement: {e}")
        tasks_data = {}

# -- Fonction globale pour gérer la perte de focus des inputs
def handle_focus_out(event):
    # Récupérer le widget qui a actuellement le focus
    focused_widget = root.focus_get()
    
    # Vérifier si on a cliqué sur un widget valide
    if not isinstance(event.widget, str):
        # Si on clique ailleurs que sur un input, on retire le focus
        if isinstance(focused_widget, ctk.CTkEntry) and event.widget != focused_widget:
            focused_widget.master.focus()  # Donner le focus au parent du widget
        
def update_tasks_display():
    # Mettre à jour l'affichage
    for widget in tasks_frame.winfo_children():
        widget.destroy()
        
    row_index = 0
    for group_title, tasks_list in tasks_data.items():
        # Titre du groupe (ex: "Today (4)")
        group_label = ctk.CTkLabel(tasks_frame, text=group_title, font=("Arial", 14, "bold"))
        group_label.grid(row=row_index, column=0, sticky="w", pady=(10, 5))
        row_index += 1

        # Pour chaque tâche, on crée une ligne : [Checkbox] [Titre] (Date) (Heure à droite)
        for task_title, task_date, task_time in tasks_list:
            task_row_frame = ctk.CTkFrame(tasks_frame)
            task_row_frame.grid(row=row_index, column=0, sticky="ew", pady=2)
            task_row_frame.grid_columnconfigure(0, weight=0)  # checkbox
            task_row_frame.grid_columnconfigure(1, weight=1)  # label de la tâche
            task_row_frame.grid_columnconfigure(2, weight=0)  # horaire

            checkbox = ctk.CTkCheckBox(task_row_frame, text="")
            checkbox.grid(row=0, column=0, sticky="w")

            task_label = ctk.CTkLabel(task_row_frame, text=task_title)
            task_label.grid(row=0, column=0, sticky="w", padx=(30, 0))  # Décalé de 25px pour laisser place à la checkbox

            # Formatage de la date
            today = datetime.now().date()
            task_datetime = datetime.strptime(task_date, "%Y-%m-%d").date()
            
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
            date_label.grid(row=0, column=2, padx=(0, 35), sticky="e")

            time_label = ctk.CTkLabel(task_row_frame, text=task_time, text_color="gray")
            time_label.grid(row=0, column=2, padx=(0, 10), sticky="e")

            row_index += 1

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
    nav_btn1 = ctk.CTkButton(nav_frame, text="", width=40, height=40, fg_color="#FAEBD7",
                            image=ctk.CTkImage(light_image=Image.open("assets/circle-user.png"),
                                             dark_image=Image.open("assets/circle-user.png"),
                                             size=(20, 20)))
    nav_btn1.grid(row=0, column=0, padx=10, pady=(10,5))

    nav_btn2 = ctk.CTkButton(nav_frame, text="", width=40, height=40, fg_color="#FAEBD7",
                            image=ctk.CTkImage(light_image=Image.open("assets/settings.png"),
                                             dark_image=Image.open("assets/settings.png"), 
                                             size=(20, 20)))
    nav_btn2.grid(row=1, column=0, padx=10, pady=5)

    nav_btn3 = ctk.CTkButton(nav_frame, text="", width=40, height=40, fg_color="#FAEBD7",
                            image=ctk.CTkImage(light_image=Image.open("assets/circle-check.png"),
                                             dark_image=Image.open("assets/circle-check.png"),
                                             size=(20, 20)))
    nav_btn3.grid(row=2, column=0, padx=10, pady=5)

    nav_btn4 = ctk.CTkButton(nav_frame, text="", width=40, height=40, fg_color="#FAEBD7",
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

# -- Section "rapide" : Today, Next 7 Days, Inbox
lbl_today = ctk.CTkButton(sideview_frame, text="Aujourd'hui (10)", fg_color="transparent", anchor="w")
lbl_today.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

lbl_next_7_days = ctk.CTkButton(sideview_frame, text="7 Prochains Jours (94)", fg_color="transparent", anchor="w")
lbl_next_7_days.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

lbl_inbox = ctk.CTkButton(sideview_frame, text="Boîte de réception (1)", fg_color="transparent", anchor="w")
lbl_inbox.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

# -- Petite séparation
sep1 = ctk.CTkLabel(sideview_frame, text="—" * 18, text_color="gray", anchor="w")
sep1.grid(row=3, column=0, padx=5, pady=(5, 5), sticky="ew")

# -- Section "Lists"
lbl_lists_title = ctk.CTkLabel(sideview_frame, text="Listes", font=("Arial", 14, "bold"))
lbl_lists_title.grid(row=4, column=0, padx=10, pady=(5, 5), sticky="w")

task_lists_data = [
    "⏱️Tâches Quotidiennes",
    "💼Tâches Professionnelles",
    "📚Tâches École",
    "🛒Courses",
    "Cette Semaine",
    "✈️Plans de Voyage",
    "Non Planifié"
]

for index, list_name in enumerate(task_lists_data):
    list_btn = ctk.CTkButton(sideview_frame, text=list_name, fg_color="transparent", anchor="w")
    list_btn.grid(row=5+index, column=0, padx=10, pady=5, sticky="ew")

# Laisser de la place en bas si besoin
sep2 = ctk.CTkLabel(sideview_frame, text="")
sep2.grid(row=5+len(task_lists_data), column=0, pady=10)

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
add_task_btn = ctk.CTkButton(main_frame, text="+ Ajouter une tâche", height=35, command=lambda: show_add_task_popup())
add_task_btn.grid(row=1, column=0, sticky="ew", padx=10, pady=20)

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
                
            # Ajouter la tâche à la liste sélectionnée
            tasks_data[selected_list] = tasks_data.get(selected_list, []) + [(task_name, task_date, task_time)]
                
            update_tasks_display()
            
            # Sauvegarder les données après l'ajout d'une tâche
            save_tasks_data()
            
            popup.destroy()
    
    # Boutons Annuler/Créer
    buttons_frame = ctk.CTkFrame(popup, fg_color="transparent")
    buttons_frame.pack(pady=(0, 10))
    
    cancel_btn = ctk.CTkButton(buttons_frame, text="Annuler", command=popup.destroy)
    cancel_btn.pack(side="left", padx=(0,5))
    
    create_btn = ctk.CTkButton(buttons_frame, text="Créer", command=add_task)
    create_btn.pack(side="right", padx=(5,0))

# -- Cadre pour la liste des tâches
tasks_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
tasks_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
tasks_frame.grid_columnconfigure(0, weight=1)

# Initialisation des données de tâches
tasks_data = {}

# Charger les données au démarrage
load_tasks_data()

update_tasks_display()

# Lier l'événement de clic à la fonction globale
root.bind_all("<Button-1>", handle_focus_out)

# -- Lancement de la boucle principale
root.protocol("WM_DELETE_WINDOW", lambda: (save_tasks_data(), root.destroy()))
root.mainloop()