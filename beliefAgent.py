import numpy as np
import beliefBase

class BeliefAgent:

    def __init__(self):
        self.KB = beliefBase.BeliefBase()
        self.t = 0

    def getAction(self,percept):
        self.KB.tell(self.perceptSentence(percept),self.t)
        action = self.KB.ask(self.actionQuery())
        self.KB.tell(self.actionSentence(action),self.t)
        self.t += 1
        return action

    def perceptSentence(self,percept):


    def actionQuery(self):


    def actionSentence(self,action):
        
