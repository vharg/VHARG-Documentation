# Tephra2 inversion on the cluster

Tephra2 inversion is on Komodo at `/home/volcano/Tephra2Inversion/`.

Basically follow Seb's procedure!: https://e5k.github.io/codes/utilities/2018/06/06/inversion/

If you have no information on likely ESPs, it makes sense to use 'Batch' to simulate across a broad range, and then 'Seed' to zoom in on a much more restricted ESP range to see the effect of the seed number of optimised inversion runs.

Good practice is to note (in the relevant excel sheet perhaps) your rationale for each new set of simulations.

The heat fit map, along with the isopachs and ObsVsComp plots, will help you identify smaller ranges to zoom in on, if an inversion fit is possible (sometimes you may only reliably be able to invert for some, not all, parameters).

## Run issues
If there are permissions errors in the log files (output as default to your home account at ~/jobno.komodo2.des.OU), then either copy the folder to your home account and run there, or ask Edwin to fix your permissions in /home/volcano.

Each run folder must be named 1/, 2/, 3/, etc.. for comparison sheets to be provided in the summary excel file (found in the Inversion/ folder, not your eruption folder.

## Interpreting the outputs
Some things to consider:
- Typically, mass is going to be easier to constrain than plume height.
- The fit values should be considered in relation to each other, rather than in terms of their absolute number.
- The ObsVComp outputs, isopachs and fit matrix are all useful in combination to identify what observations the inversion can and cannot reproduce.

## Using the 'heat' fit matrix
- The GUI in matlab lets you change the maximum fit value you consider, the parameters you're considering, as well as the size of the grid cells (recommend applying the XGrid and YGrid in Edit to avoid over-interpolation and to let you see the simulation boundaries better). 
- Each black cross represents the optimum solution for your defined grid cell after a certain number of Tephra2 runs - if the solution is often pushing close to a mass boundary, perhaps it would give a better solution in the next cell. If the boundary is the edge of your simulated values, you need to expand your simulated ESP range.
- The red numbers show the top 10 best fits - if they're clustered it would suggest a more robust inversion for specific values than disparate values, which suggests non-unique solutions.

:warning: Warning: Be critical! |
|---|
This method is intended to give you insight into how well Tephra2 can fit the data and with what parameters, different sets of parameters. It isn't ever going to give you the definitive answer, and should be considered critically. 

