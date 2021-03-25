#! /usr/bin/env python

# Porting Dr. Rogan's code from C++ to Python

# imports of external packages to use in our code
import sys
import math
import numpy as np
import matplotlib.pyplot as plt

# import our Random class from python/Random.py file
sys.path.append(".")
from python.MySort import MySort


if __name__ == "__main__":
    
    haveInput = False

    # if the user includes the flag -h or --help print the options
    if '-h' in sys.argv or '--help' in sys.argv:
        print ("Usage: %s [-seed number] -H0 filename -H1 filename -alpha float" % sys.argv[0])
        print
        sys.exit(1)

    # input files
    f0 = None
    f1 = None

    # read the user-provided seed from the command line (if there)
    if '-H0' in sys.argv:
        p = sys.argv.index('-H0')
        f0 = sys.argv[p+1]
    if '-H1' in sys.argv:
        p = sys.argv.index('-H1')
        f1 = sys.argv[p+1]
    if '-alpha' in sys.argv:
        p = sys.argv.index('-alpha')
        alpha = float(sys.argv[p+1])

    # read in data from files
    Ncount_max = 0
    fs = [[],[]]
    for i, file in enumerate([f0, f1]):
        with open(file) as f:
            lines = f.readlines()
            data = []
            for line in lines:
                newdata = line.split()
                data.append(newdata)
                for num in newdata:
                    if int(num) > Ncount_max:
                        Ncount_max = int(num)
            data = np.array(data, dtype=np.int64) # numpy actually makes converting arrays of strings to numbers really easy, huh
            fs[i] = data
    fs = np.array(fs)

    # probability distributions
    hist0, bins0 = np.histogram(fs[0], np.max(fs[0])+1, range=(-0.5, np.max(fs[0])+0.5), density=True) # np.max(fs[0])
    hist1, bins1 = np.histogram(fs[1], np.max(fs[1])+1, range=(-0.5, np.max(fs[1])+0.5), density=True) # np.max(fs[1])

    # log likelihood ratios
    llrs = [[],[]]

    for i in range(2):
        Nexp = len(fs[i])
        for e in range(Nexp):
            Nmeas = len(fs[i][e])
            llr = 0
            ok_llr = True
            for m in range(Nmeas):
                ind0 = np.digitize(fs[i][e][m], bins0)-1
                ind1 = np.digitize(fs[i][e][m], bins1)-1
                #print(ind0, ind1)
                try:
                    p_H0 = hist0[ind0]
                except Exception as ex:
                    p_H0 = 0
                try:
                    p_H1 = hist1[ind1]
                except Exception as ex:
                    p_H1 = 0

                if (p_H0 > 0) and (p_H1 > 0):
                    llr += np.log(p_H1)
                    llr -= np.log(p_H0)
                else:
                    ok_llr = False
            if ok_llr:
                llrs[i].append(llr)

    # sort all our stuff
    Sorter = MySort()

    fs[0] = Sorter.DefaultSort(fs[0])
    fs[1] = Sorter.DefaultSort(fs[1])

    llrs[0] = Sorter.DefaultSort(llrs[0])
    llrs[1] = Sorter.DefaultSort(llrs[1])

    a0 = llrs[0]
    a1 = llrs[1]


    n0 = np.size(a0)
    n1 = np.size(a1)
    hmin = min(a0[0], a1[0])
    hmax = max(a0[n0-1],a1[n1-1])

    #print(n0, n1, hmin, hmax)

    # getting alpha and beta

    if alpha > 1.0/n0:
        #print(int((1.0-alpha)*n0), " ",  n0-1)
        lam_crit = a0[min(int((1.0-alpha)*n0), n0-1)]
        beta = 0.0

        #print(min(int((1.0-alpha)*n0), n0-1))
        #print(lam_crit)

        histp0 = []
        for i in range(n0):
            if a0[i] > lam_crit:
                histp0.append(a0[i])

        histp1 = []
        for i in range(n1):
            if a1[i] < lam_crit:
                histp1.append(a0[i])
                beta += 1.0

        beta /= n1

        #print(lam_crit, beta)

    fig = plt.figure(figsize=(10,6))
    plt.hist(fs[0].flatten(), 100, density=True, alpha=0.5, label="H0")
    plt.hist(fs[1].flatten(), 100, density=True, alpha=0.5, label="H1")
    plt.yscale("log")
    plt.title("Impacts per Measurement")
    plt.xlabel("Number of Impacts")
    plt.ylabel("Probability")
    plt.legend()
    plt.show()
    fig.savefig("impact_probability.jpg", dpi=180)

    fig1 = plt.figure(figsize=(10,6))
    # LLR histograms
    plt.hist(llrs[0], 100, density=True, alpha=0.5, label=r"$P(\lambda|H0)$")
    plt.hist(llrs[1], 100, density=True, alpha=0.5, label=r"$P(\lambda|H1)$")
    plt.yscale("log")
    plt.xlabel(r"$\lambda = log[\mathcal{L}(H1) / \mathcal{L}(H0)]$")
    plt.axvline(lam_crit, ls="--", c="k", label=r"$\lambda_\alpha$ = {:.3f}".format(lam_crit))
    plt.figtext(0.8, 0.7, r"$\alpha$ = {:.2f}".format(alpha), fontsize="large")
    plt.figtext(0.8, 0.67, r"$\beta$ = {:.3f}".format(beta), fontsize="large")
    plt.title("{} meas. / exp.".format(Nmeas))
    plt.ylabel("Probability")
    plt.legend()
    plt.show()
    fig1.savefig("impact_llrs.jpg", dpi=180)