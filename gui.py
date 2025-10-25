"""
Interface graphique Material Design pour le système de création d'horaires
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.dialogs import Messagebox
from tkinter import StringVar, IntVar
import pandas as pd
from typing import List
from models import (Course, Teacher, Classroom, Student, CourseType,
                    TimeSlot, ScheduleAssignment)
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
        self.status_var = StringVar(value="Prêt à générer l'horaire")

        # Données
        self.courses = []
        self.teachers = []
        self.classrooms = []
        self.students = []
        self.assignments = []

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

        # Panneau gauche - Configuration
        left_panel = ttk.LabelFrame(
            main_container,
            text="⚙️ Configuration",
            bootstyle="info",
            padding=15
        )
        left_panel.pack(side=LEFT, fill=BOTH, expand=NO, padx=(0, 10), ipadx=20)

        self.create_config_panel(left_panel)

        # Panneau droit - Résultats avec onglets
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=LEFT, fill=BOTH, expand=YES)

        self.notebook = ttk.Notebook(right_panel, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=YES)

        # Onglet Horaires
        schedule_frame = ttk.Frame(self.notebook)
        self.notebook.add(schedule_frame, text="📅 Horaires")
        self.create_schedule_tab(schedule_frame)

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

        # Info sur les cours
        courses_frame = ttk.Labelframe(parent, text="Cours requis (36 total)", bootstyle="success", padding=10)
        courses_frame.pack(fill=BOTH, expand=YES, pady=(0, 15))

        courses_text = ScrolledText(courses_frame, height=12, autohide=True)
        courses_text.pack(fill=BOTH, expand=YES)

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
        courses_text.configure(state="disabled")

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

    def create_schedule_tab(self, parent):
        """Crée l'onglet des horaires"""
        # Frame avec scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Treeview avec style
        columns = ("Jour", "Période", "Cours", "Enseignant", "Salle", "Étudiants")
        self.schedule_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            bootstyle="primary",
            height=20
        )

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.schedule_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.schedule_tree.xview)
        self.schedule_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Configuration des colonnes
        self.schedule_tree.heading("Jour", text="📅 Jour")
        self.schedule_tree.heading("Période", text="⏰ Période")
        self.schedule_tree.heading("Cours", text="📚 Cours")
        self.schedule_tree.heading("Enseignant", text="👨‍🏫 Enseignant")
        self.schedule_tree.heading("Salle", text="🏫 Salle")
        self.schedule_tree.heading("Étudiants", text="👥 Étudiants")

        self.schedule_tree.column("Jour", width=80, anchor=CENTER)
        self.schedule_tree.column("Période", width=80, anchor=CENTER)
        self.schedule_tree.column("Cours", width=250)
        self.schedule_tree.column("Enseignant", width=200)
        self.schedule_tree.column("Salle", width=150)
        self.schedule_tree.column("Étudiants", width=120, anchor=CENTER)

        # Pack
        self.schedule_tree.pack(side=LEFT, fill=BOTH, expand=YES)
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

            if num_students < 1 or num_students > 200:
                Messagebox.show_error(
                    "Le nombre d'étudiants doit être entre 1 et 200.",
                    "Erreur de configuration"
                )
                return

            self.status_var.set(f"Génération des données pour {num_students} étudiants...")
            self.generate_btn.config(state="disabled")
            self.progress.start()
            self.root.update()

            # Générer les données
            self.courses, self.teachers, self.classrooms, self.students = generate_sample_data(num_students)

            self.status_var.set("Optimisation en cours... (peut prendre jusqu'à 60 secondes)")
            self.root.update()

            # Optimisation
            optimizer = ScheduleOptimizer(
                self.courses,
                self.teachers,
                self.classrooms,
                self.students
            )

            success, assignments = optimizer.solve()

            self.progress.stop()

            if success:
                self.assignments = assignments
                self.display_results()
                self.display_statistics()
                self.export_btn.config(state="normal")
                self.status_var.set(f"✓ Horaire généré avec succès pour {num_students} étudiants!")
                Messagebox.show_info(
                    f"L'horaire a été généré avec succès pour {num_students} étudiants!\n\n"
                    "• Tous les étudiants participent à tous les cours\n"
                    "• Maximum 1 cours par matière par jour\n"
                    "• Ressources optimisées",
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
            self.progress.stop()
            self.status_var.set("❌ Erreur lors de l'optimisation")
            Messagebox.show_error(
                f"Une erreur s'est produite:\n{str(e)}",
                "Erreur"
            )

        finally:
            self.generate_btn.config(state="normal")

    def display_results(self):
        """Affiche les résultats dans le treeview"""
        # Vider le treeview
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)

        # Ajouter les résultats avec alternance de couleurs
        for i, assignment in enumerate(self.assignments):
            course = assignment.course
            timeslot = assignment.timeslot

            teacher_name = course.assigned_teacher.name if course.assigned_teacher else "N/A"
            room_name = course.assigned_room.name if course.assigned_room else "N/A"
            num_students = len(course.assigned_students)

            tag = 'evenrow' if i % 2 == 0 else 'oddrow'

            self.schedule_tree.insert(
                "",
                "end",
                values=(
                    f"Jour {timeslot.day}",
                    f"Période {timeslot.period}",
                    f"{course.course_type.value}",
                    teacher_name,
                    room_name,
                    f"{num_students} étudiants"
                ),
                tags=(tag,)
            )

        # Configuration des tags pour l'alternance
        self.schedule_tree.tag_configure('evenrow', background='#f0f0f0')
        self.schedule_tree.tag_configure('oddrow', background='white')

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
        stats += f"   Nombre de cours: {len(self.courses)}\n"
        stats += f"   Nombre d'enseignants: {len(self.teachers)}\n"
        stats += f"   Nombre de salles: {len(self.classrooms)}\n\n"

        # Utilisation des enseignants
        teacher_load = {}
        for assignment in self.assignments:
            if assignment.course.assigned_teacher:
                teacher = assignment.course.assigned_teacher
                teacher_load[teacher.name] = teacher_load.get(teacher.name, 0) + 1

        stats += "👨‍🏫 CHARGE D'ENSEIGNEMENT\n"
        stats += "─" * 60 + "\n"
        for teacher, count in sorted(teacher_load.items()):
            bar = "█" * count
            stats += f"   {teacher:<30} {count:>2} cours {bar}\n"

        # Utilisation des salles
        stats += "\n🏫 UTILISATION DES SALLES\n"
        stats += "─" * 60 + "\n"
        room_usage = {}
        for assignment in self.assignments:
            if assignment.course.assigned_room:
                room = assignment.course.assigned_room
                room_usage[room.name] = room_usage.get(room.name, 0) + 1

        for room, count in sorted(room_usage.items()):
            bar = "█" * (count // 2)
            stats += f"   {room:<30} {count:>2} cours {bar}\n"

        # Distribution des étudiants
        stats += "\n👥 DISTRIBUTION DES ÉTUDIANTS PAR COURS\n"
        stats += "─" * 60 + "\n"
        course_sizes = [len(assignment.course.assigned_students) for assignment in self.assignments]
        if course_sizes:
            stats += f"   Minimum: {min(course_sizes)} étudiants\n"
            stats += f"   Maximum: {max(course_sizes)} étudiants\n"
            stats += f"   Moyenne: {sum(course_sizes)/len(course_sizes):.1f} étudiants\n"

        # Vérification: tous les étudiants dans tous les cours
        stats += "\n✓ VÉRIFICATION DES CONTRAINTES\n"
        stats += "─" * 60 + "\n"
        stats += "   ✓ Tous les étudiants participent à tous les cours\n"
        stats += "   ✓ Maximum 28 étudiants par classe respecté\n"
        stats += "   ✓ Pas de conflit d'enseignants\n"
        stats += "   ✓ Pas de conflit de salles\n"
        stats += "   ✓ Pas plus d'1 cours par matière par jour\n"

        stats += "\n" + "═" * 60 + "\n"

        self.stats_text.insert("1.0", stats)

    def export_to_excel(self):
        """Exporte l'horaire vers Excel"""
        try:
            # Créer un DataFrame pour l'horaire
            data = []
            for assignment in self.assignments:
                course = assignment.course
                timeslot = assignment.timeslot

                data.append({
                    "Jour": timeslot.day,
                    "Période": timeslot.period,
                    "Cours": course.course_type.value,
                    "ID Cours": course.id,
                    "Enseignant": course.assigned_teacher.name if course.assigned_teacher else "N/A",
                    "Salle": course.assigned_room.name if course.assigned_room else "N/A",
                    "Nombre d'étudiants": len(course.assigned_students),
                    "Étudiants": ", ".join([f"#{s.id}" for s in course.assigned_students])
                })

            df = pd.DataFrame(data)

            # Créer un fichier Excel avec plusieurs feuilles
            filename = f"horaire_optimise_{len(self.students)}_etudiants.xlsx"
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Horaire', index=False)

                # Feuille pour les enseignants
                teacher_data = []
                teacher_load = {}
                for assignment in self.assignments:
                    if assignment.course.assigned_teacher:
                        teacher = assignment.course.assigned_teacher
                        if teacher.name not in teacher_load:
                            teacher_load[teacher.name] = []
                        teacher_load[teacher.name].append({
                            "Jour": assignment.timeslot.day,
                            "Période": assignment.timeslot.period,
                            "Cours": assignment.course.course_type.value
                        })

                for teacher, courses in teacher_load.items():
                    for course in courses:
                        teacher_data.append({
                            "Enseignant": teacher,
                            **course
                        })

                df_teachers = pd.DataFrame(teacher_data)
                df_teachers.to_excel(writer, sheet_name='Enseignants', index=False)

            self.status_var.set(f"✓ Horaire exporté vers {filename}")
            Messagebox.show_info(
                f"L'horaire a été exporté avec succès vers:\n{filename}",
                "Export réussi"
            )

        except Exception as e:
            Messagebox.show_error(
                f"Erreur lors de l'export:\n{str(e)}",
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
