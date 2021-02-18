from os.path import join

import numpy as np

from code.fitter import s_shaped_fit, linear_fit
from code.plotter import plot_linear_approximation, create_subplots_figure, add_plot, plot_single, save_subplots_figure


class IncorrectDetectionMethodException(Exception):
    pass


class IncorrectYaxesException(Exception):
    pass


def amplification_data_process(x_name, x_line_fit, wells, data, detection, threshold, pmod):
    # curve data calculations
    ttr_data = {x_name: [], "cts": [], "drfus": []}

    if pmod == "multiplot":
        fig = create_subplots_figure(data[wells[0]]['x'], detection, threshold)
    else:
        fig = None

    # colors calculations
    colors_code = dict()
    for xp, code in zip(set(x_line_fit), [each for each in np.linspace(0, 1, len(set(x_line_fit)))]):
        colors_code[xp] = code

    # amplification data process
    colored = []
    for well, xp in zip(wells, x_line_fit):
        if xp not in colored:
            label = f"{x_name} = {xp}"
            colored.append(xp)
        else:
            label = None

        ct, drfu = _process_well(fig, well, colors_code[xp], data[well]['x'], data[well]['y'], detection=detection,
                                 threshold=threshold, pmod=pmod, label=label)
        ttr_data[x_name].append(xp)
        ttr_data["cts"].append(ct)
        ttr_data["drfus"].append(drfu)
    if pmod == "multiplot":
        save_subplots_figure("multiplot")

    # save linear fit data
    with open(join("results", "ttr_data.txt"), "w") as f:
        f.write(f"well\t{x_name}\tct\tdrfu\n")
        for well, x_line_fit, ct, drfu in zip(wells, ttr_data[x_name], ttr_data["cts"], ttr_data["drfus"]):
            f.write(f"{well}\t{x_line_fit}\t{ct}\t{drfu}\n")
    return ttr_data


def linear_fit_data_process(linear_fit_data, method='lsq', log_x: bool = True, eff: bool = True):
    x_name, y_name = linear_fit_data["x_name"], linear_fit_data["y_name"]
    if log_x:
        x = np.log10(np.array(linear_fit_data["x"]))
        x_label = f"log({x_name})"
    else:
        x = np.array(linear_fit_data["x"])
        x_label = x_name

    y = np.array(linear_fit_data["y"])

    plot_linear_approximation(*linear_fit(x, y, method), eff=eff, x_label=x_label, y_label=y_name)


def get_linear_fit_data(x_name: str, y_name: str, ttr_data: dict) -> dict:
    if y_name == "ct":
        y = ttr_data["cts"]
        y_label = "Ct"
    elif y_name == "drfu":
        y = ttr_data["drfus"]
        y_label = r"${\Delta}Rn$'"
    else:
        raise IncorrectYaxesException(f"Incorrect y axes: {y_name}")
    return {"x": ttr_data[x_name], "y": y, "x_name": x_name, "y_name": y_label}


def _process_well(fig, name: str, color_code, x: list, y: list, detection="linear", threshold=0, pmod="singleplot",
                  label=None) -> (float, float):
    x_fit, y_fit = s_shaped_fit(x, y)

    # derivative
    der = np.diff(y_fit) / np.diff(x_fit)
    x_der = (x_fit[:-1] + x_fit[1:]) / 2

    ct, df = _detect_signal_point(x_fit, y_fit, x_der, der, detection, threshold)

    if pmod == "multiplot":
        add_plot(fig, label, color_code, x, y, x_fit, y_fit, x_der, der)
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
