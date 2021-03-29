import numpy as np
import collections as col
from functools import partial
from tqdm import tqdm
import sys

import rulesandinstructions
import lindenmayer


def string_to_collection(sInput, dctInstructions, lDimensions, npaPos=None, npaFac=None, deqPos=None, deqFac=None):
    """
    Return a list of numpy arrays which interprets the input string using a dictionary of instructions.
    :param sInput: String.  Each character corresponds to some instructions, in the style of turtle graphics
    :param dctInstructions: Dictionary.  Maps each character to its corresponding instruction
    :param lDimensions: Int.  The number of dimensions, usually 2, in which this operation takes place
    :param npaPos: numpy array.  The initial position of the turtle
    :param npaFac: numpy array.  The inital facing vector of the turtle
    :param deqPos: deque.  A deque of positions to and from which instructions may push and pop.
    :param deqFac: deque.  A deque of facings to and from which instructions may push and pop
    :return: List. Each element is a tuple of numpy arrays, which contain the coordinates of lines to be rendered.
    """
    if npaPos is None:
        npaPos = np.array([0 for _i in range(lDimensions)])
    if npaFac is None:
        npaFac = np.array([0 for _i in range(lDimensions)])
        npaFac[0] = 1
    if deqPos is None:
        deqPos = col.deque()
    if deqFac is None:
        deqFac = col.deque()
    liOut = []
    for char in tqdm(sInput, desc="Interpreting string", file=sys.stdout):
        try:
            dctInstruction = dctInstructions[char]
        except KeyError:
            continue
        if dctInstruction["pop-push"][0]:
            npaPos = deqPos.pop()
        if dctInstruction["pop-push"][1]:
            npaFac = deqFac.pop()
        if dctInstruction["pop-push"][2]:
            deqPos.append(npaPos)
        if dctInstruction["pop-push"][3]:
            deqFac.append(npaFac)
        npaFac = dctInstruction["rotation"].dot(npaFac)
        npaDest = npaPos + dctInstruction["movement"] * npaFac
        if dctInstruction["draw"]:
            liOut.append(np.vstack((npaPos, npaDest)))
        npaPos = npaDest
        if dctInstruction["pop-push"][4]:
            npaPos = deqPos.pop()
        if dctInstruction["pop-push"][5]:
            npaFac = deqFac.pop()
        if dctInstruction["pop-push"][6]:
            deqPos.append(npaPos)
        if dctInstruction["pop-push"][7]:
            deqFac.append(npaFac)
    if not liOut:
        liOut.append(np.zeros((lDimensions, 2)))
    return liOut


def main():
    lItPerLoop = 6
    fncGeneratorMaker = partial(lindenmayer.lindenator,
                                rulesandinstructions.liKochCurveRules,
                                lMaxReturns=lItPerLoop
                                )
    itLoopedGenerator = lindenmayer.generator_looper(fncGeneratorMaker)
    bKeepGoing = True
    while bKeepGoing:
        sText = next(itLoopedGenerator)
        liCoords = string_to_collection(sInput=sText,
                                        dctInstructions=rulesandinstructions.dct2dStdInstructions,
                                        lDimensions=2,
                                        npaFac=np.array([1, 0])
                                        )
        print(sText)
        print(liCoords)
        sInput = input("type 'end' to end")
        if sInput == "end":
            bKeepGoing = False
    print("ended")


if __name__ == "__main__":
    main()
