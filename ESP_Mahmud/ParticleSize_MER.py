import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import t, invgamma, multivariate_normal
from typing import Optional, Tuple, List, Union
from matplotlib.colors import LogNorm

class Predict_ASH_BELOW_63_Micron:
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the Predict_ASH_BELOW_63_Micron class for Bayesian Regression.

        :param data: Input dataset as a DataFrame.
        """
        self.data = data.copy()
        self.xvar = 'Height_km.a.v.l'
        self.yvar = 'MER_kg/s'
        self._prepare_data()
        self._fit_model()
        self.posterior_samples_cache = None  # Cache for posterior samples

    def set_xvar(self, new_xvar: str):
        """
        Change the independent variable (xvar) used in the model and reinitialize the dataset.

        :param new_xvar: The new column name to be used as the independent variable.
        """
        if new_xvar not in self.data.columns:
            raise ValueError(f"Column {new_xvar} does not exist in the dataset.")

        self.xvar = new_xvar
        self._update_model()

    def set_yvar(self, new_yvar: str):
        """
        Change the dependent variable (yvar) used in the model and reinitialize the dataset.

        :param new_yvar: The new column name to be used as the dependent variable.
        """
        if new_yvar not in self.data.columns:
            raise ValueError(f"Column {new_yvar} does not exist in the dataset.")

        self.yvar = new_yvar
        self._update_model()

    def _update_model(self):
        """
        Update the dataset, refit the model, and update outputs after changing xvar or yvar.
        """
        self._prepare_data()
        self._fit_model()
        print(f"Model updated with xvar='{self.xvar}' and yvar='{self.yvar}'.")

    def _prepare_data(self):
        """
        Prepares the dataset by ensuring the necessary columns exist and converting to log space.
        """
        if self.xvar not in self.data.columns or self.yvar not in self.data.columns:
            raise ValueError(f"Columns {self.xvar} and {self.yvar} must exist in the dataset.")

        self.data = self.data.dropna(subset=[self.xvar, self.yvar])
        self.data['log_x'] = np.log10(self.data[self.xvar])
        self.data['log_y'] = np.log10(self.data[self.yvar])

    def _fit_model(self):
        """
        Performs Bayesian linear regression using Maximum Likelihood Estimation (MLE).
        """
        X = np.vstack([np.ones(self.data.shape[0]), self.data['log_x']]).T
        y = self.data['log_y'].values

        self.beta = np.linalg.inv(X.T @ X) @ X.T @ y  # MLE for beta
        residuals = y - X @ self.beta
        self.sigma2 = np.sum(residuals**2) / (len(y) - 2)  # MLE for variance
        self.X = X
        self.y = y
        self.residuals = residuals
        # Clear cache after model fit
        self.posterior_samples_cache = None

    def sample_posterior(self, size: int = 10000) -> pd.DataFrame:
        """
        Draw samples from the posterior distributions of the model parameters.

        :param size: Number of posterior samples to draw.
        :return: DataFrame of sampled parameters (intercept, slope, sigma2).
        """
        if self.posterior_samples_cache is not None and len(self.posterior_samples_cache) == size:
            return self.posterior_samples_cache
        samples = []
        for _ in range(size):
            sigma2_sample = invgamma.rvs(self.data.shape[0] / 2, scale=self.sigma2 * self.data.shape[0] / 2)
            beta_sample = multivariate_normal.rvs(mean=self.beta, cov=sigma2_sample * np.linalg.inv(self.X.T @ self.X))
            samples.append([*beta_sample, sigma2_sample])
        
        self.posterior_samples_cache = pd.DataFrame(samples, columns=['intercept', 'slope', 'sigma2'])
        
        return self.posterior_samples_cache
        
        

    def predictive_intervals(self, x: np.ndarray, alpha: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute predictive intervals for new data points.

        :param x: Array of new x values (in original space).
        :param alpha: Significance level for intervals.
        :return: Lower and upper predictive intervals.
        """
        log_x = np.log10(x)
        y_mean = self.beta[0] + self.beta[1] * log_x
        mean_x = np.mean(self.data['log_x'])
        var_x = np.var(self.data['log_x'])
        n = len(self.y)

        interval_var = self.sigma2 * (1 + 1 / n + (log_x - mean_x)**2 / (n * var_x))
        t_dist = t(df=n - 2)
        margin = t_dist.ppf(1 - alpha / 2) * np.sqrt(interval_var)

        return y_mean - margin, y_mean + margin

    def calculate_percentiles(self, x: Union[float, np.ndarray], percentiles: List[int] = [5, 25, 50, 75, 95]) -> pd.DataFrame:
        """
        Calculate posterior predictive percentiles for given x values.

        :param x: Single value or array of new x values (in original space).
        :param percentiles: List of percentiles to calculate.
        :return: DataFrame with calculated percentiles.
        """
        if isinstance(x, (float, int)):
            x = np.array([x])

        log_x = np.log10(x)
        y_mean = self.beta[0] + self.beta[1] * log_x

        results = pd.DataFrame({self.xvar: x})
        for p in percentiles:
            results[f'{self.yvar}_Percentile_{p}'] = 10**(y_mean + t.ppf(p / 100, df=len(self.y) - 2) * np.sqrt(self.sigma2))

        return results
    
    
    def calculate_percentiles_with_uncertainty(self, x: Union[float, np.ndarray], percentiles: List[int] = [5, 25, 50, 75, 95], num_samples: int = 10000) -> pd.DataFrame:
        """
        Calculate posterior predictive percentiles and uncertainty for given x values.

        :param x: Single value or array of new x values (in original space).
        :param percentiles: List of percentiles to calculate.
        :param num_samples: Number of posterior samples for uncertainty estimation.
        :return: DataFrame with calculated percentiles and their uncertainties.
        """
        if isinstance(x, (float, int)):
            x = np.array([x])

        posterior_samples = self.sample_posterior(size=num_samples)
        log_x = np.log10(x)
        results = pd.DataFrame({self.xvar: x})

        for p in percentiles:
            percentile_values = []
            for _, row in posterior_samples.iterrows():
                y_pred = row['intercept'] + row['slope'] * log_x
                percentile_values.append(10**y_pred)

            percentiles_array = np.percentile(percentile_values, p, axis=0)
            results[f'{self.yvar}_Percentile_{p}'] = percentiles_array

            results[f'Uncertainty_Lower_{p}'] = np.percentile(percentile_values, max(p - 5, 0), axis=0)
            results[f'Uncertainty_Upper_{p}'] = np.percentile(percentile_values, min(p + 5, 100), axis=0)

        return results
    
    
    def predict_with_uncertainty(self, x_vals: Union[float, np.ndarray], percentiles: List[int] = [5, 25, 50, 75, 95], output_file: Optional[str] = None) -> pd.DataFrame:
        """
        Predict Y values from given x values and include uncertainty estimates.

        :param x_vals: Single value or array of new x values (in original space).
        :param percentiles: List of percentiles to calculate.
        :param output_file: If provided, saves the output DataFrame to the specified CSV file.
        :return: DataFrame with predicted percentiles and uncertainty estimates.
        """
        results = self.calculate_percentiles_with_uncertainty(x_vals, percentiles)

        if output_file:
            results.to_csv(output_file, index=False)
            print(f"Predictions with uncertainty saved to {output_file}")

        return results
    

    def plot_posterior_predictive(self):
        """
        Plot posterior predictive PDFs and CDFs.
        """
        x_vals = np.linspace(self.data[self.xvar].min(), self.data[self.xvar].max(), 100)
        log_x_vals = np.log10(x_vals)
        y_mean = self.beta[0] + self.beta[1] * log_x_vals

        lower, upper = self.predictive_intervals(x_vals)
        
        num_data_points = len(self.data)

        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, 10**y_mean, label='Mean Prediction', color='blue')
        plt.fill_between(x_vals, 10**lower, 10**upper, color='lightblue', alpha=0.5, label='Predictive Interval')
        plt.scatter(self.data[self.xvar], self.data[self.yvar], color='black', label=f'Data Points (n={num_data_points})')
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel(self.xvar)
        plt.ylabel(self.yvar)
        plt.legend()
        plt.title('Posterior Predictive Plot')
        plt.show()

    def plot_percentiles_with_uncertainty(self, x_vals: np.ndarray, percentiles: List[int] = [5, 25, 50, 75, 95]):
        """
        Plot percentiles with uncertainty ribbons vs the independent variable.

        :param x_vals: Array of x values for prediction.
        :param percentiles: List of percentiles to plot.
        """
        results = self.calculate_percentiles_with_uncertainty(x_vals, percentiles)

        plt.figure(figsize=(10, 6))
        for p in percentiles:
            plt.plot(results[self.xvar], results[f'{self.yvar}_Percentile_{p}'], label=f'{p}th Percentile')
            plt.fill_between(
                results[self.xvar],
                results[f'Uncertainty_Lower_{p}'],
                results[f'Uncertainty_Upper_{p}'],
                alpha=0.3,
                label=f'{p}th Percentile Uncertainty'
            )

        plt.xscale('log')
        #plt.yscale('log')
        plt.xlabel(self.xvar)
        plt.ylabel(self.yvar)
        plt.title(f'Percentiles vs {self.xvar} with Uncertainty')
        plt.legend()
        plt.show()

    def plot_percentiles(self):
        """
        Plot percentiles vs the independent variable with predicted percentile values in the colorbar.
        """
        x_vals = np.logspace(np.log10(self.data[self.xvar].min()), np.log10(self.data[self.xvar].max()), 100)
        percentiles = [5, 25, 50, 75, 95]
        results = self.calculate_percentiles(x_vals, percentiles)

        plt.figure(figsize=(12, 8))
        for p in percentiles:
            plt.plot(results[self.xvar], results[f'{self.yvar}_Percentile_{p}'], 
                     label=f'{p}th Percentile', linewidth=2.5)

        plt.xscale('log')
        plt.xlabel(self.xvar)
        plt.ylabel(self.yvar)
        plt.title(f'Percentiles of {self.yvar} vs {self.xvar}')
        plt.legend()
        plt.grid(alpha=0.5)
        plt.show()

        height = results[self.xvar]
        MERs = np.array([results[f'{self.yvar}_Percentile_{p}'] for p in percentiles])

        X, Y = np.meshgrid(height, percentiles)
        Z = MERs


        plt.figure(figsize=(12, 8))
        contour = plt.contourf(X, Y, Z, levels=20, cmap='viridis', alpha=0.9)
        contour_lines = plt.contour(X, Y, Z, levels=20, colors='black', linewidths=0.8)  # Add contour lines
        fmt = lambda x: f"{x:.1f}"  # Formatting contour labels to include "km"
        labels = plt.clabel(contour_lines, inline=True, fontsize=10, fmt=fmt)  # Add contour labels
        for label in labels:
            label.set_color('white')  # Set label font color to white
            
        plt.colorbar(contour, label=f'{self.yvar}')
        plt.xlabel(self.xvar)
        plt.ylabel('Percentiles')
        plt.title(f'2D Contour Plot: {self.xvar} vs Percentiles of {self.yvar}')
        plt.grid(alpha=0.5)
        plt.show()
