# LogicalHMM
PRISM Implementation of a Logical Hidden Markov Model (LOHMM).  LOHMMs generalize hidden Markov models by introducing unification of logical variables.

Formally:
LM = (SIGMA, MU, DELTA, UPSILON)
* SIGMA := logical alphabet
* MU := selection (grounding) probability over SIGMA
* DELTA := set of abstract transitions T = (p : H <- B emitting O)
* UPSILON := set of abstract transitions encoding a prior distribution of states
     
Models
---
Contains PRISM models of the LOHMM structure for various synthetic and aquired datasets.

Utils
---
Contains parser implementations used on aquired datasets.

Latex
---
Contains some pdfs of mathematical formulations of some of the LOHMM structures implemented.
