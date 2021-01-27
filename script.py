import math
import pandas as pd
import numpy as np

from matplotlib import pyplot
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

print(results)

# getting x and y from xls file
x = np.array(results['A1']['x'])
y = np.array(results['A1']['y'])

# interpolate + smooth
f = interpolate.interp1d(x, y, kind="linear")
x_int = np.linspace(x[0], x[-1], 1000)
window_size, poly_order = 201, 3
y_int = savgol_filter(f(x_int), window_size, poly_order)


# or fit to a global function
def func(x, A, B, x0, sigma):
    return A+B*np.tanh((x-x0)/sigma)


fit, _ = curve_fit(func, x, y)
y_fit = func(x_int, *fit)

# derivative
der = np.diff(y_fit) / np.diff(x_int)
x2 = (x_int[:-1] + x_int[1:]) / 2

pyplot.plot(x, y, 'r.', label='amplification data')
pyplot.plot(x_int, y_int, 'k', label="Smoothed curve")
pyplot.plot(x_int, y_fit, 'b--', label=r"$f(x) = A + B \tanh\left(\frac{x-x_0}{\sigma}\right)$")
pyplot.plot(x2, der)
pyplot.legend(loc='best')
pyplot.show()
