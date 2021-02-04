from os.path import join

import numpy as np
import matplotlib.pyplot as plt

import matplotlib.ticker as ticker


def plot_linear_approximation(title: str, x, y, err, alpha: float, beta: float, dalpha: float, dbeta: float,
                              eff: bool = True, x_label: str = "x", y_label="y"):
    label_info = f'Fitted line:\ny={round(alpha, 2)}*x+{round(beta, 2)}\n' + \
                 r"${\Delta\alpha}$" + f"={round(dalpha, 2)}, " + r"${\Delta\beta}$" + f"={round(dbeta, 2)}"
    plt.title(title)
    plt.errorbar(x, y, yerr=err, fmt='.k', ecolor='red', elinewidth=1, capsize=2)
    plt.plot([min(x), max(x)], alpha * np.array([min(x), max(x)]) + beta, 'b--', label=label_info)
    plt.legend()

    if eff:
        E = (10 ** (1 / np.abs(alpha)) - 1) * 100
        dE = 10 ** (1 / np.abs(alpha)) * np.log(10) / alpha ** 2 * dalpha * 100
        bottom, top = plt.ylim()
        left, right = plt.xlim()
        text = f"Эффективность\nE = {round(E, 1)}" + r"${\pm}$" + f"{round(dE, 1)} %"
        plt.text(left + (right - left) / 30, bottom + (top - bottom) / 30, text)

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.savefig(join("results", "std_curve.png"), bbox_inches='tight', dpi=150)


def create_subplots_figure(x, detection, threshold):
    fig = plt.figure(figsize=(15, 10))

    # adjust ax1
    ax1 = fig.add_subplot(211)
    _adjust_top_axe(ax1, x, detection, threshold)

    # adjust ax2
    ax2 = fig.add_subplot(212)
    _adjust_bottom_axe(ax2)
    return fig


def save_subplots_figure(name):
    plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9, hspace=0.3)
    plt.savefig(join("results", name + ".png"), bbox_inches='tight', dpi=150)
    plt.close()


def plot_single(name, x, y, x_fit, y_fit, x_der, der, ct, df, detection, threshold):
    ax1, ax2 = create_subplots_figure(x, detection, threshold).get_axes()

    # plotting
    ax1.plot(x, y, 'k.', markersize=3, label=f'{name} amplification data')
    ax1.plot(x_fit, y_fit, 'b--', label=r"$f(x) = A + B \tanh\left(\frac{x-x_0}{\sigma}\right)$")
    ax1.legend()

    if detection == "linear":
        ax2.plot([ct, ct], [0, df], 'k--')
        ax2.text(ct-5, df+df*0.05, f"({round(ct, 1)};{round(df, 1)})")
    ax2.plot(x_der, der, label=f'{name} first derivative')
    ax2.axis(ymin=0, ymax=max(der) + max(der) * 0.2)
    ax2.legend()

    save_subplots_figure(name)


def add_plot(figure, name, x, y, x_fit, y_fit, x_der, der):
    ax1, ax2 = figure.get_axes()
    ax1.plot(x, y, '.', markersize=3, label=name)
    ax1.plot(x_fit, y_fit, '--')
    ax1.legend()

    ax2.plot(x_der, der, label=f'{name} first derivative')
    new_top = max(der) + max(der) * 0.2

    if new_top > ax2.get_ylim()[1]:
        ax2.axis(ymin=0, ymax=new_top)
    ax2.legend()


def _adjust_top_axe(ax1, x, detection, threshold):
    ax1.set_xlabel('cycle')
    ax1.set_ylabel(r'${\Delta}Rn$')
    ax1.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax1.xaxis.set_minor_locator(ticker.MultipleLocator(5))
    if detection == "threshold":
        ax1.plot([x[0], x[-1]], [threshold, threshold], 'r--', label="threshold")
    ax1.legend()


def _adjust_bottom_axe(ax2):
    ax2.set_xlabel('cycle')
    ax2.set_ylabel(r"${\Delta}Rn$'")
    ax2.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax2.xaxis.set_minor_locator(ticker.MultipleLocator(5))
    ax2.legend()
