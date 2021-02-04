from os.path import join

import numpy as np

from code.fitter import s_shaped_fit, linear_fit
from code.plotter import plot_linear_approximation, create_subplots_figure, add_plot, plot_single, save_subplots_figure


class IncorrectDetectionMethodException(BaseException):
    pass


class IncorrectYaxesException(BaseException):
    pass


def amplification_data_process(x_name, x, wells, data, detection, threshold, pmod):
    # curve data calculations
    std_curve_data = {x_name: [], "cts": [], "drfus": []}

    if pmod == "multiplot":
        fig = create_subplots_figure(data[wells[0]]['x'], detection, threshold)
    else:
        fig = None

    for well, xp in zip(wells, x):
        ct, drfu = _process_well(fig, well, data[well]['x'], data[well]['y'], detection=detection,
                                 threshold=threshold, pmod=pmod)
        std_curve_data[x_name].append(xp)
        std_curve_data["cts"].append(ct)
        std_curve_data["drfus"].append(drfu)

    if pmod == "multiplot":
        save_subplots_figure("multiplot")

    # save curve data
    with open(join("results", "cts.txt"), "w") as f:
        f.write(f"well\t{x_name}\tct\tdrfu\n")
        for well, x, ct, drfu in zip(wells, std_curve_data[x_name], std_curve_data["cts"], std_curve_data["drfus"]):
            f.write(f"{well}\t{x}\t{ct}\t{drfu}\n")
    return std_curve_data


def curve_data_process(curve_data, x_name, y_axes='ct', method='lsq', log_x: bool = True, eff: bool = True):
    if log_x:
        x = np.log10(np.array(curve_data[x_name]))
        x_label = f"log({x_name})"
    else:
        x = np.array(curve_data[x_name])
        x_label = x_name

    if y_axes == "ct":
        y = np.array(curve_data["cts"])
        y_label = "Ct"
    elif y_axes == "drfu":
        y = np.array(curve_data["drfus"])
        y_label = r"${\Delta}Rn$'"
    else:
        raise IncorrectYaxesException(f"Incorrect y axes: {y_axes}")

    plot_linear_approximation(*linear_fit(x, y, method), eff=eff, x_label=x_label, y_label=y_label)


def _process_well(fig, name: str, x: list, y: list, detection="linear", threshold=0, pmod="singleplot") -> (float, float):
    x_fit, y_fit = s_shaped_fit(x, y)

    # derivative
    der = np.diff(y_fit) / np.diff(x_fit)
    x_der = (x_fit[:-1] + x_fit[1:]) / 2

    ct, df = _detect_signal_point(x_fit, y_fit, x_der, der, detection, threshold)

    if pmod == "multiplot":
        add_plot(fig, name, x, y, x_fit, y_fit, x_der, der)
    if pmod == "singleplot":
        plot_single(name, x, y, x_fit, y_fit, x_der, der, ct, df, detection, threshold)
    print(f"{name} data fitted: Ct = {round(ct)}; drfu = {round(df)}")
    return ct, df


def _detect_signal_point(x_fit, y_fit, x_der, der, detection, threshold):
    ct, df = 0, 0
    if detection == "linear":
        max_fit = max(zip(x_der, der), key=lambda t: t[1])
        ct = round(max_fit[0], 2)
        df = round(max_fit[1])
    elif detection == "threshold":
        for i, yf in enumerate(y_fit):
            if yf > threshold:
                ct, df = x_fit[i], der[i]
                break
    else:
        raise IncorrectDetectionMethodException(f"Unknown detection method: {detection}")
    return ct, df
