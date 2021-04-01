import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import matplotlib.animation as animation
from functools import partial
# from itertools import count
from collections import namedtuple
from datetime import datetime
from tqdm import tqdm
from PIL import Image
import json
from pygifsicle import optimize
import warnings
import sys

import lindenmayer
import rulesandinstructions
import stringparser
import junkdrawer


def render_2d_line_segments(liData, fLimScale=1.1, fLimOffset=1):
    """
    Plot a list of numpy arrays representing 2D points.
    :param liData: List. Each element is a tuple of numpy arrays, which contain the coordinates of lines to be rendered.
    :param fLimScale: Float. Scaling factor for determining plot limits. A higher value 'zooms out'.
    :param fLimOffset: Float. Offset factor for determining plot limits. A higher value 'zooms out'.
    """
    liXs = np.hstack([ra[:, 0] for ra in liData])
    liYs = np.hstack([ra[:, 1] for ra in liData])
    liXs = np.append(liXs, 0)
    liYs = np.append(liYs, 0)
    fig, ax = plt.subplots()
    ax.set_xlim((np.min(liXs) - fLimOffset) / fLimScale, (np.max(liXs) + fLimOffset) * fLimScale)
    ax.set_ylim((np.min(liYs) - fLimOffset) / fLimScale, (np.max(liYs) + fLimOffset) * fLimScale)

    line_segments = LineCollection(liData,
                                   linewidths=0.5,
                                   linestyles='solid',
                                   colors=(0, 0, 0, 1)
                                   )

    ax.add_collection(line_segments)
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_title('Output')


def render_3d_line_segments(liData, fLimScale=1.1, fLimOffset=1):
    """
    Plot a list of numpy arrays representing 3D points.
    :param liData: List. Each element is a tuple of numpy arrays, which contain the coordinates of lines to be rendered.
    :param fLimScale: Float. Scaling factor for determining plot limits. A higher value 'zooms out'.
    :param fLimOffset: Float. Offset factor for determining plot limits. A higher value 'zooms out'.
    """
    lXMax = np.max(np.append(np.hstack([ra[:, 0] for ra in liData]), 1))
    lYMax = np.max(np.append(np.hstack([ra[:, 1] for ra in liData]), 1))
    lZMax = np.max(np.append(np.hstack([ra[:, 2] for ra in liData]), 1))
    npaScaleMatrix = np.array([[1/lXMax, 0, 0], [0, 1/lYMax, 0], [0, 0, 1/lZMax]])
    liScaledData = [npa.dot(npaScaleMatrix) for npa in liData]
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    line_segments = Line3DCollection(liScaledData,
                                     linewidths=0.5,
                                     linestyles='solid',
                                     colors=(0, 0, 0, 1)
                                     )

    ax.add_collection(line_segments)
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    ax.set_title('Output')


def render_next_on_close():
    """
    Render fractal one generation at a time.
    Render a plot, on plot close pause for user input. 'end' will end the process
    """
    lItPerLoop = 6
    fncGeneratorMaker = partial(lindenmayer.lindenator,
                                rulesandinstructions.liKochCurveRules,
                                sInput="FF+F-F-F+FF",
                                lMaxReturns=lItPerLoop
                                )
    itLoopedGenerator = lindenmayer.generator_looper(fncGeneratorMaker)

    bKeepGoing = True
    while bKeepGoing:

        sText = next(itLoopedGenerator)
        liCoords = stringparser.string_to_collection(sInput=sText,
                                                     dctInstructions=rulesandinstructions.dct2dStdInstructions,
                                                     lDimensions=2,
                                                     npaFac=np.array([1, 0])
                                                     )
        render_2d_line_segments(liCoords)
        plt.show()
        sInput = input("type 'end' to end")
        if sInput == "end":
            bKeepGoing = False
    print("ended")


def init_fig_2d(objFig, objAx, ntArtists):
    """
    Init function for animation.FuncAnimation within render_2d_frame_by_frame_animation.
    """
    return ntArtists


def frame_iter_2d(itLoopedGenerator, fncInterpreter, lMod, lLastFrameHang=1):
    """
    Frames function for animation.FuncAnimation within render_2d_frame_by_frame_animation.
    """
    i = 0
    for i in range(lMod-1):
        sText = next(itLoopedGenerator)
        liData = fncInterpreter(sText)
        yield liData, "Generation {}".format(i)
    sText = next(itLoopedGenerator)
    liData = fncInterpreter(sText)
    i += 1
    for j in tqdm(range(lLastFrameHang), desc="Last Frame Repeat: ", file=sys.stdout):
        yield liData, "Generation {}".format(i)


def update_artists_2d(tFrameYield, ntArtists, tAspectRatio=(1, 1)):
    """
    Update function for animation.FuncAnimation within render_2d_frame_by_frame_animation.
    """
    liData, sTracker = tFrameYield

    lXMin = np.min(np.append(np.hstack([ra[:, 0] for ra in liData]), 0))
    lYMin = np.min(np.append(np.hstack([ra[:, 1] for ra in liData]), 0))
    npaTranslationMatrix = np.array([[lXMin, lYMin], [lXMin, lYMin]])
    npaTranslationMatrix = npaTranslationMatrix.dot(-1)
    liData = [npa + npaTranslationMatrix for npa in liData]
    lXMax = np.max(np.append(np.hstack([ra[:, 0] for ra in liData]), 1))  # * tAspectRatio[1]
    lYMax = np.max(np.append(np.hstack([ra[:, 1] for ra in liData]), 1))  # * tAspectRatio[0]
    lMax = np.max([lXMax, lYMax])
    npaScaleMatrix = np.array([[tAspectRatio[0]/lXMax, 0], [0, tAspectRatio[1]/lMax]])
    liData = [npa.dot(npaScaleMatrix) for npa in liData]

    ntArtists.objText.set_text(sTracker)
    ntArtists.lcCoords.set_segments(liData)


def render_2d_frame_by_frame_animation(sName, liRules, dctInstructions, sStartingString, lItPerLoop,
                                       npaStartPos=None, npaStartFac=None,
                                       tAspectRatio=(1, 1), lLastFrameHang=1):
    """
    Render a fractal as a gif, encoding as a comment the parameters used to make it (its 'makerkey').
    :param sName: String. Name of gif. Will get appended with timestamp and file extension.
    :param liRules: List. Stochastic Lindenmayer rules for string replacement.
    :param dctInstructions: Dictionary. Instructions for interpreting characters in string as drawing directions
    :param sStartingString: String.  The axiom for the Lindenmayer system.
    :param lItPerLoop: Integer. The number of generations for iteration.
    :param npaStartPos: Numpy array.  The starting position of the turtle which draws the fractal.
    :param npaStartFac: Numpy array.  The starting facing of the turtle which draws the fractal.
    :param tAspectRatio: Tuple.  The aspect ratio of the resulting plots and gif.
    :param lLastFrameHang: Integer. The number of frames to let the last frame "hang" on.
    :return: String. File name of gif.
    """
    fncGeneratorMaker = partial(lindenmayer.lindenator,
                                liRules,
                                sInput=sStartingString,
                                lMaxReturns=lItPerLoop
                                )
    itLoopedGenerator = lindenmayer.generator_looper(fncGeneratorMaker)

    # string_to_collection(sInput, dctInstructions, lDimensions, npaPos=None, npaFac=None, deqPos=None, deqFac=None)
    fncInterpreter = partial(stringparser.string_to_collection,
                             dctInstructions=dctInstructions,
                             lDimensions=2,
                             npaPos=npaStartPos,
                             npaFac=npaStartFac
                             )

    objFig, objAx = plt.subplots(figsize=(9, 9))
    # objAx.set_xlabel('X axis')
    # objAx.set_ylabel('Y axis')
    objAx.set_xlim(-0.1, 1*tAspectRatio[0] + 0.1)
    objAx.set_ylim(-0.1, 1*tAspectRatio[1] + 0.1)
    plt.axis('off')
    clsArtists = namedtuple("Artists", ("lcCoords", "objText"))
    ntArtists = clsArtists(
                           objAx.add_collection(LineCollection([],
                                                               linewidths=0.5,
                                                               linestyles='solid',
                                                               colors=(0, 0, 0, 1)
                                                               )
                                               ),
                           objAx.text(x=.05, y=.05, s="")
                           )

    #  init_fig_2d(ntArtists):
    fncInit = partial(init_fig_2d, objFig=objFig, objAx=objAx, ntArtists=ntArtists)
    #  frame_iter_2d(itGenerator, lCounter, lMod):
    fncStep = partial(frame_iter_2d, itLoopedGenerator=itLoopedGenerator, fncInterpreter=fncInterpreter,
                      lMod=lItPerLoop, lLastFrameHang=1)
    # update_artists_2d(frames, objAx, fncInterpreter)
    fncUpdate = partial(update_artists_2d, ntArtists=ntArtists, tAspectRatio=tAspectRatio)

    objAnim = animation.FuncAnimation(
        fig=objFig,
        func=fncUpdate,
        frames=fncStep,
        init_func=fncInit,
        cache_frame_data=False,
        interval=500,
        repeat_delay=2000,
        # blit=True
    )

    # plt.show()

    # Set up formatting for the movie files
    # Just kidding, mp4 doesn't seem to work well for these few-frame animations...viewers each interpret the files
    # differently
    # clsWriter = animation.writers['ffmpeg']
    # writer = clsWriter(fps=10, metadata=dict(artist='Jeff Maher'), bitrate=1800)

    objNow = datetime.now()
    # TODO: un-hardcode this
    sFileName = 'static/Saved_Animations/' + sName + objNow.strftime("_%Y-%m-%d_%H-%M-%S") + '.gif'

    objAnim.save(sFileName)

    sMakerKey = json.dumps({"sName": sName,
                            "liRules": liRules,
                            "dctInstructions": dctInstructions,
                            "sStartingString": sStartingString,
                            "lItPerLoop": lItPerLoop,
                            "npaStartPos": npaStartPos,
                            "npaStartFac": npaStartFac,
                            "tAspectRatio": tAspectRatio,
                            "lLastFrameHang": lLastFrameHang
                            }, cls=junkdrawer.JeffSONEncoder)
    liFrames = []
    with Image.open(sFileName) as imgNewGif:
        for i in range(imgNewGif.n_frames):
            imgNewGif.seek(i)
            liFrames.append(imgNewGif.copy())
    for i in range(lLastFrameHang):
        liFrames.append(liFrames[-1])
    liFrames[-1].save(sFileName,
                      save_all=True,
                      loop=0,
                      duration=500,
                      append_images=liFrames[:-1],
                      optimize=True,
                      include_color_table=False,
                      comment=sMakerKey)
    try:
        optimize(sFileName)
    except FileNotFoundError:
        warnings.warn("Failed to find gifsicle to optimize filesize.")
    finally:
        return sFileName


def clone_2d_gif(sFile):
    """
    Generate a clone of a fractal based on its makerkey.
    :param sFile: String. Filename of fractal gif, must contain makerkey as a comment.
    :return: String. File name of new gif.
    """
    return render_2d_frame_by_frame_animation(**get_makerkey(sFile))


def get_makerkey(fileName):
    """
    Unpack the makerkey stored in a fractal.
    :param sFile: String. Filename of fractal gif, must contain makerkey as a comment.
    :return: Dictionary. Makerkey.
    """
    with Image.open(fileName) as imgGif:
        dctRenderParams = json.loads(imgGif.info["comment"], cls=junkdrawer.JeffSONDecoder)
    return dctRenderParams


def main():
    render_next_on_close()
    tAspectRatio = (1, 1)
    liRules = [
               rulesandinstructions.new_rule("F",
                                             [(.1, "F[-X][+X]"),
                                              (.2, "FFF"),
                                              (1, "FF")],
                                             sName="Growing"),
               rulesandinstructions.new_rule("(Z)",
                                             [(.4, r"F[-\1][\1]+F[+\1][\1]"),
                                              (.8, r"F[+\1][\1]+F[-\1][\1]"),
                                              (.9, r"F[-\1][\1].F[+\1][\1]"),
                                              (1, r"F[+\1][\1].F[-\1][\1]"),
                                              ],
                                             sName="Left Branch"),
               rulesandinstructions.new_rule("(X)",
                                             [(.4, r"F[,X][\1]F[.X][\1]"),
                                              (.8, r"F[.X][\1]F[,X][\1]"),
                                              (.9, r"F[-X][\1]F[+X][\1]"),
                                              (1, r"F[+X][\1]F[-X][\1]"),
                                              ],
                                             sName="Center Branch"),
               rulesandinstructions.new_rule("(C)",
                                             [(.4, r"F[-\1][\1]-F[+\1][\1]"),
                                              (.8, r"F[+\1][\1]-F[-\1][\1]"),
                                              (.9, r"F[-\1][\1],F[+\1][\1]"),
                                              (1, r"F[+\1][\1],F[-\1][\1]"),
                                              ],
                                             sName="Right Branch")
               ]
    liRules = rulesandinstructions.LiPlant2Rules
    dctInstructions = rulesandinstructions.std_2d_instructions(np.pi * 0.125)
    sStartingString = "[+X][X][-X]"
    lItPerLoop = 7
    npaStartPos = np.array([.5, 0])
    npaStartFac = np.array([0, 1])
    sName = "Plant"
    sFile = render_2d_frame_by_frame_animation(sName, liRules, dctInstructions, sStartingString, lItPerLoop,
                                               npaStartPos, npaStartFac, tAspectRatio, 4)


if __name__ == "__main__":
    main()
