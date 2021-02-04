import math
import pandas as pd


def extract_config() -> dict:
    xls = pd.ExcelFile('config.xls')
    sheet = xls.parse(0)
    return {"annealing_filename": sheet["filename"][0],
            "method": str(sheet["method"][0]),
            "y_axes": str(sheet["y_axes"][0]),
            "detection": str(sheet["detection"][0]),
            "threshold": sheet["threshold"][0],
            "wells": [well for well in sheet["wells"] if str(well) != "nan"],
            "x": sheet["x"],
            "x_name": sheet["x_name"][0],
            "need_log_x": bool(sheet["need_log_x"][0]),
            "need_eff": bool(sheet["need_eff"][0]),
            "pmod": str(sheet["pmod"][0])
            }


def extract_data(filename: str) -> dict:
    xls = pd.ExcelFile(filename)
    sheet = xls.parse(1)

    well = sheet['Block Type'][7:]
    cycles = sheet['Unnamed: 2'][7:]
    drs = sheet['Unnamed: 5'][7:]

    data = {}
    for i, dr in enumerate(drs):
        if not math.isnan(dr):
            if well[i + 7] in data.keys():
                data[well[i + 7]]['x'].append(cycles[i + 7])
                data[well[i + 7]]['y'].append(dr)
            else:
                data[well[i + 7]] = {'x': [cycles[i + 7]], 'y': [dr]}
    return data
