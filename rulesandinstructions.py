import numpy as np

# http://paulbourke.net/fractals/lsys/
""" Idea for character set:
Character        Meaning
   F	         Move forward by line length drawing a line
   G	         Move forward by line length drawing a line 
   f	         Move forward by line length without drawing a line
   +	         Turn left by turning angle
   -	         Turn right by turning angle
   |	         Reverse direction (ie: turn by 180 degrees)
   [	         Push current drawing state onto stack
   ]	         Pop current drawing state from the stack
   #	         Increment the line width by line width increment
   !	         Decrement the line width by line width increment
   @	         Draw a dot with line width radius
   {	         Open a polygon
   }	         Close a polygon and fill it with fill colour
   >	         Multiply the line length by the line length scale factor
   <	         Divide the line length by the line length scale factor
   &	         Swap the meaning of + and -
   (	         Decrement turning angle by turning angle increment
   )	         Increment turning angle by turning angle increment
   Any other character does nothing
"""


def rotation_matrix_2d(theta):
    """
    Create rotation matrix in 2D space based on theta in radians.
    :param theta: Float. Radians.
    :return: numpy array. Rotation Matrix.
    """
    fSin = np.round(np.sin(theta), 10)
    fCos = np.round(np.cos(theta), 10)
    return np.array([[fCos, -fSin],
                     [fSin, fCos]])


def std_2d_instructions(fTheta, fRTheta=None):
    if fRTheta is None:
        fRTheta = 2. * np.pi - fTheta
    dctOut = {
        "F": {"draw": True,
              "pop-push": [0, 0, 0, 0, 0, 0, 0, 0],
              "rotation": np.array([[1, 0], [0, 1]]),
              "movement": 1
              },
        "G": {"draw": True,
              "pop-push": [0, 0, 0, 0, 0, 0, 0, 0],
              "rotation": np.array([[1, 0], [0, 1]]),
              "movement": 1
              },
        "f": {"draw": False,
              "pop-push": [0, 0, 0, 0, 0, 0, 0, 0],
              "rotation": np.array([[1, 0], [0, 1]]),
              "movement": 1
              },
        "+": {"draw": False,
              "pop-push": [0, 0, 0, 0, 0, 0, 0, 0],
              "rotation": rotation_matrix_2d(fTheta),
              "movement": 0
              },
        "-": {"draw": False,
              "pop-push": [0, 0, 0, 0, 0, 0, 0, 0],
              "rotation": rotation_matrix_2d(fRTheta),
              "movement": 0
              },
        ".": {"draw": False,
              "pop-push": [0, 0, 0, 0, 0, 0, 0, 0],
              "rotation": rotation_matrix_2d(fTheta / 16),
              "movement": 0
              },
        ",": {"draw": False,
              "pop-push": [0, 0, 0, 0, 0, 0, 0, 0],
              "rotation": rotation_matrix_2d(2 * np.pi - (2 * np.pi - fRTheta) / 16),
              "movement": 0
              },
        "|": {"draw": False,
              "pop-push": [0, 0, 0, 0, 0, 0, 0, 0],
              "rotation": np.array([[-1, 0], [0, -1]]),
              "movement": 0
              },
        "[": {"draw": False,
              "pop-push": [0, 0, 1, 1, 0, 0, 0, 0],
              "rotation": np.array([[1, 0], [0, 1]]),
              "movement": 0
              },
        "]": {"draw": False,
              "pop-push": [1, 1, 0, 0, 0, 0, 0, 0],
              "rotation": np.array([[1, 0], [0, 1]]),
              "movement": 0
              },
    }
    return dctOut


def new_rule(sPredecessor, liSuccessors, sName='', bEnabled=True, bProtected=True):
    return {
        "name": sName,
        "enabled": bEnabled,
        "protected": bProtected,
        "predecessor": sPredecessor,
        "successor": liSuccessors
    }


def std_2d_koch(sElaboration, sAxiom=None):
    liOut = []
    if sAxiom is not None:
        liOut.append(new_rule(r"^$", [(1, sAxiom)], "Axiom"))
    liOut.append(new_rule("F", [(1, sElaboration)], "Elaboration"))
    return liOut


dct2dStdInstructions = {
    "F": {"draw": True,
          "pop-push": [0, 0, 0, 0, 0, 0, 0, 0],
          "rotation": np.array([[1, 0], [0, 1]]),
          "movement": 1
          },
    "f": {"draw": False,
          "pop-push": [0, 0, 0, 0, 0, 0, 0, 0],
          "rotation": np.array([[1, 0], [0, 1]]),
          "movement": 1
          },
    "+": {"draw": False,
          "pop-push": [0, 0, 0, 0, 0, 0, 0, 0],
          "rotation": np.array([[0, -1], [1, 0]]),
          "movement": 0
          },
    "-": {"draw": False,
          "pop-push": [0, 0, 0, 0, 0, 0, 0, 0],
          "rotation": np.array([[0, 1], [-1, 0]]),
          "movement": 0
          },
    "|": {"draw": False,
          "pop-push": [0, 0, 0, 0, 0, 0, 0, 0],
          "rotation": np.array([[-1, 0], [0, -1]]),
          "movement": 0
          },
    "[": {"draw": False,
          "pop-push": [0, 0, 1, 1, 0, 0, 0, 0],
          "rotation": np.array([[1, 0], [0, 1]]),
          "movement": 0
          },
    "]": {"draw": False,
          "pop-push": [1, 1, 0, 0, 0, 0, 0, 0],
          "rotation": np.array([[1, 0], [0, 1]]),
          "movement": 0
          },
}

liKochCurveRules = [
    {
        "name": "Axiom",
        "enabled": True,
        "protected": True,
        "predecessor": r"^$",
        "successor": [(1, "F")]
    }, {
        "name": "Elaboration",
        "enabled": True,
        "protected": True,
        "predecessor": r"F",
        "successor": [(1, "F+F-F-FF+F+F-F")]
    },
]

liPlant1Rules = [new_rule("F", [(.2, "FFF"), (1, "FF")], sName="Growing"),
                 new_rule("X", [(1, "F-[[X]+X]+F+[[X]-X]")], sName="Branching")]

LiPlant2Rules = [new_rule("F",
                          [(.2, "FFF"),
                           (.3, "F[X]F"),
                           (.4, "F[+X][-X]F"),
                           (1, "FF")],
                          sName="Growing"),
                 new_rule("X",
                          [(.2, r"F.-[[X],+,+X],+,+F,+,+[X][.-X].-F"),
                           (.4, r"F,-[[X].+.+X].+.+F.+.+[X][,-X],-F"),
                           (.5, r"F,+[[X].-.-X].-.-F.-.-[X][,+X],+F"),
                           (.8, r"F.+[[X],-,-X],-,-F,-,-[X][.+X],+F"),
                           (1, r"F[+X][-X]F[+X][-X]F[X]")],
                          sName="Branching"),
                 ]

liTreeRules = [
    {'name': 'Growing',
     'enabled': True,
     'protected': True,
     'predecessor': 'F',
     'successor': [[0.1, 'F'], [0.2, 'FFF'], [0.3, 'F[X]F'], [0.4, 'F[+X][-X]F'], [1, 'FF']]},
    {'name': 'Left Branch',
     'enabled': True,
     'protected': True,
     'predecessor': '(Z)',
     'successor': [[0.4, 'F+[-\\1][\\1]+F[+\\1][\\1]+F'], [0.8, 'F+[+\\1][\\1]+F[-\\1][\\1]+F'],
                   [0.9, 'F[-\\1][\\1]F[+\\1][\\1]F'], [1, 'F[+\\1][\\1]F[-\\1][\\1]F']]},
    {'name': 'Center Branch',
     'enabled': True,
     'protected': True,
     'predecessor': '(X)',
     'successor': [[0.4, 'FF[,-\\1][\\1]FF[.+\\1][\\1]FF'], [0.8, 'FF[.+\\1][\\1]FF[,-\\1][\\1]FF'],
                   [0.9, 'FF[-\\1][\\1]FF[+\\1][\\1]FF'], [1, 'FF[+\\1][\\1]FF[-\\1][\\1]FF']]},
    {'name': 'Right Branch',
     'enabled': True,
     'protected': True,
     'predecessor': '(C)',
     'successor': [[0.4, 'F,[-\\1][\\1],F[+\\1][\\1],F'], [0.8, 'F,[+\\1][\\1],F[-\\1][\\1],F'],
                   [0.9, 'F[-\\1][\\1]F[+\\1][\\1]F'], [1, 'F[+\\1][\\1]F[-\\1][\\1]F']]}]