import time
import numpy as np

OPERATORS = ["not", "and", "or", "implies", "equal", "(", ")"]

'''
BeliefBase class
A class that is the overall structure of a belief base. It consists of facts and rules (clauses). 
All in the form of propositional logic. It is possible to add new propositions with that are either facts or facts connected by operators (and, or, implies,
equal), and all propositions can be negated with a not. Informaiton can be contracted with BeliefRule as an input. It is also possible to ask
if a proposition is valid within the belief base 
'''
class BeliefBase:
    '''
    Initialises the BeliefBase with empty facts and rules
    '''
    def __init__(self):
        self.facts = [] 
        self.rules = []

    '''
    String representation of the BeliefBase. It states the content and all the facts and rules
    '''
    def __str__(self):
        string = "Content: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    '''
    Returns the facts of the BeliefBase
    '''
    def getFacts(self):
        return self.facts

    '''
    Returns the facts of the BeliefBase
    '''
    def getRules(self):
        return self.rules


    '''
    Adds a proposition to the belief base such that it become in a CNF form. 
    Inputs:
    p: A proper written proposition only consisting of facts and operators (and, or, implies, equal, not)
    rank: How certain you are of the propositoin
    t: time of the proposition
    '''
    def tell(self,p, rank=1,t=np.inf):
        prop = p.split()
        if len(prop) <= 2:
            new_fact = self.addFact(prop,rank,t)
    
            check = self.ask([new_fact], self.facts)
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
            if "and" in newBelief.getRule():
                beliefs, facts = self.splitRule(newBelief)
                combined = beliefs + facts
                check = self.ask(combined, self.facts)
                if check:
                    for belief in beliefs:
                        self.rules.append(belief)
                    for fact in facts:
                        self.facts.append(fact)
                else:
                    new_facts_neg = self.negateProposition(facts)
                    new_beliefs_neg = self.negateProposition(beliefs)
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
                if check:
                    if not newBelief in self.rules:
                        self.rules.append(newBelief)
                else:
                    new_belief_neg = self.negateProposition([newBelief])
                    self.contract(new_belief_neg)
                    check = self.ask([newBelief], self.facts)
                    if check:
                        if not newBelief in self.rules:
                            self.rules.append(newBelief)

        self.updateFacts(rank,t)

    '''
    Updates the facts of the BeliefBase such that new facts that can be directly derived from the rules are added
    Input:
    rank : How certain you are of the facts
    t : time of the update
    '''
    def updateFacts(self, rank, t):
        add_rule = []
        for rule in self.rules:
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
                for i in range(1,len(new_syms)):
                    p.append("or")
                    p += new_syms[i]
                newBelief = BeliefRule(p,rank=rank,t=t)
                add_rule.append(newBelief)
        for rule in add_rule:
            if rule not in self.rules:
                self.rules.append(rule)
                


    '''
    Creates and returns a fact instance such it adheres to the input proposition
    Inputs:
    prop: Proposition that should be a fact
    rank: How certain you are of the propositoin
    t: time of the proposition 
    '''
    def addFact(self,prop,rank,t):
        if len(prop) == 2:
            state = False
            proposition = prop[1]
        else:
            state = True
            proposition = prop[0]
        newBelief = BeliefFact(proposition,state,rank=rank,t=t)
        return newBelief

    '''
    Splits a rule up such that it comes in CNF-form
    Input:
    ruleInst: The rule that should be splitted up at the "and"s
    '''
    def splitRule(self,ruleInst):
        return_rules = []
        return_facts = []
        and_idx = 0
        rule = ruleInst.getRule()
        for i in range(1,len(rule) - 1):
            if rule[i] == "and":
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
            else:
                return_facts.append(self.addFact(rule2.getRule(),rank=ruleInst.rank,t=ruleInst.t))
        return return_rules, return_facts

    '''
    Takes and checks if added clauses is compliant with the current rules and facts. 
    Inputs:
    clauses: The things that are to be tested if they are logically sound
    facts: The things that are currently true in the model
    '''
    def ask(self, clauses = [], facts = []):
        rules = []
        symbols = []
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
        return self.DPLL(rules,symbols,model)

    '''
    Finds pure symbols in a number of clauses. A pure symbol is a symbol only having only "not"s or having no "not"s at all
    Input:
    rules: rules in a CNF form
    symbols: All the symbols in the rules
    '''
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


    '''
    Finds unit clauses or all clauses that given the model only have one option to become true.
    Inputs:
    rules: rules in CNF form
    model: List of facts that have already been determined to be either true or false
    '''
    def findUC(self,rules,model):
        unit_clause = []
        truth_val = []
        unit_rule = []
        for rule in rules:
            num_p = 0
            contradictions = 0
            sym = ''
            truth_p = False
            for i in range(len(rule)):
                if rule[i] not in OPERATORS:
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
                            truth_p = True
                            sym = rule[i]        
            if num_p - contradictions == 1:
                unit_clause.append(sym)
                truth_val.append(truth_p)
                unit_rule.append(rule)
        return unit_clause, truth_val, unit_rule

    '''
    Implementation of the DPLL-algorithm to determine wether a set of rules are valid within a given model.
    Inputs:
    rules_ins: Rules that needs to be tested whether they are logically sound
    symbols: All the symbols in the given rules
    model: List of facts already determined either true or false
    '''
    def DPLL(self,rules_ins, symbols,model):
        rules = rules_ins.copy()
        undecided = False
        decided_idx = []
        for rule in rules:
            num_p = 0
            contradictions = 0
            cur_undecided = True
            for i in range(len(rule)):
                if not rule[i] in OPERATORS:
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
            if contradictions == num_p:
                return False
        if not undecided:
            return True
        for decided in decided_idx:
            rules.remove(decided)
        pureSymbols, truth_val = self.findPure(rules,symbols)
        if len(pureSymbols) > 0:
            for i in range(len(pureSymbols)):
                if pureSymbols[i] in symbols:
                    symbols.remove(pureSymbols[i])
                if not truth_val[i]:
                    model.append(["not", pureSymbols[i]])
                else:
                    model.append(pureSymbols[i])
            return self.DPLL(rules, symbols,model)
        unit_clauses, truth_val,unit_rule = self.findUC(rules,model)
        if len(unit_clauses) > 0:
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
            return self.DPLL(rules, symbols[1:],model_true) or self.DPLL(rules,symbols[1:],model_false)


    '''
    Contracts a given proposition from the base.
    Inputs:
    proposition: A list proposition of the type either BeliefFact or BeliefRule that wished to be removed
    rank: How certain you are that they should be removed
    '''
    def contract(self,proposition,rank = 1):
        neg_proposition = self.negateProposition(proposition,rank)
        print(neg_proposition[0])
        facts_keep = []
        facts_contract = []
        rules_keep = []
        rules_contract = []
        lower_rank = False
        for fact in self.facts:
            test_facts = facts_keep + [fact]
            keep = self.ask(neg_proposition,facts=test_facts)
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


    '''
    Negates a proposition
    Inputs:
    proposition: A list proposition of the type either BeliefFact or BeliefRule that wished to be removed
    rank: How certain you are that they should be removed
    '''
    def negateProposition(self, proposition,rank = 1):
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
            print(rank)
            newBelief = BeliefRule(combined,rank=rank)
            new_proposition = []
            if "and" in newBelief.getRule():
                new_rules, new_facts = self.splitRule(newBelief)
                for rule in new_rules:
                    if rule not in new_proposition:
                        new_proposition.append(rule)
                for fact in new_facts:
                    if fact.getState():
                        new_proposition.append(BeliefRule(fact.getName(),rank=rank))
                    else:
                        new_proposition.append(BeliefRule(["not", fact.getName()],rank=rank))
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

    '''
    String format of the BeliefFact
    '''
    def __str__(self):
        return self.name + " " + str(self.state) + " , Rank: " + str(self.rank)

    '''
    Checks equality of self and other. To be equal both has to be BeliefFact and have same name and state
    '''
    def __eq__(self,other):
        if isinstance(other,BeliefFact):
            return self.name == other.getName() and self.state == other.getState()
        else:
            return False
    
    '''
    Returns time of fact
    '''
    def getTime(self):
        return self.t
    
    '''
    Returns state of fact
    '''
    def getState(self):
        return self.state

    '''
    Returns name of fact
    '''
    def getName(self):
        return self.name

    '''
    Returns rank of fact
    '''
    def getRank(self):
        return self.rank
    


class BeliefRule:

    '''
    Initialises a rule with rank and time. If no time is given it is set to infinity which is interpreted as always valid.
    The rank says how valid a rule is. The lower the rank the less valid it is assumed.
    Inputs:
    rule: a rule/proposition consisting of facts and valid operators (and, or, implies, equal, not)
    rank: How certain you are of the propositoin
    t: time of the proposition 
    '''
    def __init__(self,rule,rank=1,t=np.inf):
        self.t = t
        self.rule = rule
        self.rank = rank
        self.splitRule()
        self.makeCNF()
        self.checkOuterPar()

    '''
    String format of the rule
    '''
    def __str__(self):
        string = ""
        for part in self.rule:
            string += str(part) + " "
        return string + ", Rank: " + str(self.rank)

    '''
    Checks equality of self and other. To be equal they have to be of type BeliefRule and consists of the exactly same facts with the same states
    '''
    def __eq__(self,other):
        if isinstance(other,BeliefRule):
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
        else:
            return False
        
        
    '''
    Returns all the symbols in the rule
    '''
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


    '''
    Returns the self.rule
    '''
    def getRule(self):
        return self.rule

    '''
    Returns the rank of the rule
    '''
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
        self.handleInconsistent()
        self.handleParAround()
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
    Handle inconsistencies in and'ed facts. E.g. (a and not a) would be removed
    '''
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
    
    '''
    Handle the case where a fact has been sorunded by parenteses. E.g. "(a)" becomes a and "(not a)" becomes "not a"
    '''
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
                    self.rule = self.rule[0:par_start] + self.rule[par_start+1:i+skip_val+1] + self.rule[i+skip_val:-1]
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
