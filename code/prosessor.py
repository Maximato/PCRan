import numpy as np
from scipy.optimize import curve_fit

from code.plotter import plot_linear_approximation, plot_amplification_data


class NoSuchMethodException(BaseException):
    pass


class IncorrectDetectionMethodException(BaseException):
    pass


class NotSupportedMethodForThisDataException(BaseException):
    pass


class IncorrectYaxesException(BaseException):
    pass


def fit_data(name: str, x: list, y: list, detection="linear", threshold=0) -> (float, float):
    x, y = np.array(x), np.array(y)

    x_fit = np.linspace(x[0], x[-1], 1000)
    fit, _ = curve_fit(_func, x, y, p0=[7e+04, 7e+04, 30, 3])
    y_fit = _func(x_fit, *fit)

    # derivative
    der = np.diff(y_fit) / np.diff(x_fit)
    x_der = (x_fit[:-1] + x_fit[1:]) / 2

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

    plot_amplification_data(name, x, y, x_fit, y_fit, x_der, der, ct, df, detection, threshold)
    print(f"{name} data fitted: Ct = {round(ct)}; drfu = {round(df)}")
    return ct, df


def plot_curve(std_curve_data, x_name, y_axes='ct', method='lsq', log_x: bool = True, eff: bool = True):
    if log_x:
        x = np.log10(np.array(std_curve_data[x_name]))
        x_label = f"log({x_name})"
    else:
        x = np.array(std_curve_data[x_name])
        x_label = x_name

    if y_axes == "ct":
        y = np.array(std_curve_data["cts"])
        y_label = "Ct"
    elif y_axes == "drfu":
        y = np.array(std_curve_data["drfus"])
        y_label = r"${\Delta}Rn$'"
    else:
        raise IncorrectYaxesException(f"Incorrect y axes: {y_axes}")

    # MLS (least square)
    if method == "lsq":
        param_approx = _least_square_approximation(x, y)
    # hi2 method
    elif method == "hi2":
        param_approx = _hi2_approximation(x, y)
    else:
        raise NoSuchMethodException(f"Unknown method: {method}")
    plot_linear_approximation(*param_approx, eff=eff, x_label=x_label, y_label=y_label)
    return param_approx


def _least_square_approximation(x, y):
    title = 'Метод наименьших квадратов'
    err = None
    mx = np.mean(x)
    my = np.mean(y)

    covx = np.mean((x - mx) ** 2)
    covy = np.mean((y - my) ** 2)

    alpha = (np.mean(x * y) - mx * my) / (np.mean(x ** 2) - mx ** 2)
    beta = my - alpha * mx

    dalpha = np.sqrt(1 / (len(x) - 2) * (covy / covx - alpha ** 2))
    dbeta = dalpha * np.sqrt(np.mean(x ** 2))
    return title, x, y, err, alpha, beta, dalpha, dbeta


def _hi2_approximation(x, y):
    title = 'Хи 2 метод'
    points = _get_unique_points(x, y)
    x = np.array(points['x'])
    y = np.array(points['y'])
    err = np.array(points['err'])
    if 0 in err:
        raise NotSupportedMethodForThisDataException("This method not supported for points without error")
    weights = 1 / err

    wmx = _wmean(x, weights)
    wmy = _wmean(y, weights)

    covx = np.mean((x - np.mean(x)) ** 2)

    alpha = (_wmean(x * y, weights) - wmx * wmy) / (_wmean(x ** 2, weights) - wmx ** 2)
    beta = wmy - alpha * wmx

    dalpha = np.sqrt(1 / (sum(weights) * covx))
    dbeta = dalpha * np.sqrt(np.mean(x ** 2))
    return title, x, y, err, alpha, beta, dalpha, dbeta


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
# plot_linear_approximation(std_data, "conc")
