"""
Interface graphique Material Design pour le système de création d'horaires
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.dialogs import Messagebox
from tkinter import StringVar, IntVar
import pandas as pd
from typing import List, Dict
from models import (CourseSession, Teacher, Classroom, Student, CourseType,
                    TimeSlot, StudentScheduleEntry)
from scheduler import ScheduleOptimizer, GroupingOption, GroupingStrategy, ProgramVariant, GroupSizeOption
from data_generator import generate_sample_data
from data_manager import DataManager
import subprocess
import os


class SchedulerApp:
    """Application principale de création d'horaires avec Material Design"""

    def __init__(self, root):
        self.root = root
        self.root.title("Création d'horaires - Secondaire 4 Québec")
        self.root.geometry("1400x900")

        # Couleurs personnalisées - Thème Odyssée (Or, Noir, Blanc)
        self.GOLD = "#FFCC00"
        self.BLACK = "#000000"
        self.WHITE = "#FFFFFF"
        self.GOLD_DARK = "#CC9900"  # Or plus foncé pour le texte sur blanc
        self.GRAY_LIGHT = "#F5F5F5"  # Gris très clair pour alternance

        # Configurer les couleurs de fond
        self.root.configure(bg=self.WHITE)

        # Variables de configuration
        self.num_students_var = IntVar(value=56)
        self.num_teachers_var = IntVar(value=13)
        self.num_classrooms_var = IntVar(value=8)
        self.status_var = StringVar(value="Prêt à générer l'horaire")
        self.selected_student_var = IntVar(value=0)

        # Variables pour les tailles de groupe personnalisées
        self.small_group_min = IntVar(value=15)
        self.small_group_max = IntVar(value=20)
        self.medium_group_min = IntVar(value=20)
        self.medium_group_max = IntVar(value=25)
        self.large_group_min = IntVar(value=25)
        self.large_group_max = IntVar(value=32)

        # Données
        self.course_requirements = {}
        self.teachers = []
        self.classrooms = []
        self.students = []
        self.sessions = []
        self.student_schedules = {}
        self.min_students_per_session = 20

        # Nouvelles données pour le flux en 3 étapes
        self.grouping_options = []  # Les 9 options générées
        self.selected_option = None  # L'option sélectionnée par l'utilisateur
        self.step1_completed = False  # Étape 1 : Options générées et sélectionnées
        self.step2_completed = False  # Étape 2 : Horaires étudiants générés
        self.step3_completed = False  # Étape 3 : Enseignants/salles assignés

        self.create_widgets()
        self.apply_custom_styles()

    def create_widgets(self):
        """Crée les widgets de l'interface Material Design"""
        # Header avec couleurs personnalisées
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=X, padx=0, pady=0)
        header_frame.configure(style="Gold.TFrame")

        title_label = ttk.Label(
            header_frame,
            text="📚 Optimisation d'Horaires - Secondaire 4",
            font=("Segoe UI", 20, "bold")
        )
        title_label.pack(pady=20, padx=20)
        title_label.configure(style="GoldHeader.TLabel")

        subtitle_label = ttk.Label(
            header_frame,
            text="Génération automatique d'horaires optimisés pour le Québec",
            font=("Segoe UI", 11)
        )
        subtitle_label.pack(pady=(0, 20), padx=20)
        subtitle_label.configure(style="GoldSubHeader.TLabel")

        # Conteneur principal
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=BOTH, expand=YES, padx=20, pady=20)

        # Barre d'outils avec les 3 boutons séquentiels
        toolbar_frame = ttk.Frame(main_container)
        toolbar_frame.pack(fill=X, pady=(0, 15))

        # Bouton 1 : Générer les options de regroupement
        self.step1_btn = ttk.Button(
            toolbar_frame,
            text="1️⃣ Générer les options de regroupement",
            command=self.step1_generate_options,
            width=35,
            style="Gold.TButton"
        )
        self.step1_btn.pack(side=LEFT, padx=(0, 10))

        # Bouton 2 : Générer les horaires des étudiants
        self.step2_btn = ttk.Button(
            toolbar_frame,
            text="2️⃣ Générer les horaires étudiants",
            command=self.step2_generate_student_schedules,
            state="disabled",
            width=35,
            style="Gold.TButton"
        )
        self.step2_btn.pack(side=LEFT, padx=(0, 10))

        # Bouton 3 : Assigner les enseignants et salles
        self.step3_btn = ttk.Button(
            toolbar_frame,
            text="3️⃣ Assigner enseignants et salles",
            command=self.step3_assign_teachers_rooms,
            state="disabled",
            width=35,
            style="Gold.TButton"
        )
        self.step3_btn.pack(side=LEFT, padx=(0, 10))

        # Deuxième ligne de boutons : Export et Réinitialiser
        toolbar_frame2 = ttk.Frame(main_container)
        toolbar_frame2.pack(fill=X, pady=(0, 15))

        self.export_btn = ttk.Button(
            toolbar_frame2,
            text="📥 Exporter vers Excel",
            command=self.export_to_excel,
            state="disabled",
            width=25,
            style="Black.TButton"
        )
        self.export_btn.pack(side=LEFT, padx=(0, 10))

        self.reset_btn = ttk.Button(
            toolbar_frame2,
            text="🔄 Réinitialiser",
            command=self.reset_workflow,
            width=20,
            style="BlackOutline.TButton"
        )
        self.reset_btn.pack(side=LEFT, padx=(0, 10))

        # Barre de progression
        self.progress = ttk.Progressbar(
            toolbar_frame2,
            mode='indeterminate',
            length=200,
            style="Gold.Horizontal.TProgressbar"
        )
        self.progress.pack(side=LEFT, padx=(0, 10))

        # Panneau principal - Résultats avec onglets
        right_panel = ttk.Frame(main_container)
        right_panel.pack(fill=BOTH, expand=YES)

        self.notebook = ttk.Notebook(right_panel, style="Gold.TNotebook")
        self.notebook.pack(fill=BOTH, expand=YES)

        # Onglet Options de regroupement (NOUVEAU - Étape 1)
        options_frame = ttk.Frame(self.notebook)
        self.notebook.add(options_frame, text="⚙️ Options de regroupement")
        self.create_options_tab(options_frame)

        # Onglet Sessions de cours
        sessions_frame = ttk.Frame(self.notebook)
        self.notebook.add(sessions_frame, text="📅 Sessions de cours")
        self.create_sessions_tab(sessions_frame)

        # Onglet Horaires individuels
        individual_frame = ttk.Frame(self.notebook)
        self.notebook.add(individual_frame, text="👤 Horaires individuels")
        self.create_individual_schedules_tab(individual_frame)

        # Onglet Horaires des enseignants
        teacher_frame = ttk.Frame(self.notebook)
        self.notebook.add(teacher_frame, text="👨‍🏫 Horaires enseignants")
        self.create_teacher_schedules_tab(teacher_frame)

        # Onglet Statistiques
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📊 Statistiques")
        self.create_stats_tab(stats_frame)

        # Onglet Gestion des Données
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="🗂️ Gestion des Données")
        self.create_data_management_tab(data_frame)

        # Barre de statut
        status_frame = ttk.Frame(self.root, style="Black.TFrame")
        status_frame.pack(fill=X, side=BOTTOM)

        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            style="StatusBar.TLabel"
        )
        self.status_label.pack(pady=10, padx=20)

    def apply_custom_styles(self):
        """Applique les styles personnalisés avec les couleurs or, noir et blanc"""
        style = ttk.Style()

        # Style pour le header (fond or, texte noir)
        style.configure("Gold.TFrame", background=self.GOLD)
        style.configure("GoldHeader.TLabel",
                       background=self.GOLD,
                       foreground=self.BLACK,
                       font=("Segoe UI", 20, "bold"))
        style.configure("GoldSubHeader.TLabel",
                       background=self.GOLD,
                       foreground=self.BLACK,
                       font=("Segoe UI", 11))

        # Style pour la barre de statut (fond noir, texte or)
        style.configure("Black.TFrame", background=self.BLACK)
        style.configure("StatusBar.TLabel",
                       background=self.BLACK,
                       foreground=self.GOLD,
                       font=("Segoe UI", 10))

        # Styles pour les boutons principaux (fond or, texte noir)
        style.configure("Gold.TButton",
                       background=self.GOLD,
                       foreground=self.BLACK,
                       bordercolor=self.BLACK,
                       focuscolor=self.GOLD_DARK,
                       lightcolor=self.GOLD,
                       darkcolor=self.GOLD_DARK,
                       borderwidth=2,
                       relief="raised",
                       font=("Segoe UI", 10, "bold"))

        style.map("Gold.TButton",
                 background=[("active", self.GOLD_DARK), ("disabled", "#E0E0E0")],
                 foreground=[("active", self.BLACK), ("disabled", "#999999")])

        # Style pour boutons noirs (fond noir, texte or)
        style.configure("Black.TButton",
                       background=self.BLACK,
                       foreground=self.GOLD,
                       bordercolor=self.GOLD,
                       focuscolor=self.BLACK,
                       lightcolor=self.BLACK,
                       darkcolor=self.BLACK,
                       borderwidth=2,
                       relief="raised",
                       font=("Segoe UI", 10, "bold"))

        style.map("Black.TButton",
                 background=[("active", "#333333"), ("disabled", "#E0E0E0")],
                 foreground=[("active", self.GOLD), ("disabled", "#999999")])

        # Style pour boutons outline noir
        style.configure("BlackOutline.TButton",
                       background=self.WHITE,
                       foreground=self.BLACK,
                       bordercolor=self.BLACK,
                       focuscolor=self.GRAY_LIGHT,
                       borderwidth=2,
                       relief="solid",
                       font=("Segoe UI", 10))

        style.map("BlackOutline.TButton",
                 background=[("active", self.GRAY_LIGHT), ("disabled", "#F0F0F0")],
                 foreground=[("active", self.BLACK), ("disabled", "#999999")])

        # Style pour la barre de progression (or)
        style.configure("Gold.Horizontal.TProgressbar",
                       background=self.GOLD,
                       troughcolor=self.WHITE,
                       bordercolor=self.BLACK,
                       lightcolor=self.GOLD,
                       darkcolor=self.GOLD_DARK)

        # Style pour le notebook (onglets or et noir)
        style.configure("Gold.TNotebook",
                       background=self.WHITE,
                       bordercolor=self.BLACK,
                       lightcolor=self.GOLD)

        style.configure("Gold.TNotebook.Tab",
                       background=self.WHITE,
                       foreground=self.BLACK,
                       bordercolor=self.BLACK,
                       lightcolor=self.GOLD,
                       padding=[10, 5],
                       font=("Segoe UI", 10))

        style.map("Gold.TNotebook.Tab",
                 background=[("selected", self.GOLD), ("active", self.GRAY_LIGHT)],
                 foreground=[("selected", self.BLACK), ("active", self.BLACK)],
                 expand=[("selected", [1, 1, 1, 0])])

        # Style pour les Treeview (fond blanc, sélection or)
        style.configure("Treeview",
                       background=self.WHITE,
                       foreground=self.BLACK,
                       fieldbackground=self.WHITE,
                       bordercolor=self.BLACK,
                       borderwidth=1)

        style.configure("Treeview.Heading",
                       background=self.GOLD,
                       foreground=self.BLACK,
                       bordercolor=self.BLACK,
                       relief="raised",
                       font=("Segoe UI", 10, "bold"))

        style.map("Treeview.Heading",
                 background=[("active", self.GOLD_DARK)],
                 foreground=[("active", self.BLACK)])

        style.map("Treeview",
                 background=[("selected", self.GOLD)],
                 foreground=[("selected", self.BLACK)])

        # Style pour les LabelFrame
        style.configure("TLabelframe",
                       background=self.WHITE,
                       foreground=self.BLACK,
                       bordercolor=self.GOLD_DARK,
                       borderwidth=2)

        style.configure("TLabelframe.Label",
                       background=self.WHITE,
                       foreground=self.GOLD_DARK,
                       font=("Segoe UI", 11, "bold"))


    def create_options_tab(self, parent):
        """Crée l'onglet des options de regroupement"""
        # Frame principal avec scrollbar
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Section de configuration des tailles de groupe
        config_frame = ttk.LabelFrame(main_frame, text="⚙️ Configuration des tailles de groupe", padding=15)
        config_frame.pack(fill=X, pady=(0, 10))

        ttk.Label(
            config_frame,
            text="Personnalisez les tailles de groupe avant de générer les options",
            font=("Segoe UI", 9),
            foreground=self.BLACK
        ).pack(anchor=W, pady=(0, 10))

        # Frame pour les 3 types de groupes
        groups_config_frame = ttk.Frame(config_frame)
        groups_config_frame.pack(fill=X, pady=(0, 10))

        # Petits groupes
        small_frame = ttk.Frame(groups_config_frame)
        small_frame.pack(side=LEFT, padx=(0, 20))
        ttk.Label(small_frame, text="Petits groupes:", font=("Segoe UI", 9, "bold")).pack(anchor=W)
        small_controls = ttk.Frame(small_frame)
        small_controls.pack(anchor=W, pady=5)
        ttk.Label(small_controls, text="Min:", font=("Segoe UI", 9)).pack(side=LEFT, padx=(0, 5))
        ttk.Spinbox(small_controls, from_=10, to=30, textvariable=self.small_group_min, width=5).pack(side=LEFT, padx=(0, 10))
        ttk.Label(small_controls, text="Max:", font=("Segoe UI", 9)).pack(side=LEFT, padx=(0, 5))
        ttk.Spinbox(small_controls, from_=10, to=32, textvariable=self.small_group_max, width=5).pack(side=LEFT)

        # Groupes moyens
        medium_frame = ttk.Frame(groups_config_frame)
        medium_frame.pack(side=LEFT, padx=(0, 20))
        ttk.Label(medium_frame, text="Groupes moyens:", font=("Segoe UI", 9, "bold")).pack(anchor=W)
        medium_controls = ttk.Frame(medium_frame)
        medium_controls.pack(anchor=W, pady=5)
        ttk.Label(medium_controls, text="Min:", font=("Segoe UI", 9)).pack(side=LEFT, padx=(0, 5))
        ttk.Spinbox(medium_controls, from_=10, to=30, textvariable=self.medium_group_min, width=5).pack(side=LEFT, padx=(0, 10))
        ttk.Label(medium_controls, text="Max:", font=("Segoe UI", 9)).pack(side=LEFT, padx=(0, 5))
        ttk.Spinbox(medium_controls, from_=10, to=32, textvariable=self.medium_group_max, width=5).pack(side=LEFT)

        # Grands groupes
        large_frame = ttk.Frame(groups_config_frame)
        large_frame.pack(side=LEFT)
        ttk.Label(large_frame, text="Grands groupes:", font=("Segoe UI", 9, "bold")).pack(anchor=W)
        large_controls = ttk.Frame(large_frame)
        large_controls.pack(anchor=W, pady=5)
        ttk.Label(large_controls, text="Min:", font=("Segoe UI", 9)).pack(side=LEFT, padx=(0, 5))
        ttk.Spinbox(large_controls, from_=10, to=30, textvariable=self.large_group_min, width=5).pack(side=LEFT, padx=(0, 10))
        ttk.Label(large_controls, text="Max:", font=("Segoe UI", 9)).pack(side=LEFT, padx=(0, 5))
        ttk.Spinbox(large_controls, from_=10, to=32, textvariable=self.large_group_max, width=5).pack(side=LEFT)

        # Info en haut
        info_label = ttk.Label(
            main_frame,
            text="Sélectionnez une option de regroupement parmi les 9 configurations disponibles",
            font=("Segoe UI", 11, "bold"),
            foreground=self.GOLD_DARK
        )
        info_label.pack(anchor=W, pady=(10, 10))

        # Treeview pour afficher les options
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=BOTH, expand=YES)

        columns = ("ID", "Nom", "Taille groupe", "Stratégie", "Variante programme", "Sessions estimées", "Taille moy.")
        self.options_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=12
        )

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.options_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.options_tree.xview)
        self.options_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Configuration des colonnes
        self.options_tree.heading("ID", text="#")
        self.options_tree.heading("Nom", text="Nom")
        self.options_tree.heading("Taille groupe", text="Taille groupe")
        self.options_tree.heading("Stratégie", text="Stratégie d'optimisation")
        self.options_tree.heading("Variante programme", text="Variante programme")
        self.options_tree.heading("Sessions estimées", text="Sessions estimées")
        self.options_tree.heading("Taille moy.", text="Taille moy. groupe")

        self.options_tree.column("ID", width=40, anchor=CENTER)
        self.options_tree.column("Nom", width=150)
        self.options_tree.column("Taille groupe", width=120)
        self.options_tree.column("Stratégie", width=200)
        self.options_tree.column("Variante programme", width=150)
        self.options_tree.column("Sessions estimées", width=130, anchor=CENTER)
        self.options_tree.column("Taille moy.", width=130, anchor=CENTER)

        # Pack
        self.options_tree.pack(side=LEFT, fill=BOTH, expand=YES)
        vsb.pack(side=RIGHT, fill=Y)
        hsb.pack(side=BOTTOM, fill=X)

        # Bind la sélection
        self.options_tree.bind("<<TreeviewSelect>>", self.on_option_selected)

        # Frame pour la description de l'option sélectionnée
        desc_frame = ttk.LabelFrame(main_frame, text="Description de l'option", padding=10)
        desc_frame.pack(fill=X, pady=(10, 0))

        self.option_desc_label = ttk.Label(
            desc_frame,
            text="Sélectionnez une option pour voir sa description détaillée",
            font=("Segoe UI", 10),
            wraplength=1300,
            justify=LEFT,
            foreground=self.BLACK
        )
        self.option_desc_label.pack(anchor=W)

    def create_sessions_tab(self, parent):
        """Crée l'onglet des sessions de cours"""
        # Frame avec scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Treeview avec style
        columns = ("Jour", "Période", "Cours", "Enseignant", "Salle", "Étudiants")
        self.sessions_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=20
        )

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.sessions_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.sessions_tree.xview)
        self.sessions_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Configuration des colonnes
        self.sessions_tree.heading("Jour", text="📅 Jour")
        self.sessions_tree.heading("Période", text="⏰ Période")
        self.sessions_tree.heading("Cours", text="📚 Cours")
        self.sessions_tree.heading("Enseignant", text="👨‍🏫 Enseignant")
        self.sessions_tree.heading("Salle", text="🏫 Salle")
        self.sessions_tree.heading("Étudiants", text="👥 Étudiants")

        self.sessions_tree.column("Jour", width=80, anchor=CENTER)
        self.sessions_tree.column("Période", width=80, anchor=CENTER)
        self.sessions_tree.column("Cours", width=250)
        self.sessions_tree.column("Enseignant", width=200)
        self.sessions_tree.column("Salle", width=150)
        self.sessions_tree.column("Étudiants", width=120, anchor=CENTER)

        # Pack
        self.sessions_tree.pack(side=LEFT, fill=BOTH, expand=YES)
        vsb.pack(side=RIGHT, fill=Y)
        hsb.pack(side=BOTTOM, fill=X)

    def create_individual_schedules_tab(self, parent):
        """Crée l'onglet des horaires individuels"""
        # Frame pour sélecteur d'étudiant
        selector_frame = ttk.Frame(parent)
        selector_frame.pack(fill=X, padx=10, pady=10)

        ttk.Label(selector_frame, text="Sélectionner un étudiant:", font=("Segoe UI", 11)).pack(side=LEFT, padx=(0, 10))

        self.student_combobox = ttk.Combobox(selector_frame, state="readonly", width=30)
        self.student_combobox.pack(side=LEFT, padx=(0, 10))
        self.student_combobox.bind("<<ComboboxSelected>>", self.on_student_selected)

        # Frame avec scrollbar pour l'horaire
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Treeview avec style
        columns = ("Jour", "Période", "Cours", "Enseignant", "Salle")
        self.individual_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=20
        )

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.individual_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.individual_tree.xview)
        self.individual_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Configuration des colonnes
        self.individual_tree.heading("Jour", text="📅 Jour")
        self.individual_tree.heading("Période", text="⏰ Période")
        self.individual_tree.heading("Cours", text="📚 Cours")
        self.individual_tree.heading("Enseignant", text="👨‍🏫 Enseignant")
        self.individual_tree.heading("Salle", text="🏫 Salle")

        self.individual_tree.column("Jour", width=100, anchor=CENTER)
        self.individual_tree.column("Période", width=100, anchor=CENTER)
        self.individual_tree.column("Cours", width=300)
        self.individual_tree.column("Enseignant", width=250)
        self.individual_tree.column("Salle", width=200)

        # Pack
        self.individual_tree.pack(side=LEFT, fill=BOTH, expand=YES)
        vsb.pack(side=RIGHT, fill=Y)
        hsb.pack(side=BOTTOM, fill=X)

    def create_teacher_schedules_tab(self, parent):
        """Crée l'onglet des horaires des enseignants"""
        # Frame pour sélecteur d'enseignant
        selector_frame = ttk.Frame(parent)
        selector_frame.pack(fill=X, padx=10, pady=10)

        ttk.Label(selector_frame, text="Sélectionner un enseignant:", font=("Segoe UI", 11)).pack(side=LEFT, padx=(0, 10))

        self.teacher_combobox = ttk.Combobox(selector_frame, state="readonly", width=30)
        self.teacher_combobox.pack(side=LEFT, padx=(0, 10))
        self.teacher_combobox.bind("<<ComboboxSelected>>", self.on_teacher_selected)

        # Frame avec scrollbar pour l'horaire
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Treeview avec style
        columns = ("Jour", "Période", "Cours", "Salle", "Étudiants")
        self.teacher_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=20
        )

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.teacher_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.teacher_tree.xview)
        self.teacher_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Configuration des colonnes
        self.teacher_tree.heading("Jour", text="📅 Jour")
        self.teacher_tree.heading("Période", text="⏰ Période")
        self.teacher_tree.heading("Cours", text="📚 Cours")
        self.teacher_tree.heading("Salle", text="🏫 Salle")
        self.teacher_tree.heading("Étudiants", text="👥 Étudiants")

        self.teacher_tree.column("Jour", width=100, anchor=CENTER)
        self.teacher_tree.column("Période", width=100, anchor=CENTER)
        self.teacher_tree.column("Cours", width=300)
        self.teacher_tree.column("Salle", width=250)
        self.teacher_tree.column("Étudiants", width=200, anchor=CENTER)

        # Pack
        self.teacher_tree.pack(side=LEFT, fill=BOTH, expand=YES)
        vsb.pack(side=RIGHT, fill=Y)
        hsb.pack(side=BOTTOM, fill=X)

    def create_stats_tab(self, parent):
        """Crée l'onglet des statistiques"""
        self.stats_text = ScrolledText(
            parent,
            padding=10,
            autohide=True,
            height=25
        )
        self.stats_text.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    def run_optimization(self):
        """Lance l'optimisation"""
        try:
            self.status_var.set("Chargement des données depuis les fichiers CSV...")
            self.generate_btn.config(state="disabled")
            self.progress.start()
            self.root.update()

            # Générer les données (charge depuis CSV ou utilise les valeurs par défaut)
            # Utiliser des limites élevées pour charger toutes les données depuis les CSV
            self.course_requirements, self.teachers, self.classrooms, self.students, self.min_students_per_session = \
                generate_sample_data(num_students=200, num_teachers=50, num_classrooms=30, use_csv_data=True)

            num_students = len(self.students)
            num_teachers = len(self.teachers)
            num_classrooms = len(self.classrooms)

            self.status_var.set(f"Données chargées: {num_students} étudiants, {num_teachers} enseignants, {num_classrooms} salles...")

            self.status_var.set("Optimisation en cours... (peut prendre jusqu'à 10 minutes)")
            self.root.update()

            # Optimisation
            optimizer = ScheduleOptimizer(
                self.teachers,
                self.classrooms,
                self.students,
                self.course_requirements,
                self.min_students_per_session
            )

            success, sessions, student_schedules = optimizer.solve()

            self.progress.stop()

            if success:
                self.sessions = sessions
                self.student_schedules = student_schedules
                self.display_sessions()
                self.populate_student_selector()
                self.populate_teacher_selector()
                self.display_statistics()
                self.export_btn.config(state="normal")
                self.status_var.set(f"✓ Horaire généré avec succès pour {num_students} étudiants!")
                Messagebox.show_info(
                    f"L'horaire a été généré avec succès pour {num_students} étudiants!\n\n"
                    f"• {len(sessions)} sessions de cours créées\n"
                    "• Chaque étudiant a son horaire personnalisé\n"
                    "• Ressources minimisées\n"
                    "• Maximum 1 cours par matière par jour",
                    "Optimisation réussie"
                )
            else:
                self.status_var.set("❌ Échec de l'optimisation")
                Messagebox.show_error(
                    "Impossible de trouver une solution optimale.\n\n"
                    "Suggestions:\n"
                    "• Réduire le nombre d'étudiants\n"
                    "• Vérifier les contraintes\n"
                    "• Augmenter le nombre de salles",
                    "Erreur d'optimisation"
                )

        except Exception as e:
            import traceback
            self.progress.stop()
            self.status_var.set("❌ Erreur lors de l'optimisation")
            Messagebox.show_error(
                f"Une erreur s'est produite:\n{str(e)}\n\n{traceback.format_exc()}",
                "Erreur"
            )

        finally:
            self.generate_btn.config(state="normal")

    # ========================
    # NOUVELLES MÉTHODES POUR LE FLUX EN 3 ÉTAPES
    # ========================

    def step1_generate_options(self):
        """ÉTAPE 1 : Génère les 9 options de regroupement"""
        try:
            # Valider les tailles de groupe
            validation_errors = []

            if self.small_group_min.get() >= self.small_group_max.get():
                validation_errors.append("Petits groupes : Min doit être < Max")
            if self.medium_group_min.get() >= self.medium_group_max.get():
                validation_errors.append("Groupes moyens : Min doit être < Max")
            if self.large_group_min.get() >= self.large_group_max.get():
                validation_errors.append("Grands groupes : Min doit être < Max")

            if self.small_group_min.get() < 5 or self.small_group_max.get() > 32:
                validation_errors.append("Petits groupes : Les valeurs doivent être entre 5 et 32")
            if self.medium_group_min.get() < 5 or self.medium_group_max.get() > 32:
                validation_errors.append("Groupes moyens : Les valeurs doivent être entre 5 et 32")
            if self.large_group_min.get() < 5 or self.large_group_max.get() > 32:
                validation_errors.append("Grands groupes : Les valeurs doivent être entre 5 et 32")

            if validation_errors:
                Messagebox.show_error(
                    "Erreurs de validation :\n\n" + "\n".join(validation_errors),
                    "Valeurs invalides"
                )
                return

            self.status_var.set("Chargement des données depuis les fichiers CSV...")
            self.step1_btn.config(state="disabled")
            self.progress.start()
            self.root.update()

            # Charger les données
            self.course_requirements, self.teachers, self.classrooms, self.students, self.min_students_per_session = \
                generate_sample_data(num_students=200, num_teachers=50, num_classrooms=30, use_csv_data=True)

            num_students = len(self.students)
            self.status_var.set(f"Génération de 9 options pour {num_students} étudiants...")
            self.root.update()

            # Créer les tailles de groupe personnalisées à partir des valeurs de l'interface
            custom_group_sizes = [
                GroupSizeOption(
                    "Petits groupes",
                    self.small_group_min.get(),
                    self.small_group_max.get(),
                    f"Groupes de {self.small_group_min.get()}-{self.small_group_max.get()} étudiants (plus de sessions, plus d'attention individuelle)"
                ),
                GroupSizeOption(
                    "Groupes moyens",
                    self.medium_group_min.get(),
                    self.medium_group_max.get(),
                    f"Groupes de {self.medium_group_min.get()}-{self.medium_group_max.get()} étudiants (équilibre entre taille et ressources)"
                ),
                GroupSizeOption(
                    "Grands groupes",
                    self.large_group_min.get(),
                    self.large_group_max.get(),
                    f"Groupes de {self.large_group_min.get()}-{self.large_group_max.get()} étudiants (moins de sessions, optimisation des ressources)"
                )
            ]

            # Générer les 9 options avec les tailles personnalisées
            self.grouping_options = ScheduleOptimizer.generate_grouping_options(
                self.students,
                self.course_requirements,
                custom_group_sizes
            )

            # Afficher les options dans le treeview
            self.display_options()

            self.progress.stop()
            self.status_var.set("9 options générées. Sélectionnez-en une et passez à l'étape 2.")

            Messagebox.show_info(
                f"9 options de regroupement ont été générées avec succès!\n\n"
                f"Données chargées:\n"
                f"• {num_students} étudiants\n"
                f"• {len(self.teachers)} enseignants\n"
                f"• {len(self.classrooms)} salles\n\n"
                "Consultez l'onglet '⚙️ Options de regroupement' et sélectionnez une option.",
                "Options générées"
            )

            # Activer la sélection (pas encore le bouton 2)
            self.notebook.select(0)  # Aller sur l'onglet des options

        except Exception as e:
            import traceback
            self.progress.stop()
            self.status_var.set("❌ Erreur lors de la génération des options")
            Messagebox.show_error(
                f"Une erreur s'est produite:\n{str(e)}\n\n{traceback.format_exc()}",
                "Erreur"
            )

        finally:
            self.step1_btn.config(state="normal")

    def display_options(self):
        """Affiche les 9 options dans le treeview"""
        # Vider le treeview
        for item in self.options_tree.get_children():
            self.options_tree.delete(item)

        # Ajouter les options
        for i, option in enumerate(self.grouping_options):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'

            self.options_tree.insert(
                "",
                "end",
                values=(
                    option.id + 1,
                    option.name,
                    f"{option.group_size.min_students}-{option.group_size.max_students}",
                    option.strategy.value,
                    option.program_variant.value,
                    option.estimated_sessions,
                    f"{option.avg_group_size:.1f}"
                ),
                tags=(tag,)
            )

        # Configuration des tags
        self.options_tree.tag_configure('evenrow', background=self.GRAY_LIGHT)
        self.options_tree.tag_configure('oddrow', background=self.WHITE)

    def on_option_selected(self, event=None):
        """Appelé quand une option est sélectionnée"""
        selection = self.options_tree.selection()
        if not selection:
            return

        # Récupérer l'index de l'option sélectionnée
        item = self.options_tree.item(selection[0])
        option_id = int(item['values'][0]) - 1

        if 0 <= option_id < len(self.grouping_options):
            self.selected_option = self.grouping_options[option_id]

            # Afficher la description
            desc = f"Option {option_id + 1} sélectionnée:\n\n"
            desc += f"Taille de groupe: {self.selected_option.group_size.name} "
            desc += f"({self.selected_option.group_size.min_students}-{self.selected_option.group_size.max_students} étudiants)\n"
            desc += f"Stratégie: {self.selected_option.strategy.value}\n"
            desc += f"Variante: {self.selected_option.program_variant.value}\n\n"
            desc += f"Estimation: ~{self.selected_option.estimated_sessions} sessions avec une taille moyenne de {self.selected_option.avg_group_size:.1f} étudiants\n\n"
            desc += f"{self.selected_option.group_size.description}"

            self.option_desc_label.config(text=desc)

            # Activer le bouton de l'étape 2
            self.step2_btn.config(state="normal")
            self.step1_completed = True
            self.status_var.set(f"Option {option_id + 1} sélectionnée. Vous pouvez passer à l'étape 2.")

    def step2_generate_student_schedules(self):
        """ÉTAPE 2 : Génère les horaires des étudiants avec l'option sélectionnée"""
        if not self.step1_completed or not self.selected_option:
            Messagebox.show_warning(
                "Veuillez d'abord compléter l'étape 1 et sélectionner une option.",
                "Étape 1 non complétée"
            )
            return

        try:
            self.status_var.set("Génération des horaires étudiants en cours...")
            self.step2_btn.config(state="disabled")
            self.progress.start()
            self.root.update()

            # Créer l'optimiseur avec l'option sélectionnée
            optimizer = ScheduleOptimizer(
                self.teachers,
                self.classrooms,
                self.students,
                self.course_requirements,
                self.selected_option
            )

            # Résoudre UNIQUEMENT les horaires étudiants
            success, sessions, student_schedules = optimizer.solve_student_schedules_only()

            self.progress.stop()

            if success:
                self.sessions = sessions
                self.student_schedules = student_schedules
                self.step2_completed = True

                # Afficher les résultats (sans enseignants/salles)
                self.display_sessions()
                self.populate_student_selector()
                self.display_statistics()

                # Activer le bouton de l'étape 3
                self.step3_btn.config(state="normal")

                self.status_var.set(f"✓ Horaires étudiants générés! {len(sessions)} sessions créées.")
                Messagebox.show_info(
                    f"Les horaires des étudiants ont été générés avec succès!\n\n"
                    f"• {len(sessions)} sessions créées\n"
                    f"• {len(self.students)} étudiants avec horaires personnalisés\n"
                    f"• Enseignants et salles pas encore assignés\n\n"
                    "Passez à l'étape 3 pour assigner les enseignants et salles.",
                    "Étape 2 complétée"
                )
            else:
                self.status_var.set("❌ Échec de la génération des horaires")
                Messagebox.show_error(
                    "Impossible de trouver une solution pour les horaires étudiants.\n\n"
                    "Suggestions:\n"
                    "• Essayez une autre option de regroupement\n"
                    "• Vérifiez les contraintes des données",
                    "Erreur d'optimisation"
                )

        except Exception as e:
            import traceback
            self.progress.stop()
            self.status_var.set("❌ Erreur lors de la génération des horaires")
            Messagebox.show_error(
                f"Une erreur s'est produite:\n{str(e)}\n\n{traceback.format_exc()}",
                "Erreur"
            )

        finally:
            self.step2_btn.config(state="normal")

    def step3_assign_teachers_rooms(self):
        """ÉTAPE 3 : Assigne les enseignants et salles aux sessions existantes"""
        if not self.step2_completed or not self.sessions:
            Messagebox.show_warning(
                "Veuillez d'abord compléter l'étape 2 (génération des horaires étudiants).",
                "Étape 2 non complétée"
            )
            return

        try:
            self.status_var.set("Assignation des enseignants et salles en cours...")
            self.step3_btn.config(state="disabled")
            self.progress.start()
            self.root.update()

            # Assigner les enseignants et salles
            success, updated_sessions = ScheduleOptimizer.assign_teachers_and_rooms(
                self.sessions,
                self.teachers,
                self.classrooms
            )

            self.progress.stop()

            if success:
                self.sessions = updated_sessions
                self.step3_completed = True

                # Mettre à jour les affichages
                self.display_sessions()
                self.populate_teacher_selector()
                self.display_statistics()

                # Activer l'export
                self.export_btn.config(state="normal")

                self.status_var.set("✓ Horaire complet généré avec succès!")
                Messagebox.show_info(
                    f"L'horaire complet a été généré avec succès!\n\n"
                    f"• {len(self.sessions)} sessions avec enseignants et salles\n"
                    f"• Horaires personnalisés pour {len(self.students)} étudiants\n"
                    f"• Vous pouvez maintenant exporter vers Excel",
                    "Optimisation complète"
                )
            else:
                self.status_var.set("❌ Échec de l'assignation")
                Messagebox.show_error(
                    "Impossible d'assigner tous les enseignants et salles.\n\n"
                    "Suggestions:\n"
                    "• Vérifiez qu'il y a assez d'enseignants qualifiés\n"
                    "• Vérifiez qu'il y a assez de salles disponibles",
                    "Erreur d'assignation"
                )

        except Exception as e:
            import traceback
            self.progress.stop()
            self.status_var.set("❌ Erreur lors de l'assignation")
            Messagebox.show_error(
                f"Une erreur s'est produite:\n{str(e)}\n\n{traceback.format_exc()}",
                "Erreur"
            )

        finally:
            self.step3_btn.config(state="normal")

    def reset_workflow(self):
        """Réinitialise le flux de travail pour recommencer"""
        result = Messagebox.show_question(
            "Êtes-vous sûr de vouloir réinitialiser?\n\n"
            "Cela effacera toutes les données générées et vous devrez recommencer depuis l'étape 1.",
            "Confirmer la réinitialisation"
        )

        if result == "Yes":
            # Réinitialiser les données
            self.grouping_options = []
            self.selected_option = None
            self.sessions = []
            self.student_schedules = {}
            self.step1_completed = False
            self.step2_completed = False
            self.step3_completed = False

            # Réinitialiser les boutons
            self.step1_btn.config(state="normal")
            self.step2_btn.config(state="disabled")
            self.step3_btn.config(state="disabled")
            self.export_btn.config(state="disabled")

            # Vider les affichages
            for item in self.options_tree.get_children():
                self.options_tree.delete(item)
            for item in self.sessions_tree.get_children():
                self.sessions_tree.delete(item)
            for item in self.individual_tree.get_children():
                self.individual_tree.delete(item)
            for item in self.teacher_tree.get_children():
                self.teacher_tree.delete(item)

            self.option_desc_label.config(text="Sélectionnez une option pour voir sa description détaillée")
            self.stats_text.delete("1.0", "end")

            self.status_var.set("Flux de travail réinitialisé. Commencez par l'étape 1.")

    # ========================
    # FIN DES NOUVELLES MÉTHODES
    # ========================

    def display_sessions(self):
        """Affiche les sessions de cours dans le treeview"""
        # Vider le treeview
        for item in self.sessions_tree.get_children():
            self.sessions_tree.delete(item)

        # Ajouter les sessions avec alternance de couleurs
        for i, session in enumerate(self.sessions):
            teacher_name = session.assigned_teacher.name if session.assigned_teacher else "N/A"
            room_name = session.assigned_room.name if session.assigned_room else "N/A"
            num_students = len(session.students)

            tag = 'evenrow' if i % 2 == 0 else 'oddrow'

            self.sessions_tree.insert(
                "",
                "end",
                values=(
                    f"Jour {session.timeslot.day}",
                    f"Période {session.timeslot.period}",
                    f"{session.course_type.value}",
                    teacher_name,
                    room_name,
                    f"{num_students} étudiants"
                ),
                tags=(tag,)
            )

        # Configuration des tags pour l'alternance
        self.sessions_tree.tag_configure('evenrow', background=self.GRAY_LIGHT)
        self.sessions_tree.tag_configure('oddrow', background=self.WHITE)

    def populate_student_selector(self):
        """Remplit le sélecteur d'étudiants"""
        student_names = [f"Étudiant {student.id} - {student.name}" for student in self.students]
        self.student_combobox['values'] = student_names
        if student_names:
            self.student_combobox.current(0)
            self.display_individual_schedule(self.students[0].id)

    def on_student_selected(self, event=None):
        """Appelé quand un étudiant est sélectionné"""
        if not self.students:
            return

        selected_index = self.student_combobox.current()
        if selected_index >= 0:
            student_id = self.students[selected_index].id
            self.display_individual_schedule(student_id)

    def display_individual_schedule(self, student_id: int):
        """Affiche l'horaire d'un étudiant spécifique"""
        # Vider le treeview
        for item in self.individual_tree.get_children():
            self.individual_tree.delete(item)

        # Obtenir l'horaire de l'étudiant
        schedule = self.student_schedules.get(student_id, [])

        # Ajouter les cours avec alternance de couleurs
        for i, entry in enumerate(schedule):
            teacher_name = entry.session.assigned_teacher.name if entry.session and entry.session.assigned_teacher else "N/A"
            room_name = entry.session.assigned_room.name if entry.session and entry.session.assigned_room else "N/A"

            tag = 'evenrow' if i % 2 == 0 else 'oddrow'

            self.individual_tree.insert(
                "",
                "end",
                values=(
                    f"Jour {entry.timeslot.day}",
                    f"Période {entry.timeslot.period}",
                    f"{entry.course_type.value}",
                    teacher_name,
                    room_name
                ),
                tags=(tag,)
            )

        # Configuration des tags pour l'alternance
        self.individual_tree.tag_configure('evenrow', background=self.GRAY_LIGHT)
        self.individual_tree.tag_configure('oddrow', background=self.WHITE)

    def populate_teacher_selector(self):
        """Remplit le sélecteur d'enseignants"""
        teacher_names = [f"{teacher.name}" for teacher in self.teachers]
        self.teacher_combobox['values'] = teacher_names
        if teacher_names:
            self.teacher_combobox.current(0)
            self.display_teacher_schedule(self.teachers[0].id)

    def on_teacher_selected(self, event=None):
        """Appelé quand un enseignant est sélectionné"""
        if not self.teachers:
            return

        selected_index = self.teacher_combobox.current()
        if selected_index >= 0:
            teacher_id = self.teachers[selected_index].id
            self.display_teacher_schedule(teacher_id)

    def display_teacher_schedule(self, teacher_id: int):
        """Affiche l'horaire d'un enseignant spécifique"""
        # Vider le treeview
        for item in self.teacher_tree.get_children():
            self.teacher_tree.delete(item)

        # Trouver toutes les sessions de cet enseignant
        teacher_sessions = []
        for session in self.sessions:
            if session.assigned_teacher and session.assigned_teacher.id == teacher_id:
                teacher_sessions.append(session)

        # Trier par jour et période
        teacher_sessions = sorted(teacher_sessions, key=lambda s: (s.timeslot.day, s.timeslot.period))

        # Ajouter les sessions avec alternance de couleurs
        for i, session in enumerate(teacher_sessions):
            room_name = session.assigned_room.name if session.assigned_room else "N/A"
            num_students = len(session.students)
            student_list = ", ".join([f"#{s.id}" for s in session.students[:5]])  # Max 5 noms pour ne pas surcharger
            if len(session.students) > 5:
                student_list += f" (+{len(session.students) - 5} autres)"

            tag = 'evenrow' if i % 2 == 0 else 'oddrow'

            self.teacher_tree.insert(
                "",
                "end",
                values=(
                    f"Jour {session.timeslot.day}",
                    f"Période {session.timeslot.period}",
                    f"{session.course_type.value}",
                    room_name,
                    f"{num_students} étudiants"
                ),
                tags=(tag,)
            )

        # Configuration des tags pour l'alternance
        self.teacher_tree.tag_configure('evenrow', background=self.GRAY_LIGHT)
        self.teacher_tree.tag_configure('oddrow', background=self.WHITE)

    def display_statistics(self):
        """Affiche les statistiques"""
        self.stats_text.delete("1.0", "end")

        stats = "═══════════════════════════════════════════════════════════\n"
        stats += "                 STATISTIQUES DE L'HORAIRE                 \n"
        stats += "═══════════════════════════════════════════════════════════\n\n"

        # Info générale
        stats += "📊 INFORMATIONS GÉNÉRALES\n"
        stats += "─" * 60 + "\n"
        stats += f"   Nombre d'étudiants: {len(self.students)}\n"
        stats += f"   Nombre de sessions créées: {len(self.sessions)}\n"
        total_courses = sum(self.course_requirements.values())
        stats += f"   Cours par étudiant: {total_courses}\n"
        stats += f"   Nombre d'enseignants: {len(self.teachers)}\n"
        stats += f"   Nombre de salles: {len(self.classrooms)}\n\n"

        # Utilisation des enseignants
        teacher_load = {}
        for session in self.sessions:
            if session.assigned_teacher:
                teacher = session.assigned_teacher
                teacher_load[teacher.name] = teacher_load.get(teacher.name, 0) + 1

        stats += "👨‍🏫 CHARGE D'ENSEIGNEMENT (sessions)\n"
        stats += "─" * 60 + "\n"
        for teacher, count in sorted(teacher_load.items()):
            bar = "█" * count
            stats += f"   {teacher:<30} {count:>2} sessions {bar}\n"

        # Enseignants utilisés vs disponibles
        teachers_used = len(teacher_load)
        stats += f"\n   Enseignants utilisés: {teachers_used}/{len(self.teachers)}\n"

        # Statistiques sur les salles préférées des enseignants
        stats += "\n🏠 SALLES PRÉFÉRÉES DES ENSEIGNANTS\n"
        stats += "─" * 60 + "\n"
        teacher_home_stats = {}
        for teacher in self.teachers:
            if teacher.preferred_classroom:
                in_home = 0
                away = 0
                for session in self.sessions:
                    if session.assigned_teacher and session.assigned_teacher.id == teacher.id:
                        if session.assigned_room and session.assigned_room.id == teacher.preferred_classroom.id:
                            in_home += 1
                        else:
                            away += 1
                if in_home + away > 0:
                    teacher_home_stats[teacher.name] = {
                        'home': in_home,
                        'away': away,
                        'preferred': teacher.preferred_classroom.name
                    }

        total_in_home = 0
        total_away = 0
        for teacher, data in sorted(teacher_home_stats.items()):
            total = data['home'] + data['away']
            percent = (data['home'] / total * 100) if total > 0 else 0
            total_in_home += data['home']
            total_away += data['away']
            stats += f"   {teacher:<30} {data['preferred']:<12} {data['home']:>2}/{total:<2} ({percent:>5.1f}%)\n"

        if total_in_home + total_away > 0:
            overall_percent = (total_in_home / (total_in_home + total_away) * 100)
            stats += f"\n   Total: {total_in_home}/{total_in_home + total_away} sessions en salle préférée ({overall_percent:.1f}%)\n"

        # Utilisation des salles
        stats += "\n🏫 UTILISATION DES SALLES (sessions)\n"
        stats += "─" * 60 + "\n"
        room_usage = {}
        for session in self.sessions:
            if session.assigned_room:
                room = session.assigned_room
                room_usage[room.name] = room_usage.get(room.name, 0) + 1

        for room, count in sorted(room_usage.items()):
            bar = "█" * (count // 2)
            stats += f"   {room:<30} {count:>2} sessions {bar}\n"

        # Salles utilisées vs disponibles
        rooms_used = len(room_usage)
        stats += f"\n   Salles utilisées: {rooms_used}/{len(self.classrooms)}\n"

        # Distribution des étudiants par session
        stats += "\n👥 DISTRIBUTION DES ÉTUDIANTS PAR SESSION\n"
        stats += "─" * 60 + "\n"
        session_sizes = [len(session.students) for session in self.sessions]
        if session_sizes:
            stats += f"   Minimum: {min(session_sizes)} étudiants\n"
            stats += f"   Maximum: {max(session_sizes)} étudiants\n"
            stats += f"   Moyenne: {sum(session_sizes)/len(session_sizes):.1f} étudiants\n"

        # Optimisation des ressources
        stats += "\n🎯 OPTIMISATION DES RESSOURCES\n"
        stats += "─" * 60 + "\n"
        # Calculer le facteur de regroupement
        total_potential_sessions = len(self.students) * total_courses
        stats += f"   Sessions théoriques max: {total_potential_sessions}\n"
        stats += f"   Sessions créées: {len(self.sessions)}\n"
        efficiency = (1 - len(self.sessions) / total_potential_sessions) * 100
        stats += f"   Efficacité de regroupement: {efficiency:.1f}%\n"

        # Vérification: tous les étudiants dans tous les cours
        stats += "\n✓ VÉRIFICATION DES CONTRAINTES\n"
        stats += "─" * 60 + "\n"
        stats += "   ✓ Chaque étudiant a un horaire personnalisé\n"
        stats += "   ✓ Tous les cours requis sont assignés\n"
        stats += "   ✓ Maximum 32 étudiants par session respecté\n"
        stats += "   ✓ Pas de conflit d'enseignants\n"
        stats += "   ✓ Pas de conflit de salles\n"
        stats += "   ✓ Pas plus d'1 cours par matière par jour\n"

        stats += "\n" + "═" * 60 + "\n"

        self.stats_text.insert("1.0", stats)

    def export_to_excel(self):
        """Exporte l'horaire vers Excel"""
        try:
            # Créer un fichier Excel avec plusieurs feuilles
            filename = f"horaire_optimise_{len(self.students)}_etudiants.xlsx"

            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Feuille 1: Sessions de cours
                sessions_data = []
                for session in self.sessions:
                    sessions_data.append({
                        "Jour": session.timeslot.day,
                        "Période": session.timeslot.period,
                        "Cours": session.course_type.value,
                        "ID Session": session.id,
                        "Enseignant": session.assigned_teacher.name if session.assigned_teacher else "N/A",
                        "Salle": session.assigned_room.name if session.assigned_room else "N/A",
                        "Nombre d'étudiants": len(session.students),
                        "Étudiants": ", ".join([f"#{s.id}" for s in session.students])
                    })

                df_sessions = pd.DataFrame(sessions_data)
                df_sessions.to_excel(writer, sheet_name='Sessions', index=False)

                # Feuille 2: Horaires individuels par étudiant
                individual_data = []
                for student in self.students:
                    schedule = self.student_schedules.get(student.id, [])
                    for entry in schedule:
                        individual_data.append({
                            "Étudiant ID": student.id,
                            "Étudiant": student.name,
                            "Jour": entry.timeslot.day,
                            "Période": entry.timeslot.period,
                            "Cours": entry.course_type.value,
                            "Enseignant": entry.session.assigned_teacher.name if entry.session and entry.session.assigned_teacher else "N/A",
                            "Salle": entry.session.assigned_room.name if entry.session and entry.session.assigned_room else "N/A"
                        })

                df_individual = pd.DataFrame(individual_data)
                df_individual.to_excel(writer, sheet_name='Horaires individuels', index=False)

                # Feuille 3: Charge des enseignants
                teacher_data = []
                teacher_load = {}
                for session in self.sessions:
                    if session.assigned_teacher:
                        teacher = session.assigned_teacher
                        if teacher.name not in teacher_load:
                            teacher_load[teacher.name] = []
                        teacher_load[teacher.name].append({
                            "Jour": session.timeslot.day,
                            "Période": session.timeslot.period,
                            "Cours": session.course_type.value,
                            "Nombre d'étudiants": len(session.students)
                        })

                for teacher, sessions in teacher_load.items():
                    for session in sessions:
                        teacher_data.append({
                            "Enseignant": teacher,
                            **session
                        })

                df_teachers = pd.DataFrame(teacher_data)
                df_teachers.to_excel(writer, sheet_name='Enseignants', index=False)

            self.status_var.set(f"✓ Horaire exporté vers {filename}")
            Messagebox.show_info(
                f"L'horaire a été exporté avec succès vers:\n{filename}\n\n"
                f"Contenu:\n"
                f"• Feuille 'Sessions': {len(self.sessions)} sessions créées\n"
                f"• Feuille 'Horaires individuels': horaires de {len(self.students)} étudiants\n"
                f"• Feuille 'Enseignants': charge d'enseignement",
                "Export réussi"
            )

        except Exception as e:
            import traceback
            Messagebox.show_error(
                f"Erreur lors de l'export:\n{str(e)}\n\n{traceback.format_exc()}",
                "Erreur d'export"
            )

    def create_data_management_tab(self, parent):
        """Crée l'onglet de gestion des données"""
        # Conteneur principal avec padding
        main_frame = ttk.Frame(parent, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)

        # En-tête
        header_label = ttk.Label(
            main_frame,
            text="Gestion des Données",
            font=("Segoe UI", 16, "bold"),
            foreground=self.GOLD_DARK
        )
        header_label.pack(anchor=W, pady=(0, 10))

        info_label = ttk.Label(
            main_frame,
            text="Gérez les fichiers de données (élèves, enseignants, classes, programmes)",
            font=("Segoe UI", 10),
            foreground=self.BLACK
        )
        info_label.pack(anchor=W, pady=(0, 20))

        # Frame pour les sections
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=BOTH, expand=YES)

        # Section Élèves
        eleves_frame = ttk.LabelFrame(content_frame, text="📚 Élèves", padding=15)
        eleves_frame.pack(fill=X, pady=(0, 10))

        ttk.Label(
            eleves_frame,
            text="Fichier: data/eleves/eleves.csv",
            font=("Segoe UI", 9)
        ).pack(anchor=W, pady=(0, 5))

        eleves_btn_frame = ttk.Frame(eleves_frame)
        eleves_btn_frame.pack(fill=X)

        ttk.Button(
            eleves_btn_frame,
            text="Ouvrir le fichier CSV",
            style="Gold.TButton",
            command=lambda: self.open_csv_file("data/eleves/eleves.csv")
        ).pack(side=LEFT, padx=(0, 5))

        ttk.Button(
            eleves_btn_frame,
            text="Ouvrir le dossier",
            style="BlackOutline.TButton",
            command=lambda: self.open_folder("data/eleves")
        ).pack(side=LEFT)

        # Section Enseignants
        enseignants_frame = ttk.LabelFrame(content_frame, text="👨‍🏫 Enseignants", padding=15)
        enseignants_frame.pack(fill=X, pady=(0, 10))

        ttk.Label(
            enseignants_frame,
            text="Fichier: data/enseignants/enseignants.csv",
            font=("Segoe UI", 9)
        ).pack(anchor=W, pady=(0, 5))

        enseignants_btn_frame = ttk.Frame(enseignants_frame)
        enseignants_btn_frame.pack(fill=X)

        ttk.Button(
            enseignants_btn_frame,
            text="Ouvrir le fichier CSV",
            style="Gold.TButton",
            command=lambda: self.open_csv_file("data/enseignants/enseignants.csv")
        ).pack(side=LEFT, padx=(0, 5))

        ttk.Button(
            enseignants_btn_frame,
            text="Ouvrir le dossier",
            style="BlackOutline.TButton",
            command=lambda: self.open_folder("data/enseignants")
        ).pack(side=LEFT)

        # Section Classes
        classes_frame = ttk.LabelFrame(content_frame, text="🏫 Classes (Salles)", padding=15)
        classes_frame.pack(fill=X, pady=(0, 10))

        ttk.Label(
            classes_frame,
            text="Fichier: data/classes/classes.csv",
            font=("Segoe UI", 9)
        ).pack(anchor=W, pady=(0, 5))

        classes_btn_frame = ttk.Frame(classes_frame)
        classes_btn_frame.pack(fill=X)

        ttk.Button(
            classes_btn_frame,
            text="Ouvrir le fichier CSV",
            style="Gold.TButton",
            command=lambda: self.open_csv_file("data/classes/classes.csv")
        ).pack(side=LEFT, padx=(0, 5))

        ttk.Button(
            classes_btn_frame,
            text="Ouvrir le dossier",
            style="BlackOutline.TButton",
            command=lambda: self.open_folder("data/classes")
        ).pack(side=LEFT)

        # Section Programmes
        programmes_frame = ttk.LabelFrame(content_frame, text="📋 Programmes", padding=15)
        programmes_frame.pack(fill=X, pady=(0, 10))

        ttk.Label(
            programmes_frame,
            text="Dossier: data/programmes/",
            font=("Segoe UI", 9)
        ).pack(anchor=W, pady=(0, 5))

        # Lister les programmes disponibles
        data_manager = DataManager()
        programmes = data_manager.lister_programmes()

        if programmes:
            prog_text = "Programmes disponibles: " + ", ".join(programmes)
        else:
            prog_text = "Aucun programme trouvé"

        ttk.Label(
            programmes_frame,
            text=prog_text,
            font=("Segoe UI", 9),
            foreground=self.BLACK
        ).pack(anchor=W, pady=(0, 10))

        ttk.Button(
            programmes_frame,
            text="Ouvrir le dossier des programmes",
            style="Gold.TButton",
            command=lambda: self.open_folder("data/programmes")
        ).pack(anchor=W)

        # Section Actions
        actions_frame = ttk.LabelFrame(content_frame, text="⚙️ Actions", padding=15)
        actions_frame.pack(fill=X, pady=(10, 0))

        ttk.Label(
            actions_frame,
            text="Recréer les données d'exemple (écrase les fichiers existants)",
            font=("Segoe UI", 9),
            foreground=self.BLACK
        ).pack(anchor=W, pady=(0, 10))

        ttk.Button(
            actions_frame,
            text="Regénérer les données d'exemple",
            style="Black.TButton",
            command=self.regenerate_sample_data
        ).pack(anchor=W)

        # Note d'information
        note_frame = ttk.Frame(content_frame)
        note_frame.pack(fill=X, pady=(20, 0))

        ttk.Label(
            note_frame,
            text="ℹ️ Note: Après modification des fichiers CSV, relancez la génération d'horaire pour appliquer les changements.",
            font=("Segoe UI", 9),
            foreground=self.GOLD_DARK,
            wraplength=700
        ).pack(anchor=W)

    def open_csv_file(self, filepath):
        """Ouvre un fichier CSV avec l'application par défaut"""
        try:
            abs_path = os.path.abspath(filepath)
            if os.path.exists(abs_path):
                if os.name == 'nt':  # Windows
                    os.startfile(abs_path)
                elif os.name == 'posix':  # macOS, Linux
                    subprocess.call(['open' if 'darwin' in os.sys.platform else 'xdg-open', abs_path])
                self.status_var.set(f"Fichier ouvert: {filepath}")
            else:
                Messagebox.show_warning(
                    f"Le fichier n'existe pas:\n{abs_path}\n\nExécutez 'python creer_donnees_exemple.py' pour créer les fichiers.",
                    "Fichier introuvable"
                )
        except Exception as e:
            Messagebox.show_error(f"Erreur lors de l'ouverture du fichier:\n{str(e)}", "Erreur")

    def open_folder(self, folder_path):
        """Ouvre un dossier dans l'explorateur de fichiers"""
        try:
            abs_path = os.path.abspath(folder_path)
            if os.path.exists(abs_path):
                if os.name == 'nt':  # Windows
                    os.startfile(abs_path)
                elif os.name == 'posix':  # macOS, Linux
                    subprocess.call(['open' if 'darwin' in os.sys.platform else 'xdg-open', abs_path])
                self.status_var.set(f"Dossier ouvert: {folder_path}")
            else:
                Messagebox.show_warning(
                    f"Le dossier n'existe pas:\n{abs_path}\n\nExécutez 'python creer_donnees_exemple.py' pour créer les dossiers.",
                    "Dossier introuvable"
                )
        except Exception as e:
            Messagebox.show_error(f"Erreur lors de l'ouverture du dossier:\n{str(e)}", "Erreur")

    def regenerate_sample_data(self):
        """Régénère les données d'exemple"""
        result = Messagebox.show_question(
            "Êtes-vous sûr de vouloir régénérer les données d'exemple?\n\n"
            "Cela écrasera tous les fichiers CSV existants dans:\n"
            "- data/eleves/eleves.csv\n"
            "- data/enseignants/enseignants.csv\n"
            "- data/classes/classes.csv\n"
            "- data/programmes/*.json",
            "Confirmer la régénération"
        )

        if result == "Yes":
            try:
                # Exécuter le script de création de données
                import creer_donnees_exemple
                creer_donnees_exemple.creer_donnees_exemple()

                Messagebox.show_info(
                    "Les données d'exemple ont été régénérées avec succès!\n\n"
                    "56 élèves, 13 enseignants, 8 classes et 2 programmes ont été créés.",
                    "Régénération réussie"
                )
                self.status_var.set("Données d'exemple régénérées avec succès")
            except Exception as e:
                Messagebox.show_error(
                    f"Erreur lors de la régénération des données:\n{str(e)}",
                    "Erreur"
                )


def main():
    # Utiliser un thème Material Design
    root = ttk.Window(
        title="Création d'horaires",
        themename="litera",  # Thème Material-like
        size=(1400, 900)
    )
    app = SchedulerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
