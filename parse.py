import copy  # Includes the deepcopy function for deep copying objects

# Grammar for 0^i 1^i, i >= 1 in Chomsky Normal Form
V1 = ["S", "A", "B", "C"]
Sigma1 = ["0", "1"]
R1 = { 
    "S" : [ ["C", "B"], ["A", "B"] ],
    "C" : [ ["A", "S"]],
    "A" : [["0"]],
    "B" : [["1"]]
}
S1 = "S"
grammar1 = (V1, Sigma1, R1, S1)

# Grammar for balanced parens (excluding epsilon) NOT in Chomsky Normal Form
V2 = ["S"]
Sigma2 = ["(", ")"]
R2 = {"S": [["S", "S"], ["(", "S", ")"], ["(", ")"]]}
S2 = "S"
grammar2 = (V2, Sigma2, R2, S2)

# Grammar from example in Handout 6 
V3 = ["S", "A", "B"]
Sigma3 = ["a", "b"]
R3 = {"S": [["A", "S", "A"], ["a", "B"], ["A"]],
     "A": [["B"], ["S"]],
     "B": [["b"]]}
S3 = "S"
grammar3 = (V3, Sigma3, R3, S3)

# Grammar for binary palindromes
V4 = ["S"]
Sigma4 = ["0", "1"]
R4 = {"S": [["0", "S", "0"],
            ["1", "S", "1"],
            ["0"], ["1"],
            ["0", "0"], ["1", "1"]]}
S4 = "S"
grammar4 = (V4, Sigma4, R4, S4)

def parse(grammar, string):
    """ Takes as input a grammar G = (V, Sigma, R, S) and a string and 
    returns a tuple (Boolean, ParseTree).  If the string is not in the 
    language of the grammar, then this Function returns (False, None).  
    If the string is in the language of the grammar, the function
    returns (True, ParseTree) where ParseTree is a ParseTree for that
    string. A ParseTree is either of the form (Variable, Left, Right) where
    Variable is a variable in the grammar and Left and Right are themselves
    parse trees or (Variable, terminal). """

    cnfGrammar = cnf(grammar)
    V, Sigma, R, S = cnfGrammar
    return cyk(R, S, string, {})

def cyk(rules, variable, string, memo):
    """ Takes grammar rules in Chomsky Normal Form, a variable in that 
    grammar,a string to parse, and a memo dictionary and returns True if the
    string is derivable beginning with that variable and False otherwise. """

    if (variable, string) in memo: return memo[(variable, string)]
    elif len(string) == 1 and [string] in rules[variable]: 
        memo[(variable, string)] = (True, (variable, string))
        return memo[(variable, string)]
    else:
        for i in range(1, len(string)):
            left = string[:i]
            right = string[i:]
            for item in rules[variable]:
                if len(item) == 2:  # rhs of rule is of form XY
                    variable1 = item[0]
                    variable2 = item[1]

                result1 = cyk(rules, variable1, left, memo)

                if result1[0]:
                    result2 = cyk(rules, variable2, right, memo)

                    if result2[0]:
                        memo[(variable, string)] = (True, (variable, result1[1], result2[1]))
                        return memo[(variable, string)]
        memo[(variable, string)] = (False, None)
        return memo[(variable, string)]
    
def removeUnitRules(grammar):
    V, Sigma, R, S = grammar
    newR = {}

    for variable in V:
        reachable = [variable]
        for r in reachable:
            for rule in R[r]:
                if len(rule) == 1 and rule[0] in V:
                    if rule[0] not in reachable:
                        reachable.append(rule[0])
        
        newR[variable] = []
        for r in reachable:
            for rule in R[r]:
                if not (len(rule) == 1 and rule[0] in V):
                    if rule not in newR[variable]:
                        newR[variable].append(copy.deepcopy(rule))
    
    return (copy.deepcopy(V), Sigma, newR, S)

def addVariableToTerminalRules(grammar):
    V, Sigma, R, S = grammar
    V = copy.deepcopy(V)
    R = copy.deepcopy(R)

    for terminal in Sigma:
        variable = "T" + terminal
        V.append(variable)
        R[variable] = [[terminal]]

    return (V, Sigma, R, S)

def replaceTerminalsWithVariables(grammar):
    V, Sigma, R, S = grammar
    R = copy.deepcopy(R)

    for variable in V:
        for rule in R[variable]:
            if len(rule) >= 2:
                for i in range(len(rule)):
                    if rule[i] in Sigma:
                        rule[i] = "T" + rule[i]
    
    return (V, Sigma, R, S)

def makeLongRulesShort(grammar):
    V, Sigma, R, S = grammar
    V = copy.deepcopy(V)
    newR = {variable: [] for variable in V}
    count = 0

    for variable in R:
        for rule in R[variable]:
            if len(rule) <= 2:
                newR[variable].append(copy.deepcopy(rule))
            else:
                c = variable

                for s in rule[:-2]:
                    nextVar = "C" + str(count)
                    count = count + 1
                    V.append(nextVar)
                    newR[nextVar] = []
                    newR[c].append([s, nextVar])
                    c = nextVar

                newR[c].append(rule[-2:])
    
    return (V, Sigma, newR, S)       

def cnf(grammar):
    """ A grammar is a four tuple (V, Sigma, R, S) where V is a a list
    of variables (each is a string of length 1), Sigma is an alphabet,
    R is the rules dictionary with keys from V and values comprising a 
    list of tuples, and S is a string (of length 1) representing the 
    start symbol. Returns a grammar in Chomsky Normal Form. """

    V, Sigma, R, S = grammar
    # Make deep copies of V and R since we'll be modifying these.
    newV = copy.deepcopy(V)
    newR = copy.deepcopy(R)

    newGrammar = (newV, Sigma, newR, S)

    newGrammar = removeUnitRules(newGrammar)
    newGrammar = addVariableToTerminalRules(newGrammar)
    newGrammar = replaceTerminalsWithVariables(newGrammar)
    newGrammar = makeLongRulesShort(newGrammar)

    return newGrammar

# Grammar 1
print("\nGrammar 1:")
print(parse(grammar1, "01"), "True")
print(parse(grammar1, "0011"), "True")
print(parse(grammar1, "000111"), "True")
print(parse(grammar1, "001"), "False")
print(parse(grammar1, "0101"), "False")

# Grammar 2
print("\nGrammar 2:")
print(parse(grammar2, "()"), "True")
print(parse(grammar2, "(())()"), "True")
print(parse(grammar2, "((()))"), "True")
print(parse(grammar2, "(()"), "False")
print(parse(grammar2, ")("), "False")

# Grammar 3
print("\nGrammar 3:")
print(parse(grammar3, "b"), "True")
print(parse(grammar3, "ab"), "True")
print(parse(grammar3, "bbb"), "True")
print(parse(grammar3, "a"), "False")

# Grammar 4
print("\nGrammar 4:")
print(parse(grammar4, "0"), "True")
print(parse(grammar4, "00"), "True")
print(parse(grammar4, "0110"), "True")
print(parse(grammar4, "10101"), "True")
print(parse(grammar4, "1001"), "True")
print(parse(grammar4, "1010"), "False")
print(parse(grammar4, "001"), "False")
print(parse(grammar4, ""), "False")
