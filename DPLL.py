rules = ["S or not Q", "Q or T", "not P or Q or not T", "S or P", "not P or T or not Q", "S or R"]
symbols = ["S", "Q", "P", "R", "T"]


def findPure(rules, symbols):
    pureSymbols = []
    for i in symbols:
        notString = "not " + i
        isPure = 1
        for j in rules:
            if notString in j:
                isPure = 0
                break
        if isPure == 1:
            pureSymbols.append(i)
    return pureSymbols

def findUC(rules):
    for j in range(len(rules)):
        if len(rules[j]) == 1:
            notString = "not " + rules[j]
            for i in range(len(rules)):
                if notString in rules[i]:
                    orNotString = " or " + notString
                    notOrString = notString + " or "
                    rules[i] = rules[i].replace(orNotString, "")
                    rules[i] = rules[i].replace(notOrString, "")
                    rules[i] = rules[i].replace(notString, "")
                if rules[j] in rules[i]:
                    rules[i] = rules[j]
    return rules
    
def DPLL(rules, symbols):
    #print(rules)
    pureSymbols = findPure(rules, symbols)
    if len(pureSymbols) > 0:
        for i in pureSymbols:
            for j in range(len(rules)):
                if i in rules[j]:
                    rules[j] = i
        for i in pureSymbols:
            symbols.remove(i)
        return DPLL(rules, symbols)
    findUC(rules)
    if symbols == []:
        return 0
    else:
        rules.append(symbols[0])
        symbols.remove(symbols[0])
        return DPLL(rules, symbols)


#if len(rules[i]) == 1:
#    for j in range(len(rules)):
#        if rules[i] in rules[j] and i != j:
#            if notString in rules[j]:
#                pass
#            else:
#                indexValue = rules[j].index(rules[i])
#                rules[j] = rules[j][indexValue]

clauses = rules.copy()
DPLL(rules, symbols)
print(clauses)
print(rules[0:len(clauses)])