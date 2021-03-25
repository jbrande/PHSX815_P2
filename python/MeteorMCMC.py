#! /usr/bin/env python

# Porting Dr. Rogan's code from C++ to Python


# imports of external packages to use in our code
import sys
import numpy as np

# import our Random class from python/Random.py file
sys.path.append(".")
from python.Random import Random


if __name__ == "__main__":
    # if the user includes the flag -h or --help print the options
    if '-h' in sys.argv or '--help' in sys.argv:
        print ("Usage: %s [-seed number] -Nmeas number -Nexp number [-Nburn number] [-Nskip number] (--model0 or --model1) [-output filename]" % sys.argv[0])
        print
        sys.exit(1)

    # default seed
    seed = 5555

    # default number of time measurements (time to next missing cookie) - per experiment
    Nmeas = 1

    # default number of experiments
    Nexp = 1

    # number of burn in steps
    Nburn = 0

    # number of steps to skip between writing data
    Nskip = 0

    # output file defaults
    doOutputFile = False

    # model specification
    model = 0

    # read the user-provided arguments from the command line (if there)
    if '-seed' in sys.argv:
        p = sys.argv.index('-seed')
        seed = sys.argv[p+1]
    if '-Nmeas' in sys.argv:
        p = sys.argv.index('-Nmeas')
        Nt = int(sys.argv[p+1])
        if Nt > 0:
            Nmeas = Nt
    else:
        print("You must specify a number of measurements.")
        sys.exit(1)

    if '-Nexp' in sys.argv:
        p = sys.argv.index('-Nexp')
        Ne = int(sys.argv[p+1])
        if Ne > 0:
            Nexp = Ne
    else:
        print("You must specify a number of experiments.")
        sys.exit(1)
    if '-Nburn' in sys.argv:
        p = sys.argv.index('-Nburn')
        Nb = int(sys.argv[p+1])
        if Nb > 0:
            Nburn = Nb
    if '-Nskip' in sys.argv:
        p = sys.argv.index('-Nskip')
        Ns = int(sys.argv[p+1])
        if Ns > 0:
            Nskip = Ns
    if '--model0' in sys.argv:
        model = 0
    elif '--model1' in sys.argv:
        model = 1
    else:
        print("You must specify a model.")
        sys.exit(1)

    if '-output' in sys.argv:
        p = sys.argv.index('-output')
        OutputFileName = sys.argv[p+1]
        doOutputFile = True

    # class instance of our Random class using seed
    random = Random(seed)

    def getObservation():

        # model 0
        # alpha and beta for our gamma distribution
        alpha = 2.7
        beta = 1.57

        if model == 1: # model 1
            alpha, beta = random.PriorRand(alpha, beta)

        # get rate for given parameters
        rate = np.random.gamma(alpha, beta)

        return np.random.poisson(rate)


    # do MCMC burn-in steps
    for i in range(Nburn):
        getObservation()

    # do main MCMC draws and print output
    if doOutputFile:
        outfile = open(OutputFileName, 'w+')
        for e in range(0,Nexp):
            for t in range(0,Nmeas):
                for i in range(0,Nskip):
                    getObservation()
                outfile.write(str(getObservation())+" ")
            outfile.write(" \n")
        outfile.close()
    else:
        print(rate)
        for e in range(0,Nexp):
            for t in range(0,Nmeas):
                for i in range(0,Nskip):
                    getObservation()
                print(getObservation(), end=' ')
            print(" ")
