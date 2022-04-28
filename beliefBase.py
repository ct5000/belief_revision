import time
import numpy as np

OPERATORS = ["not", "and", "or", "implies", "equal", "(", ")"]

class BeliefBase:

    def __init__(self):
        self.facts = [] 
        self.rules = []
        self.symbols = []


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
            new_fact = self.addFact(prop,rank,t)
            check = self.ask([new_fact], self.facts)
            #print("check", check)
            self.facts.append(new_fact)
        else:
            newBelief = BeliefRule(prop,rank=rank,t=t)
            #print("new rule", newBelief)
            if "and" in newBelief.getRule():
                beliefs, facts = self.splitRule(newBelief)
                check = self.ask(beliefs, self.facts)
                #print("check", check)
                for belief in beliefs:
                    self.rules.append(belief)
            else:
                if not newBelief in self.rules:
                    #print("here")
                    check = self.ask([newBelief], self.facts)
                    #print("check 2",check)
                    belief = self.addBelief(newBelief,rank=rank,t=t)
                    self.rules.append(belief)

                


    def addFact(self,prop,rank,t):
        if len(prop) == 2:
            state = False
            proposition = prop[1]
        else:
            state = True
            proposition = prop[0]
        newBelief = BeliefFact(proposition,state,rank=rank,t=t)
        if newBelief not in self.facts:
            if proposition not in self.symbols:
                self.symbols.append(proposition)
            #self.facts.append(newBelief)
            return newBelief


    def addBelief(self, newBelief, rank,t):
        belief_sym = newBelief.getSymbols()
        idx = []
        for fact in self.facts:
            for i in range(len(belief_sym)):
                if i not in idx and fact.getName() in belief_sym[i]:
                    if fact.getState() and "not" in belief_sym[i]:
                        idx.append(i)
                    elif not fact.getState() and not "not" in belief_sym[i]:
                        idx.append(i)
        if len(belief_sym) - len(idx) == 0:
            pass
        elif len(belief_sym) - len(idx) == 1:
            new_syms = []
            for i in range(0,len(belief_sym)):
                if i not in idx:
                    new_syms = belief_sym[i]
            self.addFact(new_syms,rank=rank,t=t)
        else:
            new_syms = []
            for i in range(0,len(belief_sym)):
                if i not in idx:
                    new_syms.append(belief_sym[i])
            p = new_syms[0]

            if len(new_syms[0]) > 1 and new_syms[0][1] not in self.symbols:
                self.symbols.append(new_syms[1][0])
            elif len(new_syms[0]) == 1 and new_syms[0][0] not in self.symbols:
                self.symbols.append(new_syms[0][0])
            
            for i in range(1,len(new_syms)):
                p.append("or")
                p += new_syms[i]
                if len(new_syms[i]) > 1 and new_syms[i][1] not in self.symbols:
                    self.symbols.append(new_syms[i][1])
                elif len(new_syms[i]) == 1 and new_syms[i][0] not in self.symbols:
                    self.symbols.append(new_syms[i][0])
            newBelief = BeliefRule(p,rank=rank,t=t)
            #self.rules.append(newBelief)
            return newBelief

    '''
    Splits a rule up such that it comes in CNF-form
    '''
    def splitRule(self,ruleInst):
        print("start split")
        return_rules = []
        return_facts = []
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
        and_inner = 0
        print(and_idx)
        if and_idx == 0:
            and_idx = rule.index("and")
            if rule[0] == "(":
                and_inner = 1
        print(rule)
        left_part = rule[0+and_inner:and_idx]
        right_part = rule[and_idx+1:]
        if and_inner and rule[-1] == ")":
            right_part = right_part[:-1]
        print("left", left_part)
        print("right", right_part)
        rule1 = BeliefRule(left_part,rank = ruleInst.rank, t = ruleInst.t)
        rule2 = BeliefRule(right_part,rank = ruleInst.rank, t = ruleInst.t)
        # Checks if the rules are in CNF-form. If not it calls splitRule again on the new rule
        if "and" in rule1.getRule():
            new_rules, new_facts = self.splitRule(rule1)
            return_rules += new_rules
            return_facts += new_facts
        else:
            if len(rule1.getRule()) > 2:
                if not rule1 in self.rules:
                    return_rules += [self.addBelief(rule1, rank = ruleInst.rank, t= ruleInst.t)]
            else:
                return_facts.append(self.addFact(rule1.getRule(),rank=ruleInst.rank,t=ruleInst.t))
        if "and" in rule2.getRule():
            new_rules, new_facts = self.splitRule(rule2)
            return_rules += new_rules
            return_facts += new_facts
        else:
            if len(rule2.getRule()) > 2:
                if not rule2 in self.rules:
                    return_rules += [self.addBelief(rule2, rank = ruleInst.rank, t= ruleInst.t)]
            else:
                return_facts.append(self.addFact(rule2.getRule(),rank=ruleInst.rank,t=ruleInst.t))
        print("Split_rules: ", return_rules)
        return return_rules, return_facts

    '''
    Takes and checks if added clauses is compliant with the current rules and facts. 
    
    '''
    def ask(self, clauses = [], facts = []):
        rules = []
        symbols = []
        for rule in self.rules:
            rules.append(rule.getRule())
        model = []
        model_sym = []
        for fact in facts:
            if not fact.getState():
                model.append(["not", fact.getName()])
                model_sym.append(fact.getName())
            else:
                model.append(fact.getName())
                model_sym.append(fact.getName())
        for clause in clauses:
            if isinstance(clause, BeliefRule):
                rules.append(clause.getRule())
                for part in clause.getRule():
                    if part not in OPERATORS and part not in symbols and part not in model_sym:
                        symbols.append(part)
            elif isinstance(clause, BeliefFact):
                part = clause.getName()
                if not clause.getState():
                    rules.append(["not",part])
                else:
                    rules.append(part)
                if part not in symbols and part not in model_sym:
                    symbols.append(part)
            
        #print(rules)
        return self.DPLL(rules,symbols,model)


    def findPure(self,rules, symbols):
        pureSymbols = []
        truth_val = []
        for sym in symbols:
            nots = 0
            trues = 0
            for rule in rules:
                for i in range(len(rule)):
                    if sym in rule[i] and i > 0 and rule[i-1] == "not":
                        nots += 1
                    elif sym in rule[i] and ((i > 0 and rule[i-1] != "not") or i == 0):
                        trues += 1
            if not (nots >= 1 and trues >= 1):
                pureSymbols.append(sym)
                if nots:
                    truth_val.append(False)
                else:
                    truth_val.append(True)
        return pureSymbols, truth_val

    def findUC(self,rules,model):
        unit_clause = []
        truth_val = []
        unit_rule = []
        for rule in rules:
            #print(rule)
            num_p = 0
            contradictions = 0
            sym = ''
            truth_p = False
            for i in range(len(rule)):
                if rule[i] not in OPERATORS:
                    #print("Cur rule", rule[i])
                    num_p +=1
                    in_contradiction = False
                    for fact in model:
                        
                        if "not" in fact and fact[1] == rule[i] and not (i > 0 and rule[i-1] == "not"):
                            contradictions += 1
                            in_contradiction = True
                            continue
                        elif fact[0] == rule[i] and i > 0 and rule[i-1] == "not":
                            contradictions += 1
                            in_contradiction = True
                            continue
                    if not in_contradiction:
                        if i > 0 and rule[i-1] == "not":
                            truth_p = False
                            sym = rule[i]
                        else:
                            #print("Alternate way",fact)
                            truth_p = True
                            sym = rule[i] 
                    #print("num_p", num_p, "contradiction",contradictions)         
            if num_p - contradictions == 1:
                #print("Contraditions", contradictions, "num_p", num_p)
                #print("Adds UC", sym)
                unit_clause.append(sym)
                truth_val.append(truth_p)
                unit_rule.append(rule)
        return unit_clause, truth_val, unit_rule

    def DPLL(self,rules_ins, symbols,model):
        rules = rules_ins.copy()
        undecided = False
        decided_idx = []
        #print("new run")
        #print("rules",rules)
        #print("symbols", symbols)
        #print("model", model)
        #print(rules)
        for rule in rules:
            #print("rule",rule)
            num_p = 0
            contradictions = 0
            cur_undecided = True
            for i in range(len(rule)):
                if not rule[i] in OPERATORS:
                    #print("here")
                    num_p += 1
                    for fact in model:
                        if "not" in fact and fact[1] == rule[i] and not (i > 0 and rule[i-1] == "not"):
                            contradictions += 1
                        elif fact[0] == rule[i] and i > 0 and rule[i-1] == "not":
                            contradictions += 1
                        elif "not" in fact and fact[1] == rule[i] and i > 0 and rule[i-1] == "not":
                            cur_undecided = False
                        elif fact[0] == rule[i]:
                            cur_undecided = False
            if cur_undecided:
                undecided = True
            else: 
                decided_idx.append(rule)
            #print("contra", contradictions)
            #print("num_p", num_p)
            if contradictions == num_p:
                return False
        if not undecided:
            return True
        for decided in decided_idx:
            rules.remove(decided)
        pureSymbols, truth_val = self.findPure(rules,symbols)
        #print("pure", pureSymbols)
        if len(pureSymbols) > 0:
            '''
            for sym in pureSymbols:
                j = 0
                while j < len(rules):
                    if sym in rules[j]:
                        rules.pop(j)
                        j -= 1
                    j += 1
            '''
            for i in range(len(pureSymbols)):
                if pureSymbols[i] in symbols:
                    symbols.remove(pureSymbols[i])
                if not truth_val[i]:
                    model.append(["not", pureSymbols[i]])
                else:
                    model.append(pureSymbols[i])
            return self.DPLL(rules, symbols,model)
        unit_clauses, truth_val,unit_rule = self.findUC(rules,model)
        #print("UC", unit_clauses)
        #print(truth_val)
        if len(unit_clauses) > 0:
            # Redo remove part
            '''
            for rule in unit_rule:
                rules.remove(rule)
            '''
            for i in range(len(unit_clauses)):
                if unit_clauses[i] in symbols:
                    symbols.remove(unit_clauses[i])
                if not truth_val[i]:
                    model.append(["not", unit_clauses[i]])
                else:
                    model.append(unit_clauses[i])
            return self.DPLL(rules, symbols,model)
        if symbols == []:
            return 0
        else:
            model_false = model.copy()
            model_true = model.copy()
            p_sym = symbols[0]
            model_true.append(p_sym)
            model_false.append(["not",p_sym])
            #print("P_sym",p_sym)
            return self.DPLL(rules, symbols[1:],model_true) or self.DPLL(rules,symbols[1:],model_false)


    '''
    Input to the function is a list of beliefs
    '''
    def contract(self,proposition):
        neg_proposition = self.negateProposition(proposition)
        extended_beliefs = self.rules + neg_proposition
        conformity = self.ask(extended_beliefs,facts = self.facts)
        while not conformity:
            print("Was here")
            break

    def negateProposition(self, proposition):
        combined = ["not", "("]
        for prop in proposition:
            combined.append("(")
            if isinstance(prop, BeliefFact):
                part = prop.getName()
                if not prop.getState():
                    combined += ["not",part]
                else:
                    combined.append(part)
            elif isinstance(prop, BeliefRule):
                for part in prop.getRule():
                    combined.append(part)
            combined.append(")")
            combined.append("and")
        combined.pop()
        combined.append(")")
        print("combined",combined)
        newBelief = BeliefRule(combined)
        new_proposition = []
        print(newBelief)
        if "and" in newBelief.getRule():
            new_rules, new_facts = self.splitRule(newBelief)
            for rule in new_rules:
                new_proposition.append(rule)
            for fact in new_facts:
                if fact.getState():
                    new_proposition.append(BeliefRule(fact.getName()))
                else:
                    new_proposition.append(BeliefRule(["not", fact.getName()]))
        else:
            new_proposition.append(newBelief)
        return new_proposition


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

    def __eq__(self,other):
        return self.name == other.getName() and self.state == other.getState()
    
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
        other_symbols = other.getSymbols()
        self_symbols = self.getSymbols()
        if len(other_symbols) != len(self_symbols):
            return False
        one_way = True
        for sym in other_symbols:
            if not sym in self_symbols:
                one_way = False
        other_way = True
        for sym in self_symbols:
            if not sym in other_symbols:
                other_way = False
        return one_way and other_way
        
        

    def getSymbols(self):
        symbols = []
        for i in range(len(self.rule)):
            if self.rule[i] not in OPERATORS and self.rule[i] not in symbols:
                sym_ins = []
                if i > 0 and self.rule[i-1] == "not":
                    sym_ins.append("not")
                sym_ins.append(self.rule[i])
                symbols.append(sym_ins)
        return symbols



    def getRule(self):
        return self.rule

    '''
    Split the rule such the parenteses is not seen as a part of a proposition
    '''
    def splitRule(self):
        i = 0
        while len(self.rule) > i:
            if self.rule[i][0] == "(" and len(self.rule[i]) > 1:
                self.rule[i] = self.rule[i][1:]
                self.rule.insert(i, "(")
                #i -= 1
            elif self.rule[i][-1] == ")" and len(self.rule[i]) > 1:
                self.rule[i] = self.rule[i][:-1]
                self.rule.insert(i+1,")")
                i -= 1
            i += 1
            

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
                #not_ar = 0
                
                if self.rule[par_start] == "(" and left_skip:
                    par_start += 1
                not_prop = 0
                if self.rule[par_start] != "not":
                    new_array.append("not")
                else:
                    par_start += 1
                    not_prop = 1
                new_array += self.rule[par_start:i]
                new_array.append("or")
                if self.rule[par_end-1] == ")" and left_skip:
                    par_end -= 1
                new_array+= self.rule[i+1:par_end]
                self.rule = self.rule[0:par_start - not_prop] + new_array + self.rule[par_end:len(self.rule)]
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
                if "and" in self.rule[j:i]:
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
                else:
                    self.rule = self.rule[0:par_start] + self.rule[par_start+1:i+skip_val] + self.rule[i+1+skip_val:]
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
                if "and" in self.rule[j:par_end]:
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
                else:
                    self.rule = self.rule[0:i+skip_val] + self.rule[j:par_end] + self.rule[par_end+1:]
                i = 0
            i += 1

    '''
    Checks if there are outer parentesis that incloses the full rule and if so removes them
    '''
    def checkOuterPar(self):
        not_outer = False
        while not not_outer:
            #if self.rule[0] == "(":
            i = 1
            left_par = 1
            right_par = 0
            while left_par != right_par and i < len(self.rule):
                if self.rule[i] == "(":
                    left_par += 1
                elif self.rule[i] == ")":
                    right_par += 1
                i += 1
            if i == len(self.rule) and self.rule[0] == "(":
                self.rule = self.rule[1:-1]
            else:
                not_outer = True
            


                            
                            

               
                    
    

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

#KB.tell("(a or b) and (c or d)")
#KB.tell("john or pip")
#KB.tell("(john implies pip) or (bob and claus)")
#KB.tell("(not A or (C or E)) and ((not C or not E) or A)")
#KB.tell("a and b")
#KB.tell("(not p) equal s")
#KB.tell("r equal p")
#KB.tell("r implies s")
#KB.tell("r")
#KB.tell("(r implies p) and (r implies s)")
#KB.tell("a")
#KB.tell("not a")
#KB.tell("not b or c")
#KB.tell("b")
#KB.tell("not a or not b or c or d")
#KB.tell("(not a or c) and (not b and c)")
#KB.tell("a equal b")
#KB.tell("a implies (c and d)")

#KB.tell("c")
#KB.tell("e")
#KB.tell("not b")

#print(KB.ask([["not", "a", "or", "c", "or", "e"], ["not", "c", "or", "a"],["not", "e", "or", "a"],["not","e","or","d"],["not","b","or","not","f","or","c"],
           # ["not","e","or","c"],["not","c", "or","f"],["not","c","or","b"]]))
#KB.tell("a or not c")
#KB.tell("not b or not c")
#KB.tell("p or s")
#KB.tell("r or not s")
#KB.tell("a equal b")
#KB.tell("not a equal b")

#print(KB.ask([["a", "or", "b"],["not","a","or","not","b"],["a","or","not","b"],["not","a","or","b"]]))
KB.tell("a")
fact = BeliefFact("a",True)
KB.contract([fact])

'''
belief = BeliefRule(["a", "or", "b"])
belief2 = BeliefFact("a",False)
print("here")
new_beliefs = KB.negateProposition([belief,belief2])
print(new_beliefs)
for new_belief in new_beliefs:
    print(new_belief)
'''
print(KB)




