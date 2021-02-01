from os.path import join

import numpy as np
import matplotlib.pyplot as plt

import matplotlib.ticker as ticker

from scipy.optimize import curve_fit


class NoSuchMethodException(BaseException):
    pass


class NotSupportedMethodForThisData(BaseException):
    pass


def fit_data(name: str, x: list, y: list) -> float:
    x = np.array(x)
    y = np.array(y)

    x_int = np.linspace(x[0], x[-1], 1000)
    fit, _ = curve_fit(_func, x, y, p0=[7e+04, 7e+04, 30, 3])
    y_fit = _func(x_int, *fit)

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
    ax1.plot(x, y, 'k.', label='amplification data')
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
    plt.close()
    print(f"{name} data fitted: Ct({name}) = {ct}")
    return ct


def plot_linear_approximation(x, y, method: str = 'lsq'):
    err = None
    # MLS (least square)
    if method == "lsq":
        title = 'Метод наименьших квадратов'
        mx = np.mean(x)
        my = np.mean(y)

        covx = np.mean((x - mx) ** 2)
        covy = np.mean((y - my) ** 2)

        alpha = (np.mean(x * y) - mx * my) / (np.mean(x ** 2) - mx ** 2)
        beta = my - alpha * mx

        dalpha = np.sqrt(1 / (len(x) - 2) * (covy / covx - alpha ** 2))
        dbeta = dalpha * np.sqrt(np.mean(x ** 2))
    # hi2 method
    elif method == "hi2":
        title = 'Хи 2 метод'
        points = _get_unique_points(x, y)
        x = np.array(points['x'])
        y = np.array(points['y'])
        err = np.array(points['err'])
        if 0 in err:
            raise NotSupportedMethodForThisData("This method not supported for points without error")
        weights = 1 / err

        wmx = _wmean(x, weights)
        wmy = _wmean(y, weights)

        covx = np.mean((x - np.mean(x)) ** 2)

        alpha = (_wmean(x * y, weights) - wmx * wmy) / (_wmean(x ** 2, weights) - wmx ** 2)
        beta = wmy - alpha * wmx

        dalpha = np.sqrt(1 / (sum(weights) * covx))
        dbeta = dalpha * np.sqrt(np.mean(x ** 2))
    else:
        raise NoSuchMethodException(f"Unknown method: {method}")

    label_info = f'Fitted line:\ny={round(alpha, 2)}*x+{round(beta, 2)}\n' + \
                 r"${\Delta\alpha}$" + f"={round(dalpha, 2)}, " + r"${\Delta\beta}$" + f"={round(dbeta, 2)}"

    plt.title(title)
    plt.errorbar(x, y, yerr=err, fmt='.k', ecolor='red', elinewidth=1, capsize=2)
    plt.plot([min(x), max(x)], alpha * np.array([min(x), max(x)]) + beta, 'b--', label=label_info)
    plt.legend()
    return alpha, beta, dalpha, dbeta


def plot_std_curve(std_curve_data, x_name, method='lsq', log_x: bool = True, eff: bool = True):
    if log_x:
        x = np.log10(np.array(std_curve_data["conc"]))
        x_label = f"log({x_name})"
    else:
        x = np.array(std_curve_data[x_name])
        x_label = x_name
    y = np.array(std_curve_data["cts"])

    alpha, beta, dalpha, dbeta = plot_linear_approximation(x, y, method=method)

    if eff:
        E = (10 ** (1 / np.abs(alpha)) - 1) * 100
        dE = 10 ** (1 / np.abs(alpha)) * np.log(10) / alpha ** 2 * dalpha * 100
        bottom, top = plt.ylim()
        left, right = plt.xlim()
        text = f"Эффективность\nE = {round(E, 1)}" + r"${\pm}$" + f"{round(dE, 1)} %"
        plt.text(left + (right - left) / 30, bottom + (top - bottom) / 30, text)

    plt.xlabel(x_label)
    plt.ylabel("Ct")
    # plt.show()
    plt.savefig(join("results", "std_curve.png"), bbox_inches='tight')


# fit to a global function
def _func(x, A, B, x0, sigma):
    return A + B * np.tanh((x - x0) / sigma)


def _get_unique_points(x, y) -> dict:
    combine = dict()
    for xp, yp in zip(x, y):
        if xp not in combine:
            combine[xp] = [yp]
        else:
            combine[xp].append(yp)

    points = {'x': [], 'y': [], 'err': []}
    for p in combine:
        points['x'].append(p)
        points['y'].append(np.mean(combine[p]))
        points['err'].append(np.abs(max(combine[p]) - min(combine[p])) / 2)
    return points


def _wmean(x, weights):
    return sum(x * weights) / sum(weights)


# st BLA1 data
std_data = {
    "conc": [10, 10, 1, 1, 1 / 10, 1 / 10, 1 / 100, 1 / 100, 1e-03, 1e-03, 1e-04, 1e-04, 1e-05, 1e-05, 1e-06, 1e-06],
    "cts": [12.707, 12.928, 15.401, 15.854, 19.434, 19.443, 23.635, 23.632, 26.985, 26.949, 31.618, 31.57, 32.797,
            34.331, 34.953, 34.009]
}
# plot_std_curve(std_data, "conc")
