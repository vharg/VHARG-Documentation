'''
## Contact Details

**Dr. Mahmud Muhammad**  
(PhD, MSc, and BSc in Geology)  
Email: [mahmud.geology@hotmail.com](mailto:mahmud.geology@hotmail.com)  
Website: [mahmudm.com](http://mahmudm.com) 

'''
#####################
import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_probability as tfp
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


tfd = tfp.distributions
tfb = tfp.bijectors

####################

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import t, invgamma, multivariate_normal
from typing import Optional, Tuple, List, Union


class PlumeHeightPredictor:
    
    """
PlumeHeightPredictor

This class predicts volcanic plume heights based on Mass Eruption Rates (MERs) using Bayesian linear regression. 
It fits a logarithmic model to input data, samples posterior distributions, and generates uncertainty-aware 
predictions for plume heights.

Key Features:
- Bayesian linear regression using Maximum Likelihood Estimation (MLE).
- Sampling from posterior distributions for intercept, slope, and variance.
- Prediction of plume heights at specified MERs with percentile-based uncertainty quantification.
- Visualization of posterior predictive distributions, credible intervals, and percentiles.

Attributes:
    data (pd.DataFrame): Input data containing columns for Mass Eruption Rate and plume height.
    xvar (str): Column name representing the independent variable (MER).
    yvar (str): Column name representing the dependent variable (plume height).
    beta (np.ndarray): MLE-estimated coefficients for the linear model.
    sigma2 (float): MLE-estimated variance of the residuals.
    posterior_samples (pd.DataFrame): Posterior samples of model parameters.
    predictions (pd.DataFrame): Predicted plume heights and uncertainty measures.

Methods:
    __init__(data: pd.DataFrame):
        Initializes the predictor with input data and prepares the dataset.
    
    _prepare_data():
        Prepares the dataset by ensuring required columns exist, removing NaNs, and transforming data to logarithmic scale.

    _fit_model():
        Fits a linear model to the data using Maximum Likelihood Estimation.

    sample_posterior(size: int = 100000) -> pd.DataFrame:
        Samples the posterior distributions for the model parameters.

    calculate_percentiles_with_uncertainty(
        x: Union[float, np.ndarray], 
        percentiles: List[int] = [5, 25, 50, 75, 95], 
        num_samples: int = 100
    ) -> pd.DataFrame:
        Calculates percentiles of predicted plume heights with uncertainty.

    predict_height_with_uncertainty(
        mer_values: Union[float, List[float]], 
        output_file: str = 'predicted_height_with_uncertainty.csv', 
        percentiles: List[int] = [5, 25, 50, 75, 95], 
        plot: bool = True
    ) -> pd.DataFrame:
        Predicts plume heights for given MER values and saves the results to a file. Optionally generates plots.

    plot_posterior_predictive(num_posterior_samples_to_visualize=100, confidence=0.95):
        Visualizes posterior predictive distributions with credible intervals.

    plot_percentiles_with_uncertainty(percentiles=[]):
        Plots predicted percentiles of plume heights against MER with uncertainty.

    plot_percentiles_vs_mer():
        Creates a 2D filled contour plot showing MER vs. plume height percentiles.
"""

    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.xvar = 'MER_kg/s'
        self.yvar = 'Height_km.a.v.l'
        self._prepare_data()
        self._fit_model()
        self.posterior_samples = None
        self.predictions = None
        # self.find_best_model()
        # self.fit_selected_model()
        # self.models = []
        # self.selected_model = None

    def _prepare_data(self):
        if self.xvar not in self.data.columns or self.yvar not in self.data.columns:
            raise ValueError(f"Columns {self.xvar} and {self.yvar} must exist in the dataset.")

        self.data = self.data.dropna(subset=[self.xvar, self.yvar])
        self.data['log_x'] = np.log10(self.data[self.xvar])
        self.data['log_y'] = np.log10(self.data[self.yvar])

    def _fit_model(self):
        X = np.vstack([np.ones(self.data.shape[0]), self.data['log_x']]).T
        y = self.data['log_y'].values

        self.beta = np.linalg.inv(X.T @ X) @ X.T @ y  # MLE for beta
        residuals = y - X @ self.beta
        self.sigma2 = np.sum(residuals**2) / (len(y) - 2)  # MLE for variance
        self.X = X
        self.y = y
        self.residuals = residuals
        self.posterior_samples = None # Clear cache after model fit

    def sample_posterior(self, size: int = 10000) -> pd.DataFrame:
        if self.posterior_samples is not None:
            return self.posterior_samples  # Use cached samples if available

        samples = []
        for _ in range(size):
            sigma2_sample = invgamma.rvs(self.data.shape[0] / 2, scale=self.sigma2 * self.data.shape[0] / 2)
            beta_sample = multivariate_normal.rvs(mean=self.beta, cov=sigma2_sample * np.linalg.inv(self.X.T @ self.X))
            samples.append([*beta_sample, sigma2_sample])
        
        self.posterior_samples = pd.DataFrame(samples, columns=['intercept', 'slope', 'sigma2'])
        return self.posterior_samples

    

        
    def calculate_percentiles_with_uncertainty(self, x: Union[float, np.ndarray], percentiles: List[int] = [5, 25, 50, 75, 95], num_samples: int = 100) -> pd.DataFrame:
        if isinstance(x, (float, int)):
            x = np.array([x])

        if self.posterior_samples is None:  # Ensure posterior samples are available
            self.sample_posterior()

        log_x = np.log10(x)
        results = pd.DataFrame({'MER_kg/s': x})

        for p in percentiles:
            percentile_values = []
            for _, row in self.posterior_samples.iterrows():
                y_pred = row['intercept'] + row['slope'] * log_x
                percentile_values.append(10**y_pred)
            percentiles_array = np.percentile(percentile_values, p, axis=0)
            results[f'HeightPercentile_{p}'] = percentiles_array

            # # Uncertainty estimation
            # results[f'Uncertainty_Lower_{p}'] = np.percentile(percentile_values, max(p - 5, 0), axis=0)
            # results[f'Uncertainty_Upper_{p}'] = np.percentile(percentile_values, min(p + 5, 100), axis=0)

        if 'HeightPercentile_95' in results and 'HeightPercentile_5' in results:
            results['90%_interpercentile_Height_range_km'] = (results['HeightPercentile_95'] - results['HeightPercentile_5'])

        # if 'Uncertainty_Upper_95' in results and 'Uncertainty_Upper_5' in results:
        #     results['90%_interpercentile_Height_range_km_Uncertainty'] = (
        #         (results['Uncertainty_Upper_95'] - results['Uncertainty_Upper_5'])
        #     )
        #     results['90%_interpercentile_Height_2std'] = (results['90%_interpercentile_Height_range_km'] +
        #                                                   results['90%_interpercentile_Height_range_km_Uncertainty'])
        return results
    
    
#     def calculate_percentiles_with_uncertainty(
#     self,
#     x: Union[float, np.ndarray], 
#     vei: Union[float, np.ndarray] = None,
#     percentiles: List[int] = [5, 25, 50, 75, 95], 
#     num_samples: int = 100, 
#     include_uncertainty: bool = False, 
#     plot: bool = True
# ) -> pd.DataFrame:
#         # Ensure x and vei are arrays
#         if isinstance(x, (float, int)):
#             x = np.array([x])
#         if vei is not None and isinstance(vei, (float, int)):
#             vei = np.array([vei])
        
#         # Validate inputs
#         if vei is not None:
#             if vei is not None and len(vei) != len(x):
#                 raise ValueError("Length of VEI array must match the length of x values.")
#         if self.posterior_samples is None:
#             self.sample_posterior(size=num_samples)

#         # Logarithm of x
#         log_x = np.log10(x)
#         results = pd.DataFrame({'MER_kg/s': x})

#         # VEI constraints
#         vei_constraints = {
#             1: (0.1, 1),       # 100 meters to 1 km
#             2: (1, 5),         # 1 to 5 km
#             3: (3, 15),        # 3 to 15 km
#             4: (10, None),     # >10 km
#             5: (10, None),     # >10 km and more than VEI 4
#             6: (20, None),     # >20 km
#             7: (20, None),     # >20 km and more than VEI 6
#             8: (20, None)      # >20 km and more than VEI 7
#         }

#         # Compute percentiles
#         for p in percentiles:
#             percentile_values = []
#             for _, row in self.posterior_samples.iterrows():
#                 y_pred = row['intercept'] + row['slope'] * log_x
#                 percentile_values.append(10**y_pred)
#             percentiles_array = np.percentile(percentile_values, p, axis=0)

#             # Apply VEI constraints
#             if vei is not None:
#                 for idx, v in enumerate(vei):
#                     min_val, max_val = vei_constraints.get(v, (None, None))
#                     if min_val is not None:
#                         percentiles_array[idx] = max(percentiles_array[idx], min_val)
#                     if max_val is not None:
#                         percentiles_array[idx] = min(percentiles_array[idx], max_val)

#             results[f'HeightPercentile_{p}'] = percentiles_array

#             # Include uncertainty ranges
#             if include_uncertainty:
#                 lower_bound = max(p - 5, 0)
#                 upper_bound = min(p + 5, 100)
#                 uncertainty_values = np.percentile(percentile_values, [lower_bound, upper_bound], axis=0)
#                 results[f'Uncertainty_Lower_{p}'] = uncertainty_values[0]
#                 results[f'Uncertainty_Upper_{p}'] = uncertainty_values[1]

#         # Calculate inter-percentile range
#         if 'HeightPercentile_95' in results and 'HeightPercentile_5' in results:
#             results['90%_interpercentile_Height_range_km'] = (
#                 results['HeightPercentile_95'] - results['HeightPercentile_5']
#             )

#         return results

    def predict_height_with_uncertainty(self, mer_values: Union[float, List[float]], output_file: str = 'predicted_height_with_uncertainty.csv',
                                        percentiles: List[int] = [5, 25, 50, 75, 95], plot: bool = True) -> pd.DataFrame:
        if isinstance(mer_values, (float, int)):
            mer_values = [mer_values]
            
      
        
        mer_values = np.array(mer_values)
        
        
        
        if percentiles is None:
            percentiles = [5, 25, 50, 75, 95]
        
        predictions = self.calculate_percentiles_with_uncertainty(x=mer_values , percentiles=percentiles)
        predictions.to_csv(output_file, index=False)
        print(f"Predictions with uncertainty saved to {output_file}")
        self.predictions = predictions
        if plot:
            self.plot_percentiles_vs_mer()
            self.plot_posterior_predictive()
            self.plot_percentiles_with_uncertainty(percentiles=percentiles)
        
        return predictions

    def plot_posterior_predictive(self, num_posterior_samples_to_visualize=100, confidence=0.95):
        log_x_vals = np.linspace(np.log10(self.data[self.xvar].min()), np.log10(self.data[self.xvar].max()), 100)
        x_vals = 10**log_x_vals  # Convert back to linear scale

        num_posterior_samples = len(self.posterior_samples)
        posterior_predictive_points = np.zeros((num_posterior_samples, len(x_vals)))

        for i in range(num_posterior_samples):
            intercept_sample = self.posterior_samples["intercept"].iloc[i]
            slope_sample = self.posterior_samples["slope"].iloc[i]
            sigma2_sample = self.posterior_samples["sigma2"].iloc[i]

            noise = np.random.normal(0, np.sqrt(sigma2_sample), len(x_vals))
            y_pred = intercept_sample + slope_sample * log_x_vals + noise
            posterior_predictive_points[i] = 10**y_pred

        x_repeated = np.repeat(x_vals, num_posterior_samples)
        y_pred_flat = posterior_predictive_points.T.flatten()

        mean_intercept = self.posterior_samples["intercept"].mean()
        mean_slope = self.posterior_samples["slope"].mean()
        mean_y_pred = mean_intercept + mean_slope * log_x_vals

        lower_percentile = (1 - confidence) / 2 * 100
        upper_percentile = (1 + confidence) / 2 * 100
        credible_intervals = np.percentile(posterior_predictive_points, [lower_percentile, upper_percentile], axis=0)

        plt.figure(figsize=(10, 6))
        plt.scatter(self.data[self.xvar], self.data[self.yvar], color="black", label="Observed Data")
        plt.scatter(x_repeated, y_pred_flat, color="blue", alpha=0.1, label=f"Posterior Predictive Samples n={len(y_pred_flat)}", s=10)
        plt.plot(x_vals, 10**mean_y_pred, color="red", label="Mean Posterior Prediction", linewidth=2)
        plt.fill_between(x_vals, credible_intervals[0], credible_intervals[1], color="black", alpha=0.3, label="Credible Interval")
        plt.xscale("log")
        plt.yscale("log")
        plt.xlabel(self.xvar)
        plt.ylabel(self.yvar)
        plt.legend()
        plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)
        plt.tight_layout()
        plt.show()

    def plot_percentiles_with_uncertainty(self, percentiles=[]):
        results = self.predictions
        plt.figure(figsize=(10, 6))
        for p in percentiles:
            plt.plot(results['MER_kg/s'], results[f'HeightPercentile_{p}'], label=f'{p}th Percentile')
            #plt.fill_between(results['MER_kg/s'], results[f'Uncertainty_Lower_{p}'], results[f'Uncertainty_Upper_{p}'], alpha=0.3)

        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel(self.xvar)
        plt.ylabel(self.yvar)
        plt.title('Percentiles with Uncertainty')
        plt.legend()
        plt.show()

    def plot_percentiles_vs_mer(self):
        results = self.predictions
        mer = results['MER_kg/s']
        heights = np.array([results[f'HeightPercentile_{p}'] for p in [5, 25, 50, 75, 95]])
        X, Y = np.meshgrid(mer, [5, 25, 50, 75, 95])
        Z = heights

        # 2D Filled contour plot
        plt.figure(figsize=(12, 8))
        contour = plt.contourf(X, Y, Z, levels=20, cmap='viridis', alpha=0.9)
        contour_lines = plt.contour(X, Y, Z, levels=20, colors='black', linewidths=0.8)  # Add contour lines
        fmt = lambda x: f"{x:.1f} km"  # Formatting contour labels to include "km"
        labels = plt.clabel(contour_lines, inline=True, fontsize=10, fmt=fmt)  # Add contour labels
        for label in labels:
            label.set_color('white')  # Set label font color to white

        cbar = plt.colorbar(contour)
        cbar.set_label('Height (km a.v.l)', weight='bold')

        #plt.xscale('log')
        # Set labels, title, and grid
        plt.xlabel(' MER (kg/s)', weight='bold')
        plt.ylabel('Percentiles', weight='bold')
        plt.title('2D Filled Contour Plot: MER vs Plume Height Percentiles', weight='bold')
        plt.grid(alpha=0.5)
        plt.tight_layout()
        plt.show()
