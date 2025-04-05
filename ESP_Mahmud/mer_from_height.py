'''

## Contact Details

**Dr. Mahmud Muhammad**  
(PhD, MSc, and BSc in Geology)  
Email: [mahmud.geology@hotmail.com](mailto:mahmud.geology@hotmail.com)  
Website: [mahmudm.com](http://mahmudm.com)


'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import t, invgamma, multivariate_normal
from typing import Optional, Tuple, List, Union
from matplotlib.colors import LogNorm

class MERPredictorFromHeight:
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the MERPredictor class for Bayesian Regression.

        :param data: Input dataset as a DataFrame.
        """
        self.data = data.copy()
        self.xvar = 'Height_km.a.v.l'
        self.yvar = 'MER_kg/s'
        self._prepare_data()
        self._fit_model()
        self.posterior_samples=None

    
    def set_xvar(self, new_xvar: str):
        """
        Change the independent variable (xvar) used in the model and reinitialize the dataset.

        :param new_xvar: The new column name to be used as the independent variable.
        """
        if new_xvar not in self.data.columns:
            raise ValueError(f"Column {new_xvar} does not exist in the dataset.")

        self.xvar = new_xvar
        self._prepare_data()
        self._fit_model()
        print(f"xvar has been updated to '{new_xvar}' and the model has been refitted.")

    def set_yvar(self, new_yvar: str):
        """
        Change the independent variable (xvar) used in the model and reinitialize the dataset.

        :param new_xvar: The new column name to be used as the independent variable.
        """
        if new_yvar not in self.data.columns:
            raise ValueError(f"Column {new_yvar} does not exist in the dataset.")

        self.xvar = new_yvar
        self._prepare_data()
        self._fit_model()
        print(f"xvar has been updated to '{new_yvar}' and the model has been refitted.")
    
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
        results = pd.DataFrame({'Height_km.a.v.l': x})

        for p in percentiles:
            percentile_values = []
            for _, row in posterior_samples.iterrows():
                y_pred = row['intercept'] + row['slope'] * log_x
                percentile_values.append(10**(y_pred))
            
            percentiles_array = np.percentile(percentile_values, p, axis=0)
            results[f'MERPercentile_{p}'] = percentiles_array

            # Uncertainty estimation
            results[f'Uncertainty_Lower_{p}'] = np.percentile(percentile_values, max(p - 5, 0), axis=0)
            results[f'Uncertainty_Upper_{p}'] = np.percentile(percentile_values, min(p + 5, 100), axis=0)

            # Calculate Best_MER_Estimate_km from the 95th and 5th percentiles
        if 'MERPercentile_95' in results and 'MERPercentile_5' in results:
            results['Best_MER_Estimate_km'] = (results['MERPercentile_95'] - results['MERPercentile_5'])
            
            
            # Calculate Best_MER_Estimate_km_Uncertainty
        if 'Uncertainty_Upper_95' in results and 'Uncertainty_Upper_5' in results:
            results['Best_MER_Estimate_km_Uncertainty'] = (
                (results['Uncertainty_Upper_95'] - results['Uncertainty_Upper_5'])
            )
            
        
        return results

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

        results = pd.DataFrame({'Height_km.a.v.l': x})
        for p in percentiles:
            results[f'MERPercentile_{p}'] = 10**(y_mean + t.ppf(p / 100, df=len(self.y) - 2) * np.sqrt(self.sigma2))

        return results

    def predict_MER_with_uncertainty(self, mer_values: Union[float, List[float]], output_file: str = 'predicted_MER_with_uncertainty.csv') -> pd.DataFrame:
        """
        Predict MER values from single or multiple MER values and include uncertainty estimates.

        :param mer_values: Single MER value or a list of MER values.
        :param output_file: Output CSV filename.
        """
        if isinstance(mer_values, (float, int)):
            mer_values = [mer_values]
        mer_values = np.array(mer_values)

        predictions = self.calculate_percentiles_with_uncertainty(mer_values)
        predictions.to_csv(output_file, index=False)
        print(f"Predictions with uncertainty saved to {output_file}")
        
        return predictions

    # def plot_posterior_predictive(self):
    #     """
    #     Plot posterior predictive PDFs and CDFs.
    #     """
    #     x_vals = np.linspace(self.data[self.xvar].min(), self.data[self.xvar].max(), 100)
    #     log_x_vals = np.log10(x_vals)
    #     y_mean = self.beta[0] + self.beta[1] * log_x_vals

    #     lower, upper = self.predictive_intervals(x_vals)
    #     num_data_points = len(self.data)

    #     plt.figure(figsize=(10, 6))
    #     plt.plot(x_vals, 10**y_mean, label='Mean Prediction', color='blue')
    #     plt.fill_between(x_vals, 10**lower, 10**upper, color='lightblue', alpha=0.5, label='Predictive Interval')
    #     plt.scatter(self.data[self.xvar], self.data[self.yvar], color='black', label=f'Data Points (n={num_data_points})')
    #     plt.xscale('log')
    #     plt.yscale('log')
    #     plt.xlabel(self.xvar)
    #     plt.ylabel(self.yvar)
    #     plt.legend()
    #     plt.title('Posterior Predictive Plot')
    #     plt.show()
    
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

    def plot_percentiles_with_uncertainty(self, x_vals: np.ndarray, percentiles: List[int] = [5, 25, 50, 75, 95]):
        """
        Plot percentiles with uncertainty ribbons vs Height_km.a.v.l.

        :param x_vals: Array of x values for prediction.
        :param percentiles: List of percentiles to plot.
        """
        results = self.calculate_percentiles_with_uncertainty(x_vals, percentiles)

        plt.figure(figsize=(10, 6))
        for p in percentiles:
            plt.plot(results['Height_km.a.v.l'], results[f'MERPercentile_{p}'], label=f'{p}th Percentile')
            plt.fill_between(
                results['Height_km.a.v.l'],
                results[f'Uncertainty_Lower_{p}'],
                results[f'Uncertainty_Upper_{p}'],
                alpha=0.3,
                label=f'{p}th Percentile Uncertainty'
            )

        #plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('Height_km.a.v.l')
        plt.ylabel('MER_km.a.v.l')
        plt.title('Percentiles vs Height_km.a.v.l with Uncertainty')
        plt.legend()
        plt.show()

    def plot_percentiles_vs_mer(self):
        """
        Plot percentiles vs Height_km.a.v.l with predicted percentile values in the colorbar.
        """
        x_vals = np.logspace(np.log10(self.data[self.xvar].min()), np.log10(self.data[self.xvar].max()), 100)
        percentiles = [5, 25, 50, 75, 95]
        results = self.calculate_percentiles(x_vals, percentiles)

        # Set figure aesthetics
        plt.rcParams.update({
                'font.size': 12,
                'font.family': 'serif',
                'axes.labelweight': 'bold',
                'axes.titlesize': 16,
                'axes.titleweight': 'bold',
                'legend.fontsize': 12,
                'grid.alpha': 0.5
            })
        # Plot percentiles
        plt.figure(figsize=(12, 8))
        for p in percentiles:
            plt.plot(results['Height_km.a.v.l'], results[f'MERPercentile_{p}'], 
                    label=f'{p}th Percentile', linewidth=2.5)

        plt.yscale('log')
        plt.xlabel('Height km.a.v.l')
        plt.ylabel('MER (kg/s)')
        plt.title('Percentiles of MER vs Height')
        plt.legend(loc='best', fancybox=True, shadow=True)
        plt.grid(alpha=0.5)
        plt.tight_layout()
        plt.show()

        # Prepare data for 2D filled contour plot
        height = np.log10(results['Height_km.a.v.l'])  # Log scale for MER
        height=results['Height_km.a.v.l']
        
        MERs = np.array([results[f'MERPercentile_{p}'] for p in percentiles])

        # Create 2D grid
        X, Y = np.meshgrid(height, percentiles)  # X for MER, Y for percentiles
        Z = MERs  # Z values are MERs
        
        # 2D Filled contour plot
        plt.figure(figsize=(12, 8))
        contour = plt.contourf(X, Y, Z, levels=20, cmap='viridis', alpha=0.9, norm=LogNorm(vmin=Z.min(), vmax=Z.max()))
        contour_lines = plt.contour(X, Y, Z, levels=20, colors='black', linewidths=0.8, norm=LogNorm(vmin=Z.min(), vmax=Z.max()))  # Add contour lines
        fmt = lambda x: f"{x:.1f} kg/s"  # Formatting contour labels to include "km"
        labels = plt.clabel(contour_lines, inline=True, fontsize=10, fmt=fmt)  # Add contour labels
        for label in labels:
            label.set_color('white')  # Set label font color to white

        cbar = plt.colorbar(contour)
        cbar.set_label('MER (kg/s)', weight='bold')

        #plt.xscale('log')
        # Set labels, title, and grid
        plt.xlabel('Height km.a.v.l', weight='bold')
        plt.ylabel('Percentiles', weight='bold')
        plt.title('2D Filled Contour Plot: Height vs MER Percentiles', weight='bold')
        plt.grid(alpha=0.5)
        plt.tight_layout()
        plt.show()
    