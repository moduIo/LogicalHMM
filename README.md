# LogicalHMM
PRISM Implementation of a Logical Hidden Markov Model (LOHMM).  LOHMMs generalize hidden Markov models by introducing unification of logical variables.

Formally:
LM = (SIGMA, MU, DELTA, UPSILON)
* SIGMA := logical alphabet
* MU := selection (grounding) probability over SIGMA
* DELTA := set of abstract transitions T = (p : H <- B emitting O)
* UPSILON := set of abstract transitions encoding a prior distribution of states

References: 
[1] "Logical Hidden Markov Models" - Kersting, De Raedt, Raiko; https://www.aaai.org/Papers/JAIR/Vol25/JAIR-2512.pdf 
[2] Greenberg, S. (1988). "Using Unix: collected traces of 168 users", https://prism.ucalgary.ca/handle/1880/45929
     
Models
---
Contains PRISM models of the LOHMM structure for various synthetic and aquired datasets presented in [1].

* `LogicalHMM/models/Example/lohmm_example.psm` example taken from Figure 1 [1]. 
* `LogicalHMM/models/UNIX Model/lohmm_unix.psm` example taken from a long running example in [1].

Utils
---
Contains parser implementations used on aquired datasets. The UNIX dataset represents user actions collected from a bash terminal [2].

Latex
---
Contains some pdfs of mathematical formulations of some of the LOHMM structures implemented.
