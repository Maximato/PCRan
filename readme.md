# PCRan

### About
The PCRan program is designed to process raw PCR thermocycler data, downloaded in `.xls` format or fit prepared PCR data in `.txt` format by line (standard line).

## Running
To run the program PCRan you need to install the libraries `pandas`, `matplotlib` and `scipy`, set the necessary parameters in **config.xls** file and run **PCRan.py** script. All results are saved to a folder **results**.

PCRan work in two modes: `rampl` and `lfd`.
- `rampl` is analyze raw amplification data from PCR thermocycler in the `.xls` format. This data is stored as three columns (`Well` -- well ID, `Cycle` -- cycle of amplification, `dRn` -- fluorescence on the current cycle). In this mode PCRan plot amplification curves, calculate Ct for each well, fit this data by line and plot results.
- `lfd` mode is needed to fit by line the prepared data which are specified in the `.txt` file. This data is stored as two columns: where the first column refers to `x` and the second to `y`. In this mode PCRan plot only results of liner fit.

Parameters in **config.xls**:
- `filename` --- the name of the file to use as data
- `mode` --- the type of data the file `filename` contains (`rampl` or `lfd`)
- `method` --- linear fit method (`lsq` or `hi2`)
- `y_name` --- the name of the values used as `y` for linear fit (`ct`, `drfu` or another)
- `x_name` --- the name of the values used as `x` for linear fit
- `need_log_x` --- need to logarithm of the `x` axis
- `need_eff` --- need efficiency calculation
- `wells` --- well IDs whose `ct` or `drfu` is used as `y` when constructing a straight line
- `x` --- values used as `x` for linear fit
- `detection` --- method for determining the point at which a signal is detected (`threshold` or `linear`)
- `threshold` --- number greater than 0, ignored for `linear` detection
- `pmod` --- plotting of amplification signals (`singleplot` or `multiplot`)


You can run PCRan with pre-prepared data located in "static\test_data". Set parameters in **config.xls** according to `Example 1` or `Example 2` and run program.

### Example 1

- `filename` --- **static/test_data/ampl.xls**
- `mode` --- **rampl**
- `method` --- **hi2**
- `y_name` --- **ct**
- `x_name` --- **conc**
- `need_log_x` --- **True**
- `need_eff` --- **True**
- `wells` --- **A1, B1, C1, A2, B2, C2, A3, B3, C3 (in column)**
- `x` --- **10000, 10000, 10000, 100, 100, 100, 1, 1, 1 (in column)**
- `detection` --- **threshold**
- `threshold` --- **5000**
- `pmod` --- **multiplot**

### Example 2

- `filename` --- **static/test_data/conc-ct.txt**
- `mode` --- **lfd**
- `method` --- **lsq**
- `y_name` --- **y**
- `x_name` --- **x**
- `need_log_x` --- **True**
- `need_eff` --- **False**
- `wells` --- *irrelevant*
- `x` --- *irrelevant*
- `detection` --- *irrelevant*
- `threshold` --- *irrelevant*
- `pmod` --- *irrelevant*

## Implementation
### Amplification data approximation
Functions of the sigmoid family are suitable for approximation of PCR reaction amplification data. The program uses hyperbolic tangent fitting function `curve_fit` from `scipy` library.

![formula](https://render.githubusercontent.com/render/math?math=y=A%2BB\th(\cfrac{x-x_0}{\sigma}))

![Alt text](static/pics/fit_amplification.png?raw=true)

### Determination of the threshold number of cycles Ct
Determination of the threshold number of cycles in the program is implemented in two different ways: by the threshold line (by the excess of the fluorescence signal of a given value) or by the linearity point of the amplification curve growth (the maximum value of the derivative of the function that fits the amplification data).

![Alt text](static/pics/ct_by_threshold.png?raw=true)

![Alt text](static/pics/ct_by_linear.png?raw=true)

### Fitting data by line and calculating efficiency
The program implements the fitting data by line by two known methods: the least squares method and the chi 2 method. The chi 2 method requires several replicates (more than one), which are necessary to calculate the errors at a given point. As a rule, few replicates are used in the experiment (less than 10), therefore, the [formula](https://www.animations.physics.unsw.edu.au/sf/toolkits/Errors_and_Error_Estimation.pdf) can be used as an estimate of the errors.

![formula](https://render.githubusercontent.com/render/math?math=\Delta%20x=\cfrac{x^{%2B}%2Bx^-}{2})

Where:
- x<sup>+</sup> is the maximum value of the dataset
- x<sup>-</sup> is the minimum value of the dataset

Also, the program evaluates the errors of the coefficients of the straight line and calculates the efficiency.

![Alt text](static/pics/std_curve.png?raw=true)

## Theory
### PCR amplification
During the amplification process the PCR reaction product accumulates which leads to an exponential increase in the fluorescence signal at the initial stages. Then, there is a gradual slowing down of the reaction and reaching a "plateau" as a result of depletion of the reaction. This dependence can be described by one of the functions of the sigmoid family, for example:

![formula](https://render.githubusercontent.com/render/math?math=y=A%2BB\th(\cfrac{x-x_0}{\sigma}))

### Threshold number of cycles
The cycle threshold indicates at what point the fluorescence signal has reached a certain value or growth phase. The Ct threshold cycle can be different for the same data, depending on the method and different parameters.

### Efficiency calculation
The accumulation of the PCR reaction product is described by an exponential law:

![formula](https://render.githubusercontent.com/render/math?math=C=C_0(1%2BE)^n)

Where:
- C is the product concentration
- C<sub>0</sub> is the initial product concentration
- E is the reaction efficiency
- n is the number of cycles.

In the ideal case, when the doubling of the reaction product occurs for each cycle, the reaction efficiency is 1 and the dependence takes on a simpler form:

![formula](https://render.githubusercontent.com/render/math?math=C=C_{0}2^n)

To assess the effectiveness of E, a standard reaction curve is constructed — the dependence of the number of cycles to a positive reaction response (Ct) on the decimal logarithm of the concentration. This dependence is described by a linear law (a straight line), the slope of which contains information about efficiency. The slope of the standard curve in this case shows how many cycles the product concentration will change by one order of magnitude (that is, 10 times). Thus, equation can be rewritten as:

![formula](https://render.githubusercontent.com/render/math?math=10C_0=C_0(1%2BE)^\alpha)

Where:
- α is the modulus of the slope angle of the standard straight line

Solving this equation for E, we find the formula for calculating the reaction efficiency E. Knowing the error with which the slope angle α was determined, the efficiency error can be estimated using the formula.

![formula](https://render.githubusercontent.com/render/math?math=E=10^\frac{1}{\alpha}-1)

![formula](https://render.githubusercontent.com/render/math?math=\Delta%20E=\cfrac{\ln{10}\times10^\frac{1}{\alpha}}{\alpha^2}\Delta\alpha)

Where:
- E is the efficiency
- α is the slope coefficient of the straight line
- ∆α is the error in estimating the slope angle coefficient of the straight line

### Linear data fit methods
#### Least square method
The simplest method for constructing a direct approximation is the least squares method, which minimizes the sum:

![formula](https://render.githubusercontent.com/render/math?math=S(\alpha,\beta)=\sum_{i=1}^{n}(y_i-\alpha%20x_i-\beta)^2)

Where:
- n is the number of experimental points
- y<sub>i</sub> are the values along the ordinate
- x<sub>i</sub> are the values along the abscissa
- α is the slope parameter of the straight line
- β is the cutoff parameter of the straight line

The solution to the problem of finding the minimum value of the sum S (α, β) has the form:

![formula](https://render.githubusercontent.com/render/math?math=\alpha=\cfrac{\langle%20xy\rangle-\langle%20x\rangle\langle%20y\rangle}{\langle%20x^2\rangle-\langle%20x\rangle^2})

![formula](https://render.githubusercontent.com/render/math?math=\beta=\langle%20y\rangle-\alpha\langle%20x\rangle)

If we assume that the measurement error x is negligible, and the errors in 𝑦 are the same for all experimental points, are independent and have a random nature, then the estimation of the parameter errors is described according to:

![formula](https://render.githubusercontent.com/render/math?math=\Delta\alpha=\sqrt{\cfrac{1}{n-2}(\frac{D_{yy}}{D_{xx}}-\alpha^2)})

![formula](https://render.githubusercontent.com/render/math?math=\Delta\beta=\Delta\alpha\sqrt{\langle%20x^2\rangle})

Where:
- α is the slope coefficient of the straight line,
- n is the number of experimental points
- ![formula](https://render.githubusercontent.com/render/math?math=D_{yy}=\langle(y-%20<y>)^2\rangle) is the covariance y
- ![formula](https://render.githubusercontent.com/render/math?math=D_{xx}=\langle(x-<x>)^2\rangle) is the covariance x

#### Chi Method 2
Another popular method is chi square, which also takes into account the uncertainty of each measurement. This method minimizes the sum of chi 2:

![formula](https://render.githubusercontent.com/render/math?math=\chi^2(\alpha,\beta)=\sum_{i=1}^{n}w_i(y_i-\alpha%20x_i-\beta)^2)

Where:
- ![formula](https://render.githubusercontent.com/render/math?math=w_i=1/\sigma_i^2)
- n is the number of experimental points
- y<sub>i</sub> are the values along the ordinate
- x<sub>i</sub> are the values along the abscissa
- α is the slope parameter of the straight line.
- β is the cutoff parameter of the straight line

The solution to the problem of finding the minimum value of the sum ![formula](https://render.githubusercontent.com/render/math?math=\chi^2(\alpha,\beta)) has the form:

![formula](https://render.githubusercontent.com/render/math?math=\alpha=\cfrac{<xy>'-<x>'<y>'}{<x^2>'-<x>'^2})

![formula](https://render.githubusercontent.com/render/math?math=\beta=<y>'-\alpha<x>')

Where the weighted average is defined as:

![formula](https://render.githubusercontent.com/render/math?math=<x>'=\cfrac{1}{W}\sum_{i=1}^{n}w_i%20x_i)

![formula](https://render.githubusercontent.com/render/math?math=W=\sum_{i=1}^{n}w_i)

The estimation of parameter errors is described according to:

![formula](https://render.githubusercontent.com/render/math?math=\Delta\alpha=\sqrt{\cfrac{1}{WD_{xx}}})

![formula](https://render.githubusercontent.com/render/math?math=\Delta\beta=\Delta\alpha\sqrt{<x^2>})
