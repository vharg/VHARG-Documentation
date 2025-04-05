
# PlumeHeightPredictor

The `PlumeHeightPredictor` Python module is designed for Bayesian regression modeling to predict volcanic plume heights based on mass eruption rates (MER). It includes functionalities for data preparation, model fitting, posterior sampling, percentile calculations, uncertainty estimation, and visualization.

## Features

- **Bayesian Linear Regression:** Perform regression to model the relationship between MER and plume height.
- **Posterior Sampling:** Draw samples from the posterior distributions of the regression parameters.
- **Predictive Intervals:** Calculate predictive intervals for new data points.
- **Percentile Calculations:** Compute percentiles of the predictive distributions with uncertainty estimation.
- **Visualization:** Create various plots, including posterior predictive distributions, percentile comparisons, and contour plots.

## Installation

Ensure you have the following Python packages installed:

- `numpy`
- `pandas`
- `matplotlib`
- `scipy`

Install the dependencies using pip:

```bash
pip install numpy pandas matplotlib scipy
```

## Usage

### 1. Initialization

Create an instance of the `PlumeHeightPredictor` class by providing a pandas DataFrame containing the required columns (`MER_kg/s` and `Height_km.a.v.l`).

```python
from plume_rise_predict import PlumeHeightPredictor

# Example DataFrame
data = pd.DataFrame({
    "MER_kg/s": [1e6, 1e7, 1e8],
    "Height_km.a.v.l": [10, 15, 20]
})

predictor = PlumeHeightPredictor(data)
```

### 2. Sampling Posterior

Generate samples from the posterior distributions of the model parameters:

```python
posterior_samples = predictor.sample_posterior(size=10000)
print(posterior_samples.head())
```

### 3. Predictive Intervals

Compute predictive intervals for new MER values:

```python
mer_values = np.array([1e6, 1e7, 1e8])
lower, upper = predictor.predictive_intervals(mer_values)
print("Lower bounds:", lower)
print("Upper bounds:", upper)
```

### 4. Percentiles with Uncertainty

Calculate posterior predictive percentiles with uncertainty for new MER values:

```python
percentiles_results = predictor.calculate_percentiles_with_uncertainty(
    x=np.array([1e6, 1e7, 1e8]),
    percentiles=[5, 25, 50, 75, 95]
)
print(percentiles_results)
```

### 5. Visualization

#### Posterior Predictive Plot

Visualize posterior predictive distributions:

```python
predictor.plot_posterior_predictive()
```

#### Percentiles vs MER

Visualize percentile predictions:

```python
predictor.plot_percentiles_vs_mer()
```

#### Contour Plot

Generate a contour plot showing relationships between MER and predicted percentiles:

```python
x_vals = np.logspace(6, 8, 50)
predictor.plot_percentiles_with_uncertainty(x_vals)
```

## Methods

### `__init__(data)`
Initializes the class with the input dataset.

- **Parameters:**
  - `data` (pd.DataFrame): DataFrame with columns `MER_kg/s` and `Height_km.a.v.l`.

### `sample_posterior(size=10000)`
Draw samples from the posterior distributions.

- **Parameters:**
  - `size` (int): Number of posterior samples.
- **Returns:**
  - `pd.DataFrame`: DataFrame containing sampled parameters (`intercept`, `slope`, `sigma2`).

### `predictive_intervals(x, alpha=0.05)`
Compute predictive intervals for new data points.

- **Parameters:**
  - `x` (np.ndarray): New `MER_kg/s` values.
  - `alpha` (float): Significance level.
- **Returns:**
  - `Tuple[np.ndarray, np.ndarray]`: Lower and upper predictive intervals.

### `calculate_percentiles_with_uncertainty(x, percentiles=[5, 25, 50, 75, 95], num_samples=10000)`
Calculate posterior predictive percentiles with uncertainty.

- **Parameters:**
  - `x` (float or np.ndarray): New `MER_kg/s` values.
  - `percentiles` (list): Percentiles to calculate.
  - `num_samples` (int): Number of posterior samples.
- **Returns:**
  - `pd.DataFrame`: DataFrame with calculated percentiles and uncertainties.

### `plot_posterior_predictive()`
Visualize posterior predictive distributions.

### `plot_percentiles_vs_mer()`
Plot predicted percentiles vs `MER_kg/s`.

### `plot_percentiles_with_uncertainty(x_vals, percentiles=[5, 25, 50, 75, 95])`
Plot percentiles with uncertainty ribbons.

## Author

**Dr. Mahmud Muhammad**  
(PhD, MSc, and BSc in Geology)  
Email: [mahmud.geology@hotmail.com](mailto:mahmud.geology@hotmail.com)  
Website: [mahmudm.com](http://mahmudm.com)

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## Contact

For further inquiries, please contact the author at the email address provided above.
