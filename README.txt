1. Introduction
This is the source code for paper "An ant colony optimization method for the mixed storage and pre-marshalling problem considering pre-processing". 

2. Structure of the codes
-instances: Files of the test instances
-ACO.py: Main body of the ACO algorithm
-Environment.py: Interacting with aco.py to perform some yard-related functions, such as calculating heuristic values.
-Heuristic_wvaluation.py: Codes to analysis the coefficient between features and the outbound relocation
-LA_N.py: Calculate outbound relocation number for a given storage configuration, which is re-implemented to Petering & Hussein 2013
-Main_ACO.py: The main entrance of ACO
-Utiles.py: Some helper functions.

3. How to start
(1) Unfold the instances
(2) Modified the loading and save address in Main_ACO.py (line 12, line 16, and line 37)
(3) Run!



