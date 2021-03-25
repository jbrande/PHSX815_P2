#! /usr/bin/env python

import math
import numpy as np

#################
# Random class
#################
# class that can generate random numbers
class Random:
    """A random number generator class"""


    # initialization method for Random class
    def __init__(self, seed = 5555):
        self.seed = seed
        self.m_v = np.uint64(4101842887655102017)
        self.m_w = np.uint64(1)
        self.m_u = np.uint64(1)
        
        self.m_u = np.uint64(self.seed) ^ self.m_v
        self.int64()
        self.m_v = self.m_u
        self.int64()
        self.m_w = self.m_v
        self.int64()

        # for mcmc prior
        self.aprev = 1.0
        self.bprev = 1.0

    # function returns a random 64 bit integer
    def int64(self):
        with np.errstate(over='ignore'):
            self.m_u = np.uint64(self.m_u * np.uint64(2862933555777941757) + np.uint64(7046029254386353087))
        self.m_v ^= self.m_v >> np.uint64(17)
        self.m_v ^= self.m_v << np.uint64(31)
        self.m_v ^= self.m_v >> np.uint64(8)
        self.m_w = np.uint64(np.uint64(4294957665)*(self.m_w & np.uint64(0xffffffff))) + np.uint64((self.m_w >> np.uint64(32)))
        x = np.uint64(self.m_u ^ (self.m_u << np.uint64(21)))
        x ^= x >> np.uint64(35)
        x ^= x << np.uint64(4)
        with np.errstate(over='ignore'):
            return (x + self.m_v)^self.m_w

    # function returns a random floating point number between (0, 1) (uniform)
    def rand(self):
        return 5.42101086242752217E-20 * self.int64()

    # function returns a random integer (0 or 1) according to a Bernoulli distr.
    def Bernoulli(self, p=0.5):
        if p < 0. or p > 1.:
            return 1
        
        R = self.rand()

        if R < p:
            return 1
        else:
            return 0

    # function returns a random double (0 to infty) according to an exponential distribution
    def Exponential(self, beta=1.):
      # make sure beta is consistent with an exponential
      if beta <= 0.:
        beta = 1.

      R = self.rand();

      while R <= 0.:
        R = self.rand()

      X = -math.log(R)/beta

      return X

    # returns random double according to logistic distribution
    def Logistic(self, mu=0.0, sig=1.0):
        u = self.rand()
        while u*(1.-u) <= 0.:
            u = self.rand()

        return mu + 0.551328895421792050*sig*math.log(u/(1.-u))

    # random double from gaussian distribution
    def GaussianRand(self, mu=0.0, sig=1.0):
        m_match = 1
        sigma_match = 1

        m_tailprob = 1.0 / (m_match*np.exp(-1*m_match*m_match/2.0))
        m_tailprob = m_tailprob / (2*m_tailprob + 2*m_match)


        if sig < 0:
            sig = 1

        accept = False

        x = None
        while (not accept):
            r1 = self.rand()
            r2 = self.rand()
            ratio = None
            if r1 < m_tailprob:
                x = -1*m_match + math.log(r2)/m_match
                ratio = math.exp(-1*x*x/2.0) / (math.exp(m_match*m_match/2.)*math.exp(x*m_match))
            elif r1 > 1.0 - m_tailprob:
                x = m_match - math.log(r2)/m_match
                ratio = math.exp(-1*x*x/2.0) / (math.exp(m_match*m_match/2.)*math.exp(x*m_match))
            else:
                x = -1*m_match + r2*2.*m_match
                ratio = math.exp(-1*x*x/2.)

            r3 = self.rand()
            if r3 <= ratio:
                accept = True

        return mu + sig*x


    # probability of x according to gaussian PDF
    def GaussianProb(self, x, mu=0.0, sig=0.0):
        if sig < 0:
            sig = 1.0

        return 1.0 / math.sqrt(2.0*math.acos(-1)) / sig*math.exp(-1*(x - mu)*(x - mu)/2.0/sig/sig)

    # probability of a, b according to prior PDF with a0, b0
    def PriorProb(self, a, b, a0, b0):
        Na = 3.0
        Nb = 1.0

        if a0 <=0:
            a0 = 1
        if b0 <=0:
            b0 = 1

        return math.pow(a0, Na*(a - 1.0))*math.exp(-1*Nb*b*b0)/math.pow(math.gamma(a), Na)/math.pow(b, -1*Nb*a)

    # random a,b from prior distributions
    def PriorRand(self, a,b):
        anew = -1
        bnew = -1

        gmu = 0.0
        gsig = 1.0

        while anew < 0:
            x = self.GaussianRand(gmu, gsig)
            anew = self.aprev + x

        while bnew < 0:
            x = self.GaussianRand(gmu, gsig)
            bnew = self.bprev + x

        x = anew - self.aprev
        Psample_new = self.GaussianProb(x, gmu, gsig)
        x = bnew - self.bprev
        Psample_new *= self.GaussianProb(x, gmu, gsig)

        x = self.aprev - anew
        Psample_old = self.GaussianProb(x, gmu, gsig)
        x = self.bprev - bnew
        Psample_old *= self.GaussianProb(x, gmu, gsig)

        Pfunc_new = self.PriorProb(anew, bnew, a, b)
        Pfunc_old = self.PriorProb(self.aprev, self.bprev, a, b)

        A = min(1.0, Pfunc_new*Psample_old / (Pfunc_old*Psample_new))

        r = self.rand()
        if r <= A:
            self.aprev = anew
            self.bprev = bnew
            return [anew, bnew]
        else:
            return [self.aprev, self.bprev]

