from os import listdir, remove
from os.path import join

from code.dataExtractor import extract_config, extract_data
from code.prosessor import fit_data, plot_std_curve

config = extract_config()
annealing_filename, wells, conc = config["annealing_filename"], config["wells"], config["conc"]

data = extract_data(annealing_filename)

# clear old results
for file in listdir("results"):
    remove(join("results", file))

# run process
std_curve_data = {"conc": [], "cts": []}
with open(join("results", "cts.txt"), "w") as f:
    f.write("well\tct\n")
    for well, c in zip(wells, conc):
        ct = fit_data(well, data[well]['x'], data[well]['y'])
        std_curve_data["conc"].append(c)
        std_curve_data["cts"].append(ct)
        f.write(f"{well}\t{ct}\n")

# plot standard curve
plot_std_curve(std_curve_data)
