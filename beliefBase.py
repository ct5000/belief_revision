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

    def tell(self,p, rank=1,t=np.inf):
        prop = p.split()
        if len(prop) <= 2:
            if len(prop) == 2:
                state = False
                proposition = prop[1]
            else:
                state = True
                proposition = prop[0]
            newBelief = BeliefFact(proposition,state,rank=rank,t=t)
            self.facts.append(newBelief)
        else:
            newBelief = BeliefRule(prop,rank=rank,t=t)
            self.rules.append(newBelief)

    def ask(self):
        return False



class BeliefFact:

    def __init__(self,name,state,rank=1,t=np.inf):
        self.t = t
        self.name = name
        self.state = state
        self.rank = rank

    def __str__(self):
        return self.name + " " + str(self.state) + " , Rank: " + str(self.rank)
    
    def getTime(self):
        return self.t
    

    def getState(self):
        return self.state

    def getName(self):
        return self.name
    


class BeliefRule:

    def __init__(self,rule,rank=1,t=np.inf):
        self.t = t
        self.rule = rule
        self.rank = rank
        self.splitRule()
        self.makeCNF()

    def __str__(self):
        string = ""
        for part in self.rule:
            string += str(part) + " "
        return string + ", Rank: " + str(self.rank)

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

    def makeCNF(self):
        


KB = BeliefBase()
KB.tell("p", rank = 2)
KB.tell("not q", rank = 2)
KB.tell("p and q", rank = 1)
KB.tell("(s and t) and r")
KB.tell("( s and t ) and r")
KB.tell("s implies t")
print(KB)


