
# MERPredictor Module

## Overview

The `MERPredictor` module is a Python-based implementation designed for Bayesian regression analysis, specifically to model and predict Mass Eruption Rate (MER) from Total Erupted Mass (TEM). This module facilitates Bayesian inference, posterior sampling, and the generation of predictive intervals. It is tailored for geoscientists working on volcanic eruption analysis.

## Features

1. **Data Preparation**
   - Converts TEM and MER to log space for linear regression modeling.
   - Handles missing values.

2. **Bayesian Regression**
   - Fits a Bayesian linear regression model using Maximum Likelihood Estimation (MLE).
   - Computes posterior distributions for model parameters.

3. **Posterior Sampling**
   - Draws posterior samples for the intercept, slope, and variance using Bayesian inference.

4. **Predictive Analysis**
   - Generates predictive intervals for new data points.
   - Computes posterior predictive percentiles and uncertainties.

5. **MER Predictions**
   - Predicts MER from given TEM values and exports results to CSV.
   - Converts MER predictions to eruption durations.

6. **Visualization**
   - Plots posterior predictive intervals.
   - Displays percentiles versus TEM values.

## Installation

Ensure you have Python 3.7 or higher installed. The module requires the following dependencies:

- `numpy`
- `pandas`
- `matplotlib`
- `scipy`

Install these dependencies using pip if not already installed:

```bash
pip install numpy pandas matplotlib scipy
```

## Usage

### Initializing the Class

```python
import pandas as pd
from mer_predict import MERPredictor

# Load your data into a Pandas DataFrame
data = pd.read_csv('your_dataset.csv')

# Initialize the predictor
predictor = MERPredictor(data)
```

### Sampling from the Posterior

```python
posterior_samples = predictor.sample_posterior(size=10000)
print(posterior_samples.head())
```

### Predictive Intervals

```python
import numpy as np

x_new = np.array([1e9, 5e9])  # Example TEM values
lower, upper = predictor.predictive_intervals(x_new)
print(f"Lower bounds: {lower}, Upper bounds: {upper}")
```

### Predicting MER

```python
tem_values = [1e9, 2e9, 5e9]
results = predictor.predict_mer(tem_values, output_file='predicted_mer.csv')
print(results)
```

### Visualizing Results

```python
predictor.plot_posterior_predictive()
```

## Methods

### Initialization

`__init__(self, data: pd.DataFrame)`  
Initializes the predictor with the input dataset.

### Data Preparation

`_prepare_data(self)`  
Prepares the data for regression by ensuring required columns exist and converting values to log space.

### Model Fitting

`_fit_model(self)`  
Fits a Bayesian linear regression model using MLE.

### Posterior Sampling

`sample_posterior(self, size: int = 10000) -> pd.DataFrame`  
Generates posterior samples for model parameters.

### Predictive Intervals

`predictive_intervals(self, x: np.ndarray, alpha: float = 0.05) -> Tuple[np.ndarray, np.ndarray]`  
Computes predictive intervals for new TEM values.

### Percentile Calculations

`calculate_percentiles(self, x: Union[float, np.ndarray], percentiles: List[int] = [5, 25, 50, 75, 95], num_samples: int = 10000) -> pd.DataFrame`  
Calculates posterior predictive percentiles and uncertainties.

### MER Predictions

`predict_mer(self, tem_values: Union[float, List[float]], output_file: str = 'predicted_mer.csv') -> pd.DataFrame`  
Predicts MER values for given TEM values and saves results to a CSV file.

### Duration Conversion

`convert_percentiles_to_duration(self, tem_values: Union[float, List[float]]) -> pd.DataFrame`  
Converts MER percentiles to eruption durations.

### Visualization

`plot_posterior_predictive(self)`  
Plots posterior predictive PDFs and CDFs.

## Example Dataset

Ensure your dataset has the following columns:

- `TEM_kg`: Total erupted mass (in kilograms).
- `MER_kg/s`: Mass eruption rate (in kilograms per second).

## Contact Details

For questions or support, feel free to reach out to the author or create an issue on the project's repository.

**Dr. Mahmud Muhammad**  
(PhD, MSc, and BSc in Geology)  
Email: [mahmud.geology@hotmail.com](mailto:mahmud.geology@hotmail.com)  
Website: [mahmudm.com](http://mahmudm.com)

## Contributing

Contributions to enhance this module are welcome. Please fork the repository and create a pull request with detailed changes.

## License

This project is licensed under the MIT License.

---
