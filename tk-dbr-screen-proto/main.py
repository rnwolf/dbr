import tkinter as tk
from tkinter import ttk


def main():
    window = tk.Tk()
    window.title("Hello World App")
    window.geometry("300x200")

    label = ttk.Label(master=window, text="Hello World!")
    label.pack(expand=True)

    window.mainloop()


if __name__ == "__main__":
    main()
