import random
import re
from functools import partial
from tqdm import tqdm

from junkdrawer import generator_looper


def lindenate(liRules, sInput="", lIterations=1):
    """This function iteratively processes a set of find-and-replace rules, liRules, on a given string, sInput.
        By default, it only goes through a single iteration, and processes the rules against an empty string.
            In a traditional Lindenmayer system, rules replace a single character (called the predecessor) with a string
        (called the successor).  In stochastic Lindenmayer systems, this successor can be chosen at random from a
        number of options. This function is modeled after a stochastic L-system, but with a few modifications;
            In this function, predecessors and successors are defined using Regex, which allows for multi-character and
        pattern-based matching, as well as smart replacement via capture groups. This also opens the door for characters
        or character sets which would match to more than one rule, meaning that, unlike L-systems, the order of rule
        application here matters.  With ordered rule application comes the possibility of a later rule affecting the
        successors of the previous rules inside of a single iteration; what I refer as a rule being "protected".
        Inputs:
            liRules:
                list of rule dictionaries. Each dctRule must have the following pairs:
                        "name":
                            string. Becomes description for progress bar
                        "enabled":
                            boolean. Whether this rule should be applied, or skipped.
                        "protected":
                            boolean. Whether the successor(s) introduced by this rule can be modified by rules
                            later in the list.
                        "predecessor":
                            string (regex). The regex expression searched for in the find-and-replace process
                        "successor":
                            list of tuples; [(number, string (regex)),(number, string (regex))]
                            The successor is stochastically determined via random.random.
                            The first element is a number between 0 and 1 representing the max random.random
                            value for which its corresponding successor, the second element, will be chosen.
                            If the random value is above all options, the successor is an empty string.
                            The tuples MUST be sorted in ascending order by their first element.
            sInput:
                String. The text to be mutated by the function
            lIterations:
                Number. The number of times to process the string through the rules.
        Output:
            String. The input text, as transformed by (lMaxGen - lCurrGen) iterations through liRules.
    """
    # If we're out of iterations to perform...
    if lIterations <= 0:
        # ...return the input
        return sInput
    sOut = sInput
    # This protection string is a string of equal length to the output.
    # The character sOut[x] is protected if sProtect[x] == "1"
    sProtect = "0" * len(sInput)
    # Loop through each rule
    for dctRule in liRules:
        # if the rule is not enabled...
        if not dctRule["enabled"]:
            # ...skip it
            continue
        # sTempProtect serves the purpose of sProtect within each rule, as a rule is never allowed to overwrite itself
        sTempProtect = sProtect
        objRgx = re.compile(dctRule["predecessor"])
        liReplacements = dctRule["successor"]
        itMatches = objRgx.finditer(sOut)
        lOffset = 0
        # Loop through all matches
        for objMatch in tqdm(itMatches, desc=dctRule["name"]):
            lStart = objMatch.span()[0] + lOffset
            lEnd = objMatch.span()[1] + lOffset
            sShieldCheck = sTempProtect[lStart:lEnd]
            # Check whether the match overlaps any protected substrings
            if "1" in sShieldCheck:
                # If there are some zeros in here, this match could be eclipsing another match.
                if "0" not in sShieldCheck:
                    continue
                # Find the next match.  This will either be the eclipsed match, or simply the next math in the iterable
                objMatch = objRgx.search(sOut[lStart+1:])
                # If there aren't any matches left at all in the string, we're done.
                if objMatch is None:
                    break
                # Adjust lStart and lEnd to account for how we sliced the string in line 111
                lStart += objMatch.span()[0] + 1
                lEnd += objMatch.span()[0] + 1
                # sPredecessor = objMatch.group(0)
            # Choose a successor
            fRand = random.random()
            lChoice = -1
            for i in range(len(liReplacements)):
                if fRand > liReplacements[i][0]:
                    continue
                else:
                    lChoice = i
                    break
            if lChoice == -1:
                sSuccessor = ''
            else:
                # The rest of the string is used here in case there are lookahead groups that are referenced by the
                # successor pattern (since they will not be captured in objMatch.group(0))
                sSuccessor = liReplacements[lChoice][1]
                # Manually swap out backreferences, checking for all notation types: \1, \g<1>, \g<name>
                # Step backward so that \20 gets replaced by group 20, not group 2
                for i in reversed(range(len(objMatch.groups())+1)):
                    sSuccessor = sSuccessor.replace("\\" + str(i), objMatch.group(i))
                    sSuccessor = sSuccessor.replace(r"\g<" + str(i) + ">", objMatch.group(i))
                for sGroupName in objMatch.groupdict():
                    sSuccessor = sSuccessor.replace(r"\g<" + sGroupName + ">", objMatch.group(sGroupName))
            # Stitch things back together
            sOut = sOut[:lStart] + sSuccessor + sOut[lEnd:]
            # Protect the affected substring.
            sShield = "1" * len(sSuccessor)
            sTempProtect = sTempProtect[:lStart] + sShield + sTempProtect[lEnd:]
            if dctRule["protected"]:
                sProtect = sProtect[:lStart] + sShield + sProtect[lEnd:]
            else:
                sProtect = sProtect[:lStart] + "0"*len(sShield) + sProtect[lEnd:]
            # The span of the remaining regex matches has already been set, so we need to accommodate for changing
            # string lengths with the lOffset
            lOffset += len(sSuccessor) - (lEnd - lStart)
    # If we're just spinning our wheels and not transforming the string...
    if sInput == sOut:
        # ...there's no need to run through future iterations.
        return sOut
    lIterations -= 1
    sOut = lindenate(liRules, sOut, lIterations)
    return sOut


def lindenator(liRules, sInput="", lIterations=1, lMaxReturns=None):
    """returns a generator object that returns lIterations additional iteration(s) (by default, 1) of lindenate from its
        previous return. First return is simply sInput. if specified, exhausts after lMaxReturns.
    """
    # Are infinite loops better than recursion? I think so
    # yield sInput
    # yield from lindenator(liRules, lindenate(liRules, sInput, lIterations), lIterations)
    if lMaxReturns is None:
        while True:
            yield sInput
            sInput = lindenate(liRules, sInput, lIterations)
    elif lMaxReturns > 0:
        for _i in range(lMaxReturns):
            yield sInput
            sInput = lindenate(liRules, sInput, lIterations)


def main():
    liRules = [
        {
            "name": "Rule1",
            "enabled": False,
            "protected": False,
            "predecessor": r"test",
            "successor": [(1, r"ans")]
        }, {
            "name": "Rule2",
            "enabled": True,
            "protected": True,
            "predecessor": r"1",
            "successor": [(1, r"3")]
        }, {
            "name": "Rule3",
            "enabled": True,
            "protected": True,
            "predecessor": r"(2(?P<middleLetter>[a-z])2)",
            "successor": [(1, r"Z\g<middleLetter>Z")]
        }, {
            "name": "Rule4",
            "enabled": True,
            "protected": True,
            "predecessor": r"[a-zA-Z][\d]",
            "successor": [(.5, r"7"), (1, r"9")]
        },
    ]
    liOverlapRules = [
        {
            "name": "Axiom",
            "enabled": True,
            "protected": True,
            "predecessor": r"^$",
            "successor": [(1, "ABBAAAA")]
        }, {
            "name": "Rule One",
            "enabled": True,
            "protected": True,
            "predecessor": r"(.)(?=AAA)",
            "successor": [(1, "Z")]
        }, {
            "name": "Rule Two",
            "enabled": True,
            "protected": True,
            "predecessor": r"AA",
            "successor": [(1, "CC")]
        }, {
            "name": "Rule Three",
            "enabled": True,
            "protected": True,
            "predecessor": r"A",
            "successor": [(1, "B")]
        }, {
            "name": "Rule Four",
            "enabled": True,
            "protected": True,
            "predecessor": r"B",
            "successor": [(1, "AAAA")]
        },

    ]
    """
    print(lindenate(liRules, "ttest8est82a22b2", 1))
    print(lindenate(liRules, "ttest8est82a22b2", 2))
    print(lindenate(liOverlapRules, "BBAAAA"))
    print(lindenate(liOverlapRules, lIterations=8))
    """
    sInput = input("test?")
    objLReturn = generator_looper(partial(lindenator, liOverlapRules, sInput, lMaxReturns=10))
    bKeepGoing = True
    while bKeepGoing:
        print(next(objLReturn))
        sInput = input("type 'end' to end")
        if sInput == "end":
            bKeepGoing = False
    print("ended")


if __name__ == "__main__":
    main()
