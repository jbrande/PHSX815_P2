# PHSX815_P2

This project uses Markov Chain Monte Carlo methods to simulate observing meteor impacts in the Earth's atmosphere. 

python/MeteorMCMC.py will run the MCMC process. It can be called with several parameters:

-h/--help			prints the usage of the program.
-seed				(number) sets the seed of the random number generator.
-Nmeas				(number, required) sets the number of measurements to make per experiment
-Nexp				(number, required) sets the number of experiments to run
-Nburn				(number) sets the number of burn-in steps
-Nskip				(number) sets the number of MCMC steps to skip when printing output
--model0/--model1	(required) specifies the model to be used
-output 			(filename) specifies the file to print output to

If the output is specified, the MCMC results will be printed to that file, one experiment per line. Otherwise, the output will be printed to the console, one experiment per line.


python/MeteorAnalysis.py will read two output files, one for each model, and will plot the probability distributions of those models and the log-likelihood ratio distributions of the MCMC process. Its parameters are:

-h/--help 			prints the usage of the program
-H0					(filename, required) the input file containing the H0 data
-H1 				(filename, required) the input file containing the H1 data
-alpha 				(float) the alpha value of the test

The program shows the plots and then saves them in the main directory.