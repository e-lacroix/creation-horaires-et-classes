"""
Interface graphique pour le système de création d'horaires
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List
import pandas as pd
from models import (Course, Teacher, Classroom, Student, CourseType,
                    TimeSlot, ScheduleAssignment)
from scheduler import ScheduleOptimizer
from data_generator import generate_sample_data


class SchedulerApp:
    """Application principale de création d'horaires"""

    def __init__(self, root):
        self.root = root
        self.root.title("Création d'horaires - Secondaire Québec")
        self.root.geometry("1200x800")

        # Données
        self.courses = []
        self.teachers = []
        self.classrooms = []
        self.students = []
        self.assignments = []

        self.create_widgets()
        self.generate_initial_data()

    def create_widgets(self):
        """Crée les widgets de l'interface"""
        # Frame principal avec notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Onglet 1: Configuration
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="Configuration")
        self.create_config_tab()

        # Onglet 2: Résultats
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Horaires")
        self.create_results_tab()

        # Onglet 3: Statistiques
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistiques")
        self.create_stats_tab()

    def create_config_tab(self):
        """Crée l'onglet de configuration"""
        # Info frame
        info_frame = ttk.LabelFrame(self.config_frame, text="Information", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        info_text = """
        Configuration pour 56 étudiants du Secondaire 4
        - Maximum 28 étudiants par classe
        - 4 périodes par jour
        - 9 jours de cours
        - Optimisation pour minimiser le nombre d'enseignants et de salles
        """
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()

        # Cours requis frame
        courses_frame = ttk.LabelFrame(self.config_frame, text="Cours requis", padding=10)
        courses_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.course_text = scrolledtext.ScrolledText(courses_frame, height=15, width=60)
        self.course_text.pack(fill=tk.BOTH, expand=True)

        # Boutons
        button_frame = ttk.Frame(self.config_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.optimize_btn = ttk.Button(
            button_frame,
            text="Générer l'horaire optimisé",
            command=self.run_optimization
        )
        self.optimize_btn.pack(side=tk.LEFT, padx=5)

        self.export_btn = ttk.Button(
            button_frame,
            text="Exporter vers Excel",
            command=self.export_to_excel,
            state=tk.DISABLED
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)

        # Barre de progression
        self.progress = ttk.Progressbar(button_frame, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.status_label = ttk.Label(button_frame, text="Prêt")
        self.status_label.pack(side=tk.LEFT, padx=5)

    def create_results_tab(self):
        """Crée l'onglet de résultats"""
        # Frame pour le treeview
        tree_frame = ttk.Frame(self.results_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        # Treeview
        self.schedule_tree = ttk.Treeview(
            tree_frame,
            columns=("Jour", "Période", "Cours", "Enseignant", "Salle", "Étudiants"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.config(command=self.schedule_tree.yview)
        hsb.config(command=self.schedule_tree.xview)

        # Colonnes
        self.schedule_tree.heading("Jour", text="Jour")
        self.schedule_tree.heading("Période", text="Période")
        self.schedule_tree.heading("Cours", text="Cours")
        self.schedule_tree.heading("Enseignant", text="Enseignant")
        self.schedule_tree.heading("Salle", text="Salle")
        self.schedule_tree.heading("Étudiants", text="Nb Étudiants")

        self.schedule_tree.column("Jour", width=60)
        self.schedule_tree.column("Période", width=70)
        self.schedule_tree.column("Cours", width=200)
        self.schedule_tree.column("Enseignant", width=150)
        self.schedule_tree.column("Salle", width=100)
        self.schedule_tree.column("Étudiants", width=100)

        # Pack
        self.schedule_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

    def create_stats_tab(self):
        """Crée l'onglet de statistiques"""
        self.stats_text = scrolledtext.ScrolledText(self.stats_frame, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def generate_initial_data(self):
        """Génère les données initiales"""
        self.courses, self.teachers, self.classrooms, self.students = generate_sample_data()

        # Afficher les cours
        course_info = "Cours requis:\n\n"
        course_counts = {}
        for course in self.courses:
            course_type = course.course_type.value
            course_counts[course_type] = course_counts.get(course_type, 0) + 1

        for course_type, count in sorted(course_counts.items()):
            course_info += f"  • {course_type}: {count} classe(s)\n"

        course_info += f"\nTotal: {len(self.courses)} classes\n"
        course_info += f"Enseignants: {len(self.teachers)}\n"
        course_info += f"Salles: {len(self.classrooms)}\n"
        course_info += f"Étudiants: {len(self.students)}\n"

        self.course_text.insert(tk.END, course_info)
        self.course_text.config(state=tk.DISABLED)

    def run_optimization(self):
        """Lance l'optimisation"""
        self.status_label.config(text="Optimisation en cours...")
        self.optimize_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.root.update()

        try:
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
                self.export_btn.config(state=tk.NORMAL)
                self.status_label.config(text="Optimisation réussie!")
                messagebox.showinfo(
                    "Succès",
                    "L'horaire a été généré avec succès!"
                )
            else:
                self.status_label.config(text="Échec de l'optimisation")
                messagebox.showerror(
                    "Erreur",
                    "Impossible de trouver une solution optimale.\n"
                    "Essayez d'ajuster les contraintes."
                )

        except Exception as e:
            self.progress.stop()
            self.status_label.config(text="Erreur")
            messagebox.showerror("Erreur", f"Une erreur s'est produite:\n{str(e)}")

        finally:
            self.optimize_btn.config(state=tk.NORMAL)

    def display_results(self):
        """Affiche les résultats dans le treeview"""
        # Vider le treeview
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)

        # Ajouter les résultats
        for assignment in self.assignments:
            course = assignment.course
            timeslot = assignment.timeslot

            teacher_name = course.assigned_teacher.name if course.assigned_teacher else "N/A"
            room_name = course.assigned_room.name if course.assigned_room else "N/A"
            num_students = len(course.assigned_students)

            self.schedule_tree.insert(
                "",
                tk.END,
                values=(
                    timeslot.day,
                    timeslot.period,
                    f"{course.course_type.value} #{course.id}",
                    teacher_name,
                    room_name,
                    num_students
                )
            )

    def display_statistics(self):
        """Affiche les statistiques"""
        self.stats_text.delete(1.0, tk.END)

        stats = "=== STATISTIQUES DE L'HORAIRE ===\n\n"

        # Utilisation des enseignants
        teacher_load = {}
        for assignment in self.assignments:
            if assignment.course.assigned_teacher:
                teacher = assignment.course.assigned_teacher
                teacher_load[teacher.name] = teacher_load.get(teacher.name, 0) + 1

        stats += "CHARGE D'ENSEIGNEMENT:\n"
        for teacher, count in sorted(teacher_load.items()):
            stats += f"  {teacher}: {count} cours\n"

        # Utilisation des salles
        stats += "\nUTILISATION DES SALLES:\n"
        room_usage = {}
        for assignment in self.assignments:
            if assignment.course.assigned_room:
                room = assignment.course.assigned_room
                room_usage[room.name] = room_usage.get(room.name, 0) + 1

        for room, count in sorted(room_usage.items()):
            stats += f"  {room}: {count} cours\n"

        # Distribution des étudiants
        stats += "\nDISTRIBUTION DES ÉTUDIANTS PAR COURS:\n"
        course_sizes = [len(assignment.course.assigned_students) for assignment in self.assignments]
        if course_sizes:
            stats += f"  Minimum: {min(course_sizes)} étudiants\n"
            stats += f"  Maximum: {max(course_sizes)} étudiants\n"
            stats += f"  Moyenne: {sum(course_sizes)/len(course_sizes):.1f} étudiants\n"

        # Vérification de couverture des étudiants
        stats += "\nCOUVERTURE DES COURS PAR ÉTUDIANT:\n"
        student_courses = {}
        for assignment in self.assignments:
            for student in assignment.course.assigned_students:
                if student.id not in student_courses:
                    student_courses[student.id] = []
                student_courses[student.id].append(assignment.course.course_type.value)

        for student_id in list(student_courses.keys())[:5]:  # Afficher 5 exemples
            courses = student_courses[student_id]
            stats += f"  Étudiant #{student_id}: {len(courses)} cours\n"
            stats += f"    ({', '.join(sorted(set(courses)))})\n"

        self.stats_text.insert(tk.END, stats)

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
            filename = "horaire_optimise.xlsx"
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

            messagebox.showinfo(
                "Export réussi",
                f"L'horaire a été exporté vers {filename}"
            )
            self.status_label.config(text="Export réussi")

        except Exception as e:
            messagebox.showerror("Erreur d'export", f"Erreur lors de l'export:\n{str(e)}")


def main():
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
