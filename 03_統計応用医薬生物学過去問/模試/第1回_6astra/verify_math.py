"""Independent numerical/symbolic checks from the problem's model and data.

This program does not read the solution booklet. Python/SciPy are verification
tools only; the booklet's numerical answers use arithmetic, sqrt and tables.
Run: python verify_math.py (requires numpy, scipy, sympy).
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import json
import math
import re
import numpy as np
import sympy as sp
from scipy.integrate import quad
from scipy.optimize import minimize_scalar
from scipy.stats import norm, chi2, binom

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
results = {}
checks = 0


def close(a, b, tol=1e-9):
    global checks
    assert np.allclose(a, b, rtol=tol, atol=tol), (a, b)
    checks += 1


# Parse the original patient table, not the solution's risk sets.
problem = (HERE / 'SA_第1回_6astra_問題.tex').read_text(encoding='utf-8')
rows = re.findall(r'^([CT]\d) & ([01]) & ([\d.]+) & ([\d.]+) & ([01])', problem, re.M)
assert len(rows) == 8
patients = [(pid, int(g), float(a), float(y), int(d)) for pid,g,a,y,d in rows]
events = sorted((y,g) for pid,g,a,y,d in patients if d)
risks = []
survival = [F(1), F(1)]
pooled, naive = F(1), F(1)
theta = sp.symbols('theta', positive=True)
likelihood = sp.Integer(1)
score = F(0)
information = F(0)
for t, group in events:
    risk = [sum(a <= t <= y and g == j for _,g,a,y,d in patients) for j in (0,1)]
    risks.append(risk)
    survival[group] *= 1-F(1,risk[group])
    pooled *= 1-F(1,sum(risk))
    naive *= 1-F(1,sum(y >= t for _,g,a,y,d in patients))
    likelihood *= theta**group/(risk[0]+risk[1]*theta)
    prob = F(risk[1],sum(risk))
    score += group-prob
    information += prob*(1-prob)
root = sp.solve(sp.diff(likelihood,theta),theta)[0]
numeric = minimize_scalar(lambda b: -float(sp.log(likelihood).subs(theta,math.exp(b))),
                          bounds=(-4,4), method='bounded')
close(float(root), math.exp(numeric.x), tol=2e-6)
close([float(v) for v in survival], [1/3,4/9])
close([float(pooled),float(naive),float(score),float(information)], [.4,.45,-.2,.98])
results['q1'] = dict(risks=risks, km_groups=list(map(str,survival)), km_pooled=str(pooled),
                    km_naive=str(naive), likelihood=str(sp.factor(likelihood)),
                    maximizing_theta=str(root), score=str(score), information=str(information),
                    score_test=float(score**2/information))

# Poisson offset model; fit via numerical likelihood separately.
years = np.array([[5000,1250],[1250,5000]],dtype=float)
deaths = np.array([[40,60],[10,240]],dtype=float)
ref = np.array([.01,.04])
expected = years*ref
crude = deaths.sum(axis=1)/years.sum(axis=1)
smr = deaths.sum(axis=1)/expected.sum(axis=1)
direct = (deaths/years).mean(axis=1)
fit = minimize_scalar(lambda th: float(np.sum(th*expected[0]-deaths[0]*np.log(th*expected[0]))),
                      bounds=(.01,4),method='bounded')
close(fit.x,smr[0],tol=2e-6)
gof = np.sum((deaths[0]-smr[0]*expected[0])**2/(smr[0]*expected[0]))
close(gof,4)
table_exp = 1.2092+.6*(1.2214-1.2092)
ci_table = [1/table_exp,table_exp]
ci_exact = np.exp(np.array([-1,1])*norm.isf(.025)/10)
close(ci_table,ci_exact,tol=3e-5)
results['q2'] = dict(crude=crude.tolist(),smr=smr.tolist(),direct=direct.tolist(),
                    poisson_fit=fit.x,gof=float(gof),gof_p=float(chi2.sf(gof,1)),
                    log_ci_table=ci_table,log_ci_exact=ci_exact.tolist())

# Enumerate the two independent binomial counts to recover the variance.
q,a,b=.2,.4,.05
x1=np.arange(201); x0=np.arange(101)
v=(q*x1[:,None]/200+(1-q)*x0[None,:]/100)
weights=binom.pmf(x1,200,a)[:,None]*binom.pmf(x0,100,b)[None,:]
mean=float(np.sum(weights*v)); variance=float(np.sum(weights*(v-mean)**2))
close(mean,.12);close(variance,.000352)
joint=np.array([[.2*.4,.2*.6],[.8*.05,.8*.95]])
selected=joint*np.array([[1],[1/8]])
selected/=selected.sum()
sens=joint[0,0]/joint[:,0].sum();spec=joint[1,1]/joint[:,1].sum()
naive_sens=selected[0,0]/selected[:,0].sum()
naive_spec=selected[1,1]/selected[:,1].sum()
close([sens,spec,naive_sens,naive_spec],[2/3,19/22,16/17,19/43])
results['q3'] = dict(joint=joint.tolist(),sensitivity=sens,specificity=spec,
                    naive_sensitivity=naive_sens,naive_specificity=naive_spec,
                    mean=mean,variance=variance,se=math.sqrt(variance),
                    ci=[mean-1.96*math.sqrt(variance),mean+1.96*math.sqrt(variance)])

# Form the entire covariance matrix rather than substituting the derived formula.
K,m,sb,se=12,10,4,36
cov=np.kron(np.eye(2*K),sb*np.ones((m,m))+se*np.eye(m))
contrast=np.r_[-np.ones(K*m),np.ones(K*m)]/(K*m)
variance=float(contrast@cov@contrast)
close(variance,19/15)
power={k:float(norm.sf(norm.isf(.025)-2/math.sqrt(2*(sb+se/m)/k))) for k in [29,30]}
assert power[29]<.8<=power[30]
checks += 1
designs=[]
for mi in range(1,5101):
    ki=5200//(100+mi)
    if ki: designs.append((2*(sb+se/mi)/ki,mi,ki))
opt=min(designs)
close(opt,[.26,30,40])
results['q4']=dict(variance=variance,z=3/math.sqrt(variance),
                  ci=[3-1.96*math.sqrt(variance),3+1.96*math.sqrt(variance)],
                  exact_power=power,integer_budget_optimum=dict(variance=opt[0],m=opt[1],K=opt[2]))

# Independent quadrature of the maximum's density, using sigma=1.
moments=[quad(lambda x: x**r*2*norm.pdf(x)*norm.cdf(x),-np.inf,np.inf)[0] for r in [0,1,2]]
close(moments,[1,1/math.sqrt(math.pi),1])
close(moments[2]-moments[1]**2,1-1/math.pi)
zvals=[2.58,2.10,1.96,.20]
table=(ROOT/'統計検定1級出題表/統計検定1級_付表数値表.md').read_text(encoding='utf-8')
normal={}
for line in table.split('## 付表2')[0].splitlines():
    parts=[x.strip() for x in line.split('|')[1:-1]]
    if len(parts)==11 and re.fullmatch(r'\d\.\d',parts[0]):
        for i,s in enumerate(parts[1:]): normal[round(float(parts[0])+i/100,2)]=float(s)
pvals=[normal[z] for z in zvals]
close(pvals,[.0049,.0179,.0250,.4207])
for z in [1.96,.84,2.24]+zvals:
    close(normal[z],norm.sf(z),tol=5.1e-5)


def holm(pvals,alpha=.05):
    reject=[]
    for k,j in enumerate(sorted(range(len(pvals)),key=lambda j:pvals[j])):
        if pvals[j]>alpha/(len(pvals)-k): break
        reject.append(j)
    return reject


assert holm(pvals)==[0]
checks+=1
# Finite exhaustive check of the error-event containment used in the proof.
event_checks=0
for pvec in product([.001,.0125,.0179,.025,.04,.1,.7],repeat=4):
    rejected=set(holm(pvec))
    for mask in range(1,16):
        true={j for j in range(4) if mask&(1<<j)}
        if rejected&true:
            assert min(pvec[j] for j in true)<=.05/len(true)
        event_checks+=1
results['q5']=dict(max_moments_sigma1=moments,max_variance=moments[2]-moments[1]**2,
                  independent_fwer=1-.95**4,table_p_values=pvals,
                  exact_bonferroni_cutoff=float(norm.isf(.0125)),
                  holm_rejected_indices_1based=[j+1 for j in holm(pvals)],
                  checked_error_event_containments=event_checks)
allocations=[[7,11,7,5],[4,6,10,6,4],[4,8,10,8],[4,7,5,7,7],[8,5,4,5,8]]
close([sum(v) for v in allocations],[30]*5)
results['verification']=dict(numeric_checks=checks,error_event_cases=event_checks,
                             status='all passed',solution_booklet_read=False)
(HERE/'検算結果.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
