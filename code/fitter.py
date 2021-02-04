import numpy as np
from scipy.optimize import curve_fit


class NoSuchMethodException(BaseException):
    pass


class NotSupportedMethodForThisDataException(BaseException):
    pass


def s_shaped_fit(x: list, y: list) -> (float, float):
    x, y = np.array(x), np.array(y)

    x_fit = np.linspace(x[0], x[-1], 1000)
    fit, _ = curve_fit(_func, x, y, p0=[7e+04, 7e+04, 30, 3])
    y_fit = _func(x_fit, *fit)
    return x_fit, y_fit


def linear_fit(x, y, method='lsq'):
    # MLS (least square)
    if method == "lsq":
        param_approx = _least_square_approximation(x, y)
    # hi2 method
    elif method == "hi2":
        param_approx = _hi2_approximation(x, y)
    else:
        raise NoSuchMethodException(f"Unknown method: {method}")
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
