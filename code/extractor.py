import math
import pandas as pd


def extract_config() -> dict:
    """
    Extract configuration parameters from .xls file for running program
    :return: configuration parameters as dict
    """
    xls = pd.ExcelFile('config.xls')
    sheet = xls.parse(0)
    return {"filename": sheet["filename"][0],
            "mode": sheet["mode"][0],
            "method": str(sheet["method"][0]),
            "y_name": str(sheet["y_name"][0]),
            "detection": str(sheet["detection"][0]),
            "threshold": sheet["threshold"][0],
            "wells": [well for well in sheet["wells"] if str(well) != "nan"],
            "x": [x for x in sheet["x"] if str(x) != "nan"],
            "x_name": sheet["x_name"][0],
            "need_log_x": bool(sheet["need_log_x"][0]),
            "need_eff": bool(sheet["need_eff"][0]),
            "pmod": str(sheet["pmod"][0])
            }


def extract_raw_data(filename: str) -> dict:
    """
    Extracting raw data of amplification
    :param filename: path to file with raw data of amplification
    :return: extracted data {'well1': {'x': list, 'y': list},  'well2': {'x': list, 'y': list} ...}
    """
    xls = pd.ExcelFile(filename)
    sheet = xls.parse(0)

    well = sheet['Well']
    cycles = sheet['Cycle']
    drs = sheet['dRn']

    data = {}
    for i, dr in enumerate(drs):
        if not math.isnan(dr):
            if well[i] in data.keys():
                data[well[i]]['x'].append(cycles[i])
                data[well[i]]['y'].append(dr)
            else:
                data[well[i]] = {'x': [cycles[i]], 'y': [dr]}
    return data


def extract_data_for_linear_fit(filename: str) -> dict:
    """
    Extracting data for fitting by line
    :param filename: path to file with data
    :return: data dict {"x": list, "y": list}
    """
    data = {"x": [], "y": []}
    with open(filename, "r") as f:
        for line in f:
            x, y = line.split()
            data["x"].append(float(x))
            data["y"].append(float(y))
    return data
