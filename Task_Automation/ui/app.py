
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
import math
import time

from core.backup import create_backup, restore_backup
from core.duplicates import find_duplicates
from core.organizer import scan_images, organize_images
from core.logger import get_logger

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


BG = "#090914"
PANEL = "#121326"
PANEL2 = "#191a31"
WHITE = "#f3f4ff"
MUTED = "#9295b4"
CYAN = "#00f5ff"
PURPLE = "#a855f7"
PINK = "#ff38c7"
GREEN = "#39ff9c"
ORANGE = "#ffb347"


class Hologram(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent, bg=BG, highlightthickness=0, **kwargs
        )
        self.phase = 0
        self.bind("<Configure>", self.draw)
        self.animate()

    def animate(self):
        self.phase += 0.045
        self.draw()
        self.after(35, self.animate)

    def draw(self, event=None):
        self.delete("all")
        w = max(self.winfo_width(), 250)
        h = max(self.winfo_height(), 200)
        cx, cy = w / 2, h / 2
        radius = min(w, h) * 0.29

        colors = [CYAN, PURPLE, PINK, GREEN]
        self.create_oval(
            cx-radius-22, cy-radius-22,
            cx+radius+22, cy+radius+22,
            outline="#282449", width=2
        )

        for i, color in enumerate(colors):
            angle = self.phase + i * math.pi / 2
            x = cx + math.cos(angle) * radius * 0.2
            y = cy + math.sin(angle) * radius * 0.2
            self.create_oval(
                x-radius, y-radius, x+radius, y+radius,
                outline=color, width=2
            )

        # Holographic core
        for i in range(12, 0, -1):
            r = radius * i / 12
            color = colors[i % len(colors)]
            self.create_oval(
                cx-r, cy-r, cx+r, cy+r,
                outline=color, width=1
            )

        self.create_oval(
            cx-radius*0.43, cy-radius*0.43,
            cx+radius*0.43, cy+radius*0.43,
            fill="#21183d", outline=CYAN, width=2
        )
        self.create_text(
            cx, cy-8, text="TASK",
            fill=WHITE, font=("Segoe UI", 17, "bold")
        )
        self.create_text(
            cx, cy+17, text="AUTOMATION CORE",
            fill=CYAN, font=("Consolas", 8, "bold")
        )

        for i in range(28):
            angle = self.phase * 0.5 + i * math.tau / 28
            r = radius + 28 + math.sin(self.phase+i)*7
            x = cx + math.cos(angle)*r
            y = cy + math.sin(angle)*r
            self.create_oval(
                x-2, y-2, x+2, y+2,
                fill=colors[i % 4], outline=""
            )


class TaskAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TASK AUTOMATION PRO | RGB HOLOGRAPHIC")
        self.root.geometry("1200x760")
        self.root.minsize(950, 650)
        self.root.configure(bg=BG)

        self.project = Path(__file__).resolve().parent.parent
        self.logger = get_logger()
        self.current_page = None
        self.image_files = []
        self.duplicate_groups = []
        self.preview_image = None

        self.build_layout()
        self.show_page("Dashboard")
        self.refresh_dashboard()
        self.refresh_logs()

    def build_layout(self):
        header = tk.Frame(self.root, bg=BG, height=75)
        header.pack(fill="x", padx=22, pady=(14, 5))
        header.pack_propagate(False)

        tk.Label(
            header, text="◈ TASK AUTOMATION",
            bg=BG, fg=CYAN,
            font=("Segoe UI", 21, "bold")
        ).pack(side="left")

        tk.Label(
            header, text="PRO 3.0  |  HOLOGRAPHIC EDITION",
            bg=BG, fg=PINK,
            font=("Consolas", 10, "bold")
        ).pack(side="right", padx=10)

        tk.Frame(
            self.root, bg=PURPLE, height=1
        ).pack(fill="x", padx=22)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=18, pady=15)

        self.sidebar = tk.Frame(
            body, bg=PANEL, width=205
        )
        self.sidebar.pack(side="left", fill="y", padx=(0, 15))
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar, text="CONTROL CENTER",
            bg=PANEL, fg=MUTED,
            font=("Consolas", 10, "bold")
        ).pack(anchor="w", padx=17, pady=(22, 18))

        self.pages = {}
        self.nav_buttons = {}

        for name, symbol in [
            ("Dashboard", "◈"),
            ("Image Scanner", "▧"),
            ("Duplicate Finder", "⧉"),
            ("Backup Manager", "⬡"),
            ("Activity Logs", "≋"),
        ]:
            button = tk.Button(
                self.sidebar,
                text=f"  {symbol}   {name}",
                command=lambda n=name: self.show_page(n),
                bg=PANEL, fg=WHITE,
                activebackground=PANEL2,
                activeforeground=CYAN,
                font=("Segoe UI", 10, "bold"),
                relief="flat", anchor="w",
                padx=10, pady=13, cursor="hand2"
            )
            button.pack(fill="x", padx=9, pady=3)
            self.nav_buttons[name] = button

        tk.Frame(
            self.sidebar, bg="#292746", height=1
        ).pack(fill="x", padx=15, pady=18)

        tk.Label(
            self.sidebar, text="SYSTEM STATUS",
            bg=PANEL, fg=MUTED,
            font=("Consolas", 9, "bold")
        ).pack(anchor="w", padx=17)

        tk.Label(
            self.sidebar, text="●  CORE ONLINE",
            bg=PANEL, fg=GREEN,
            font=("Consolas", 10, "bold")
        ).pack(anchor="w", padx=17, pady=10)

        tk.Label(
            self.sidebar, text="PYTHON DESKTOP APP",
            bg=PANEL, fg=MUTED,
            font=("Consolas", 8)
        ).pack(side="bottom", pady=18)

        self.content = tk.Frame(body, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        for name in [
            "Dashboard", "Image Scanner",
            "Duplicate Finder", "Backup Manager",
            "Activity Logs"
        ]:
            page = tk.Frame(self.content, bg=BG)
            self.pages[name] = page

        self.build_dashboard()
        self.build_scanner()
        self.build_duplicates()
        self.build_backup()
        self.build_logs()

        footer = tk.Frame(self.root, bg=BG)
        footer.pack(fill="x", padx=22, pady=(0, 12))

        self.status_label = tk.Label(
            footer, text="● SYSTEM READY",
            bg=BG, fg=GREEN,
            font=("Consolas", 9)
        )
        self.status_label.pack(side="left")

        tk.Label(
            footer, text="ADARSH GUPTA  |  TASK AUTOMATION PRO",
            bg=BG, fg=MUTED,
            font=("Consolas", 8)
        ).pack(side="right")

    def heading(self, parent, title, subtitle):
        tk.Label(
            parent, text=title,
            bg=BG, fg=WHITE,
            font=("Segoe UI", 23, "bold")
        ).pack(anchor="w", pady=(8, 3))

        tk.Label(
            parent, text=subtitle,
            bg=BG, fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 15))

    def card(self, parent, title, value, color):
        frame = tk.Frame(
            parent, bg=PANEL,
            highlightbackground=color,
            highlightthickness=1
        )
        tk.Label(
            frame, text=title.upper(),
            bg=PANEL, fg=MUTED,
            font=("Consolas", 9, "bold")
        ).pack(anchor="w", padx=15, pady=(14, 5))

        value_label = tk.Label(
            frame, text=value,
            bg=PANEL, fg=color,
            font=("Segoe UI", 25, "bold")
        )
        value_label.pack(anchor="w", padx=15, pady=(0, 14))
        return value_label

    def button(self, parent, text, command, color=CYAN):
        return tk.Button(
            parent, text=text,
            command=command,
            bg=PANEL2, fg=color,
            activebackground="#292746",
            activeforeground=WHITE,
            font=("Segoe UI", 10, "bold"),
            relief="flat", bd=0,
            padx=16, pady=11, cursor="hand2"
        )

    def show_page(self, name):
        if self.current_page:
            self.current_page.pack_forget()

        self.current_page = self.pages[name]
        self.current_page.pack(fill="both", expand=True)

        for page_name, button in self.nav_buttons.items():
            button.configure(
                bg=PANEL2 if page_name == name else PANEL,
                fg=CYAN if page_name == name else WHITE
            )

        self.status_label.configure(
            text=f"● {name.upper()} ACTIVE", fg=GREEN
        )

        if name == "Activity Logs":
            self.refresh_logs()
        elif name == "Dashboard":
            self.refresh_dashboard()

    def build_dashboard(self):
        page = self.pages["Dashboard"]
        self.heading(
            page, "Command Dashboard",
            "Your automation control system at a glance."
        )

        cards = tk.Frame(page, bg=BG)
        cards.pack(fill="x", pady=5)

        self.image_count = self.card(
            cards, "Images Found", "0", CYAN
        )
        self.duplicate_count = self.card(
            cards, "Duplicate Groups", "0", PINK
        )
        self.backup_count = self.card(
            cards, "Backups Created", "0", PURPLE
        )

        for widget in cards.winfo_children():
            widget.pack(side="left", fill="both", expand=True, padx=5)

        self.hologram = Hologram(
            page, height=285
        )
        self.hologram.pack(fill="both", expand=True, pady=8)

        tk.Label(
            page, text="RGB HOLOGRAPHIC ENGINE  •  ONLINE",
            bg=BG, fg=CYAN,
            font=("Consolas", 10, "bold")
        ).pack(pady=5)

        self.button(
            page, "⟳ REFRESH DASHBOARD",
            self.refresh_dashboard, GREEN
        ).pack(pady=10)

    def refresh_dashboard(self):
        try:
            images = scan_images(
                self.project / "destination_images"
            )
            self.image_count.configure(text=str(len(images)))

            backup_dir = self.project / "backups"
            backups = (
                list(backup_dir.glob("*.zip"))
                if backup_dir.exists() else []
            )
            self.backup_count.configure(text=str(len(backups)))

            self.duplicate_count.configure(
                text=str(len(self.duplicate_groups))
            )
        except Exception:
            self.logger.exception("Dashboard refresh failed")

    def build_scanner(self):
        page = self.pages["Image Scanner"]
        self.heading(
            page, "Image Scanner",
            "Scan, preview and organize your image collection."
        )

        actions = tk.Frame(page, bg=BG)
        actions.pack(fill="x", pady=8)

        self.button(
            actions, "SELECT FOLDER",
            self.select_image_folder
        ).pack(side="left", padx=4)

        self.button(
            actions, "ORGANIZE / COPY",
            self.organize_selected, GREEN
        ).pack(side="left", padx=4)

        self.button(
            actions, "ORGANIZE / MOVE",
            lambda: self.organize_selected(move=True), PINK
        ).pack(side="left", padx=4)

        self.scanner_info = tk.Label(
            page, text="Select a folder to scan images.",
            bg=BG, fg=MUTED,
            font=("Segoe UI", 10)
        )
        self.scanner_info.pack(anchor="w", pady=10)

        area = tk.Frame(page, bg=PANEL)
        area.pack(fill="both", expand=True, pady=8)

        self.image_list = tk.Listbox(
            area, bg=PANEL, fg=WHITE,
            selectbackground="#41306b",
            font=("Consolas", 10),
            relief="flat", width=35
        )
        self.image_list.pack(
            side="left", fill="both", expand=True, padx=10, pady=10
        )
        self.image_list.bind(
            "<<ListboxSelect>>", self.preview_selected
        )

        self.preview = tk.Label(
            area, text="IMAGE PREVIEW",
            bg=PANEL2, fg=CYAN,
            font=("Consolas", 12, "bold"),
            width=32
        )
        self.preview.pack(
            side="right", fill="both", expand=True,
            padx=10, pady=10
        )

    def select_image_folder(self):
        folder = filedialog.askdirectory(
            title="Select image folder"
        )
        if not folder:
            return

        try:
            self.image_files = scan_images(folder)
            self.image_list.delete(0, "end")

            for path in self.image_files:
                self.image_list.insert("end", path.name)

            self.scanner_folder = Path(folder)
            self.scanner_info.configure(
                text=f"{len(self.image_files)} images found in {folder}",
                fg=GREEN
            )
            self.logger.info(
                "Scanned %s images in %s",
                len(self.image_files), folder
            )
        except Exception as error:
            messagebox.showerror("Scanner Error", str(error))

    def preview_selected(self, event=None):
        selection = self.image_list.curselection()
        if not selection:
            return

        path = self.image_files[selection[0]]

        try:
            if Image and ImageTk:
                img = Image.open(path)
                img.thumbnail((390, 330))
                self.preview_image = ImageTk.PhotoImage(img)
            else:
                self.preview_image = tk.PhotoImage(file=str(path))

            self.preview.configure(
                image=self.preview_image, text=""
            )
        except Exception as error:
            self.preview.configure(
                image="", text=f"Preview unavailable\n{error}"
            )

    def organize_selected(self, move=False):
        if not getattr(self, "image_files", None):
            messagebox.showwarning(
                "No Images", "First select an image folder."
            )
            return

        destination = filedialog.askdirectory(
            title="Select destination folder"
        )
        if not destination:
            return

        if Path(destination).resolve() == self.scanner_folder.resolve():
            messagebox.showwarning(
                "Invalid Destination",
                "Choose a different destination folder."
            )
            return

        try:
            results = organize_images(
                self.scanner_folder,
                destination,
                move=move
            )
            self.logger.info(
                "Image organization completed: %s files",
                len(results)
            )
            messagebox.showinfo(
                "Complete",
                f"{len(results)} images processed."
            )
        except Exception as error:
            self.logger.exception("Image organization failed")
            messagebox.showerror("Organizer Error", str(error))

    def build_duplicates(self):
        page = self.pages["Duplicate Finder"]
        self.heading(
            page, "Duplicate Detection",
            "Find identical files using SHA-256 hashing."
        )

        self.button(
            page, "SELECT FOLDER & SCAN",
            self.start_duplicate_scan, PINK
        ).pack(anchor="w", pady=8)

        self.duplicate_status = tk.Label(
            page, text="Ready to scan.",
            bg=BG, fg=MUTED,
            font=("Segoe UI", 10)
        )
        self.duplicate_status.pack(anchor="w", pady=10)

        area = tk.Frame(page, bg=PANEL)
        area.pack(fill="both", expand=True, pady=8)

        self.duplicate_output = tk.Text(
            area, bg=PANEL, fg=WHITE,
            insertbackground=CYAN,
            font=("Consolas", 10),
            relief="flat", wrap="word"
        )
        self.duplicate_output.pack(
            fill="both", expand=True, padx=12, pady=12
        )

    def start_duplicate_scan(self):
        folder = filedialog.askdirectory(
            title="Select folder to scan"
        )
        if not folder:
            return

        self.duplicate_status.configure(
            text="Scanning files...", fg=ORANGE
        )

        def work():
            try:
                groups = find_duplicates(folder)
                self.root.after(
                    0, lambda: self.show_duplicates(groups)
                )
            except Exception as error:
                self.root.after(
                    0, lambda e=error: self.show_error(
                        "Duplicate Scan Error", e
                    )
                )

        threading.Thread(target=work, daemon=True).start()

    def show_duplicates(self, groups):
        self.duplicate_groups = groups
        self.duplicate_output.delete("1.0", "end")

        if not groups:
            self.duplicate_output.insert(
                "end", "No duplicate files found."
            )
        else:
            for index, group in enumerate(groups, 1):
                self.duplicate_output.insert(
                    "end", f"\nGROUP {index}\n"
                )
                for path in group:
                    self.duplicate_output.insert(
                        "end", f"  {path}\n"
                    )

        self.duplicate_status.configure(
            text=f"{len(groups)} duplicate groups found.",
            fg=GREEN
        )
        self.logger.info(
            "Duplicate scan completed: %s groups", len(groups)
        )
        self.refresh_dashboard()

    def build_backup(self):
        page = self.pages["Backup Manager"]
        self.heading(
            page, "Backup & Restore",
            "Create ZIP backups and safely restore archived files."
        )

        panel = tk.Frame(
            page, bg=PANEL,
            highlightbackground=PURPLE,
            highlightthickness=1
        )
        panel.pack(fill="x", pady=15)

        tk.Label(
            panel, text="BACKUP OPERATIONS",
            bg=PANEL, fg=CYAN,
            font=("Consolas", 12, "bold")
        ).pack(anchor="w", padx=18, pady=(18, 10))

        self.button(
            panel, "CREATE BACKUP",
            self.run_backup, GREEN
        ).pack(anchor="w", padx=18, pady=8)

        self.button(
            panel, "RESTORE BACKUP",
            self.run_restore, PINK
        ).pack(anchor="w", padx=18, pady=8)

        self.backup_status = tk.Label(
            panel, text="No operation performed yet.",
            bg=PANEL, fg=MUTED,
            font=("Consolas", 9),
            justify="left", wraplength=650
        )
        self.backup_status.pack(
            anchor="w", padx=18, pady=18
        )

    def run_backup(self):
        try:
            archive = create_backup(self.project)
            self.backup_status.configure(
                text=f"Backup created:\n{archive}", fg=GREEN
            )
            self.logger.info("Backup created: %s", archive)
            self.refresh_dashboard()
            messagebox.showinfo("Backup Complete", str(archive))
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
            self.backup_status.configure(
                text=f"Restored safely into:\n{restored}",
                fg=GREEN
            )
            self.logger.info("Backup restored: %s", restored)
            messagebox.showinfo("Restore Complete", str(restored))
        except Exception as error:
            self.logger.exception("Restore failed")
            messagebox.showerror("Restore Error", str(error))

    def build_logs(self):
        page = self.pages["Activity Logs"]
        self.heading(
            page, "Activity Logs",
            "Review application events and errors."
        )

        actions = tk.Frame(page, bg=BG)
        actions.pack(fill="x", pady=8)

        self.button(
            actions, "REFRESH LOGS",
            self.refresh_logs
        ).pack(side="left", padx=4)

        self.button(
            actions, "CLEAR VIEW",
            lambda: self.log_output.delete("1.0", "end"),
            PINK
        ).pack(side="left", padx=4)

        self.log_output = tk.Text(
            page, bg=PANEL, fg="#d1e5ff",
            insertbackground=CYAN,
            relief="flat", font=("Consolas", 10),
            wrap="word"
        )
        self.log_output.pack(
            fill="both", expand=True, pady=10
        )

    def refresh_logs(self):
        if not hasattr(self, "log_output"):
            return

        path = self.project / "logs" / "task_automation.log"
        self.log_output.delete("1.0", "end")

        if path.exists():
            try:
                content = path.read_text(
                    encoding="utf-8", errors="replace"
                )
                self.log_output.insert("end", content)
                self.log_output.see("end")
            except OSError as error:
                self.log_output.insert("end", str(error))
        else:
            self.log_output.insert("end", "No logs available.")

    def show_error(self, title, error):
        self.logger.exception("%s: %s", title, error)
        self.duplicate_status.configure(
            text=str(error), fg=PINK
        )
        messagebox.showerror(title, str(error))


def launch():
    root = tk.Tk()
    TaskAutomationApp(root)
    root.mainloop()


if __name__ == "__main__":
    launch()
