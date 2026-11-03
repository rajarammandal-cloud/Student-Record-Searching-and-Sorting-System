"""
main.py
-------
Main GUI Application for the Student Record Searching and Sorting System.
Implemented using Python 3 and Tkinter (ttk).

Features:
- Professional modern UI layout with blue/purple accents
- Live KPI Dashboard (Total Students, Average, Highest, Lowest Marks)
- Full CRUD Student Management with strict input validation and CSV persistence
- Manual Algorithm 1: Linear Search
- Manual Algorithm 2: Binary Search (with separate preparation time tracking)
- Manual Algorithm 3: Bubble Sort
- Manual Algorithm 4: Quick Sort
- Empirical Performance Benchmark (N = 10, 100, 1000, 5000) with embedded Matplotlib graphs
- Comprehensive DAA Educational & Asymptotic Complexity Analysis section
"""

import sys
import os
import threading
import time
from typing import List, Dict, Any, Optional

# Ensure local imports work reliably
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from database import Database
from student_manager import StudentManager, Student
from algorithms import (
    linear_search,
    binary_search,
    binary_search_with_prep,
    bubble_sort,
    quick_sort,
    COMPLEXITY_INFO
)
from performance import run_full_benchmark, create_performance_figure


class StudentRecordApp(tk.Tk):
    """Main desktop application window and controller."""

    # UI Color Palette (Modern Slate, Blue, Purple & Light Background)
    BG_LIGHT = "#f8fafc"
    CARD_BG = "#ffffff"
    SIDEBAR_BG = "#0f172a"
    SIDEBAR_BTN = "#1e293b"
    SIDEBAR_BTN_ACTIVE = "#3b82f6"
    ACCENT_BLUE = "#2563eb"
    ACCENT_PURPLE = "#7c3aed"
    ACCENT_INDIGO = "#4f46e5"
    ACCENT_EMERALD = "#059669"
    ACCENT_ROSE = "#e11d48"
    TEXT_DARK = "#0f172a"
    TEXT_MUTED = "#64748b"
    BORDER_COLOR = "#e2e8f0"
    ROW_EVEN = "#ffffff"
    ROW_ODD = "#f1f5f9"
    HIGHLIGHT_COLOR = "#fef08a"

    def __init__(self):
        super().__init__()

        self.title("Student Record Searching and Sorting System | DAA Mini Project")
        self.geometry("1240x820")
        self.minsize(1050, 700)
        self.configure(bg=self.BG_LIGHT)

        # Initialize Business Layer
        self.manager = StudentManager()

        # Cached benchmark results
        self.benchmark_results: Optional[List[Dict[str, Any]]] = None
        self.is_benchmarking = False

        # Apply TTK Theme & Styles
        self._setup_styles()

        # Build Main UI Components
        self._build_header()
        self._build_body()

        # Default to first view: Dashboard & Records
        self.show_view("dashboard")

    # =========================================================================
    # STYLES SETUP
    # =========================================================================
    def _setup_styles(self):
        """Configure modern TTK styles for buttons, tables, and tabs."""
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        # Treeview styling
        self.style.configure(
            "Treeview",
            background=self.ROW_EVEN,
            foreground=self.TEXT_DARK,
            rowheight=30,
            fieldbackground=self.ROW_EVEN,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        self.style.configure(
            "Treeview.Heading",
            background="#e2e8f0",
            foreground=self.TEXT_DARK,
            font=("Segoe UI", 10, "bold"),
            padding=(8, 6)
        )
        self.style.map(
            "Treeview",
            background=[("selected", "#3b82f6")],
            foreground=[("selected", "#ffffff")]
        )

        # Primary Button Style
        self.style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            background=self.ACCENT_BLUE,
            foreground="#ffffff",
            borderwidth=0,
            padding=(12, 6)
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", "#1d4ed8"), ("pressed", "#1e40af")]
        )

        # Accent Purple Button Style
        self.style.configure(
            "Purple.TButton",
            font=("Segoe UI", 10, "bold"),
            background=self.ACCENT_PURPLE,
            foreground="#ffffff",
            borderwidth=0,
            padding=(12, 6)
        )
        self.style.map(
            "Purple.TButton",
            background=[("active", "#6d28d9"), ("pressed", "#5b21b6")]
        )

        # Danger Button Style
        self.style.configure(
            "Danger.TButton",
            font=("Segoe UI", 10, "bold"),
            background=self.ACCENT_ROSE,
            foreground="#ffffff",
            borderwidth=0,
            padding=(10, 6)
        )
        self.style.map(
            "Danger.TButton",
            background=[("active", "#be123c")]
        )

        # Neutral Secondary Button Style
        self.style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10),
            background="#64748b",
            foreground="#ffffff",
            borderwidth=0,
            padding=(10, 6)
        )
        self.style.map(
            "Secondary.TButton",
            background=[("active", "#475569")]
        )

    # =========================================================================
    # HEADER SECTION
    # =========================================================================
    def _build_header(self):
        """Top banner featuring project title and curriculum badge."""
        header_frame = tk.Frame(self, bg=self.SIDEBAR_BG, height=65)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        inner = tk.Frame(header_frame, bg=self.SIDEBAR_BG)
        inner.pack(fill=tk.BOTH, expand=True, padx=20)

        title_lbl = tk.Label(
            inner,
            text="Student Record Searching & Sorting System",
            font=("Segoe UI", 15, "bold"),
            fg="#ffffff",
            bg=self.SIDEBAR_BG
        )
        title_lbl.pack(side=tk.LEFT, pady=16)

        subtitle_lbl = tk.Label(
            inner,
            text="Design & Analysis of Algorithms (DAA) Laboratory Project | MCA",
            font=("Segoe UI", 10, "italic"),
            fg="#94a3b8",
            bg=self.SIDEBAR_BG
        )
        subtitle_lbl.pack(side=tk.LEFT, padx=15, pady=18)

        # Tag badges on right
        badge = tk.Label(
            inner,
            text="Manual Algorithmic Implementations (No Built-ins)",
            font=("Segoe UI", 9, "bold"),
            fg="#38bdf8",
            bg="#0369a1",
            padx=10,
            pady=4
        )
        badge.pack(side=tk.RIGHT, pady=18)

    # =========================================================================
    # BODY LAYOUT (SIDEBAR + MAIN CONTAINER)
    # =========================================================================
    def _build_body(self):
        """Main work area divided into sidebar navigation and multi-frame content."""
        self.body_frame = tk.Frame(self, bg=self.BG_LIGHT)
        self.body_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Left Sidebar Navigation
        self.sidebar_frame = tk.Frame(self.body_frame, bg=self.SIDEBAR_BG, width=230)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)

        nav_title = tk.Label(
            self.sidebar_frame,
            text="NAVIGATION MENU",
            font=("Segoe UI", 9, "bold"),
            fg="#94a3b8",
            bg=self.SIDEBAR_BG
        )
        nav_title.pack(anchor=tk.W, padx=20, pady=(25, 12))

        # Nav Buttons (Only core modules: Dashboard, Searching, Sorting)
        self.nav_buttons: Dict[str, tk.Button] = {}
        nav_items = [
            ("dashboard", "Dashboard & Records"),
            ("search", "Algorithm Searching"),
            ("sort", "Algorithm Sorting")
        ]

        for key, label in nav_items:
            btn = tk.Button(
                self.sidebar_frame,
                text=label,
                font=("Segoe UI", 10, "bold"),
                bg=self.SIDEBAR_BTN,
                fg="#f1f5f9",
                activebackground=self.SIDEBAR_BTN_ACTIVE,
                activeforeground="#ffffff",
                relief=tk.FLAT,
                bd=0,
                anchor=tk.W,
                padx=18,
                pady=12,
                cursor="hand2",
                command=lambda k=key: self.show_view(k)
            )
            btn.pack(fill=tk.X, padx=10, pady=4)
            self.nav_buttons[key] = btn

        # Project Info at Sidebar Bottom
        info_frame = tk.Frame(self.sidebar_frame, bg=self.SIDEBAR_BTN, padx=12, pady=12)
        info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=15)

        info_text = (
            "DAA Practical Project\n"
            "Algorithms Implemented:\n"
            "• Linear Search\n"
            "• Binary Search\n"
            "• Bubble Sort\n"
            "• Quick Sort\n"
            "Storage: CSV File"
        )
        tk.Label(
            info_frame,
            text=info_text,
            font=("Segoe UI", 8),
            fg="#94a3b8",
            bg=self.SIDEBAR_BTN,
            justify=tk.LEFT
        ).pack(anchor=tk.W)

        # 2. Main Container Frame
        self.container = tk.Frame(self.body_frame, bg=self.BG_LIGHT)
        self.container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Initialize View Frames
        self.views: Dict[str, tk.Frame] = {}
        self.views["dashboard"] = self._create_dashboard_view()
        self.views["search"] = self._create_search_view()
        self.views["sort"] = self._create_sort_view()

    def show_view(self, view_key: str):
        """Switch active view and update sidebar button highlights."""
        for key, frame in self.views.items():
            if key == view_key:
                frame.pack(fill=tk.BOTH, expand=True)
                self.nav_buttons[key].configure(bg=self.SIDEBAR_BTN_ACTIVE)
            else:
                frame.pack_forget()
                self.nav_buttons[key].configure(bg=self.SIDEBAR_BTN)

        # Refresh state when landing on views
        if view_key == "dashboard":
            self.refresh_records_table()
            self.update_dashboard_kpis()
        elif view_key == "search":
            self.refresh_search_source_table()
        elif view_key == "sort":
            self.refresh_sort_source_table()

    # =========================================================================
    # VIEW 1: DASHBOARD & STUDENT RECORDS (CRUD)
    # =========================================================================
    def _create_dashboard_view(self) -> tk.Frame:
        """Dashboard overview cards + CRUD Student Management table & form."""
        view = tk.Frame(self.container, bg=self.BG_LIGHT)

        # ---------------- 1. KPI Stats Cards ----------------
        kpi_row = tk.Frame(view, bg=self.BG_LIGHT)
        kpi_row.pack(fill=tk.X, pady=(0, 15))

        self.kpi_cards = {}
        card_configs = [
            ("total", "Total Students", "0", self.ACCENT_BLUE),
            ("avg", "Average Marks", "0.00", self.ACCENT_PURPLE),
            ("highest", "Highest Marks", "0.0", self.ACCENT_EMERALD),
            ("lowest", "Lowest Marks", "0.0", self.ACCENT_ROSE)
        ]

        for key, title, default_val, accent_color in card_configs:
            card = tk.Frame(kpi_row, bg=self.CARD_BG, relief=tk.SOLID, bd=1, highlightbackground=self.BORDER_COLOR)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6)

            # Left accent border strip
            strip = tk.Frame(card, bg=accent_color, width=5)
            strip.pack(side=tk.LEFT, fill=tk.Y)

            content = tk.Frame(card, bg=self.CARD_BG, padx=12, pady=10)
            content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            t_lbl = tk.Label(content, text=title.upper(), font=("Segoe UI", 8, "bold"), fg=self.TEXT_MUTED, bg=self.CARD_BG)
            t_lbl.pack(anchor=tk.W)

            v_lbl = tk.Label(content, text=default_val, font=("Segoe UI", 16, "bold"), fg=self.TEXT_DARK, bg=self.CARD_BG)
            v_lbl.pack(anchor=tk.W, pady=(2, 0))

            sub_lbl = tk.Label(content, text="", font=("Segoe UI", 8), fg=self.TEXT_MUTED, bg=self.CARD_BG)
            sub_lbl.pack(anchor=tk.W)

            self.kpi_cards[key] = (v_lbl, sub_lbl)

        # ---------------- 2. Lower Area: Form (Left) & Records Table (Right) ----------------
        lower_frame = tk.Frame(view, bg=self.BG_LIGHT)
        lower_frame.pack(fill=tk.BOTH, expand=True)

        # Form Card (Left)
        form_card = tk.LabelFrame(
            lower_frame,
            text=" Student Information Form ",
            font=("Segoe UI", 11, "bold"),
            fg=self.TEXT_DARK,
            bg=self.CARD_BG,
            padx=16,
            pady=16,
            relief=tk.SOLID,
            bd=1
        )
        form_card.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Form Inputs
        tk.Label(form_card, text="Roll Number *", font=("Segoe UI", 9, "bold"), fg=self.TEXT_DARK, bg=self.CARD_BG).pack(anchor=tk.W, pady=(4, 2))
        self.ent_roll = tk.Entry(form_card, font=("Segoe UI", 10), width=24, relief=tk.SOLID, bd=1)
        self.ent_roll.pack(anchor=tk.W, pady=(0, 8))

        tk.Label(form_card, text="Student Name *", font=("Segoe UI", 9, "bold"), fg=self.TEXT_DARK, bg=self.CARD_BG).pack(anchor=tk.W, pady=(4, 2))
        self.ent_name = tk.Entry(form_card, font=("Segoe UI", 10), width=24, relief=tk.SOLID, bd=1)
        self.ent_name.pack(anchor=tk.W, pady=(0, 8))

        tk.Label(form_card, text="Course *", font=("Segoe UI", 9, "bold"), fg=self.TEXT_DARK, bg=self.CARD_BG).pack(anchor=tk.W, pady=(4, 2))
        self.ent_course = tk.Entry(form_card, font=("Segoe UI", 10), width=24, relief=tk.SOLID, bd=1)
        self.ent_course.pack(anchor=tk.W, pady=(0, 8))

        tk.Label(form_card, text="Marks (0 - 100) *", font=("Segoe UI", 9, "bold"), fg=self.TEXT_DARK, bg=self.CARD_BG).pack(anchor=tk.W, pady=(4, 2))
        self.ent_marks = tk.Entry(form_card, font=("Segoe UI", 10), width=24, relief=tk.SOLID, bd=1)
        self.ent_marks.pack(anchor=tk.W, pady=(0, 12))

        # Form Buttons
        btn_box = tk.Frame(form_card, bg=self.CARD_BG)
        btn_box.pack(fill=tk.X, pady=4)

        btn_add = tk.Button(
            btn_box,
            text="+ Add Student",
            font=("Segoe UI", 9, "bold"),
            bg=self.ACCENT_BLUE,
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=6,
            command=self.handle_add_student
        )
        btn_add.pack(fill=tk.X, pady=3)

        btn_update = tk.Button(
            btn_box,
            text="Update Student",
            font=("Segoe UI", 9, "bold"),
            bg=self.ACCENT_PURPLE,
            fg="#ffffff",
            activebackground="#6d28d9",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=6,
            command=self.handle_update_student
        )
        btn_update.pack(fill=tk.X, pady=3)

        btn_delete = tk.Button(
            btn_box,
            text="Delete Student",
            font=("Segoe UI", 9, "bold"),
            bg=self.ACCENT_ROSE,
            fg="#ffffff",
            activebackground="#be123c",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=6,
            command=self.handle_delete_student
        )
        btn_delete.pack(fill=tk.X, pady=3)

        btn_clear = tk.Button(
            btn_box,
            text="Clear Fields",
            font=("Segoe UI", 9),
            bg="#64748b",
            fg="#ffffff",
            activebackground="#475569",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=5,
            command=self.handle_clear_fields
        )
        btn_clear.pack(fill=tk.X, pady=3)

        tk.Frame(form_card, bg=self.BORDER_COLOR, height=1).pack(fill=tk.X, pady=8)

        btn_sample = tk.Button(
            form_card,
            text="Load Sample Data",
            font=("Segoe UI", 9),
            bg="#0284c7",
            fg="#ffffff",
            activebackground="#0369a1",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            pady=5,
            command=self.handle_load_sample_data
        )
        btn_sample.pack(fill=tk.X, pady=2)

        # Records Table Card (Right)
        table_card = tk.LabelFrame(
            lower_frame,
            text=" Student Records Database (Live CSV) ",
            font=("Segoe UI", 11, "bold"),
            fg=self.TEXT_DARK,
            bg=self.CARD_BG,
            padx=12,
            pady=12,
            relief=tk.SOLID,
            bd=1
        )
        table_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Controls bar above table
        tbl_ctrl = tk.Frame(table_card, bg=self.CARD_BG)
        tbl_ctrl.pack(fill=tk.X, pady=(0, 8))

        lbl_hint = tk.Label(
            tbl_ctrl,
            text="Tip: Click any row to populate the editing form on the left.",
            font=("Segoe UI", 9, "italic"),
            fg=self.TEXT_MUTED,
            bg=self.CARD_BG
        )
        lbl_hint.pack(side=tk.LEFT)

        btn_refresh = tk.Button(
            tbl_ctrl,
            text="Refresh Records",
            font=("Segoe UI", 9),
            bg="#f1f5f9",
            fg=self.TEXT_DARK,
            relief=tk.SOLID,
            bd=1,
            cursor="hand2",
            padx=8,
            pady=3,
            command=self.refresh_records_table
        )
        btn_refresh.pack(side=tk.RIGHT)

        # Treeview with Scrollbars
        tbl_frame = tk.Frame(table_card, bg=self.CARD_BG)
        tbl_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("roll_no", "name", "course", "marks")
        self.tree = ttk.Treeview(tbl_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("roll_no", text="Roll Number")
        self.tree.heading("name", text="Student Name")
        self.tree.heading("course", text="Course")
        self.tree.heading("marks", text="Marks (%)")

        self.tree.column("roll_no", width=110, anchor=tk.CENTER)
        self.tree.column("name", width=220, anchor=tk.W)
        self.tree.column("course", width=120, anchor=tk.CENTER)
        self.tree.column("marks", width=100, anchor=tk.E)

        # Alternating row colors
        self.tree.tag_configure("evenrow", background=self.ROW_EVEN)
        self.tree.tag_configure("oddrow", background=self.ROW_ODD)
        self.tree.tag_configure("highlight", background=self.HIGHLIGHT_COLOR)

        scroll_y = ttk.Scrollbar(tbl_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self.handle_table_row_select)

        return view

    def update_dashboard_kpis(self):
        """Update KPI metric card labels from student manager calculations."""
        stats = self.manager.get_dashboard_stats()

        self.kpi_cards["total"][0].configure(text=f"{stats['total_students']}")
        self.kpi_cards["total"][1].configure(text="Registered Records")

        self.kpi_cards["avg"][0].configure(text=f"{stats['average_marks']:.2f}%")
        self.kpi_cards["avg"][1].configure(text="Batch Performance")

        self.kpi_cards["highest"][0].configure(text=f"{stats['highest_marks']:.1f}%")
        self.kpi_cards["highest"][1].configure(text=f"{stats['highest_student']}")

        self.kpi_cards["lowest"][0].configure(text=f"{stats['lowest_marks']:.1f}%")
        self.kpi_cards["lowest"][1].configure(text=f"{stats['lowest_student']}")

    def refresh_records_table(self):
        """Reload records from student manager and repopulate Treeview."""
        self.manager.refresh()
        records = self.manager.get_all()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, r in enumerate(records):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", tk.END, values=(
                r["roll_no"],
                r["name"],
                r["course"],
                f"{r['marks']:.1f}"
            ), tags=(tag,))

        self.update_dashboard_kpis()

    def handle_table_row_select(self, event):
        """Populate form input fields when a user clicks a row."""
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        if values:
            self.ent_roll.delete(0, tk.END)
            self.ent_roll.insert(0, values[0])

            self.ent_name.delete(0, tk.END)
            self.ent_name.insert(0, values[1])

            self.ent_course.delete(0, tk.END)
            self.ent_course.insert(0, values[2])

            self.ent_marks.delete(0, tk.END)
            self.ent_marks.insert(0, values[3])

    def handle_clear_fields(self):
        """Clear form input fields."""
        self.ent_roll.delete(0, tk.END)
        self.ent_name.delete(0, tk.END)
        self.ent_course.delete(0, tk.END)
        self.ent_marks.delete(0, tk.END)
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])

    def handle_add_student(self):
        """Validate and add a new student record."""
        try:
            r = self.ent_roll.get()
            n = self.ent_name.get()
            c = self.ent_course.get()
            m = self.ent_marks.get()

            new_student = self.manager.add_student(r, n, c, m)
            self.refresh_records_table()
            self.handle_clear_fields()
            messagebox.showinfo("Success", f"Student '{new_student['name']}' (Roll No: {new_student['roll_no']}) added successfully!")
        except ValueError as ve:
            messagebox.showerror("Validation Error", str(ve))
        except Exception as e:
            messagebox.showerror("System Error", f"An unexpected error occurred: {e}")

    def handle_update_student(self):
        """Validate and update an existing student record."""
        try:
            r_raw = self.ent_roll.get()
            if not r_raw.strip():
                raise ValueError("Please select or enter the Roll Number of the student to update.")
            roll_no = int(r_raw.strip())

            n = self.ent_name.get()
            c = self.ent_course.get()
            m = self.ent_marks.get()

            updated = self.manager.update_student(roll_no, n, c, m)
            self.refresh_records_table()
            messagebox.showinfo("Success", f"Student with Roll No {updated['roll_no']} updated successfully!")
        except ValueError as ve:
            messagebox.showerror("Validation Error", str(ve))
        except Exception as e:
            messagebox.showerror("System Error", f"An unexpected error occurred: {e}")

    def handle_delete_student(self):
        """Confirm and delete a student record."""
        try:
            r_raw = self.ent_roll.get()
            if not r_raw.strip():
                raise ValueError("Please select or enter the Roll Number of the student to delete.")
            roll_no = int(r_raw.strip())

            student = self.manager.get_by_roll(roll_no)
            if not student:
                raise ValueError(f"Student with Roll Number {roll_no} does not exist.")

            confirm = messagebox.askyesno(
                "Confirm Deletion",
                f"Are you sure you want to permanently delete:\n\n"
                f"Roll No: {student['roll_no']}\n"
                f"Name: {student['name']}\n"
                f"Course: {student['course']}\n\n"
                "This action cannot be undone."
            )
            if confirm:
                self.manager.delete_student(roll_no)
                self.refresh_records_table()
                self.handle_clear_fields()
                messagebox.showinfo("Deleted", f"Student record {roll_no} deleted successfully.")
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("System Error", f"An unexpected error occurred: {e}")

    def handle_load_sample_data(self):
        """Load default sample dataset into CSV."""
        added = self.manager.load_sample_data()
        self.refresh_records_table()
        if added > 0:
            messagebox.showinfo("Sample Data", f"Successfully loaded {added} new sample student records!")
        else:
            messagebox.showinfo("Sample Data", "All sample records already exist in the database. No duplicates added.")

    # =========================================================================
    # VIEW 2: SEARCHING MODULE (LINEAR SEARCH & BINARY SEARCH)
    # =========================================================================
    def _create_search_view(self) -> tk.Frame:
        """Interactive searching interface with theoretical & empirical metrics."""
        view = tk.Frame(self.container, bg=self.BG_LIGHT)

        # Top Control Card
        ctrl_card = tk.LabelFrame(
            view,
            text=" Search Configuration & Execution ",
            font=("Segoe UI", 11, "bold"),
            fg=self.TEXT_DARK,
            bg=self.CARD_BG,
            padx=16,
            pady=14,
            relief=tk.SOLID,
            bd=1
        )
        ctrl_card.pack(fill=tk.X, pady=(0, 12))

        row1 = tk.Frame(ctrl_card, bg=self.CARD_BG)
        row1.pack(fill=tk.X)

        # Algorithm Selection Dropdown
        tk.Label(row1, text="Algorithm:", font=("Segoe UI", 10, "bold"), fg=self.TEXT_DARK, bg=self.CARD_BG).pack(side=tk.LEFT, padx=(0, 6))
        self.search_algo_var = tk.StringVar(value="Linear Search")
        algo_combo = ttk.Combobox(
            row1,
            textvariable=self.search_algo_var,
            values=["Linear Search", "Binary Search"],
            state="readonly",
            width=16,
            font=("Segoe UI", 10)
        )
        algo_combo.pack(side=tk.LEFT, padx=(0, 20))

        # Target Roll Number
        tk.Label(row1, text="Roll Number to Search:", font=("Segoe UI", 10, "bold"), fg=self.TEXT_DARK, bg=self.CARD_BG).pack(side=tk.LEFT, padx=(0, 6))
        self.ent_search_roll = tk.Entry(row1, font=("Segoe UI", 10), width=14, relief=tk.SOLID, bd=1)
        self.ent_search_roll.pack(side=tk.LEFT, padx=(0, 20))

        # Run Search Button
        btn_search = tk.Button(
            row1,
            text="Execute Search",
            font=("Segoe UI", 10, "bold"),
            bg=self.ACCENT_BLUE,
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=14,
            pady=5,
            command=self.handle_execute_search
        )
        btn_search.pack(side=tk.LEFT)

        # Dual split lower area: Left (Results & Complexity), Right (Data table)
        lower_frame = tk.Frame(view, bg=self.BG_LIGHT)
        lower_frame.pack(fill=tk.BOTH, expand=True)

        # Left Column: Search Result & Complexity Details
        left_col = tk.Frame(lower_frame, bg=self.BG_LIGHT, width=420)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_col.pack_propagate(False)

        # Execution Result Box
        self.res_card = tk.LabelFrame(
            left_col,
            text=" Search Execution Metrics ",
            font=("Segoe UI", 10, "bold"),
            fg=self.TEXT_DARK,
            bg=self.CARD_BG,
            padx=14,
            pady=12,
            relief=tk.SOLID,
            bd=1
        )
        self.res_card.pack(fill=tk.X, pady=(0, 12))

        self.lbl_search_status = tk.Label(self.res_card, text="Status: Ready to Search", font=("Segoe UI", 10, "bold"), fg="#64748b", bg=self.CARD_BG)
        self.lbl_search_status.pack(anchor=tk.W, pady=2)

        self.lbl_search_details = tk.Label(self.res_card, text="Student Details: None", font=("Segoe UI", 9), fg=self.TEXT_DARK, bg=self.CARD_BG, justify=tk.LEFT)
        self.lbl_search_details.pack(anchor=tk.W, pady=2)

        self.lbl_search_time = tk.Label(self.res_card, text="Execution Time: 0.000 ms", font=("Segoe UI", 9, "bold"), fg=self.ACCENT_PURPLE, bg=self.CARD_BG)
        self.lbl_search_time.pack(anchor=tk.W, pady=2)

        self.lbl_search_comps = tk.Label(self.res_card, text="Comparisons Made: 0", font=("Segoe UI", 9), fg=self.TEXT_DARK, bg=self.CARD_BG)
        self.lbl_search_comps.pack(anchor=tk.W, pady=2)

        self.lbl_search_prep = tk.Label(self.res_card, text="", font=("Segoe UI", 8, "italic"), fg="#0284c7", bg=self.CARD_BG)
        self.lbl_search_prep.pack(anchor=tk.W, pady=2)

        # Theoretical Complexity Info Card
        self.comp_card = tk.LabelFrame(
            left_col,
            text=" Algorithm Complexity Info ",
            font=("Segoe UI", 10, "bold"),
            fg=self.TEXT_DARK,
            bg=self.CARD_BG,
            padx=14,
            pady=12,
            relief=tk.SOLID,
            bd=1
        )
        self.comp_card.pack(fill=tk.BOTH, expand=True)

        self.lbl_comp_name = tk.Label(self.comp_card, text="Algorithm: Linear Search", font=("Segoe UI", 10, "bold"), fg=self.ACCENT_BLUE, bg=self.CARD_BG)
        self.lbl_comp_name.pack(anchor=tk.W, pady=(0, 6))

        self.lbl_comp_best = tk.Label(self.comp_card, text="• Best Case: O(1) [First item match]", font=("Segoe UI", 9), fg=self.TEXT_DARK, bg=self.CARD_BG)
        self.lbl_comp_best.pack(anchor=tk.W, pady=2)

        self.lbl_comp_avg = tk.Label(self.comp_card, text="• Average Case: O(n) [Middle scan]", font=("Segoe UI", 9), fg=self.TEXT_DARK, bg=self.CARD_BG)
        self.lbl_comp_avg.pack(anchor=tk.W, pady=2)

        self.lbl_comp_worst = tk.Label(self.comp_card, text="• Worst Case: O(n) [Last item / not found]", font=("Segoe UI", 9), fg=self.TEXT_DARK, bg=self.CARD_BG)
        self.lbl_comp_worst.pack(anchor=tk.W, pady=2)

        self.lbl_comp_space = tk.Label(self.comp_card, text="• Space Complexity: O(1) [Iterative in-place]", font=("Segoe UI", 9), fg=self.TEXT_DARK, bg=self.CARD_BG)
        self.lbl_comp_space.pack(anchor=tk.W, pady=2)

        self.lbl_comp_desc = tk.Label(self.comp_card, text="", font=("Segoe UI", 8, "italic"), fg=self.TEXT_MUTED, bg=self.CARD_BG, wraplength=380, justify=tk.LEFT)
        self.lbl_comp_desc.pack(anchor=tk.W, pady=(6, 0))

        # Right Column: Records Table View
        right_col = tk.LabelFrame(
            lower_frame,
            text=" Target Dataset ",
            font=("Segoe UI", 10, "bold"),
            fg=self.TEXT_DARK,
            bg=self.CARD_BG,
            padx=10,
            pady=10,
            relief=tk.SOLID,
            bd=1
        )
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        cols = ("roll_no", "name", "course", "marks")
        self.search_tree = ttk.Treeview(right_col, columns=cols, show="headings", selectmode="browse")
        self.search_tree.heading("roll_no", text="Roll No")
        self.search_tree.heading("name", text="Student Name")
        self.search_tree.heading("course", text="Course")
        self.search_tree.heading("marks", text="Marks (%)")

        self.search_tree.column("roll_no", width=90, anchor=tk.CENTER)
        self.search_tree.column("name", width=200, anchor=tk.W)
        self.search_tree.column("course", width=100, anchor=tk.CENTER)
        self.search_tree.column("marks", width=90, anchor=tk.E)

        self.search_tree.tag_configure("evenrow", background=self.ROW_EVEN)
        self.search_tree.tag_configure("oddrow", background=self.ROW_ODD)
        self.search_tree.tag_configure("highlight", background=self.HIGHLIGHT_COLOR)

        s_scroll = ttk.Scrollbar(right_col, orient=tk.VERTICAL, command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=s_scroll.set)

        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        s_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        return view

    def refresh_search_source_table(self):
        """Populate the search view table with latest student data."""
        self.manager.refresh()
        records = self.manager.get_all()
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)

        for i, r in enumerate(records):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.search_tree.insert("", tk.END, values=(
                r["roll_no"],
                r["name"],
                r["course"],
                f"{r['marks']:.1f}"
            ), tags=(tag,))

    def handle_execute_search(self):
        """Execute selected search algorithm and display metrics & complexity."""
        algo_choice = self.search_algo_var.get()
        target_raw = self.ent_search_roll.get().strip()

        if not target_raw:
            messagebox.showerror("Search Input Error", "Please enter a Roll Number to search.")
            return

        try:
            target_roll = int(target_raw)
        except ValueError:
            messagebox.showerror("Search Input Error", "Roll Number must be a valid integer.")
            return

        records = self.manager.get_all()
        if not records:
            messagebox.showwarning("Empty Database", "There are no student records to search.")
            return

        # Update Complexity Card
        if algo_choice == "Linear Search":
            info = COMPLEXITY_INFO["linear_search"]
            self.lbl_comp_name.configure(text=f"Algorithm: {info['name']}")
            self.lbl_comp_best.configure(text=f"• Best Case: {info['best']} [First element match]")
            self.lbl_comp_avg.configure(text=f"• Average Case: {info['average']} [Scanning n/2 elements]")
            self.lbl_comp_worst.configure(text=f"• Worst Case: {info['worst']} [Element at end or not found]")
            self.lbl_comp_space.configure(text=f"• Space Complexity: {info['space']} [Iterative in-place]")
            self.lbl_comp_desc.configure(text=info["description"])

            # Execute Linear Search
            idx, student, comparisons, exec_time = linear_search(records, target_roll)
            self.lbl_search_prep.configure(text="")

            # Highlight in table if found
            self.refresh_search_source_table()
            if idx != -1 and student:
                self.lbl_search_status.configure(text="Status: Record Found", fg=self.ACCENT_EMERALD)
                self.lbl_search_details.configure(
                    text=f"• Roll No: {student['roll_no']}\n• Name: {student['name']}\n• Course: {student['course']}\n• Marks: {student['marks']:.1f}%"
                )
                # Highlight row in Treeview
                children = self.search_tree.get_children()
                if idx < len(children):
                    item_id = children[idx]
                    self.search_tree.item(item_id, tags=("highlight",))
                    self.search_tree.see(item_id)
                    self.search_tree.selection_set(item_id)
            else:
                self.lbl_search_status.configure(text="Status: Record Not Found", fg=self.ACCENT_ROSE)
                self.lbl_search_details.configure(text=f"No record matches Roll Number {target_roll}.")

            time_ms = exec_time * 1000
            time_us = exec_time * 1e6
            self.lbl_search_time.configure(text=f"Execution Time: {time_ms:.4f} ms ({time_us:.2f} µs)")
            self.lbl_search_comps.configure(text=f"Comparisons Made: {comparisons} check(s)")

        else:  # Binary Search
            info = COMPLEXITY_INFO["binary_search"]
            self.lbl_comp_name.configure(text=f"Algorithm: {info['name']}")
            self.lbl_comp_best.configure(text=f"• Best Case: {info['best']} [Target at initial midpoint]")
            self.lbl_comp_avg.configure(text=f"• Average Case: {info['average']} [Repeated bisection]")
            self.lbl_comp_worst.configure(text=f"• Worst Case: {info['worst']} [Subarray reduced to 1 element]")
            self.lbl_comp_space.configure(text=f"• Space Complexity: {info['space']} [Iterative pointers]")
            self.lbl_comp_desc.configure(text=info["description"])

            # Execute Binary Search with preparation timing separation
            idx, student, comparisons, search_time, prep_time, sorted_records = binary_search_with_prep(records, target_roll)

            # Update Treeview to show the pre-sorted array for Binary Search
            for item in self.search_tree.get_children():
                self.search_tree.delete(item)

            for i, r in enumerate(sorted_records):
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                self.search_tree.insert("", tk.END, values=(
                    r["roll_no"],
                    r["name"],
                    r["course"],
                    f"{r['marks']:.1f}"
                ), tags=(tag,))

            if idx != -1 and student:
                self.lbl_search_status.configure(text="Status: Record Found", fg=self.ACCENT_EMERALD)
                self.lbl_search_details.configure(
                    text=f"• Roll No: {student['roll_no']}\n• Name: {student['name']}\n• Course: {student['course']}\n• Marks: {student['marks']:.1f}%"
                )
                children = self.search_tree.get_children()
                if idx < len(children):
                    item_id = children[idx]
                    self.search_tree.item(item_id, tags=("highlight",))
                    self.search_tree.see(item_id)
                    self.search_tree.selection_set(item_id)
            else:
                self.lbl_search_status.configure(text="Status: Record Not Found", fg=self.ACCENT_ROSE)
                self.lbl_search_details.configure(text=f"No record matches Roll Number {target_roll}.")

            search_time_ms = search_time * 1000
            search_time_us = search_time * 1e6
            prep_time_ms = prep_time * 1000

            self.lbl_search_time.configure(text=f"Pure Search Time: {search_time_ms:.4f} ms ({search_time_us:.2f} µs)")
            self.lbl_search_comps.configure(text=f"Comparisons Made: {comparisons} division(s)")
            self.lbl_search_prep.configure(
                text=f"Dataset Sorting Prep Time: {prep_time_ms:.4f} ms (Distinguished from search time)"
            )

    # =========================================================================
    # VIEW 3: SORTING MODULE (BUBBLE SORT & QUICK SORT)
    # =========================================================================
    def _create_sort_view(self) -> tk.Frame:
        """Interactive sorting workbench with Bubble Sort & Quick Sort."""
        view = tk.Frame(self.container, bg=self.BG_LIGHT)

        # Control Panel
        ctrl_card = tk.LabelFrame(
            view,
            text=" Sorting Configuration & Controls ",
            font=("Segoe UI", 11, "bold"),
            fg=self.TEXT_DARK,
            bg=self.CARD_BG,
            padx=16,
            pady=14,
            relief=tk.SOLID,
            bd=1
        )
        ctrl_card.pack(fill=tk.X, pady=(0, 12))

        row = tk.Frame(ctrl_card, bg=self.CARD_BG)
        row.pack(fill=tk.X)

        # Algorithm Choice
        tk.Label(row, text="Algorithm:", font=("Segoe UI", 10, "bold"), fg=self.TEXT_DARK, bg=self.CARD_BG).pack(side=tk.LEFT, padx=(0, 6))
        self.sort_algo_var = tk.StringVar(value="Quick Sort")
        sort_combo = ttk.Combobox(
            row,
            textvariable=self.sort_algo_var,
            values=["Bubble Sort", "Quick Sort"],
            state="readonly",
            width=14,
            font=("Segoe UI", 10)
        )
        sort_combo.pack(side=tk.LEFT, padx=(0, 18))

        # Sort Field
        tk.Label(row, text="Sort By Field:", font=("Segoe UI", 10, "bold"), fg=self.TEXT_DARK, bg=self.CARD_BG).pack(side=tk.LEFT, padx=(0, 6))
        self.sort_field_var = tk.StringVar(value="Roll Number")
        field_combo = ttk.Combobox(
            row,
            textvariable=self.sort_field_var,
            values=["Roll Number", "Marks"],
            state="readonly",
            width=14,
            font=("Segoe UI", 10)
        )
        field_combo.pack(side=tk.LEFT, padx=(0, 18))

        # Sort Order
        tk.Label(row, text="Order:", font=("Segoe UI", 10, "bold"), fg=self.TEXT_DARK, bg=self.CARD_BG).pack(side=tk.LEFT, padx=(0, 6))
        self.sort_order_var = tk.StringVar(value="Ascending (Low → High)")
        order_combo = ttk.Combobox(
            row,
            textvariable=self.sort_order_var,
            values=["Ascending (Low → High)", "Descending (High → Low)"],
            state="readonly",
            width=22,
            font=("Segoe UI", 10)
        )
        order_combo.pack(side=tk.LEFT, padx=(0, 18))

        # Buttons
        btn_sort = tk.Button(
            row,
            text="Run Sorting",
            font=("Segoe UI", 10, "bold"),
            bg=self.ACCENT_PURPLE,
            fg="#ffffff",
            activebackground="#6d28d9",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=14,
            pady=5,
            command=self.handle_execute_sort
        )
        btn_sort.pack(side=tk.LEFT, padx=(0, 10))

        btn_reset = tk.Button(
            row,
            text="Reset Order",
            font=("Segoe UI", 10),
            bg="#f1f5f9",
            fg=self.TEXT_DARK,
            relief=tk.SOLID,
            bd=1,
            cursor="hand2",
            padx=10,
            pady=4,
            command=self.refresh_sort_source_table
        )
        btn_reset.pack(side=tk.LEFT)

        # Dual column lower area
        lower_frame = tk.Frame(view, bg=self.BG_LIGHT)
        lower_frame.pack(fill=tk.BOTH, expand=True)

        # Left Column: Metrics and Theoretical Complexity
        left_col = tk.Frame(lower_frame, bg=self.BG_LIGHT, width=380)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_col.pack_propagate(False)

        # Execution Metrics Box
        self.sort_metric_box = tk.LabelFrame(
            left_col,
            text=" Sorting Execution Metrics ",
            font=("Segoe UI", 10, "bold"),
            fg=self.TEXT_DARK,
            bg=self.CARD_BG,
            padx=14,
            pady=12,
            relief=tk.SOLID,
            bd=1
        )
        self.sort_metric_box.pack(fill=tk.X, pady=(0, 12))

        self.lbl_sort_time = tk.Label(self.sort_metric_box, text="Execution Time: 0.000 ms", font=("Segoe UI", 10, "bold"), fg=self.ACCENT_PURPLE, bg=self.CARD_BG)
        self.lbl_sort_time.pack(anchor=tk.W, pady=2)

        self.lbl_sort_comps = tk.Label(self.sort_metric_box, text="Comparisons Made: 0", font=("Segoe UI", 9), fg=self.TEXT_DARK, bg=self.CARD_BG)
        self.lbl_sort_comps.pack(anchor=tk.W, pady=2)

        self.lbl_sort_swaps = tk.Label(self.sort_metric_box, text="Swaps Performed: 0", font=("Segoe UI", 9), fg=self.TEXT_DARK, bg=self.CARD_BG)
        self.lbl_sort_swaps.pack(anchor=tk.W, pady=2)

        # Theoretical Complexity Info
        self.sort_comp_box = tk.LabelFrame(
            left_col,
            text=" Theoretical Complexity ",
            font=("Segoe UI", 10, "bold"),
            fg=self.TEXT_DARK,
            bg=self.CARD_BG,
            padx=14,
            pady=12,
            relief=tk.SOLID,
            bd=1
        )
        self.sort_comp_box.pack(fill=tk.BOTH, expand=True)

        self.lbl_sort_comp_title = tk.Label(self.sort_comp_box, text="Algorithm: Quick Sort", font=("Segoe UI", 10, "bold"), fg=self.ACCENT_BLUE, bg=self.CARD_BG)
        self.lbl_sort_comp_title.pack(anchor=tk.W, pady=(0, 6))

        self.lbl_sort_best = tk.Label(self.sort_comp_box, text="• Best Case: O(n log n)", font=("Segoe UI", 9), fg=self.TEXT_DARK, bg=self.CARD_BG)
        self.lbl_sort_best.pack(anchor=tk.W, pady=2)

        self.lbl_sort_avg = tk.Label(self.sort_comp_box, text="• Average Case: O(n log n)", font=("Segoe UI", 9), fg=self.TEXT_DARK, bg=self.CARD_BG)
        self.lbl_sort_avg.pack(anchor=tk.W, pady=2)

        self.lbl_sort_worst = tk.Label(self.sort_comp_box, text="• Worst Case: O(n²)", font=("Segoe UI", 9), fg=self.TEXT_DARK, bg=self.CARD_BG)
        self.lbl_sort_worst.pack(anchor=tk.W, pady=2)

        self.lbl_sort_space = tk.Label(self.sort_comp_box, text="• Space Complexity: O(log n)", font=("Segoe UI", 9), fg=self.TEXT_DARK, bg=self.CARD_BG)
        self.lbl_sort_space.pack(anchor=tk.W, pady=2)

        self.lbl_sort_desc = tk.Label(self.sort_comp_box, text="", font=("Segoe UI", 8, "italic"), fg=self.TEXT_MUTED, bg=self.CARD_BG, wraplength=340, justify=tk.LEFT)
        self.lbl_sort_desc.pack(anchor=tk.W, pady=(6, 0))

        # Right Column: Sorted Records Table
        right_col = tk.LabelFrame(
            lower_frame,
            text=" Sorted Student Records Output ",
            font=("Segoe UI", 10, "bold"),
            fg=self.TEXT_DARK,
            bg=self.CARD_BG,
            padx=10,
            pady=10,
            relief=tk.SOLID,
            bd=1
        )
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        cols = ("roll_no", "name", "course", "marks")
        self.sort_tree = ttk.Treeview(right_col, columns=cols, show="headings", selectmode="browse")
        self.sort_tree.heading("roll_no", text="Roll Number")
        self.sort_tree.heading("name", text="Student Name")
        self.sort_tree.heading("course", text="Course")
        self.sort_tree.heading("marks", text="Marks (%)")

        self.sort_tree.column("roll_no", width=110, anchor=tk.CENTER)
        self.sort_tree.column("name", width=220, anchor=tk.W)
        self.sort_tree.column("course", width=120, anchor=tk.CENTER)
        self.sort_tree.column("marks", width=100, anchor=tk.E)

        self.sort_tree.tag_configure("evenrow", background=self.ROW_EVEN)
        self.sort_tree.tag_configure("oddrow", background=self.ROW_ODD)

        sort_scroll = ttk.Scrollbar(right_col, orient=tk.VERTICAL, command=self.sort_tree.yview)
        self.sort_tree.configure(yscrollcommand=sort_scroll.set)

        self.sort_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sort_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        return view

    def refresh_sort_source_table(self):
        """Reset sort view table to current CSV database state."""
        self.manager.refresh()
        records = self.manager.get_all()
        for item in self.sort_tree.get_children():
            self.sort_tree.delete(item)

        for i, r in enumerate(records):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.sort_tree.insert("", tk.END, values=(
                r["roll_no"],
                r["name"],
                r["course"],
                f"{r['marks']:.1f}"
            ), tags=(tag,))

    def handle_execute_sort(self):
        """Execute Bubble Sort or Quick Sort on current records and display."""
        algo_choice = self.sort_algo_var.get()
        field_choice = self.sort_field_var.get()
        order_choice = self.sort_order_var.get()

        key = "roll_no" if field_choice == "Roll Number" else "marks"
        ascending = "Ascending" in order_choice

        records = self.manager.get_all()
        if not records:
            messagebox.showwarning("Empty Database", "There are no records to sort.")
            return

        if algo_choice == "Bubble Sort":
            info = COMPLEXITY_INFO["bubble_sort"]
            self.lbl_sort_comp_title.configure(text=f"Algorithm: {info['name']}")
            self.lbl_sort_best.configure(text=f"• Best Case: {info['best']} (Unoptimized syllabus baseline)")
            self.lbl_sort_avg.configure(text=f"• Average Case: {info['average']}")
            self.lbl_sort_worst.configure(text=f"• Worst Case: {info['worst']}")
            self.lbl_sort_space.configure(text=f"• Space Complexity: {info['space']} (In-place)")
            self.lbl_sort_desc.configure(text=info["description"])

            sorted_records, exec_time, comps, swaps = bubble_sort(records, key=key, ascending=ascending)

        else:  # Quick Sort
            info = COMPLEXITY_INFO["quick_sort"]
            self.lbl_sort_comp_title.configure(text=f"Algorithm: {info['name']}")
            self.lbl_sort_best.configure(text=f"• Best Case: {info['best']} (Balanced partitions)")
            self.lbl_sort_avg.configure(text=f"• Average Case: {info['average']}")
            self.lbl_sort_worst.configure(text=f"• Worst Case: {info['worst']} (Unbalanced pivot)")
            self.lbl_sort_space.configure(text=f"• Space Complexity: {info['space']} (Recursion stack)")
            self.lbl_sort_desc.configure(text=info["description"])

            sorted_records, exec_time, comps, swaps = quick_sort(records, key=key, ascending=ascending)

        # Repopulate table with sorted records
        for item in self.sort_tree.get_children():
            self.sort_tree.delete(item)

        for i, r in enumerate(sorted_records):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.sort_tree.insert("", tk.END, values=(
                r["roll_no"],
                r["name"],
                r["course"],
                f"{r['marks']:.1f}"
            ), tags=(tag,))

        # Update metrics
        time_ms = exec_time * 1000
        time_us = exec_time * 1e6
        self.lbl_sort_time.configure(text=f"Execution Time: {time_ms:.4f} ms ({time_us:.2f} µs)")
        self.lbl_sort_comps.configure(text=f"Comparisons Made: {comps:,}")
        self.lbl_sort_swaps.configure(text=f"Swaps Performed: {swaps:,}")

    # =========================================================================
    # VIEW 4: PERFORMANCE BENCHMARK & COMPARISON MODULE
    # =========================================================================
    def _create_performance_view(self) -> tk.Frame:
        """Benchmark workbench running real tests on 10, 100, 1000, 5000 records."""
        view = tk.Frame(self.container, bg=self.BG_LIGHT)

        # Header Control Card
        ctrl_card = tk.LabelFrame(
            view,
            text=" Empirical DAA Benchmark Suite (10, 100, 1,000, 5,000 Records) ",
            font=("Segoe UI", 11, "bold"),
            fg=self.TEXT_DARK,
            bg=self.CARD_BG,
            padx=16,
            pady=12,
            relief=tk.SOLID,
            bd=1
        )
        ctrl_card.pack(fill=tk.X, pady=(0, 10))

        row1 = tk.Frame(ctrl_card, bg=self.CARD_BG)
        row1.pack(fill=tk.X)

        self.btn_run_benchmark = tk.Button(
            row1,
            text="🚀 Run Full Benchmark Suite",
            font=("Segoe UI", 10, "bold"),
            bg=self.ACCENT_PURPLE,
            fg="#ffffff",
            activebackground="#6d28d9",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=6,
            command=self.start_benchmark_thread
        )
        self.btn_run_benchmark.pack(side=tk.LEFT, padx=(0, 20))

        self.progress_bar = ttk.Progressbar(row1, orient=tk.HORIZONTAL, length=300, mode="determinate")
        self.progress_bar.pack(side=tk.LEFT, padx=(0, 15))

        self.lbl_bench_status = tk.Label(
            row1,
            text="Status: Ready to benchmark. Click button to begin.",
            font=("Segoe UI", 9, "italic"),
            fg=self.TEXT_MUTED,
            bg=self.CARD_BG
        )
        self.lbl_bench_status.pack(side=tk.LEFT)

        # Main Performance Container (Split: Table above, Matplotlib plot below)
        perf_container = tk.Frame(view, bg=self.BG_LIGHT)
        perf_container.pack(fill=tk.BOTH, expand=True)

        # Benchmark Results Table
        table_box = tk.LabelFrame(
            perf_container,
            text=" Empirical Execution Timing Table ",
            font=("Segoe UI", 10, "bold"),
            fg=self.TEXT_DARK,
            bg=self.CARD_BG,
            padx=8,
            pady=8,
            relief=tk.SOLID,
            bd=1
        )
        table_box.pack(fill=tk.X, pady=(0, 8))

        bench_cols = ("size", "lin_time", "bin_time", "bin_prep", "quick_time", "bubble_time")
        self.bench_tree = ttk.Treeview(table_box, columns=bench_cols, show="headings", height=4)

        self.bench_tree.heading("size", text="Dataset Size (N)")
        self.bench_tree.heading("lin_time", text="Linear Search (µs)")
        self.bench_tree.heading("bin_time", text="Binary Search (µs)")
        self.bench_tree.heading("bin_prep", text="BinSearch Prep Sort (ms)")
        self.bench_tree.heading("quick_time", text="Quick Sort (ms)")
        self.bench_tree.heading("bubble_time", text="Bubble Sort (ms)")

        self.bench_tree.column("size", width=120, anchor=tk.CENTER)
        self.bench_tree.column("lin_time", width=150, anchor=tk.E)
        self.bench_tree.column("bin_time", width=150, anchor=tk.E)
        self.bench_tree.column("bin_prep", width=170, anchor=tk.E)
        self.bench_tree.column("quick_time", width=140, anchor=tk.E)
        self.bench_tree.column("bubble_time", width=140, anchor=tk.E)

        self.bench_tree.tag_configure("evenrow", background=self.ROW_EVEN)
        self.bench_tree.tag_configure("oddrow", background=self.ROW_ODD)

        self.bench_tree.pack(fill=tk.X)

        # Embedded Matplotlib Chart Canvas
        self.chart_box = tk.LabelFrame(
            perf_container,
            text=" Empirical Performance Curves (Side-by-Side Analysis) ",
            font=("Segoe UI", 10, "bold"),
            fg=self.TEXT_DARK,
            bg=self.CARD_BG,
            padx=6,
            pady=4,
            relief=tk.SOLID,
            bd=1
        )
        self.chart_box.pack(fill=tk.BOTH, expand=True)

        self.canvas_widget = None
        self.toolbar_widget = None

        return view

    def start_benchmark_thread(self):
        """Execute benchmarks in a background thread to keep Tkinter GUI responsive."""
        if self.is_benchmarking:
            return

        self.is_benchmarking = True
        self.btn_run_benchmark.configure(state=tk.DISABLED)
        self.progress_bar["value"] = 0

        thread = threading.Thread(target=self._run_benchmarks_worker, daemon=True)
        thread.start()

    def _run_benchmarks_worker(self):
        """Worker thread executing standard benchmark sizes [10, 100, 1000, 5000]."""
        sizes = [10, 100, 1000, 5000]

        def update_progress(current_step, total_steps, message):
            self.after(0, lambda: self._update_bench_ui(current_step, total_steps, message))

        try:
            results = run_full_benchmark(sizes, progress_callback=update_progress)
            self.benchmark_results = results
            self.after(0, lambda: self._finalize_benchmarks(results))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Benchmark Error", f"Benchmarking failed: {e}"))
            self.after(0, lambda: self.btn_run_benchmark.configure(state=tk.NORMAL))
            self.is_benchmarking = False

    def _update_bench_ui(self, current_step, total_steps, message):
        """Safely update progress bar and status from main thread."""
        pct = (current_step / total_steps) * 100
        self.progress_bar["value"] = pct
        self.lbl_bench_status.configure(text=f"Status: {message}")

    def _finalize_benchmarks(self, results: List[Dict[str, Any]]):
        """Render results in table and draw Matplotlib curves."""
        self.is_benchmarking = False
        self.btn_run_benchmark.configure(state=tk.NORMAL)
        self.lbl_bench_status.configure(text="Status: All benchmarks completed successfully!")

        # Populate Results Table
        for item in self.bench_tree.get_children():
            self.bench_tree.delete(item)

        for i, r in enumerate(results):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.bench_tree.insert("", tk.END, values=(
                f"{r['size']:,}",
                f"{r['linear_search_time_us']:.2f} µs",
                f"{r['binary_search_time_us']:.2f} µs",
                f"{r['binary_prep_time_ms']:.3f} ms",
                f"{r['quick_sort_time_ms']:.3f} ms",
                f"{r['bubble_sort_time_ms']:.2f} ms"
            ), tags=(tag,))

        # Render Matplotlib Figure
        fig = create_performance_figure(results)

        # Clear previous canvas
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
        if self.toolbar_widget:
            self.toolbar_widget.destroy()

        self.canvas_widget = FigureCanvasTkAgg(fig, master=self.chart_box)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        messagebox.showinfo(
            "Benchmark Complete",
            "Performance analysis finished across all 4 dataset sizes (10 to 5,000 records)!\n"
            "Notice how Bubble Sort growth curves steeply as O(n²), while Quick Sort remains rapid at O(n log n)."
        )

    # =========================================================================
    # VIEW 5: ALGORITHM ANALYSIS & THEORY SECTION
    # =========================================================================
    def _create_theory_view(self) -> tk.Frame:
        """Educational reference card reviewing DAA theoretical syllabus."""
        view = tk.Frame(self.container, bg=self.BG_LIGHT)

        # Scrollable container for rich syllabus content
        canvas = tk.Canvas(view, bg=self.BG_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(view, orient=tk.VERTICAL, command=canvas.yview)
        scroll_content = tk.Frame(canvas, bg=self.BG_LIGHT)

        scroll_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_content, anchor="nw", width=960)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ---------------- Title Banner ----------------
        title_card = tk.Frame(scroll_content, bg=self.CARD_BG, padx=18, pady=14, relief=tk.SOLID, bd=1)
        title_card.pack(fill=tk.X, pady=(0, 12))

        tk.Label(
            title_card,
            text="Design & Analysis of Algorithms (DAA) - Comprehensive Theoretical Analysis",
            font=("Segoe UI", 13, "bold"),
            fg=self.TEXT_DARK,
            bg=self.CARD_BG
        ).pack(anchor=tk.W)

        tk.Label(
            title_card,
            text="Detailed breakdown of Searching & Sorting Algorithms, Asymptotic Notations, and Complexity Trade-offs.",
            font=("Segoe UI", 9),
            fg=self.TEXT_MUTED,
            bg=self.CARD_BG
        ).pack(anchor=tk.W, pady=(4, 0))

        # ---------------- Section 1: Complexity Comparison Table ----------------
        tbl_card = tk.LabelFrame(
            scroll_content,
            text=" 1. Algorithm Complexity Master Table ",
            font=("Segoe UI", 11, "bold"),
            fg=self.TEXT_DARK,
            bg=self.CARD_BG,
            padx=14,
            pady=12,
            relief=tk.SOLID,
            bd=1
        )
        tbl_card.pack(fill=tk.X, pady=(0, 12))

        cols = ("algo", "type", "best", "avg", "worst", "space")
        tree = ttk.Treeview(tbl_card, columns=cols, show="headings", height=5)
        tree.heading("algo", text="Algorithm Name")
        tree.heading("type", text="Category")
        tree.heading("best", text="Best Case Time")
        tree.heading("avg", text="Average Case Time")
        tree.heading("worst", text="Worst Case Time")
        tree.heading("space", text="Space Complexity")

        tree.column("algo", width=140, anchor=tk.W)
        tree.column("type", width=100, anchor=tk.CENTER)
        tree.column("best", width=120, anchor=tk.CENTER)
        tree.column("avg", width=130, anchor=tk.CENTER)
        tree.column("worst", width=130, anchor=tk.CENTER)
        tree.column("space", width=130, anchor=tk.CENTER)

        master_data = [
            ("Linear Search", "Searching", "O(1)", "O(n)", "O(n)", "O(1) Auxiliary"),
            ("Binary Search", "Searching", "O(1)", "O(log n)", "O(log n)", "O(1) Iterative"),
            ("Bubble Sort", "Sorting", "O(n²) [Unoptimized]", "O(n²)", "O(n²)", "O(1) In-Place"),
            ("Quick Sort", "Sorting", "O(n log n)", "O(n log n)", "O(n²)", "O(log n) Call Stack")
        ]

        for i, row in enumerate(master_data):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            tree.insert("", tk.END, values=row, tags=(tag,))

        tree.pack(fill=tk.X)

        # ---------------- Section 2: Algorithm Explanations ----------------
        algo_card = tk.LabelFrame(
            scroll_content,
            text=" 2. In-Depth Algorithm Mechanics ",
            font=("Segoe UI", 11, "bold"),
            fg=self.TEXT_DARK,
            bg=self.CARD_BG,
            padx=16,
            pady=14,
            relief=tk.SOLID,
            bd=1
        )
        algo_card.pack(fill=tk.X, pady=(0, 12))

        explanations = [
            ("Linear Search",
             "• Mechanism: Iterates sequentially through the array comparing target key with each element.\n"
             "• Preconditions: Works on both sorted and unsorted collections.\n"
             "• Best Case: O(1) occurs when target is at index 0.\n"
             "• Average / Worst Case: O(n) occurs when target is at the end or absent, requiring n checks."),

            ("Binary Search",
             "• Mechanism: Employs divide-and-conquer on pre-sorted arrays. Computes mid = (low + high) // 2.\n"
             "  Halves search space each comparison.\n"
             "• Precondition: Dataset MUST be strictly ordered by the search key.\n"
             "• Note: If unsorted, sorting preparation time O(n log n) must be accounted for.\n"
             "• Complexity: O(log n) worst and average case, O(1) best case."),

            ("Bubble Sort",
             "• Mechanism: Compares adjacent elements (arr[j] > arr[j+1]) and swaps if out of order.\n"
             "  Heavier elements 'bubble up' to the end in successive passes.\n"
             "• Baseline Syllabus Complexity: Nested loops always execute n(n-1)/2 comparisons = O(n²).\n"
             "• Space: O(1) auxiliary space (in-place sorting)."),

            ("Quick Sort",
             "• Mechanism: Selects a pivot element, partitions array into elements ≤ pivot and elements > pivot,\n"
             "  then recursively sorts subarrays.\n"
             "• Average & Best Case: O(n log n) when partitions divide subproblems roughly equally.\n"
             "• Worst Case: O(n²) when pivot selection produces highly unbalanced partitions (e.g. 0 and n-1 elements).\n"
             "• Auxiliary Space: O(log n) required for recursive call stack frames.")
        ]

        for title, desc in explanations:
            tk.Label(algo_card, text=title, font=("Segoe UI", 10, "bold"), fg=self.ACCENT_PURPLE, bg=self.CARD_BG).pack(anchor=tk.W, pady=(6, 2))
            tk.Label(algo_card, text=desc, font=("Segoe UI", 9), fg=self.TEXT_DARK, bg=self.CARD_BG, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=(0, 6))

        # ---------------- Section 3: Asymptotic Notations & Space vs Time ----------------
        asym_card = tk.LabelFrame(
            scroll_content,
            text=" 3. Asymptotic Notations & Complexity Trade-Offs ",
            font=("Segoe UI", 11, "bold"),
            fg=self.TEXT_DARK,
            bg=self.CARD_BG,
            padx=16,
            pady=14,
            relief=tk.SOLID,
            bd=1
        )
        asym_card.pack(fill=tk.X, pady=(0, 20))

        notations = [
            ("Big-O Notation (O) - Asymptotic Upper Bound",
             "Defines the mathematical ceiling / worst-case growth rate of an algorithm. Formally: f(n) <= c * g(n) for all n >= n0."),

            ("Big-Omega Notation (Ω) - Asymptotic Lower Bound",
             "Defines the mathematical floor / best-case growth rate of an algorithm. Formally: f(n) >= c * g(n) for all n >= n0."),

            ("Big-Theta Notation (Θ) - Asymptotically Tight Bound",
             "Represents an exact match where an algorithm is bounded both from above and below by the same order of growth."),

            ("Time Complexity vs. Space Complexity",
             "• Time Complexity measures the total number of elementary operations executed as input size n expands.\n"
             "• Space Complexity measures total memory consumed, split into Fixed Space (variables/constants) and Dynamic/Auxiliary Space (recursion stack, temporary arrays).\n"
             "• Trade-off Example: Quick Sort achieves fast O(n log n) time at the expense of O(log n) recursive stack space.")
        ]

        for title, desc in notations:
            tk.Label(asym_card, text=title, font=("Segoe UI", 10, "bold"), fg=self.ACCENT_BLUE, bg=self.CARD_BG).pack(anchor=tk.W, pady=(6, 2))
            tk.Label(asym_card, text=desc, font=("Segoe UI", 9), fg=self.TEXT_DARK, bg=self.CARD_BG, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=(0, 6))

        return view


def main():
    """Application entry point."""
    app = StudentRecordApp()
    app.mainloop()


if __name__ == "__main__":
    main()
