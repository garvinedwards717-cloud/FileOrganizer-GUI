import tkinter as tk
from tkinter import filedialog, messagebox

from organizer import organize_folder, preview_organization, undo_last_operation
from watcher import FolderWatcher


class FileOrganizerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("File Organizer GUI")
        self.root.geometry("720x560")
        self.root.resizable(False, False)

        self.selected_folder = tk.StringVar()
        self.watcher = None
        self.monitoring = False

        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_ui(self) -> None:
        title_label = tk.Label(
            self.root,
            text="File Organizer",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=15)

        instruction_label = tk.Label(
            self.root,
            text="Select a folder to preview, organize, or monitor automatically",
            font=("Arial", 11)
        )
        instruction_label.pack(pady=5)

        folder_frame = tk.Frame(self.root)
        folder_frame.pack(pady=10)

        folder_entry = tk.Entry(
            folder_frame,
            textvariable=self.selected_folder,
            width=50
        )
        folder_entry.pack(side=tk.LEFT, padx=5)

        browse_button = tk.Button(
            folder_frame,
            text="Browse",
            command=self.browse_folder
        )
        browse_button.pack(side=tk.LEFT)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        preview_button = tk.Button(
            button_frame,
            text="Preview",
            font=("Arial", 10, "bold"),
            command=self.run_preview,
            width=15,
            height=2
        )
        preview_button.pack(side=tk.LEFT, padx=6)

        organize_button = tk.Button(
            button_frame,
            text="Organize Files",
            font=("Arial", 10, "bold"),
            command=self.run_organizer,
            width=15,
            height=2
        )
        organize_button.pack(side=tk.LEFT, padx=6)

        undo_button = tk.Button(
            button_frame,
            text="Undo Last Action",
            font=("Arial", 10, "bold"),
            command=self.run_undo,
            width=15,
            height=2
        )
        undo_button.pack(side=tk.LEFT, padx=6)

        monitor_frame = tk.Frame(self.root)
        monitor_frame.pack(pady=5)

        self.monitor_button = tk.Button(
            monitor_frame,
            text="Start Monitoring",
            font=("Arial", 10, "bold"),
            command=self.toggle_monitoring,
            width=20,
            height=2
        )
        self.monitor_button.pack()

        results_label = tk.Label(
            self.root,
            text="Preview / Results",
            font=("Arial", 11, "bold")
        )
        results_label.pack(pady=(15, 5))

        self.results_box = tk.Text(self.root, width=82, height=15)
        self.results_box.pack(pady=5)
        self.results_box.config(state=tk.DISABLED)

    def browse_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder.set(folder)

    def update_results_box(self, content: str, append: bool = False) -> None:
        self.results_box.config(state=tk.NORMAL)

        if not append:
            self.results_box.delete("1.0", tk.END)

        self.results_box.insert(tk.END, content + "\n")
        self.results_box.config(state=tk.DISABLED)

    def run_preview(self) -> None:
        folder = self.selected_folder.get().strip()

        if not folder:
            messagebox.showwarning("No Folder Selected", "Please select a folder first.")
            return

        try:
            preview_results = preview_organization(folder)

            if not preview_results:
                self.update_results_box("No files found to organize.")
                return

            lines = ["Preview of file organization:\n"]
            for file_name, category in preview_results:
                lines.append(f"{file_name}  ->  {category}")

            self.update_results_box("\n".join(lines))
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def run_organizer(self) -> None:
        folder = self.selected_folder.get().strip()

        if not folder:
            messagebox.showwarning("No Folder Selected", "Please select a folder first.")
            return

        try:
            moved_files, renamed_files = organize_folder(folder)

            result_message = (
                f"Organization complete.\n\n"
                f"Files moved: {moved_files}\n"
                f"Files auto-renamed: {renamed_files}\n\n"
                f"Activity saved to logs/activity.log"
            )

            self.update_results_box(result_message)
            messagebox.showinfo("Organization Complete", result_message)
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def run_undo(self) -> None:
        try:
            restored_files = undo_last_operation()
            result_message = f"Undo complete.\n\nFiles restored: {restored_files}"
            self.update_results_box(result_message)
            messagebox.showinfo("Undo Complete", result_message)
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def monitor_callback(self, message: str) -> None:
        self.root.after(0, lambda: self.update_results_box(message, append=True))

    def toggle_monitoring(self) -> None:
        folder = self.selected_folder.get().strip()

        if not self.monitoring:
            if not folder:
                messagebox.showwarning("No Folder Selected", "Please select a folder first.")
                return

            try:
                self.watcher = FolderWatcher(folder, self.monitor_callback)
                self.watcher.start()
                self.monitoring = True
                self.monitor_button.config(text="Stop Monitoring")
                self.update_results_box(f"Monitoring started for:\n{folder}")
            except Exception as error:
                messagebox.showerror("Error", str(error))
        else:
            if self.watcher:
                self.watcher.stop()

            self.monitoring = False
            self.monitor_button.config(text="Start Monitoring")
            self.update_results_box("Monitoring stopped.")

    def on_close(self) -> None:
        if self.watcher and self.monitoring:
            self.watcher.stop()
        self.root.destroy()