import tkinter as tk
from tkinter import filedialog
from LRenderer import render_2d_frame_by_frame_animation
from LRenderer import get_makerkey


def prompt_2d_clone():
    sFile = filedialog.askopenfilename()
    render_2d_frame_by_frame_animation(**get_makerkey(sFile))


def prompt_makerkey():
    sFile = filedialog.askopenfilename()
    print(get_makerkey(sFile))


def main():
    root = tk.Tk()
    root.withdraw()
    prompt_makerkey()
    # prompt_2d_clone()


if __name__ == "__main__":
    main()
