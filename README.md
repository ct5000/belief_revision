# belief_revision

This software has been developed by Andreas Goltermann, Hank Kristian Bech Hansen, and Christian Rømer Thulstrup as part of the course 02180 - Introduction to Artificial Intelligence, course at the Technical University of Denmark.

The program is a belief revision software in the form of a belief base. It is possible to add propositional logic to it and also retract information again. 


## Running the program
Run the file "beliefAgent.py" with Python 3. 

This will start the program in the commandline. Here it gives 5 options:

* 1: Prints the current belief base
* 2: Add a proposition to the belief base
* 3: Check if a proposition is valid in the current belief base
* 4: Rectract a proposition from the belief
* 5: Exit the program

### Valid inputs
For a proposition to be valid it must consists of propositions/atomic sentences connected by operators: (and, or, not, implies, equal). If it is not one of the operators it is considered as an atomic sentence. It is not allowed to have two operators in a row, except when it is not just after one of the other operators. Two atomic sentences should be sorounded by parenteses. 



