import tkinter as tk
from tkinter import filedialog
from renderer import render_2d_frame_by_frame_animation
from renderer import get_makerkey
# import junkdrawer
# import json
from PIL import Image

def prompt_2d_clone():
    sFile = filedialog.askopenfilename()
    render_2d_frame_by_frame_animation(**get_makerkey(sFile))


def prompt_makerkey():
    sFile = filedialog.askopenfilename()
    print(get_makerkey(sFile))


def prompt_makerjson():
    sFile = filedialog.askopenfilename()
    with Image.open(sFile) as imgGif:
        # jsonBlueprint = json.loads(imgGif.info["comment"], cls=junkdrawer.JeffSONDecoder)
        jsonBlueprint = imgGif.info["comment"].decode('ASCII')
    print(jsonBlueprint)


def main():
    root = tk.Tk()
    root.withdraw()
    prompt_makerjson()
    # prompt_makerkey()
    # prompt_2d_clone()


if __name__ == "__main__":
    main()
