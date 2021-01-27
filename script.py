import math
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import interpolate
from scipy.signal import savgol_filter
from scipy.optimize import curve_fit


xls = pd.ExcelFile("26012121.xls")
sheetX = xls.parse(1)

well = sheetX['Block Type'][7:]
cycles = sheetX['Unnamed: 2'][7:]
drs = sheetX['Unnamed: 5'][7:]

results = {}
for i, dr in enumerate(drs):
    if not math.isnan(dr):
        if well[i+7] in results.keys():
            results[well[i+7]]['x'].append(cycles[i+7])
            results[well[i+7]]['y'].append(dr)
        else:
            results[well[i+7]] = {'x': [cycles[i+7]], 'y': [dr]}


# getting x and y from xls file
x = np.array(results['A1']['x'])
y = np.array(results['A1']['y'])


# fit to a global function
def func(x, A, B, x0, sigma):
    return A+B*np.tanh((x-x0)/sigma)


x_int = np.linspace(x[0], x[-1], 1000)
fit, _ = curve_fit(func, x, y)
y_fit = func(x_int, *fit)


# derivative
der = np.diff(y_fit) / np.diff(x_int)
x2 = (x_int[:-1] + x_int[1:]) / 2
max_fit = max(zip(x2, der), key=lambda t: t[1])

fig = plt.figure()
ax1 = fig.add_subplot(211)
ax1.set_xlabel('cycle')
ax1.set_ylabel(r'${\Delta}Rn$')
ax1.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax1.xaxis.set_minor_locator(ticker.MultipleLocator(1))
ax1.plot(x, y, 'r.', label='amplification data')
ax1.plot(x_int, y_fit, 'b--', label=r"$f(x) = A + B \tanh\left(\frac{x-x_0}{\sigma}\right)$")
ax1.legend(loc='upper left')

ax2 = fig.add_subplot(212)
ax2.set_xlabel('cycle')
ax2.set_ylabel(r"${\Delta}Rn$'")
ax2.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax2.xaxis.set_minor_locator(ticker.MultipleLocator(1))
ax2.plot(x2, der, label=f'first derivative, maximum in {round(max_fit[0], 2)}')
ax2.legend(loc='upper left')

plt.show()
