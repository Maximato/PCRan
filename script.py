from os import listdir, remove
from os.path import join
import logging

logging.basicConfig(filename='.log', filemode='w', level=logging.ERROR)


try:
    from code.dataExtractor import extract_config, extract_data
    from code.prosessor import fit_data, plot_std_curve

    config = extract_config()

    # well extracting
    data = extract_data(config["annealing_filename"])

    # clear old results
    for file in listdir("results"):
        remove(join("results", file))

    # ct calculations process
    std_curve_data = {config["x_name"]: [], "cts": []}
    with open(join("results", "cts.txt"), "w") as f:
        f.write("well\tct\n")
        for well, xp in zip(config["wells"], config["x"]):
            ct = fit_data(well, data[well]['x'], data[well]['y'])
            std_curve_data[config["x_name"]].append(xp)
            std_curve_data["cts"].append(ct)
            f.write(f"{well}\t{ct}\n")

    # plot standard curve
    plot_std_curve(std_curve_data, config["x_name"], method=config["method"], log_x=config["need_log_x"],
                   eff=config["need_eff"])

except Exception as e:
    logging.exception("Exception occurred")
