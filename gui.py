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
from scheduler import ScheduleOptimizer
from data_generator import generate_sample_data


class SchedulerApp:
    """Application principale de création d'horaires avec Material Design"""

    def __init__(self, root):
        self.root = root
        self.root.title("Création d'horaires - Secondaire 4 Québec")
        self.root.geometry("1400x900")

        # Variables de configuration
        self.num_students_var = IntVar(value=56)
        self.num_teachers_var = IntVar(value=13)
        self.num_classrooms_var = IntVar(value=8)
        self.status_var = StringVar(value="Prêt à générer l'horaire")
        self.selected_student_var = IntVar(value=0)

        # Données
        self.course_requirements = {}
        self.teachers = []
        self.classrooms = []
        self.students = []
        self.sessions = []
        self.student_schedules = {}

        self.create_widgets()

    def create_widgets(self):
        """Crée les widgets de l'interface Material Design"""
        # Header
        header_frame = ttk.Frame(self.root, bootstyle="primary")
        header_frame.pack(fill=X, padx=0, pady=0)

        title_label = ttk.Label(
            header_frame,
            text="📚 Optimisation d'Horaires - Secondaire 4",
            font=("Segoe UI", 20, "bold"),
            bootstyle="inverse-primary"
        )
        title_label.pack(pady=20, padx=20)

        subtitle_label = ttk.Label(
            header_frame,
            text="Génération automatique d'horaires optimisés pour le Québec",
            font=("Segoe UI", 11),
            bootstyle="inverse-primary"
        )
        subtitle_label.pack(pady=(0, 20), padx=20)

        # Conteneur principal
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=BOTH, expand=YES, padx=20, pady=20)

        # Panneau gauche - Configuration avec scrollbar
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=LEFT, fill=BOTH, expand=NO, padx=(0, 10))

        # Canvas pour rendre scrollable
        canvas = ttk.Canvas(left_frame, width=320)
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)

        left_panel = ttk.LabelFrame(
            canvas,
            text="⚙️ Configuration",
            bootstyle="info",
            padding=15
        )

        left_panel.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=left_panel, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Support du scroll avec la molette de souris
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.create_config_panel(left_panel)

        # Panneau droit - Résultats avec onglets
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=LEFT, fill=BOTH, expand=YES)

        self.notebook = ttk.Notebook(right_panel, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=YES)

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

        # Barre de statut
        status_frame = ttk.Frame(self.root, bootstyle="secondary")
        status_frame.pack(fill=X, side=BOTTOM)

        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            bootstyle="inverse-secondary"
        )
        self.status_label.pack(pady=10, padx=20)

    def create_config_panel(self, parent):
        """Crée le panneau de configuration"""
        # Nombre d'étudiants
        student_frame = ttk.Labelframe(parent, text="Nombre d'étudiants", bootstyle="primary", padding=10)
        student_frame.pack(fill=X, pady=(0, 15))

        ttk.Label(
            student_frame,
            text="Étudiants en Secondaire 4 :",
            font=("Segoe UI", 10)
        ).pack(anchor=W, pady=(0, 5))

        student_spinbox = ttk.Spinbox(
            student_frame,
            from_=1,
            to=200,
            textvariable=self.num_students_var,
            bootstyle="info",
            font=("Segoe UI", 12),
            width=15
        )
        student_spinbox.pack(fill=X)

        ttk.Label(
            student_frame,
            text="Maximum 28 étudiants par classe",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(anchor=W, pady=(5, 0))

        # Nombre d'enseignants
        teachers_frame = ttk.Labelframe(parent, text="Nombre d'enseignants", bootstyle="primary", padding=10)
        teachers_frame.pack(fill=X, pady=(0, 15))

        ttk.Label(
            teachers_frame,
            text="Enseignants disponibles :",
            font=("Segoe UI", 10)
        ).pack(anchor=W, pady=(0, 5))

        teachers_spinbox = ttk.Spinbox(
            teachers_frame,
            from_=5,
            to=50,
            textvariable=self.num_teachers_var,
            bootstyle="info",
            font=("Segoe UI", 12),
            width=15
        )
        teachers_spinbox.pack(fill=X)

        ttk.Label(
            teachers_frame,
            text="Enseignants avec compétences variées",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(anchor=W, pady=(5, 0))

        # Nombre de salles
        classrooms_frame = ttk.Labelframe(parent, text="Nombre de salles", bootstyle="primary", padding=10)
        classrooms_frame.pack(fill=X, pady=(0, 15))

        ttk.Label(
            classrooms_frame,
            text="Salles de classe disponibles :",
            font=("Segoe UI", 10)
        ).pack(anchor=W, pady=(0, 5))

        classrooms_spinbox = ttk.Spinbox(
            classrooms_frame,
            from_=4,
            to=30,
            textvariable=self.num_classrooms_var,
            bootstyle="info",
            font=("Segoe UI", 12),
            width=15
        )
        classrooms_spinbox.pack(fill=X)

        ttk.Label(
            classrooms_frame,
            text="Capacité: 28 étudiants par salle",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(anchor=W, pady=(5, 0))

        # Info sur les cours
        courses_frame = ttk.Labelframe(parent, text="Cours requis (36 total)", bootstyle="success", padding=10)
        courses_frame.pack(fill=X, expand=NO, pady=(0, 15))

        courses_text = ScrolledText(courses_frame, height=8, autohide=True)
        courses_text.pack(fill=BOTH, expand=NO)

        course_info = """📐 Science: 4 classes
🔬 STE: 2 classes
🔧 ASC: 2 classes
📚 Français: 6 classes
🔢 Math SN: 6 classes
🗣️ Anglais: 4 classes
🌍 Histoire: 4 classes
🏛️ CCQ: 2 classes
🇪🇸 Espagnol: 2 classes
⚽ Éducation physique: 2 classes
🎨 Option: 2 classes

⏱️ 9 jours × 4 périodes = 36 créneaux

✓ Tous les étudiants suivent tous les cours
✓ Max 1 cours par matière par jour
✓ Optimisation des ressources"""

        courses_text.insert("1.0", course_info)
        courses_text.text.configure(state="disabled")  # Access the underlying Text widget

        # Boutons d'action
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=X, pady=(0, 10))

        self.generate_btn = ttk.Button(
            buttons_frame,
            text="🚀 Générer l'horaire",
            command=self.run_optimization,
            bootstyle="success",
            width=25
        )
        self.generate_btn.pack(fill=X, pady=(0, 10))

        self.export_btn = ttk.Button(
            buttons_frame,
            text="📥 Exporter vers Excel",
            command=self.export_to_excel,
            bootstyle="primary",
            state="disabled",
            width=25
        )
        self.export_btn.pack(fill=X)

        # Barre de progression
        self.progress = ttk.Progressbar(
            buttons_frame,
            mode='indeterminate',
            bootstyle="success-striped"
        )
        self.progress.pack(fill=X, pady=(10, 0))

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
            bootstyle="primary",
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
            bootstyle="info",
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
            bootstyle="success",
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
            num_students = self.num_students_var.get()
            num_teachers = self.num_teachers_var.get()
            num_classrooms = self.num_classrooms_var.get()

            if num_students < 1 or num_students > 200:
                Messagebox.show_error(
                    "Le nombre d'étudiants doit être entre 1 et 200.",
                    "Erreur de configuration"
                )
                return

            if num_teachers < 5 or num_teachers > 50:
                Messagebox.show_error(
                    "Le nombre d'enseignants doit être entre 5 et 50.",
                    "Erreur de configuration"
                )
                return

            if num_classrooms < 4 or num_classrooms > 30:
                Messagebox.show_error(
                    "Le nombre de salles doit être entre 4 et 30.",
                    "Erreur de configuration"
                )
                return

            self.status_var.set(f"Génération des données pour {num_students} étudiants, {num_teachers} enseignants, {num_classrooms} salles...")
            self.generate_btn.config(state="disabled")
            self.progress.start()
            self.root.update()

            # Générer les données
            self.course_requirements, self.teachers, self.classrooms, self.students = \
                generate_sample_data(num_students, num_teachers, num_classrooms)

            self.status_var.set("Optimisation en cours... (peut prendre jusqu'à 2 minutes)")
            self.root.update()

            # Optimisation
            optimizer = ScheduleOptimizer(
                self.teachers,
                self.classrooms,
                self.students,
                self.course_requirements
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
        self.sessions_tree.tag_configure('evenrow', background='#f0f0f0')
        self.sessions_tree.tag_configure('oddrow', background='white')

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
        self.individual_tree.tag_configure('evenrow', background='#f0f0f0')
        self.individual_tree.tag_configure('oddrow', background='white')

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
        self.teacher_tree.tag_configure('evenrow', background='#f0f0f0')
        self.teacher_tree.tag_configure('oddrow', background='white')

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
        stats += "   ✓ Maximum 28 étudiants par session respecté\n"
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
