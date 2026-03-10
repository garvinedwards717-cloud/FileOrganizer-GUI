import tkinter as tk

from gui import FileOrganizerApp


def main() -> None:
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()