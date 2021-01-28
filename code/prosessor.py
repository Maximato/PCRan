from os.path import join

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from scipy.optimize import curve_fit


# fit to a global function
def func(x, A, B, x0, sigma):
    return A+B*np.tanh((x-x0)/sigma)


def fit_data(name: str, x: list, y: list) -> float:
    x = np.array(x)
    y = np.array(y)

    x_int = np.linspace(x[0], x[-1], 1000)
    fit, _ = curve_fit(func, x, y, p0=[7e+04, 7e+04, 30, 3])
    y_fit = func(x_int, *fit)

    # derivative
    der = np.diff(y_fit) / np.diff(x_int)
    x2 = (x_int[:-1] + x_int[1:]) / 2
    max_fit = max(zip(x2, der), key=lambda t: t[1])
    ct = round(max_fit[0], 2)

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
    ax2.plot(x2, der, label=f'first derivative, maximum in {ct}')
    ax2.legend(loc='upper left')

    plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9, hspace=0.3)
    plt.savefig(join("results", name + ".png"), bbox_inches='tight')
    return ct