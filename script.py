from os import listdir, remove
from os.path import join

from code.dataExtractor import extract_config, extract_data
from code.prosessor import fit_data

config = extract_config()
annealing_filename, wells = config["annealing_filename"], config["wells"]

data = extract_data(annealing_filename)

# clear old results
for file in listdir("results"):
    remove(join("results", file))

# run process
with open(join("results", "cts.txt"), "w") as f:
    f.write("well\tct\n")
    for well in wells:
        ct = fit_data(well, data[well]['x'], data[well]['y'])
        f.write(f"{well}\t{ct}\n")
