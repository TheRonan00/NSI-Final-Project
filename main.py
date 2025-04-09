import customtkinter as ctk

# -- Configurer CustomTkinter pour un thème sombre et une couleur principale bleue
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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

# Boutons de navigation (pour l'instant sans icônes)
nav_btn1 = ctk.CTkButton(nav_frame, text="Nav1", width=60)
nav_btn1.grid(row=0, column=0, padx=10, pady=(10,5))

nav_btn2 = ctk.CTkButton(nav_frame, text="Nav2", width=60)
nav_btn2.grid(row=1, column=0, padx=10, pady=5)

nav_btn3 = ctk.CTkButton(nav_frame, text="Nav3", width=60)
nav_btn3.grid(row=2, column=0, padx=10, pady=5)
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

lists = [
    "⏱️Tâches Quotidiennes",
    "💼Tâches Professionnelles",
    "📚Tâches École",
    "🛒Courses",
    "Cette Semaine",
    "✈️Plans de Voyage",
    "Non Planifié"
]

for i, list_name in enumerate(lists):
    list_btn = ctk.CTkButton(sideview_frame, text=list_name, fg_color="transparent", anchor="w")
    list_btn.grid(row=5+i, column=0, padx=10, pady=5, sticky="ew")

# Laisser de la place en bas si besoin
sep2 = ctk.CTkLabel(sideview_frame, text="")
sep2.grid(row=5+len(lists), column=0, pady=10)

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
filter_btn.grid(row=0, column=1, sticky="e")

# -- Input "Add Task"
add_task_input = ctk.CTkEntry(main_frame, placeholder_text="+ Ajouter une tâche", width=100, height=35)
add_task_input.grid(row=1, column=0, sticky="ew", padx=10, pady=20)

# Fonction pour perdre le focus quand on clique ailleurs
def unfocus_input(event):
    if event.widget != add_task_input:
        add_task_input.delete(0, "end")
        add_task_input.master.focus()

# Lier l'événement de clic à la fonction
root.bind("<Button-1>", unfocus_input)

# -- Cadre pour la liste des tâches
tasks_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
tasks_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
tasks_frame.grid_columnconfigure(0, weight=1)

# Simulation de groupes de tâches
tasks_data = {
    "Aujourd'hui (4)": [
        ("Footing matinal", "07:00"),
        ("Entretien avec M. Li", "09:00"),
        ("Préparer rapport de travail", "14:00"),
        ("Lecture du soir", "22:00")
    ],
    "Demain (4)": [
        ("Vérifier emails professionnels", "08:00"),
        ("Assister à la réunion", "10:00"),
        ("Récupérer le colis", "13:00"),
        ("Revoir le projet", "16:00")
    ],
    "7 Prochains Jours (2)": [
        ("Appeler la famille", "6 sept"),
        ("Aller au contrôle médical", "6 sept")
    ]
}

row_index = 0
for group_title, tasks_list in tasks_data.items():
    # Titre du groupe (ex: "Today (4)")
    group_label = ctk.CTkLabel(tasks_frame, text=group_title, font=("Arial", 14, "bold"))
    group_label.grid(row=row_index, column=0, sticky="w", pady=(10, 5))
    row_index += 1

    # Pour chaque tâche, on crée une ligne : [Checkbox] [Titre] (Heure à droite)
    for task_title, task_time in tasks_list:
        task_row_frame = ctk.CTkFrame(tasks_frame)
        task_row_frame.grid(row=row_index, column=0, sticky="ew", pady=2)
        task_row_frame.grid_columnconfigure(0, weight=0)  # checkbox
        task_row_frame.grid_columnconfigure(1, weight=1)  # label de la tâche
        task_row_frame.grid_columnconfigure(2, weight=0)  # horaire

        checkbox = ctk.CTkCheckBox(task_row_frame, text="")
        checkbox.grid(row=0, column=0, sticky="w")

        task_label = ctk.CTkLabel(task_row_frame, text=task_title)
        task_label.grid(row=0, column=0, sticky="w", padx=(30, 0))  # Décalé de 25px pour laisser place à la checkbox

        time_label = ctk.CTkLabel(task_row_frame, text=task_time, text_color="gray")
        time_label.grid(row=0, column=2, padx=10, sticky="e")

        row_index += 1

# -- Lancement de la boucle principale
root.mainloop()