import math
import pandas as pd


def extract_config() -> dict:
    xls = pd.ExcelFile('config.xls')
    sheet = xls.parse(0)
    annealing_filename = sheet["filename"][0]
    method = sheet["method"][0]
    wells = sheet["wells"]
    conc = sheet["conc"]
    return {"annealing_filename": annealing_filename, "method": method, "wells": wells, "conc": conc}


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
