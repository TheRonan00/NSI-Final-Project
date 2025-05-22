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

def save_data():
    try:
        with open("user_data.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            data["users"]["default"]["tasks"] = tasks_data
            data["users"]["default"]["lists"] = task_lists_data
            data["users"]["default"]["profile"]["level"] = level
            data["users"]["default"]["profile"]["xp"] = current_xp
            data["users"]["default"]["profile"]["coins"] = coins
            file.seek(0)
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.truncate()
        print("Données sauvegardées avec succès")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")

def load_data():
    global task_lists_data, tasks_data, level, current_xp, coins, xp_max
    try:
        if os.path.exists("user_data.json"):
            with open("user_data.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                tasks_data = data["users"]["default"]["tasks"]
                task_lists_data = data["users"]["default"]["lists"]
                profile_data = data["users"]["default"]["profile"]
                level = profile_data.get("level", 1)
                current_xp = profile_data.get("xp", 0)
                coins = profile_data.get("coins", 0)
                xp_max = int(round(100 * (1.05 ** (level - 1))))
            print("Données chargées avec succès")
        else:
            tasks_data = {}
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
            
selected_list = "📥 Toutes"

def update_lists_display():
    global selected_list
    for widget in sideview_frame.winfo_children():
        if isinstance(widget, ctk.CTkButton) and widget not in [add_list_btn]:
            widget.destroy()
    
    default_lists = task_lists_data[:3]
    custom_lists = task_lists_data[3:]
    
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
    
    separator_frame = ctk.CTkFrame(sideview_frame, fg_color="transparent")
    separator_frame.grid(row=current_row, column=0, sticky="ew", pady=10)
    separator_frame.grid_columnconfigure(0, weight=0)
    separator_frame.grid_columnconfigure(1, weight=1)
    separator_frame.grid_columnconfigure(2, weight=0)
    
    mes_listes_label = ctk.CTkLabel(separator_frame, text="Mes listes", font=("", 14, "bold"))
    mes_listes_label.grid(row=0, column=0, sticky="w", padx=10)
    
    add_btn = ctk.CTkButton(separator_frame, text="+", width=20, height=20, command=show_add_list_popup)
    add_btn.grid(row=0, column=2, sticky="ew", padx=10)
    
    current_row += 1
    
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
    update_lists_display()
    title_label.configure(text=list_name)
    update_tasks_display()

def update_tasks_display():
    for widget in tasks_frame.winfo_children():
        widget.destroy()
        
    row_index = 0
    
    if selected_list == "📥 Toutes":
        for list_name, tasks_list in tasks_data.items():
            if tasks_list:
                group_label = ctk.CTkLabel(tasks_frame, text=list_name, font=("Arial", 14, "bold"))
                group_label.grid(row=row_index, column=0, sticky="w", pady=(10, 5))
                row_index += 1
                
                for task in tasks_list:
                    row_index = display_task(task, row_index)
    elif selected_list == "📅 Aujourd'hui":
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")
        
        for list_name, tasks_list in tasks_data.items():
            today_tasks = [task for task in tasks_list if task["date"] == today_str]
            if today_tasks:
                group_label = ctk.CTkLabel(tasks_frame, text=list_name, font=("Arial", 14, "bold"))
                group_label.grid(row=row_index, column=0, sticky="w", pady=(10, 5))
                row_index += 1
                
                for task in today_tasks:
                    row_index = display_task(task, row_index)
    elif selected_list == "📆 7 Prochains Jours":
        today = datetime.now().date()
        end_date = today + timedelta(days=7)
        
        for list_name, tasks_list in tasks_data.items():
            next_week_tasks = []
            for task in tasks_list:
                task_date = datetime.strptime(task["date"], "%Y-%m-%d").date()
                if today <= task_date <= end_date:
                    next_week_tasks.append(task)
            
            if next_week_tasks:
                group_label = ctk.CTkLabel(tasks_frame, text=list_name, font=("Arial", 14, "bold"))
                group_label.grid(row=row_index, column=0, sticky="w", pady=(10, 5))
                row_index += 1
                
                for task in next_week_tasks:
                    row_index = display_task(task, row_index)
    else:
        tasks_list = tasks_data.get(selected_list, [])
        for task in tasks_list:
            row_index = display_task(task, row_index)

xp_max = 100
xp_per_task = 10

def show_xp_bar():
    global xp_label, xp_progress, xp_bar_frame

    xp_bar_frame = ctk.CTkFrame(main_frame)
    xp_bar_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
    xp_label = ctk.CTkLabel(xp_bar_frame, text=f"Niveau {level} | {coins} 🪙 | XP : {current_xp}/{xp_max}")
    xp_label.pack(side="left", padx=10)
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
    coins += 10
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
            current_xp = xp_max + current_xp
            coins = max(0, coins - 15)
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
    task_row_frame.grid_columnconfigure(0, weight=1)
    task_row_frame.grid_columnconfigure(1, weight=0)
    task_row_frame.grid_columnconfigure(2, weight=0)

    checked_var = tk.BooleanVar(value=task.get("checked", False))

    checkbox = ctk.CTkCheckBox(task_row_frame, text="", variable=checked_var)
    checkbox.grid(row=0, column=0, sticky="w")

    task_label = ctk.CTkLabel(task_row_frame, text=task["title"])
    task_label.grid(row=0, column=0, sticky="w", padx=(30, 0))

    if checked_var.get():
        task_label.configure(font=("", 0, "overstrike"), text_color=("#888888"))

    def on_task_checked():
        if checked_var.get():
            task_label.configure(font=("", 0, "overstrike"), text_color=("#888888"))
            gain_xp_for_task()
        else:
            task_label.configure(font=("", 0, "normal"), text_color=("#FFFFFF"))
            lose_xp_for_task()
        
        task["checked"] = checked_var.get()
        save_data()

    checkbox.configure(command=on_task_checked)

    today = datetime.now().date()
    task_datetime = datetime.strptime(task["date"], "%Y-%m-%d").date()
    
    delta = (task_datetime - today).days
    
    if delta == 0:
        display_date = "Aujourd'hui"
    elif delta == 1:
        display_date = "Demain"
    elif delta == -1:
        display_date = "Hier"
    else:
        mois = ["janvier", "février", "mars", "avril", "mai", "juin", 
               "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
        jour = task_datetime.day
        mois_str = mois[task_datetime.month - 1]
        
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
        save_data()
            
def show_add_list_popup():
    popup = ctk.CTkToplevel()
    popup.title("Nouvelle Liste")
    popup.geometry("300x200")
    
    popup.geometry(f"+{int(popup.winfo_screenwidth()/2 - 150)}+{int(popup.winfo_screenheight()/2 - 100)}")
    
    title_label = ctk.CTkLabel(popup, text="Créer une nouvelle liste", font=("Arial", 16, "bold"))
    title_label.pack(pady=20)
    
    list_entry = ctk.CTkEntry(popup, placeholder_text="Nom de la liste", width=200)
    list_entry.pack(pady=10)
    
    def create_list():
        list_name = list_entry.get()
        if list_name and list_name not in task_lists_data:
            task_lists_data.append(list_name)
            update_lists_display()
            save_data()
            popup.destroy()
    
    buttons_frame = ctk.CTkFrame(popup, fg_color="transparent")
    buttons_frame.pack(pady=20)
    
    cancel_btn = ctk.CTkButton(buttons_frame, text="Annuler", command=popup.destroy)
    cancel_btn.pack(side="left", padx=10)
    
    create_btn = ctk.CTkButton(buttons_frame, text="Créer", command=create_list)
    create_btn.pack(side="left", padx=10)
    
def show_add_task_popup():
    popup = ctk.CTkToplevel()
    popup.title("Nouvelle Tâche")
    popup.geometry("400x350")
    
    popup.geometry(f"+{int(popup.winfo_screenwidth()/2 - 200)}+{int(popup.winfo_screenheight()/2 - 175)}")
    
    title_label = ctk.CTkLabel(popup, text="Créer une nouvelle tâche", font=("Arial", 16, "bold"))
    title_label.pack(pady=20)
    
    task_entry = ctk.CTkEntry(popup, placeholder_text="Nom de la tâche", width=300)
    task_entry.pack(pady=10)
    
    list_label = ctk.CTkLabel(popup, text="Liste")
    list_label.pack(anchor="w", padx=50)
    
    available_lists = [list_name for list_name in task_lists_data 
                      if list_name not in ["📥 Toutes", "📅 Aujourd'hui", "📆 7 Prochains Jours"]]
    
    list_var = ctk.StringVar(value=available_lists[0] if available_lists else "")
    list_dropdown = ctk.CTkOptionMenu(popup, values=available_lists, variable=list_var, width=300)
    list_dropdown.pack(pady=(0,10))
    
    date_frame = ctk.CTkFrame(popup, fg_color="transparent")
    date_frame.pack(fill="x", padx=50)
    
    date_label = ctk.CTkLabel(date_frame, text="Date")
    date_label.pack(anchor="w")
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    date_var = ctk.StringVar(value=today_str)
    date_entry = ctk.CTkEntry(date_frame, textvariable=date_var, width=250, state="readonly")
    date_entry.pack(side="left", pady=(0,10))
    
    def open_calendar():
        cal_window = ctk.CTkToplevel(popup)
        cal_window.title("Sélectionner une date")
        cal_window.geometry("300x300")
        
        cal_window.geometry(f"+{int(popup.winfo_x() + popup.winfo_width())}+{int(popup.winfo_y())}")

        cal = Calendar(cal_window, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(expand=True, fill="both", padx=10, pady=10)
        
        def set_date():
            date_var.set(cal.get_date())
            cal_window.destroy()
        
        select_btn = ctk.CTkButton(cal_window, text="Sélectionner", command=set_date)
        select_btn.pack(pady=10)
    
    cal_btn = ctk.CTkButton(date_frame, text="📅", width=40, command=open_calendar)
    cal_btn.pack(side="left", padx=(10,0))
    
    time_label = ctk.CTkLabel(popup, text="Heure")
    time_label.pack(anchor="w", padx=50)
    
    time_options = [f"{h:02d}:00" for h in range(24)]
    
    time_var = ctk.StringVar(value="09:00")
    time_dropdown = ctk.CTkOptionMenu(popup, values=time_options, variable=time_var, width=300)
    time_dropdown.pack(pady=(0,10))
    
    def add_task():
        task_name = task_entry.get()
        task_date = date_var.get()
        task_time = time_var.get()
        selected_list = list_var.get()
        
        if task_name:
            if not task_date:
                now = datetime.now()
                task_date = now.strftime("%Y-%m-%d")
                
            new_task = {
                "title": task_name,
                "date": task_date,
                "time": task_time,
                "checked": False
            }
                
            if selected_list not in tasks_data:
                tasks_data[selected_list] = []
            tasks_data[selected_list].append(new_task)
                
            update_tasks_display()
            save_data()
            popup.destroy()
    
    buttons_frame = ctk.CTkFrame(popup, fg_color="transparent")
    buttons_frame.pack(pady=(0, 10))
    
    cancel_btn = ctk.CTkButton(buttons_frame, text="Annuler", command=popup.destroy)
    cancel_btn.pack(side="left", padx=(0,5))
    
    create_btn = ctk.CTkButton(buttons_frame, text="Créer", command=add_task)
    create_btn.pack(side="right", padx=(5,0))

def show_shop():
    try:
        with open("user_data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            shop_items = data["users"]["default"]["shop_items"]
    except Exception:
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

    shop_window = ctk.CTkToplevel()
    shop_window.title("Boutique de Récompenses")
    shop_window.geometry("500x600")
    
    shop_window.geometry(f"+{int(shop_window.winfo_screenwidth()/2 - 250)}+{int(shop_window.winfo_screenheight()/2 - 300)}")
    
    title_frame = ctk.CTkFrame(shop_window, fg_color="transparent")
    title_frame.pack(fill="x", padx=20, pady=10)
    
    title_label = ctk.CTkLabel(title_frame, text="Boutique de Récompenses", font=("Arial", 24, "bold"))
    title_label.pack(side="left")
    
    coins_label = ctk.CTkLabel(title_frame, text=f"🪙 {coins} coins", font=("Arial", 18))
    coins_label.pack(side="right")
    
    items_frame = ctk.CTkFrame(shop_window)
    items_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    for item in shop_items:
        item_frame = ctk.CTkFrame(items_frame)
        item_frame.pack(fill="x", padx=10, pady=5)
        
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        
        header_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))
        
        icon_label = ctk.CTkLabel(header_frame, text=item["icon"], font=("Arial", 20))
        icon_label.pack(side="left", padx=(0, 10))
        
        name_label = ctk.CTkLabel(header_frame, text=item["name"], font=("Arial", 16, "bold"))
        name_label.pack(side="left")
        
        desc_label = ctk.CTkLabel(info_frame, text=item["description"], text_color="gray")
        desc_label.pack(anchor="w")
        
        def create_buy_command(item_price, item_name, item_icon):
            def buy_item():
                global coins
                if coins >= item_price:
                    coins -= item_price
                    coins_label.configure(text=f"🪙 {coins} coins")
                    show_xp_bar()
                    save_data()
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

def show_profile():
    try:
        with open("user_data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            profile_data = data["users"]["default"]["profile"]
            username = profile_data["username"]
            profile_picture = profile_data["profile_picture"]
    except Exception:
        username = "Utilisateur"
        profile_picture = "assets/default_profile.png"

    profile_window = ctk.CTkToplevel()
    profile_window.title("Profil Utilisateur")
    profile_window.geometry("400x500")
    
    profile_window.geometry(f"+{int(profile_window.winfo_screenwidth()/2 - 200)}+{int(profile_window.winfo_screenheight()/2 - 250)}")
    
    main_frame = ctk.CTkFrame(profile_window)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    try:
        profile_image = ctk.CTkImage(
            light_image=Image.open(profile_picture),
            dark_image=Image.open(profile_picture),
            size=(150, 150)
        )
        profile_image_label = ctk.CTkLabel(main_frame, image=profile_image, text="")
        profile_image_label.pack(pady=20)
    except Exception:
        profile_image_label = ctk.CTkLabel(main_frame, text="👤", font=("Arial", 80))
        profile_image_label.pack(pady=20)
    
    username_label = ctk.CTkLabel(main_frame, text=username, font=("Arial", 24, "bold"))
    username_label.pack(pady=10)
    
    stats_frame = ctk.CTkFrame(main_frame)
    stats_frame.pack(fill="x", padx=20, pady=20)
    
    level_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
    level_frame.pack(fill="x", pady=5, padx=10)
    level_label = ctk.CTkLabel(level_frame, text="Niveau", font=("Arial", 16))
    level_label.pack(side="left")
    level_value = ctk.CTkLabel(level_frame, text=str(level), font=("Arial", 16, "bold"))
    level_value.pack(side="right")
    
    xp_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
    xp_frame.pack(fill="x", pady=5, padx=10)
    xp_label = ctk.CTkLabel(xp_frame, text="XP", font=("Arial", 16))
    xp_label.pack(side="left")
    xp_value = ctk.CTkLabel(xp_frame, text=f"{current_xp}/{xp_max}", font=("Arial", 16, "bold"))
    xp_value.pack(side="right")
    
    xp_progress = ctk.CTkProgressBar(stats_frame)
    xp_progress.set(current_xp / xp_max)
    xp_progress.pack(fill="x", pady=10, padx=10)
    
    coins_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
    coins_frame.pack(fill="x", pady=5, padx=10)
    coins_label = ctk.CTkLabel(coins_frame, text="Coins", font=("Arial", 16))
    coins_label.pack(side="left")
    coins_value = ctk.CTkLabel(coins_frame, text=f"{coins} 🪙", font=("Arial", 16, "bold"))
    coins_value.pack(side="right")
    
    edit_profile_btn = ctk.CTkButton(
        main_frame,
        text="Modifier le profil",
        command=lambda: tkmb.showinfo("Information", "Cette fonctionnalité sera disponible prochainement !")
    )
    edit_profile_btn.pack(pady=20)

root = ctk.CTk()
root.title("Liste de Tâches")
root.geometry("900x600")
root.minsize(900, 450)

try:
    root.iconbitmap("assets/favicon.ico")
except Exception:
    pass

root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

container = ctk.CTkFrame(root)
container.grid(row=0, column=0, sticky="nsew")
container.grid_columnconfigure(0, weight=0)
container.grid_columnconfigure(1, weight=0)
container.grid_columnconfigure(2, weight=1)
container.grid_rowconfigure(0, weight=1)

nav_frame = ctk.CTkFrame(container, width=60, corner_radius=0)
nav_frame.grid(row=0, column=0, sticky="nsw", padx=(0,10), pady=0)
nav_frame.grid_propagate(False)
nav_frame.grid_rowconfigure(99, weight=1)

nav_btn1 = ctk.CTkButton(nav_frame, text="🏠", width=40, height=40, fg_color="#1F6AA5")
nav_btn1.grid(row=0, column=0, padx=10, pady=(10,5))

nav_btn2 = ctk.CTkButton(nav_frame, text="🛒", width=40, height=40, fg_color="#1F6AA5", command=show_shop)
nav_btn2.grid(row=1, column=0, padx=10, pady=5)

nav_btn3 = ctk.CTkButton(nav_frame, text="👤", width=40, height=40, fg_color="#1F6AA5", command=show_profile)
nav_btn3.grid(row=2, column=0, padx=10, pady=5)

sideview_frame = ctk.CTkFrame(container, width=220)
sideview_frame.grid(row=0, column=1, sticky="nsw", pady=10)
sideview_frame.grid_propagate(False)
sideview_frame.grid_rowconfigure(99, weight=1)

lbl_lists_title = ctk.CTkLabel(sideview_frame, text="Listes", font=("Arial", 14, "bold"))
lbl_lists_title.grid(row=0, column=0, padx=10, pady=(5, 5), sticky="w")

add_list_btn = ctk.CTkButton(sideview_frame, text="+ Nouvelle Liste", command=show_add_list_popup,
                            fg_color="transparent", anchor="w")
add_list_btn.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

task_lists_data = []

main_frame = ctk.CTkFrame(container)
main_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(2, weight=1)

top_bar_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
top_bar_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
top_bar_frame.grid_columnconfigure(0, weight=1)
top_bar_frame.grid_columnconfigure(1, weight=0)

title_label = ctk.CTkLabel(top_bar_frame, text=selected_list, font=("Arial", 18, "bold"), fg_color="transparent")
title_label.grid(row=0, column=0, sticky="w")

add_task_btn = ctk.CTkButton(main_frame, text="+ Ajouter une tâche", height=35, command=show_add_task_popup)
add_task_btn.grid(row=1, column=0, sticky="ew", padx=10, pady=20)

tasks_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
tasks_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
tasks_frame.grid_columnconfigure(0, weight=1)

tasks_data = {}

load_data()

show_xp_bar()

root.protocol("WM_DELETE_WINDOW", lambda: (save_data(), root.destroy()))
root.mainloop()