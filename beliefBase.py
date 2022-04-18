import numpy as np


class BeliefBase:

    def __init__(self):
        self.facts = [] 
        self.rules = []

    def __str__(self):
        string = "Content: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def tell(self, p,t=np.inf):
        prop = p.split()
        if len(prop) <= 2:
            if len(prop) == 2:
                state = False
                proposition = prop[1]
            else:
                state = True
                proposition = prop[0]
            newBelief = BeliefFact(proposition,state,t)
            self.facts.append(newBelief)
        else:
            newBelief = BeliefRule(prop)
            self.rules.append(newBelief)

    def ask(self):
        return False



class BeliefFact:

    def __init__(self,name,state,t=np.inf):
        self.t = t
        self.name = name
        self.state = state

    def __str__(self):
        return self.name + " " + str(self.state)
    
    def getTime(self):
        return self.t
    

    def getState(self):
        return self.state

    def getName(self):
        return self.name
    


class BeliefRule:

    def __init__(self,rule,t=np.inf):
        self.t = t
        self.rule = rule
        self.splitRule()

    def __str__(self):
        string = str(len(self.rule)) + " "
        for part in self.rule:
            string += str(part) + " "
        return string

    def splitRule(self):
        new_rules = []
        for p in self.rule:
            if p[0] == "(" and len(p) > 1:
                new_rules.append("(")
                new_rules.append(p[1:])
            elif p[-1] == ")" and len(p) > 1:
                new_rules.append(p[:-1])
                new_rules.append(")")
            else:
                new_rules.append(p)
        self.rule = new_rules


KB = BeliefBase()
KB.tell("p")
KB.tell("not q")
KB.tell("(s and t) and r")
KB.tell("( s and t ) and r")
KB.tell("s implies t")
print(KB)


