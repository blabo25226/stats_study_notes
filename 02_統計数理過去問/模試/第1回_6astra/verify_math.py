"""Numerical and symbolic checks of the original models (not a TeX parser).

Run: python verify_math.py
Dependencies: numpy, scipy, sympy. Seed fixed for reproducibility.
The checks supplement the analytic re-solution in 検証記録.md.
"""
import itertools
import json
import math
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.integrate import quad
from scipy.optimize import brentq, minimize_scalar
from scipy.stats import binom, norm, poisson

HERE = Path(__file__).resolve().parent
checks = 0
results = {}


def close(actual, expected, tol=1e-9):
    global checks
    assert np.allclose(actual, expected, atol=tol, rtol=tol), (actual, expected)
    checks += 1


def q1():
    # Direct conditioning on the Poisson event count, independently of the PGF.
    for lam, p in [(0.2, 0.1), (2, 0.5), (5, 0.9)]:
        masses = []
        for k in range(101):
            by_count = sum(poisson.pmf(n, lam) * binom.pmf(k-n, n, 1-p)
                           for n in range((k+1)//2, k+1))
            formula = math.exp(-lam) * sum(
                (lam*p)**(k-2*j) * (lam*(1-p))**j /
                (math.factorial(k-2*j)*math.factorial(j))
                for j in range(k//2+1))
            close(by_count, formula)
            masses.append(by_count)
        k = np.arange(len(masses))
        mu = np.dot(k, masses)
        var = np.dot((k-mu)**2, masses)
        close(sum(masses), 1)
        close(mu, lam*(2-p))
        close(var, lam*(4-3*p))
        close([(3*mu-var)/2, 2*(2*mu-var)/(3*mu-var)], [lam,p])
        for s in [0.2,0.6,1.0]:
            close(np.dot(s**k,masses), np.exp(lam*(p*s+(1-p)*s*s-1)))
    results['q1'] = {'pmf_sum_mean_variance_pgf': 'passed', 'mom_at_3_5': [2,0.5]}


def q2():
    theta, c, m, r, k, s = sp.symbols('theta c m r k s', positive=True)
    ell = m*sp.log(theta)-theta*(s+k*c*c)+(r-k)*sp.log(1-sp.exp(-theta*c*c))
    score = m/theta-s-k*c*c+(r-k)*c*c/(sp.exp(theta*c*c)-1)
    assert sp.simplify(sp.diff(ell,theta)-score)==0
    second = -m/theta**2-(r-k)*c**4*sp.exp(theta*c*c)/(sp.exp(theta*c*c)-1)**2
    assert sp.simplify(sp.diff(ell,theta,2)-second)==0
    info = -second.subs(k,r*sp.exp(-theta*c*c))
    assert sp.simplify(info-(m/theta**2+r*c**4/(sp.exp(theta*c*c)-1)))==0
    for th, cutoff in [(0.3,0.8),(1.2,1.5),(3.0,0.4)]:
        density = lambda x: 2*th*x*math.exp(-th*x*x)
        close(quad(density,0,np.inf)[0],1)
        close(quad(lambda x: x*x*density(x),0,np.inf)[0],1/th)
        close(quad(density,cutoff,np.inf)[0],math.exp(-th*cutoff**2))
        close(quad(lambda x: (1/th-x*x)**2*density(x),0,np.inf)[0],1/th**2)
        q = math.exp(-th*cutoff**2)
        score_b = [-(-cutoff**2*q)/(1-q), -cutoff**2]
        close((1-q)*score_b[0]**2+q*score_b[1]**2,cutoff**4/math.expm1(th*cutoff**2))
    for observed_k in range(5):
        # Includes k=0 and k=r; m>=1 guarantees a finite, positive maximum.
        mm,rr,ss,cc=2,4,1.7,0.9
        fun=lambda t: mm*math.log(t)-t*(ss+observed_k*cc**2)+(rr-observed_k)*math.log(-math.expm1(-t*cc**2))
        score_fun=lambda t: mm/t-ss-observed_k*cc**2+(rr-observed_k)*cc**2/math.expm1(t*cc**2)
        root=brentq(score_fun,1e-8,30)
        numerical=minimize_scalar(lambda t: -fun(t),bounds=(1e-7,30),method='bounded', options={'xatol':1e-12}).x
        close(root,numerical,2e-7)
    z=brentq(lambda t: (2-t)*math.exp(t)-2,1,2)
    optimum=minimize_scalar(lambda t: -t*t/math.expm1(t),bounds=(0.01,8),method='bounded').x
    close(z,optimum,2e-6)
    close(round(0.6931**2,3),0.480)
    results['q2']={'optimal_z':z,'relative_information_at_optimum':z*z/math.expm1(z),'mixed_mle_cases':5}


def q3():
    u,t,a,b=sp.symbols('u t a b',positive=True)
    close(float(sp.det(sp.Matrix([[t,u],[-t,1-u]]))/t),1)
    powers={}
    for theta in [0.2,1,1.5,3,8]:
        f=lambda u: 6*theta**2*u*(1-u)/(1+(theta-1)*u)**4
        close(quad(f,0,1)[0],1)
        numerical=quad(f,0,0.25)[0]
        exact=theta**2*(theta+9)/(theta+3)**3
        close(numerical,exact)
        powers[str(theta)]=numerical
    close(powers['1'],5/32)
    close(powers['3'],0.5)
    for aa,bb in [(1,4),(3,2),(2,2),(0.8,10)]:
        # Numerical optimization of the profiled full likelihood.
        ell=lambda theta: 4*math.log(4/(theta*aa+bb))+2*math.log(theta)-4
        opt=minimize_scalar(lambda th: -ell(th),bounds=(1,100),method='bounded')
        maxell=max(ell(1),-opt.fun)
        ratio=math.exp(ell(1)-maxell)
        uu=aa/(aa+bb)
        close(ratio,(4*uu*(1-uu))**2 if uu<0.5 else 1,1e-8)
    # Numerical derivative of the density ratio is negative on the entire grid.
    for theta in [1.01,2,10]:
        ratios=theta**2/(1+(theta-1)*np.linspace(0,1,501))**4
        assert np.all(np.diff(ratios)<0)
    results['q3']={'power_by_theta':powers,'full_likelihood_maximization':'passed'}


def q4(rng):
    mu,eta,sigma=1.2,-0.4,1.7
    kl=quad(lambda y: norm.pdf(y,mu,sigma)*(norm.logpdf(y,mu,sigma)-norm.logpdf(y,eta,sigma)),-np.inf,np.inf)[0]
    close(kl,(mu-eta)**2/(2*sigma**2))
    data=np.array([0.,1.,2.,5.])
    direct=lambda a: np.mean([(data[i]-a*np.delete(data,i).mean())**2 for i in range(4)])
    for a in [0,0.1,0.5,51/79,1]:
        close(direct(a),(1+a/3)**2*data.var()+(1-a)**2*data.mean()**2)
    opt=minimize_scalar(direct,bounds=(0,1),method='bounded')
    close(opt.x,51/79)
    close(opt.fun,448/79)
    # Exact symbolic expectation based on the first two sample moments.
    a,n,v,m=sp.symbols('a n v m',positive=True)
    expected=(1+a/(n-1))**2*(n-1)*v/n+(1-a)**2*(m*m+v/n)
    assert sp.simplify(expected-(v+(1-a)**2*m*m+a*a*v/(n-1)))==0
    size,n,mu,sigma,a=120000,8,0.8,1.5,0.35
    y=rng.normal(mu,sigma,(size,n))
    loo=(y.sum(axis=1)[:,None]-y)/(n-1)
    cvs=np.mean((y-a*loo)**2,axis=1)
    expectation=sigma*sigma+(1-a)**2*mu*mu+a*a*sigma*sigma/(n-1)
    se=cvs.std(ddof=1)/np.sqrt(size)
    assert abs(cvs.mean()-expectation)<5*se
    results['q4']={'cv_optimum':51/79,'minimum_cv':448/79,'simulation_cv_mean':float(cvs.mean()),'exact_cv_mean':expectation,'mc_se':float(se)}


def q5(rng):
    # Exhaustive resampling of 4 distinct observations (256 possible samples).
    x=np.array([0.2,0.7,1.1,1.8]); n=len(x)
    samples=np.array(list(itertools.product(x,repeat=n)))
    means=samples.mean(axis=1); maxima=samples.max(axis=1)
    close(means.mean(),x.mean())
    close(means.var(),x.var()/n)
    mass=float(np.mean(maxima==x.max()))
    close(mass,1-(1-1/n)**n)
    for z in [0,0.2,0.6,0.7,1.1,1.8,2]:
        close(np.mean(maxima<=z),np.mean(x<=z)**n)
    size,n,theta,alpha=200000,20,2.5,0.05
    original=rng.uniform(0,theta,(size,n)).max(axis=1)
    normalized=n*(1-original/theta)
    parametric=rng.uniform(0,1,(size,n)).max(axis=1)
    tdag=n*(1-parametric)
    for t in [0,0.2,1,2,3]:
        exact=1-(1-t/n)**n
        tolerance=5*np.sqrt(max(exact*(1-exact),1/size)/size)
        close(np.mean(normalized<=t),exact,tolerance)
        close(np.mean(tdag<=t),exact,tolerance)
    upper=original/(alpha**(1/n))
    coverage=float(np.mean((original<=theta)&(theta<=upper)))
    se=math.sqrt(alpha*(1-alpha)/size)
    assert abs(coverage-(1-alpha))<5*se
    results['q5']={'enumeration_size':256,'bootstrap_atom_at_n4':mass,'exact_ci_simulation_coverage':coverage,'nominal_coverage':1-alpha,'mc_se':se}


if __name__=='__main__':
    rng=np.random.default_rng(20261111)
    q1(); q2(); q3(); q4(rng); q5(rng)
    results['checks']={'numeric_comparisons':checks,'symbolic_and_structural_assertions':'passed','seed':20261111}
    out=HERE/'検算結果.json'
    out.write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(results,indent=2,ensure_ascii=False))
