import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import math

from core.organizer import scan_images, organize_images
from core.duplicates import find_duplicates
from core.backup import create_backup, restore_backup
from core.logger import get_logger


class TaskAutomationApp:

    def __init__(self, root):
        self.root = root
        self.project = Path(__file__).resolve().parent.parent
        self.logger = get_logger()

        self.source = tk.StringVar(
            value=str(self.project / "source_images")
        )
        self.destination = tk.StringVar(
            value=str(self.project / "destination_images")
        )

        self.photo_reference = None

        self.root.title("TASK AUTOMATION PRO 2.0")
        self.root.geometry("1150x760")
        self.root.minsize(950, 650)
        self.root.configure(bg="#10131c")

        self.setup_style()
        self.build_interface()
        self.refresh_dashboard()
        self.refresh_logs()

        self.root.after(3000, self.live_refresh)

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
            padding=(17, 11),
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
            foreground="white"
        )
        style.configure(
            "Horizontal.TProgressbar",
            troughcolor="#252b3a",
            background="#a78bfa"
        )

    def button(self, parent, title, command):
        return tk.Button(
            parent,
            text=title,
            command=command,
            bg="#7c3aed",
            fg="white",
            activebackground="#6d28d9",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=9,
            cursor="hand2"
        )

    def heading(self, parent, title, subtitle):
        tk.Label(
            parent, text=title,
            bg="#10131c", fg="white",
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w", padx=22, pady=(22, 5))

        tk.Label(
            parent, text=subtitle,
            bg="#10131c", fg="#a78bfa",
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=22, pady=(0, 18))

    def build_interface(self):
        header = tk.Frame(
            self.root, bg="#171c2a", height=85
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="TASK AUTOMATION PRO",
            bg="#171c2a", fg="white",
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w", padx=24, pady=(12, 0))

        tk.Label(
            header,
            text="PYTHON DESKTOP PRODUCTIVITY SUITE  |  VERSION 2.0",
            bg="#171c2a", fg="#a78bfa",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=26)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(
            fill="both", expand=True, padx=15, pady=15
        )

        self.tabs = {}

        for key, title in [
            ("dashboard", "Dashboard"),
            ("organizer", "Image Organizer"),
            ("duplicates", "Duplicates"),
            ("backup", "Backup & Restore"),
            ("logs", "Activity Logs")
        ]:
            frame = tk.Frame(
                self.notebook, bg="#10131c"
            )
            self.tabs[key] = frame
            self.notebook.add(frame, text=title)

        self.build_dashboard()
        self.build_organizer()
        self.build_duplicates()
        self.build_backup()
        self.build_logs()

    def card(self, parent, title):
        frame = tk.Frame(
            parent, bg="#1b2030", padx=20, pady=18
        )
        frame.pack(
            side="left", fill="both",
            expand=True, padx=8, pady=8
        )

        tk.Label(
            frame, text=title,
            bg="#1b2030", fg="#a78bfa",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        value = tk.Label(
            frame, text="0",
            bg="#1b2030", fg="white",
            font=("Segoe UI", 29, "bold")
        )
        value.pack(anchor="w", pady=10)

        return value

    def build_dashboard(self):
        tab = self.tabs["dashboard"]

        self.heading(
            tab, "Overview Dashboard",
            "Live statistics of your automation workspace."
        )

        cards = tk.Frame(tab, bg="#10131c")
        cards.pack(fill="x", padx=12)

        self.stat_source = self.card(cards, "SOURCE IMAGES")
        self.stat_destination = self.card(
            cards, "DESTINATION IMAGES"
        )
        self.stat_duplicates = self.card(
            cards, "DUPLICATE GROUPS"
        )

        self.dashboard_status = tk.Label(
            tab,
            text="SYSTEM ONLINE",
            bg="#10131c", fg="#34d399",
            font=("Segoe UI", 11, "bold")
        )
        self.dashboard_status.pack(
            anchor="w", padx=22, pady=18
        )

        self.button(
            tab, "REFRESH NOW", self.refresh_dashboard
        ).pack(anchor="w", padx=22)

    def refresh_dashboard(self):
        try:
            self.stat_source.config(
                text=str(len(scan_images(self.source.get())))
            )
            self.stat_destination.config(
                text=str(len(scan_images(self.destination.get())))
            )

            self.dashboard_status.config(
                text="SYSTEM ONLINE | LIVE STATISTICS UPDATED"
            )
        except Exception as error:
            self.logger.exception("Dashboard error")
            self.dashboard_status.config(
                text=f"Dashboard error: {error}"
            )

    def live_refresh(self):
        if self.root.winfo_exists():
            self.refresh_dashboard()
            self.root.after(3000, self.live_refresh)

    def folder_row(self, parent, label, variable):
        row = tk.Frame(parent, bg="#10131c")
        row.pack(fill="x", padx=22, pady=7)

        tk.Label(
            row, text=label, width=13,
            anchor="w", bg="#10131c",
            fg="white", font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        tk.Entry(
            row, textvariable=variable,
            bg="#252b3a", fg="white",
            insertbackground="white",
            relief="flat"
        ).pack(side="left", fill="x", expand=True, ipady=8)

        self.button(
            row, "BROWSE",
            lambda: self.browse_folder(variable)
        ).pack(side="left", padx=8)

    def browse_folder(self, variable):
        folder = filedialog.askdirectory()
        if folder:
            variable.set(folder)

    def progress_widgets(self, parent):
        self.progress = ttk.Progressbar(
            parent, mode="determinate",
            style="Horizontal.TProgressbar"
        )
        self.progress.pack(
            fill="x", padx=22, pady=(10, 4)
        )

        self.progress_label = tk.Label(
            parent, text="Ready",
            bg="#10131c", fg="#a78bfa"
        )
        self.progress_label.pack(anchor="w", padx=22)

    def update_progress(self, current, total, name):
        self.progress["maximum"] = max(total, 1)
        self.progress["value"] = current
        self.progress_label.config(
            text=f"{current}/{total}  |  {name}"
        )
        self.root.update_idletasks()

    def build_organizer(self):
        tab = self.tabs["organizer"]

        self.heading(
            tab, "Image Organizer",
            "Browse folders, preview images and organize safely."
        )

        self.folder_row(tab, "SOURCE", self.source)
        self.folder_row(tab, "DESTINATION", self.destination)

        self.organizer_mode = tk.StringVar(value="copy")

        modes = tk.Frame(tab, bg="#10131c")
        modes.pack(anchor="w", padx=22, pady=10)

        for title, value in [
            ("Safe Copy", "copy"),
            ("Move Files", "move")
        ]:
            tk.Radiobutton(
                modes, text=title,
                variable=self.organizer_mode,
                value=value,
                bg="#10131c", fg="white",
                selectcolor="#252b3a",
                activebackground="#10131c",
                activeforeground="white"
            ).pack(side="left", padx=8)

        self.button(
            tab, "SCAN IMAGES", self.preview_images
        ).pack(anchor="w", padx=22, pady=5)

        self.button(
            tab, "START ORGANIZER", self.run_organizer
        ).pack(anchor="w", padx=22, pady=5)

        self.progress_widgets(tab)

        body = tk.Frame(tab, bg="#10131c")
        body.pack(fill="both", expand=True, padx=22, pady=12)

        self.image_list = tk.Listbox(
            body, bg="#1b2030", fg="white",
            selectbackground="#7c3aed",
            relief="flat", font=("Segoe UI", 10),
            width=38
        )
        self.image_list.pack(side="left", fill="y")
        self.image_list.bind(
            "<<ListboxSelect>>", self.show_preview
        )

        preview_frame = tk.Frame(
            body, bg="#1b2030"
        )
        preview_frame.pack(
            side="left", fill="both",
            expand=True, padx=12
        )

        self.preview = tk.Label(
            preview_frame,
            text="Select an image to preview",
            bg="#1b2030", fg="#a78bfa",
            font=("Segoe UI", 12)
        )
        self.preview.pack(expand=True)

        self.organizer_output = tk.Text(
            tab, height=5,
            bg="#1b2030", fg="#d1d5db",
            insertbackground="white",
            relief="flat", font=("Consolas", 9)
        )
        self.organizer_output.pack(
            fill="x", padx=22, pady=8
        )

        self.image_files = []

    def preview_images(self):
        try:
            self.image_files = scan_images(self.source.get())
            self.image_list.delete(0, "end")

            for path in self.image_files:
                self.image_list.insert("end", path.name)

            self.preview.config(
                image="", text=f"{len(self.image_files)} images found"
            )
            self.photo_reference = None

        except Exception as error:
            messagebox.showerror("Scan Error", str(error))

    def show_preview(self, event=None):
        selection = self.image_list.curselection()
        if not selection:
            return

        path = self.image_files[selection[0]]

        try:
            photo = tk.PhotoImage(file=str(path))
            factor = max(
                1,
                math.ceil(max(
                    photo.width() / 500,
                    photo.height() / 350
                ))
            )
            photo = photo.subsample(factor, factor)

            self.photo_reference = photo
            self.preview.config(image=photo, text="")

        except tk.TclError:
            self.photo_reference = None
            self.preview.config(
                image="",
                text=(
                    f"{path.name}\n"
                    "Preview format not supported by Tkinter.\n"
                    "File remains safe and unchanged."
                )
            )

    def run_organizer(self):
        move = self.organizer_mode.get() == "move"

        if move and not messagebox.askyesno(
            "Confirm Move",
            "Original files will be moved. Continue?"
        ):
            return

        try:
            self.progress["value"] = 0
            self.organizer_output.delete("1.0", "end")

            results = organize_images(
                self.source.get(),
                self.destination.get(),
                move=move,
                progress=self.update_progress
            )

            for name, action, target in results:
                self.organizer_output.insert(
                    "end", f"{action}: {name}\n"
                )

            self.logger.info(
                "Organizer completed: %s files",
                len(results)
            )

            self.preview_images()
            self.refresh_dashboard()

            messagebox.showinfo(
                "Completed",
                f"{len(results)} files processed."
            )

        except Exception as error:
            self.logger.exception("Organizer failed")
            messagebox.showerror("Organizer Error", str(error))

    def build_duplicates(self):
        tab = self.tabs["duplicates"]

        self.heading(
            tab, "Advanced Duplicate Detector",
            "Compare file sizes and SHA-256 hashes."
        )

        self.button(
            tab, "SCAN PROJECT",
            self.run_duplicate_scan
        ).pack(anchor="w", padx=22)

        self.progress_widgets(tab)

        self.duplicate_output = tk.Text(
            tab, bg="#1b2030", fg="#d1d5db",
            insertbackground="white",
            relief="flat", font=("Consolas", 10)
        )
        self.duplicate_output.pack(
            fill="both", expand=True, padx=22, pady=18
        )

    def run_duplicate_scan(self):
        try:
            self.progress["value"] = 0
            groups = find_duplicates(
                self.project,
                progress=self.update_progress
            )

            self.duplicate_output.delete("1.0", "end")

            for number, group in enumerate(groups, 1):
                self.duplicate_output.insert(
                    "end", f"\nDUPLICATE GROUP {number}\n"
                )
                for path in group:
                    self.duplicate_output.insert(
                        "end", f"  {path}\n"
                    )

            if not groups:
                self.duplicate_output.insert(
                    "end", "No duplicates found."
                )

            self.stat_duplicates.config(text=str(len(groups)))
            self.logger.info(
                "Duplicate scan: %s groups", len(groups)
            )

        except Exception as error:
            self.logger.exception("Duplicate scan failed")
            messagebox.showerror("Duplicate Error", str(error))

    def build_backup(self):
        tab = self.tabs["backup"]

        self.heading(
            tab, "Backup & Restore Manager",
            "Create project backups and restore into a separate folder."
        )

        self.button(
            tab, "CREATE ZIP BACKUP",
            self.run_backup
        ).pack(anchor="w", padx=22, pady=10)

        self.button(
            tab, "RESTORE FROM ZIP",
            self.run_restore
        ).pack(anchor="w", padx=22, pady=10)

        self.backup_status = tk.Label(
            tab, text="Ready",
            bg="#10131c", fg="#a78bfa",
            wraplength=850, justify="left"
        )
        self.backup_status.pack(
            anchor="w", padx=22, pady=15
        )

    def run_backup(self):
        try:
            archive = create_backup(self.project)
            self.backup_status.config(
                text=f"Backup created:\n{archive}"
            )
            self.logger.info("Backup created: %s", archive)

            messagebox.showinfo(
                "Backup Complete", str(archive)
            )

        except Exception as error:
            self.logger.exception("Backup failed")
            messagebox.showerror("Backup Error", str(error))

    def run_restore(self):
        archive = filedialog.askopenfilename(
            title="Select backup",
            filetypes=[("ZIP archives", "*.zip")]
        )

        if not archive:
            return

        destination = filedialog.askdirectory(
            title="Select an EMPTY restore folder"
        )

        if not destination:
            return

        if not messagebox.askyesno(
            "Confirm Restore",
            "Restore files into the selected folder?\n"
            "The folder must be empty."
        ):
            return

        try:
            restored = restore_backup(archive, destination)
            self.backup_status.config(
                text=f"Restored safely into:\n{restored}"
            )
            self.logger.info("Backup restored: %s", restored)

            messagebox.showinfo(
                "Restore Complete", str(restored)
            )

        except Exception as error:
            self.logger.exception("Restore failed")
            messagebox.showerror("Restore Error", str(error))

    def build_logs(self):
        tab = self.tabs["logs"]

        self.heading(
            tab, "Activity Logs",
            "Review application events and errors."
        )

        self.log_output = tk.Text(
            tab, bg="#1b2030", fg="#d1d5db",
            insertbackground="white",
            relief="flat", font=("Consolas", 10)
        )
        self.log_output.pack(
            fill="both", expand=True, padx=22, pady=10
        )

        self.button(
            tab, "REFRESH LOGS", self.refresh_logs
        ).pack(anchor="w", padx=22, pady=8)

    def refresh_logs(self):
        path = self.project / "logs" / "task_automation.log"

        if not hasattr(self, "log_output"):
            return

        self.log_output.delete("1.0", "end")

        if path.exists():
            self.log_output.insert(
                "end", path.read_text(
                    encoding="utf-8", errors="replace"
                )
            )
        else:
            self.log_output.insert("end", "No logs available.")


def launch():
    root = tk.Tk()
    TaskAutomationApp(root)
    root.mainloop()
