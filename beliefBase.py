import numpy as np

OPERATORS = ["not", "and", "or", "implies", "equal", "(", ")"]

class BeliefBase:

    def __init__(self):
        self.facts = [] 
        self.rules = []

    def __str__(self):
        string = "Content: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    '''
    Adds a proposition to the belief base in a CNF form. 
    '''
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
            print(newBelief.getRule())
            if "and" in newBelief.getRule():
                self.splitRule(newBelief)
            else:
                self.rules.append(newBelief)
            
    '''
    Splits a rule up such that it comes in CNF-form
    '''
    def splitRule(self,ruleInst):
        and_idx = 0
        rule = ruleInst.getRule()

        for i in range(1,len(rule) - 1):
            if rule[i] == "and":
                #equal_right = False
                right_par = 0
                left_par = 0
                j = i - 1
                while j >= 0:
                    if rule[j] == ")":
                        right_par += 1
                    elif rule[j] == "(":
                        left_par += 1
                    j -= 1
                if right_par == left_par:
                    and_idx = i
        left_part = rule[0:and_idx]
        right_part = rule[and_idx+1:]
        rule1 = BeliefRule(left_part,rank = ruleInst.rank, t = ruleInst.t)
        rule2 = BeliefRule(right_part,rank = ruleInst.rank, t = ruleInst.t)
        # Checks if the rules are in CNF-form. If not it calls splitRule again on the new rule
        if "and" in rule1.getRule():
            self.splitRule(rule1)
        else:
            if len(rule1.getRule()) > 2:
                self.rules.append(rule1)
            else:
                if len(rule1.getRule()) == 2:
                    state = False
                    proposition = rule1.getRule()[1]
                else:
                    state = True
                    proposition = rule1.getRule()[0]
                newBelief = BeliefFact(proposition,state,rank=ruleInst.rank,t = ruleInst.t)
                self.facts.append(newBelief)
        if "and" in rule2.getRule():
            self.splitRule(rule2)
        else:
            if len(rule2.getRule()) > 2:
                self.rules.append(rule2)
            else:
                if len(rule2.getRule()) == 2:
                    state = False
                    proposition = rule2.getRule()[1]
                else:
                    state = True
                    proposition = rule2.getRule()[0]
                newBelief = BeliefFact(proposition,state,rank=ruleInst.rank,t = ruleInst.t)
                self.facts.append(newBelief)

    def ask(self):
        return False



class BeliefFact:
    '''
    Initialises a proposition with rank and time. If no time is given it is set to infinity which is interpreted as always valid.
    The rank says how valid a rule is. The lower the rank the less valid it is assumed
    '''
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

    '''
    Initialises a rule with rank and time. If no time is given it is set to infinity which is interpreted as always valid.
    The rank says how valid a rule is. The lower the rank the less valid it is assumed
    '''
    def __init__(self,rule,rank=1,t=np.inf):
        self.t = t
        self.rule = rule
        self.rank = rank
        self.splitRule()
        self.makeCNF()
        self.checkOuterPar()

    def __str__(self):
        string = ""
        for part in self.rule:
            string += str(part) + " "
        return string + ", Rank: " + str(self.rank)

    def __eq__(self,other):
        pass



    def getRule(self):
        return self.rule

    '''
    Split the rule such the parenteses is not seen as a part of a proposition
    '''
    def splitRule(self):
        new_rules = []
        for p in self.rule:
            if p[0] == "(" and p[-1] == ")":
                new_rules.append("(")
                new_rules.append(p[1:-1])
                new_rules.append(")")
            elif p[0] == "(" and len(p) > 1:
                new_rules.append("(")
                new_rules.append(p[1:])
            elif p[-1] == ")" and len(p) > 1:
                new_rules.append(p[:-1])
                new_rules.append(")")
            else:
                new_rules.append(p)
        self.rule = new_rules

    '''
    Converts the rule to CNF form
    '''
    def makeCNF(self):
        self.handleEqual()
        self.handleImplies()
        self.DeMorgan()
        self.andDistribute()

    '''
    Converts the equals to the two way implies form
    '''
    def handleEqual(self):
        i = 1
        while i < len(self.rule)-1:
            if self.rule[i] == "equal":
                left_side = self.rule[0:i]
                right_side = self.rule[i+1:len(self.rule)]
                self.rule = []
                self.rule.append("(")
                self.rule += left_side
                self.rule.append("implies")
                self.rule += right_side
                self.rule.append(")")
                self.rule.append("and")
                self.rule.append("(")
                self.rule += right_side
                self.rule.append("implies")
                self.rule += left_side
                self.rule.append(")")
                i = 1
            i += 1


    '''
    Converts all the implies from form "x implies y" to "not x or y"
    '''     
    def handleImplies(self):
        i = 1
        while i < (len(self.rule)-1):
            if self.rule[i] == "implies":
                left_skip = False
                right_pars = 0
                left_pars = 0
                par_start = i - 1
                # Finds the parenteses left of the implies
                while par_start >= 0 and left_pars <= right_pars:
                    if self.rule[par_start] == ")":
                        right_pars += 1
                    elif self.rule[par_start] == "(":
                        left_pars += 1
                    par_start -= 1
                par_start += 1
                if left_pars > right_pars:
                    left_skip = True
                par_end = i + 1
                left_pars = 0
                right_pars = 0
                # Finds the parenteses right of the implies
                while par_end < len(self.rule) and left_pars >= right_pars:
                    if self.rule[par_end] == ")":
                        right_pars += 1
                    elif self.rule[par_end] == "(":
                        left_pars += 1
                    par_end += 1
                new_array = []
                new_array.append("not")
                if self.rule[par_start] == "(" and left_skip:
                    par_start += 1
                new_array += self.rule[par_start:i]
                new_array.append("or")
                if self.rule[par_end-1] == ")" and left_skip:
                    par_end -= 1
                new_array+= self.rule[i+1:par_end]
                self.rule = self.rule[0:par_start] + new_array + self.rule[par_end:len(self.rule)]
                i = 0
            i += 1
    
    '''
    Implements the DeMorgan rule 
    '''      
    def DeMorgan(self):
        i = 0
        while i < len(self.rule) - 1:
            if self.rule[i] == "not" and self.rule[i+1] == "(":
                left_pars = 1
                right_pars = 0
                j = i + 2
                while left_pars != right_pars:
                    if self.rule[j] == "(":
                        left_pars += 1
                    elif self.rule[j] == ")":
                        right_pars += 1
                    if self.rule[j] not in OPERATORS:
                        if self.rule[j-1] == "not":
                            del self.rule[j-1]
                            j -= 1
                        else:
                            self.rule.insert(j, "not")
                            j += 1
                    if self.rule[j] == "or":
                        self.rule[j] = "and"
                    elif self.rule[j] == "and":
                        self.rule[j] = "or"
                            
                    j += 1
                del self.rule[i]
                i -= 1
            i += 1
    '''
    Used to distribute the ands out such that we do not have or'ed and-statements
    '''
    def andDistribute(self):
        i = 1
        while i < len(self.rule) - 1:
            # This part checks wheter an or comes after an parenteses. 
            # It isolates both the right side that has to be distributed
            if self.rule[i] == ")" and self.rule[i+1] == "or":
                par_start = i - 1
                while self.rule[par_start] != "(":
                    par_start -= 1
                right_side = []
                skip_val = 0
                if self.rule[i+2] == "not":
                    if self.rule[i+3] == "(":
                        pass
                    else:
                        right_side += self.rule[i+2:i+4]
                        skip_val += 1
                elif self.rule[i+2] == "(":
                    par_end = i + 3
                    while self.rule[par_end] != ")":
                        par_end += 1
                    right_side += self.rule[i+2:par_end+1]
                    skip_val = par_end - (i + 2)
                else:
                    right_side.append(self.rule[i+2])
                new_array = []
                j = par_start
                while j < i:
                    if self.rule[j] not in OPERATORS:
                        new_array.append("(")
                        new_array.append(self.rule[j])
                        new_array.append("or")
                        new_array += right_side
                        new_array.append(")")
                        new_array.append("and")
                    elif self.rule[j] == "not":
                        new_array.append("(")
                        new_array += self.rule[j:j+2]
                        new_array.append("or")
                        new_array += right_side
                        new_array.append(")")
                        new_array.append("and")
                        j += 1
                    j += 1
                self.rule = self.rule[0:par_start] + new_array[0:-1] + self.rule[i+3+skip_val:]
                #i += skip_val
                #i -= skip_val
                i = 0
            # This checks wheter a or comes before a parenteses and finds the right side that needs to be distributed
            # The left side is not checks since it is dealt with in the first if-statement
            elif self.rule[i] == "or" and self.rule[i+1] == "(":
                par_end = i + 2
                while self.rule[par_end] != ")":
                    par_end += 1
                left_side = []
                skip_val = 0
                if self.rule[i-2] == "not":
                    skip_val += 1
                    left_side += self.rule[i-2:i]
                else:
                    left_side.append(self.rule[i-1])
                new_array = []
                j = i + 2
                while j < par_end:
                    if self.rule[j] not in OPERATORS:
                        new_array.append("(")
                        new_array += left_side
                        new_array.append("or")
                        new_array.append(self.rule[j])
                        new_array.append(")")
                        new_array.append("and")
                    if self.rule[j] == "not":
                        new_array.append("(")
                        new_array += left_side
                        new_array.append("or")
                        new_array += self.rule[j:j+2]
                        new_array.append(")")
                        new_array.append("and")
                        j += 1
                    j += 1
                self.rule = self.rule[0:i-(1 + skip_val)] + new_array[0:-1] + self.rule[par_end+1:]
                #i += skip_val
                i = 0
            i += 1

    '''
    Checks if there are outer parentesis that incloses the full rule and if so removes them
    '''
    def checkOuterPar(self):
        if self.rule[0] == "(":
            i = 1
            left_par = 1
            right_par = 0
            while left_par != right_par:
                if self.rule[i] == "(":
                    left_par += 1
                elif self.rule[i] == ")":
                    right_par += 1
                i += 1
            if i == len(self.rule):
                self.rule = self.rule[1:-1]


                            
                            

               
                    
    

KB = BeliefBase()
'''
KB.tell("p", rank = 2)
KB.tell("not q", rank = 2)
KB.tell("p and q", rank = 1)
KB.tell("(s and t) and r")
KB.tell("( s and t ) and r")
KB.tell("s implies t")
'''
#KB.tell("r equal (p or s)")
#KB.tell("(t and s) or (p and q and r)")
#KB.tell("(p and q and w and t and v) or (r and s and z and abc and gh)")
#KB.tell("(john and bent) or (pip and sul)")
#KB.tell("(a or c) and (b and c)")
#KB.tell("(a or b)")
#KB.tell("john or pip")
#KB.tell("(john implies pip) or (bob and claus)")
print(KB)



