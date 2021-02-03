from os import listdir, remove
from os.path import join
import logging

logging.basicConfig(filename='.log', filemode='w', level=logging.ERROR)


try:
    from code.dataExtractor import extract_config, extract_data
    from code.prosessor import fit_data, plot_curve

    config = extract_config()

    # well extracting
    data = extract_data(config["annealing_filename"])

    # clear old results
    for file in listdir("results"):
        remove(join("results", file))

    # ct calculations process
    std_curve_data = {config["x_name"]: [], "cts": [], "drfus": []}
    with open(join("results", "cts.txt"), "w") as f:
        f.write("well\tct\tdrfu\n")
        for well, xp in zip(config["wells"], config["x"]):
            if str(well) != "nan":
                ct, drfu = fit_data(well, data[well]['x'], data[well]['y'], detection=config["detection"],
                                    threshold=config["threshold"])
                std_curve_data[config["x_name"]].append(xp)
                std_curve_data["cts"].append(ct)
                std_curve_data["drfus"].append(drfu)
                f.write(f"{well}\t{ct}\t{drfu}\n")

    # plot standard curve
    plot_curve(std_curve_data, config["x_name"], y_axes=config["y_axes"], method=config["method"],
               log_x=config["need_log_x"], eff=config["need_eff"])

except Exception as e:
    logging.exception("Exception occurred")
