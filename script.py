from os import listdir, remove
from os.path import join
import logging

logging.basicConfig(filename='.log', filemode='w', level=logging.ERROR)


try:
    from code.extractor import extract_config, extract_data
    from code.prosessor import amplification_data_process, curve_data_process

    config = extract_config()

    # well extracting
    data = extract_data(config["annealing_filename"])

    # clear old results
    for file in listdir("results"):
        remove(join("results", file))

    # ct calculations process
    std_curve_data = amplification_data_process(config["x_name"], config["x"], config["wells"], data,
                                                config["detection"], config["threshold"], config["pmod"])

    # plot standard curve
    curve_data_process(std_curve_data, config["x_name"], y_axes=config["y_axes"], method=config["method"],
               log_x=config["need_log_x"], eff=config["need_eff"])

except Exception as e:
    logging.exception("Exception occurred")
