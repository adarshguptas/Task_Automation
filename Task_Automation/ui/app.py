import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading

from core.organizer import scan_images, organize_images
from core.duplicates import find_duplicates
from core.backup import create_backup
from core.logger import get_logger


class TaskAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TASK AUTOMATION PRO")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self.root.configure(bg="#10131c")

        self.project = Path(__file__).resolve().parent.parent
        self.logger = get_logger()
        self.source = self.project / "source_images"
        self.destination = self.project / "destination_images"

        self.setup_style()
        self.build_ui()
        self.refresh_dashboard()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TNotebook",
            background="#10131c",
            borderwidth=0
        )
        style.configure(
            "TNotebook.Tab",
            background="#252b3a",
            foreground="white",
            padding=(18, 10),
            font=("Segoe UI", 10, "bold")
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", "#7c3aed")],
            foreground=[("selected", "white")]
        )
        style.configure(
            "Treeview",
            background="#1b2030",
            foreground="white",
            fieldbackground="#1b2030",
            rowheight=28
        )
        style.configure(
            "Treeview.Heading",
            background="#30384b",
            foreground="white",
            font=("Segoe UI", 10, "bold")
        )

    def button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg="#7c3aed",
            fg="white",
            activebackground="#6d28d9",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=10,
            cursor="hand2"
        )

    def build_ui(self):
        header = tk.Frame(self.root, bg="#171c2a", height=90)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="TASK AUTOMATION PRO",
            bg="#171c2a",
            fg="white",
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w", padx=25, pady=(15, 0))

        tk.Label(
            header,
            text="Python Desktop Productivity Suite",
            bg="#171c2a",
            fg="#a78bfa",
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=27)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=18, pady=18)

        self.dashboard_tab = tk.Frame(
            self.notebook, bg="#10131c"
        )
        self.organizer_tab = tk.Frame(
            self.notebook, bg="#10131c"
        )
        self.duplicates_tab = tk.Frame(
            self.notebook, bg="#10131c"
        )
        self.logs_tab = tk.Frame(
            self.notebook, bg="#10131c"
        )
        self.backup_tab = tk.Frame(
            self.notebook, bg="#10131c"
        )

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.organizer_tab, text="Image Organizer")
        self.notebook.add(self.duplicates_tab, text="Duplicates")
        self.notebook.add(self.logs_tab, text="Activity Logs")
        self.notebook.add(self.backup_tab, text="Backup Manager")

        self.build_dashboard()
        self.build_organizer()
        self.build_duplicates()
        self.build_logs()
        self.build_backup()

    def heading(self, parent, title, subtitle):
        tk.Label(
            parent, text=title,
            bg="#10131c", fg="white",
            font=("Segoe UI", 19, "bold")
        ).pack(anchor="w", padx=25, pady=(25, 5))

        tk.Label(
            parent, text=subtitle,
            bg="#10131c", fg="#9ca3af",
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=25, pady=(0, 20))

    def build_dashboard(self):
        self.heading(
            self.dashboard_tab,
            "Overview Dashboard",
            "Monitor your file automation workspace."
        )

        cards = tk.Frame(self.dashboard_tab, bg="#10131c")
        cards.pack(fill="x", padx=15)

        self.stats = {}

        for key, title in [
            ("source", "SOURCE IMAGES"),
            ("destination", "ORGANIZED IMAGES"),
            ("duplicates", "DUPLICATE GROUPS")
        ]:
            card = tk.Frame(
                cards, bg="#1b2030",
                padx=22, pady=20
            )
            card.pack(
                side="left", fill="both",
                expand=True, padx=10, pady=10
            )

            tk.Label(
                card, text=title,
                bg="#1b2030", fg="#a78bfa",
                font=("Segoe UI", 10, "bold")
            ).pack(anchor="w")

            value = tk.Label(
                card, text="0",
                bg="#1b2030", fg="white",
                font=("Segoe UI", 30, "bold")
            )
            value.pack(anchor="w", pady=10)
            self.stats[key] = value

        self.button(
            self.dashboard_tab,
            "REFRESH DASHBOARD",
            self.refresh_dashboard
        ).pack(anchor="w", padx=25, pady=20)

        self.status = tk.Label(
            self.dashboard_tab,
            text="SYSTEM READY",
            bg="#10131c", fg="#34d399",
            font=("Segoe UI", 11, "bold")
        )
        self.status.pack(anchor="w", padx=25)

    def refresh_dashboard(self):
        try:
            source_count = len(scan_images(self.source))
            destination_count = len(scan_images(self.destination))

            self.stats["source"].config(text=str(source_count))
            self.stats["destination"].config(text=str(destination_count))
            self.stats["duplicates"].config(text="--")

            self.status.config(
                text="SYSTEM ONLINE | Dashboard refreshed"
            )
        except Exception as error:
            self.logger.exception("Dashboard refresh failed")
            messagebox.showerror("Error", str(error))

    def build_organizer(self):
        self.heading(
            self.organizer_tab,
            "Image Organizer",
            "Organize images safely into your destination folder."
        )

        tk.Label(
            self.organizer_tab,
            text=f"Source: {self.source}",
            bg="#10131c", fg="white",
            wraplength=850
        ).pack(anchor="w", padx=25, pady=5)

        tk.Label(
            self.organizer_tab,
            text=f"Destination: {self.destination}",
            bg="#10131c", fg="white",
            wraplength=850
        ).pack(anchor="w", padx=25, pady=5)

        self.organizer_mode = tk.StringVar(value="copy")

        tk.Radiobutton(
            self.organizer_tab,
            text="Copy images (Safe mode)",
            variable=self.organizer_mode,
            value="copy",
            bg="#10131c", fg="white",
            selectcolor="#252b3a",
            activebackground="#10131c",
            activeforeground="white"
        ).pack(anchor="w", padx=25, pady=10)

        tk.Radiobutton(
            self.organizer_tab,
            text="Move images (Originals will leave source folder)",
            variable=self.organizer_mode,
            value="move",
            bg="#10131c", fg="white",
            selectcolor="#252b3a",
            activebackground="#10131c",
            activeforeground="white"
        ).pack(anchor="w", padx=25)

        self.button(
            self.organizer_tab,
            "RUN IMAGE ORGANIZER",
            self.run_organizer
        ).pack(anchor="w", padx=25, pady=20)

        self.organizer_output = tk.Text(
            self.organizer_tab,
            height=12, bg="#1b2030",
            fg="#d1d5db", insertbackground="white",
            relief="flat", font=("Consolas", 10)
        )
        self.organizer_output.pack(
            fill="both", expand=True, padx=25, pady=10
        )

    def run_organizer(self):
        move = self.organizer_mode.get() == "move"

        if move and not messagebox.askyesno(
            "Confirm Move",
            "Images will be moved from source. Continue?"
        ):
            return

        try:
            results = organize_images(
                self.source,
                self.destination,
                move=move
            )

            self.organizer_output.delete("1.0", "end")

            for name, action, target in results:
                self.organizer_output.insert(
                    "end", f"{action}: {name}\n"
                )

            self.logger.info(
                "Organizer completed: %s files, move=%s",
                len(results), move
            )

            messagebox.showinfo(
                "Completed",
                f"{len(results)} image files processed."
            )
            self.refresh_dashboard()
        except Exception as error:
            self.logger.exception("Organizer failed")
            messagebox.showerror("Organizer Error", str(error))

    def build_duplicates(self):
        self.heading(
            self.duplicates_tab,
            "Duplicate Detector",
            "Find identical files using SHA-256 hashing."
        )

        self.button(
            self.duplicates_tab,
            "SCAN PROJECT FILES",
            self.run_duplicate_scan
        ).pack(anchor="w", padx=25, pady=5)

        self.duplicate_output = tk.Text(
            self.duplicates_tab,
            bg="#1b2030", fg="#d1d5db",
            insertbackground="white",
            relief="flat", font=("Consolas", 10)
        )
        self.duplicate_output.pack(
            fill="both", expand=True, padx=25, pady=20
        )

    def run_duplicate_scan(self):
        try:
            groups = find_duplicates(self.project)
            self.duplicate_output.delete("1.0", "end")

            if not groups:
                self.duplicate_output.insert(
                    "end", "No duplicate files found.\n"
                )

            for number, group in enumerate(groups, 1):
                self.duplicate_output.insert(
                    "end", f"\nGROUP {number}\n"
                )
                for path in group:
                    self.duplicate_output.insert(
                        "end", f"  {path}\n"
                    )

            self.logger.info(
                "Duplicate scan completed: %s groups",
                len(groups)
            )

            self.stats["duplicates"].config(text=str(len(groups)))

        except Exception as error:
            self.logger.exception("Duplicate scan failed")
            messagebox.showerror("Scan Error", str(error))

    def build_logs(self):
        self.heading(
            self.logs_tab,
            "Activity Logs",
            "Application events and error history."
        )

        self.log_output = tk.Text(
            self.logs_tab,
            bg="#1b2030", fg="#d1d5db",
            insertbackground="white",
            relief="flat", font=("Consolas", 10)
        )
        self.log_output.pack(
            fill="both", expand=True, padx=25, pady=10
        )

        self.button(
            self.logs_tab,
            "REFRESH LOGS",
            self.refresh_logs
        ).pack(anchor="w", padx=25, pady=10)

    def refresh_logs(self):
        path = self.project / "logs" / "task_automation.log"
        self.log_output.delete("1.0", "end")

        if path.exists():
            self.log_output.insert(
                "end", path.read_text(encoding="utf-8")
            )
        else:
            self.log_output.insert("end", "No logs available.")

    def build_backup(self):
        self.heading(
            self.backup_tab,
            "Backup Manager",
            "Create a compressed backup of your project."
        )

        self.button(
            self.backup_tab,
            "CREATE PROJECT BACKUP",
            self.run_backup
        ).pack(anchor="w", padx=25, pady=15)

        self.backup_output = tk.Label(
            self.backup_tab,
            text="No backup created in this session.",
            bg="#10131c", fg="#d1d5db",
            wraplength=850
        )
        self.backup_output.pack(anchor="w", padx=25, pady=10)

    def run_backup(self):
        try:
            archive = create_backup(self.project)
            self.backup_output.config(
                text=f"Backup created successfully:\n{archive}"
            )
            self.logger.info("Backup created: %s", archive)
            messagebox.showinfo(
                "Backup Complete",
                f"Backup saved:\n{archive}"
            )
        except Exception as error:
            self.logger.exception("Backup failed")
            messagebox.showerror("Backup Error", str(error))


def launch():
    root = tk.Tk()
    TaskAutomationApp(root)
    root.mainloop()
