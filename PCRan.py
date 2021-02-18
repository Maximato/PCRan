from os import listdir, remove, mkdir
from os.path import join, isdir
import logging

logging.basicConfig(filename='.log', filemode='w', level=logging.ERROR)


try:
    from code.extractor import extract_config, extract_raw_data, extract_data_for_linear_fit
    from code.prosessor import amplification_data_process, linear_fit_data_process, plot_linear_approximation, \
        get_linear_fit_data

    # clear old results
    if isdir("results"):
        for file in listdir("results"):
            remove(join("results", file))
    else:
        mkdir("results")

    config = extract_config()

    if config["mode"] == "rampl":
        # well extracting
        data = extract_raw_data(config["filename"])

        # ct, drfu calculations process
        ttr_data = amplification_data_process(config["x_name"], config["x"], config["wells"], data,
                                                   config["detection"], config["threshold"], config["pmod"])
        line_fit_data = get_linear_fit_data(config["x_name"], config["y_name"], ttr_data)

    elif config["mode"] == "lfd":
        # data extracting
        line_fit_data = extract_data_for_linear_fit(config["filename"])
        line_fit_data["x_name"] = config["x_name"]
        line_fit_data["y_name"] = config["y_name"]
    else:
        raise AttributeError(f"Unsupported mode: {config['mode']}")

    # plot linear fit
    linear_fit_data_process(line_fit_data, method=config["method"],
                            log_x=config["need_log_x"], eff=config["need_eff"])

except Exception as e:
    logging.exception("Exception occurred")
