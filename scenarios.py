import numpy as np
import matplotlib.pyplot as plt
from compartment_model import dSIRdt_vec
from scipy.stats import poisson
from peak_ratio import month_lookup

if __name__ == '__main__':

    rec = 36   # 10 day serial interval
    migration = 1e-3 # rate of moving per year
    N0,N1 = 1e7,1e8

    # add Hubei population with parameters specified above
    #          population size, beta, rec, eps, theta, NH, containment
    params = [[N0, 2*rec, rec, 0.5, 0.0, 1,     0.5],
              [N1, 2*rec, rec, 0.5, 10.5/12, 1, 0.5],
              [N1, 2*rec, rec, 0.5, 0.5/12, 1,  0.5],
              [N1, 2*rec, rec, 0.5, 2.5/12, 1,  0.5]]
    # initially fully susceptible with one case in Hubei, no cases in NH
    populations = [[1, 1/N0], [1,0], [1,0], [1,0]]
    #total number of populations
    n_pops = len(params)


    params = np.array(params)
    populations = [np.array(populations)]

    # start simulation
    t = [2019.8]
    dt = 0.001
    tmax = 2021.5
    while t[-1]<tmax:
        dS, dI = dSIRdt_vec(populations[-1][:,0], populations[-1][:,1], t[-1], params)
        populations.append(populations[-1] + dt*np.array([dS,dI]).T)

        I_tot = (params[:,0]*populations[-1][:,1]).sum()
        populations[-1][:,1] += poisson.rvs(migration*I_tot/n_pops*dt*np.ones(n_pops))/params[:,0]
        populations[-1][populations[-1][:,1]<1/params[:,0],1] = 0
        t.append(t[-1]+dt)

    populations = np.array(populations)

    fs=16
    plt.figure()
    plt.plot(t, populations[:,0,1]*params[0, 0], lw=3, label='Hubei', ls='--')

    for pi in range(1,len(params)):
        plt.plot(t, populations[:,pi,1]*params[pi, 0],
                lw=3, label=f'NH peak {month_lookup[int(params[pi,4]*12-0.5)]}')

    plt.legend(fontsize=fs*0.8, loc=8, ncol=2)
    plt.yscale('log')
    plt.ylabel('Cases', fontsize=fs)
    plt.xticks(np.array([2020, 2020.25, 2020.5, 2020.75, 2021, 2021.25]),
               ['2020-01', '2020-04', '2020-07', '2020-10', '2021-01', '2021-04'])
    plt.tick_params(labelsize=0.8*fs)
    plt.xticks(rotation=30, horizontalalignment='right')
    plt.tight_layout()
    plt.savefig('figures/scenarios.pdf')

