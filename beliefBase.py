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

    def getFacts(self):
        return self.facts

    def getRules(self):
        return self.rules
    '''
    Adds a proposition to the belief base in a CNF form. 
    '''
    def tell(self,p, rank=1,t=np.inf):
        prop = p.split()
        print(prop)
        #print(prop)
        if len(prop) <= 2:
            print("here")
            new_fact = self.addFact(prop,rank,t)
            check = self.ask([new_fact], self.facts)
            print(check)
            #print("check", check)
            if check:
                if new_fact not in self.facts:
                    self.facts.append(new_fact)
            else:
                new_fact_neg = self.negateProposition([new_fact])
                self.contract(new_fact_neg)
                check = self.ask([new_fact], self.facts)
                if check:
                    if new_fact not in self.facts:
                        self.facts.append(new_fact)
        else:
            newBelief = BeliefRule(prop,rank=rank,t=t)
            #print(newBelief)
            #print(newBelief)
            #print("new rule", newBelief)
            if "and" in newBelief.getRule():
                beliefs, facts = self.splitRule(newBelief)
                combined = beliefs + facts
                check = self.ask(combined, self.facts)
                if check:
                #print("check", check)
                    for belief in beliefs:
                        self.rules.append(belief)
                    for fact in facts:
                        self.facts.append(fact)
                else:
                    new_facts_neg = self.negateProposition(facts)
                    new_beliefs_neg = self.negateProposition(beliefs)
                    #print(new_facts_neg)
                    #print(new_beliefs_neg)
                    new_neg = new_facts_neg + new_beliefs_neg
                    self.contract(new_neg)
                    check = self.ask(combined)
                    
                    if check:
                        for belief in beliefs:
                            self.rules.append(belief)
                        for fact in facts:
                            self.facts.append(fact)
            else:
                check = self.ask([newBelief], self.facts)
                #print("check",check)
                if check:
                    if not newBelief in self.rules:
                        #print("here")
                        #check = self.ask([newBelief], self.facts)
                        #print("check 2",check)
                        #belief = self.addBelief(newBelief,rank=rank,t=t)
                        self.rules.append(newBelief)
                else:
                    new_belief_neg = self.negateProposition([newBelief])
                    self.contract(new_belief_neg)
                    check = self.ask([newBelief], self.facts)
                    if check:
                        if not newBelief in self.rules:
                            self.rules.append(newBelief)

        self.updateFacts(rank,t)

    def updateFacts(self, rank, t):
        add_rule = []
        for rule in self.rules:
            #print(rule)
            belief_sym = rule.getSymbols()
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
                new_fact = self.addFact(new_syms,rank=rank,t=t)
                if new_fact not in self.facts:
                    self.facts.append(new_fact)
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
                add_rule.append(newBelief)
                #return newBelief
        for rule in add_rule:
            if rule not in self.rules:
                self.rules.append(rule)
                



    def addFact(self,prop,rank,t):
        if len(prop) == 2:
            state = False
            proposition = prop[1]
        else:
            state = True
            proposition = prop[0]
        newBelief = BeliefFact(proposition,state,rank=rank,t=t)
        #if newBelief not in self.facts:
            #if proposition not in self.symbols:
        self.symbols.append(proposition)
            #self.facts.append(newBelief)
        return newBelief

    '''
    def addBelief(self, newBelief, rank,t):
        print("new belief", newBelief)
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
            print("here")
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

    '''
    Splits a rule up such that it comes in CNF-form
    '''
    def splitRule(self,ruleInst):
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
        if and_idx == 0:
            and_idx = rule.index("and")
            if rule[0] == "(":
                and_inner = 1
        left_part = rule[0+and_inner:and_idx]
        right_part = rule[and_idx+1:]
        if and_inner and rule[-1] == ")":
            right_part = right_part[:-1]
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
                    return_rules.append(rule1)
                    #return_rules += [self.addBelief(rule1, rank = ruleInst.rank, t= ruleInst.t)]
            else:
                return_facts.append(self.addFact(rule1.getRule(),rank=ruleInst.rank,t=ruleInst.t))
        if "and" in rule2.getRule():
            new_rules, new_facts = self.splitRule(rule2)
            return_rules += new_rules
            return_facts += new_facts
        else:
            if len(rule2.getRule()) > 2:
                if not rule2 in self.rules:
                    return_rules.append(rule2)
                    #print(self.addBelief(rule2, rank = ruleInst.rank, t= ruleInst.t))
                    #return_rules += [self.addBelief(rule2, rank = ruleInst.rank, t= ruleInst.t)]
            else:
                return_facts.append(self.addFact(rule2.getRule(),rank=ruleInst.rank,t=ruleInst.t))
        return return_rules, return_facts

    '''
    Takes and checks if added clauses is compliant with the current rules and facts. 
    
    '''
    def ask(self, clauses = [], facts = []):
        rules = []
        symbols = []
        '''
        for rule in self.rules:
            rules.append(rule.getRule())
        '''
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
        '''
        print("new run")
        print("rules",rules)
        print("symbols", symbols)
        print("model", model)
        print(rules)
        '''
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
    def contract(self,proposition,rank = 1):
        #print("BEGIN CONTRACT")
        neg_proposition = self.negateProposition(proposition)
        '''
        print("props", len(proposition))
        for prop in proposition:
            print(prop)
        print("neg props", len(neg_proposition))
        
        for prop in neg_proposition:
            print(prop)
        print("end")
        '''
        facts_keep = []
        facts_contract = []
        rules_keep = []
        rules_contract = []
        lower_rank = False
        for fact in self.facts:
            test_facts = facts_keep + [fact]
            keep = self.ask(neg_proposition,facts=test_facts)
            #print(fact, keep)
            #print(fact)
            #print("keep", keep)
            '''
            if not keep and rank >= fact.getRank():
                facts_contract.append(fact)
            else:
                facts_keep.append(fact)
            '''
            if keep:
                facts_keep.append(fact)
            else:
                if rank >= fact.getRank():
                    facts_contract.append(fact)
                else:
                    lower_rank = True
                    break
        if not lower_rank: 
            for rule in self.rules:
                test_rules = rules_keep + [rule] + neg_proposition
                keep = self.ask(test_rules,facts = facts_keep)
                if keep:
                    rules_keep.append(rule)
                else:
                    if rank >= rule.getRank():
                        rules_contract.append(rule)
                    else:
                        lower_rank = True
                        break
        if not lower_rank:
            for fact in facts_contract:
                self.facts.remove(fact)
            for rule in rules_contract:
                self.rules.remove(rule)



    def negateProposition(self, proposition):
        if proposition:
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
            #print("combined",combined)
            newBelief = BeliefRule(combined)
            #print("newbelief",newBelief)
            new_proposition = []
            if "and" in newBelief.getRule():
                new_rules, new_facts = self.splitRule(newBelief)
                '''
                print("new_rules", len(new_rules))
                for rule in new_rules:
                    print(rule)
                '''
                for rule in new_rules:
                    if rule not in new_proposition:
                        new_proposition.append(rule)
                for fact in new_facts:
                    if fact.getState():
                        new_proposition.append(BeliefRule(fact.getName()))
                    else:
                        new_proposition.append(BeliefRule(["not", fact.getName()]))
            else:
                new_proposition.append(newBelief)
            return new_proposition
        else:
            return []


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

    def getRank(self):
        return self.rank
    


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
        #print("start",self.rule)
        self.makeCNF()
        #print("after CNF", self.rule)
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

    def getRank(self):
        return self.rank

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
        #print("After Morgen",self.rule)
        self.handleInconsistent()
        self.handleParAround()
        #print("Aften Incons", self.rule)
        self.andDistribute()
        #print("After and",self.rule)


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
    
    def handleInconsistent(self):
        i = 1
        while i < len(self.rule) - 1:
            if self.rule[i] == "and" and i > 1:
                if self.rule[i-1] == self.rule[i+2] and self.rule[i+1] == "not" and self.rule[i-2] != "not":
                    self.rule = self.rule[0:i-2] + self.rule[i+4:]
                    i = 0
                elif self.rule[i-1] == self.rule[i+1] and self.rule[i-2] == "not":
                    self.rule = self.rule[0:i-3] + self.rule[i+3:]
                    i = 0
            i += 1
        
    def handleParAround(self):
        i = 1
        while i < len(self.rule) - 1:
            if self.rule[i] not in OPERATORS:
                if (self.rule[i-1]=="(" and self.rule[i+1] ==")"):
                    self.rule = self.rule[:i-1] + [self.rule[i]] + self.rule[i+2:]
                    i = 0
                elif (self.rule[i-2]=="(" and self.rule[i+1] ==")"):
                    self.rule = self.rule[:i-2] + self.rule[i-1:i+1] + self.rule[i+2:]
                    i = 0



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
                #print(self.rule)
                #print("rule self", self.rule)
                #print(i)
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
                #print("right_side", right_side)
                new_array = []
                j = par_start
                #print("self.rule[j:i]", self.rule[j:i])
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
                    #print("new_array", new_array)
                    self.rule = self.rule[0:par_start] + new_array[0:-1] + self.rule[i+3+skip_val:]
                else:
                    '''
                    print("part 1", self.rule[0:par_start])
                    print("part 2", self.rule[par_start+1:i+skip_val+1])
                    print("part 3", self.rule[i+1+skip_val:-1])
                    print("skip_val",skip_val)
                    '''
                    self.rule = self.rule[0:par_start] + self.rule[par_start+1:i+skip_val+1] + self.rule[i+skip_val:-1]
                i = 0
            # This checks wheter a or comes before a parenteses and finds the right side that needs to be distributed
            # The left side is not checks since it is dealt with in the first if-statement
            elif self.rule[i] == "or" and self.rule[i+1] == "(":
                #print("rule self", self.rule)
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
                #print("left_side",left_side)
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
            


                            
          
 