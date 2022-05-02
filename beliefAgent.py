import numpy as np
import beliefBase

class BeliefAgent:

    def __init__(self):
        self.KB = beliefBase.BeliefBase()
        self.t = 0

    def printBase(self):
        print(self.KB)
        
    def addProposition(self):
        print("Write the proposition you want to add")
        proposition = input()
        print("How certain are you (1-5)?")
        rank = int(input())
        self.KB.tell(proposition, rank=rank)
        print("Proposition has been added")

    def askValid(self):
        print("Write proposition you want to get validity of")
        proposition_input = input()
        proposition_split = proposition_input.split()
        proposition = [beliefBase.BeliefRule(proposition_split)]
        if "and" in proposition[0].getRule():
            rules, facts = self.KB.splitRule(proposition[0])
            proposition = []
            for rule in rules:
                proposition.append(rule)
            for fact in facts:
                if fact.getState():
                    new_rule = beliefBase.BeliefRule(fact.getName())
                else:
                    new_rule = beliefBase.BeliefRule("not " + fact.getName())
                proposition.append(new_rule)

        check = self.KB.ask(proposition)
        if check:
            print("The proposition is valid in the belief base")
        else:
            print("The proposition is not valid in the belief base")

    def retractInformation(self):
        print("Write proposition you want to retract")
        proposition_input = input()
        print("How certain are you (1-5)?")
        rank = int(input())
        proposition_split = proposition_input.split()
        proposition = [beliefBase.BeliefRule(proposition_split,rank=rank)]
        if "and" in proposition[0].getRule():
            rules, facts = self.KB.splitRule(proposition[0])
            proposition = []
            for rule in rules:
                proposition.append(rule)
            for fact in facts:
                if fact.getState():
                    new_rule = beliefBase.BeliefRule(fact.getName(),rank=rank)
                else:
                    new_rule = beliefBase.BeliefRule("not " + fact.getName(),rank=rank)
                proposition.append(new_rule)

        self.KB.contract(proposition)





if __name__ == '__main__':
    agent = BeliefAgent()
    going = True
    print("Welcome to the belief agent. Here you can add information to the belief base, you can contract information, and you can ask ")
    print("if a given proposition is valid given the current belief base.")
    while going:
        print("Write a number for an action: ")
        print("1: Print base.  2: Add proposition.  3: Ask if proposition is valid.  4: Retract information.  5: Exit agent")
        action = input()
        if action == "1":
            agent.printBase()
        elif action == "2":
            agent.addProposition()
        elif action == "3":
            agent.askValid()
        elif action == "4":
            agent.retractInformation()
        elif action == "5":
            going = False
            print("Agents shutting down")
        else:
            print("Sorry I do not understand what you want")
















