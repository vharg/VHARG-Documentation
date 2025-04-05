

'''

# ## Contact Details
# **Dr. Mahmud Muhammad**  
# (PhD, MSc, and BSc in Geology)  
# Email: [mahmud.geology@hotmail.com](mailto:mahmud.geology@hotmail.com)  
# Website: [mahmudm.com](http://mahmudm.com)

'''


     
import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_probability as tfp
import matplotlib.pyplot as plt
from scipy.stats import t
from matplotlib.colors import LogNorm
from typing import Optional, Tuple, List, Union

tfd = tfp.distributions
tfb = tfp.bijectors

class MERPredictor:
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.xvar = 'TEM_kg'
        self.yvar = 'MER_kg/s'
        self.models = []
        self.selected_model = None
        self.posterior_samples = None
        self.predictions = None
        self._prepare_data()
        self.find_best_model()
        self.fit_selected_model()

    def _prepare_data(self):
        if self.xvar not in self.data.columns or self.yvar not in self.data.columns:
            raise ValueError(f"Columns {self.xvar} and {self.yvar} must exist in the dataset.")
        self.data = self.data.dropna(subset=[self.xvar, self.yvar])
        self.data['log_x'] = np.log10(self.data[self.xvar])
        self.data['log_y'] = np.log10(self.data[self.yvar])

    def plot_posterior_predictive(self, num_posterior_samples_to_visualize=100, confidence=0.95):
        """
        Plot posterior predictive samples, mean posterior line, and credible intervals.
        X-axis: Linear scale
        Y-axis: Logarithmic scale
        """
        # # Prepare grid of x-values (linear scale)
        # x_vals = np.linspace(self.data["TEM_kg"].min(), self.data["TEM_kg"].max(), 100)
        # log_x_vals = np.log10(x_vals)
        
        # Prepare grid of x-values (logarithmic spacing)
        log_x_vals = np.linspace(np.log10(self.data["TEM_kg"].min()), np.log10(self.data["TEM_kg"].max()), 100)
        x_vals = 10**log_x_vals  # Convert back to linear scale


        # Number of posterior samples to visualize
        #num_posterior_samples = min(num_posterior_samples_to_visualize, 200)

        # Generate posterior samples
        posterior_samples = self.sample_posterior()
        
        num_posterior_samples=len(posterior_samples)

        # Compute posterior predictive samples
        posterior_predictive_points = np.zeros((num_posterior_samples, len(x_vals)))
        for i in range(num_posterior_samples):
            intercept_sample = posterior_samples["intercept"].iloc[i]
            slope_sample = posterior_samples["slope"].iloc[i]
            sigma2_sample = posterior_samples["sigma2"].iloc[i]

            # Compute y-values (log-space) with added noise
            noise = np.random.normal(0, np.sqrt(sigma2_sample), len(x_vals))
            y_pred = intercept_sample + slope_sample * log_x_vals + noise
            posterior_predictive_points[i] = 10**y_pred

        # Flatten arrays for scatter plotting
        x_repeated = np.repeat(x_vals, num_posterior_samples)
        y_pred_flat = posterior_predictive_points.T.flatten()

        # Compute mean posterior line
        mean_intercept = posterior_samples["intercept"].mean()
        mean_slope = posterior_samples["slope"].mean()
        mean_y_pred = mean_intercept + mean_slope * log_x_vals

        # Compute credible intervals
        lower_percentile = (1 - confidence) / 2 * 100
        upper_percentile = (1 + confidence) / 2 * 100
        credible_intervals = np.percentile(posterior_predictive_points, [lower_percentile, upper_percentile], axis=0)

        # Plot observed data
        plt.figure(figsize=(10, 6))
        observed_data_points = len(self.data)
        plt.scatter(
            self.data["TEM_kg"],
            self.data["MER_kg/s"],
            color="black",
            label=f"Observed Data ({observed_data_points} points)",
        )

        # Plot posterior predictive scatter
        plt.scatter(
            x_repeated,
            y_pred_flat,
            color="blue",
            alpha=0.1,
            label=f"Posterior Predictive Samples ({len(y_pred_flat)})",
            s=10,
        )

        # Plot mean posterior line
        plt.plot(
            x_vals,
            10**mean_y_pred,
            color="red",
            label="Mean Posterior Prediction",
            linewidth=2,
        )

        # Fill credible interval
        plt.fill_between(
            x_vals,
            credible_intervals[0],
            credible_intervals[1],
            color="black",
            alpha=0.3,
            label=f"{int(confidence * 100)}% Credible Interval",
        )

        # Set axes scales and labels
        plt.yscale("log")
        plt.xscale("log")
        plt.xlabel("TEM_kg (Log Scale)")
        plt.ylabel("MER_kg/s (Log Scale)")
        plt.legend()
        plt.title(
            "Posterior Predictive Plot with Credible Interval (Log-Log Scale)"
        )
        plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)
        plt.tight_layout()
        plt.show()
    
    def _build_model(self, relationship: str):
        x = tf.convert_to_tensor(self.data['log_x'].values.astype(np.float32))
        y = tf.convert_to_tensor(self.data['log_y'].values.astype(np.float32))

        if relationship == 'linear':
            predictors = tf.reshape(x, [-1, 1])
        elif relationship == 'logarithmic':
            predictors = tf.reshape(tf.math.log(x), [-1, 1])
        elif relationship == 'polynomial':
            predictors = tf.stack([x, tf.pow(x, 2), tf.pow(x, 3)], axis=1)
        else:
            raise ValueError(f"Unsupported relationship: {relationship}")

        prior_intercept = tfd.Normal(loc=0., scale=10.)
        prior_slope = tfd.Normal(loc=tf.zeros(predictors.shape[1], dtype=tf.float32),
                                  scale=tf.ones(predictors.shape[1], dtype=tf.float32) * 2.)
        prior_sigma = tfd.HalfNormal(scale=1.)

        def joint_log_prob(intercept, slope, sigma):
            y_pred = intercept + tf.reduce_sum(slope * predictors, axis=-1)
            return (prior_intercept.log_prob(intercept) +
                    tf.reduce_sum(prior_slope.log_prob(slope)) +
                    prior_sigma.log_prob(sigma) +
                    tf.reduce_sum(tfd.Normal(loc=y_pred, scale=sigma).log_prob(y)))

        return joint_log_prob

    def _evaluate_model(self, relationship: str) -> float:
        joint_log_prob = self._build_model(relationship)
        num_parameters = {'linear': 2, 'logarithmic': 2, 'polynomial': 4}[relationship]

        def target_log_prob_fn(intercept, slope, sigma):
            return joint_log_prob(intercept, slope, sigma)

        initial_chain_state = [
            tf.constant(0., dtype=tf.float32),
            tf.zeros([num_parameters - 1], dtype=tf.float32),
            tf.constant(1., dtype=tf.float32)
        ]

        kernel = tfp.mcmc.HamiltonianMonteCarlo(
            target_log_prob_fn=target_log_prob_fn,
            step_size=0.01,
            num_leapfrog_steps=5
        )

        chain = tfp.mcmc.sample_chain(
            num_results=500,
            num_burnin_steps=250,
            current_state=initial_chain_state,
            kernel=kernel,
            trace_fn=None
        )

        intercept_samples, slope_samples, sigma_samples = chain
        log_likelihood = target_log_prob_fn(
            intercept_samples.numpy().mean(),
            slope_samples.numpy().mean(axis=0),
            sigma_samples.numpy().mean()
        )

        n = len(self.data)
        bic = -2 * log_likelihood + num_parameters * np.log(n)
        return bic

    def find_best_model(self):
        relationships = ['linear', 'logarithmic', 'polynomial']
        scores = {rel: self._evaluate_model(rel) for rel in relationships}
        self.selected_model = min(scores, key=scores.get)
        print(f"Selected model: {self.selected_model} with BIC = {scores[self.selected_model]}")

    def fit_selected_model(self):
        if not self.selected_model:
            raise ValueError("No model has been selected. Run find_best_model() first.")
        self.joint_log_prob = self._build_model(self.selected_model)
        self.posterior_samples = self.sample_posterior()

    def sample_posterior(self, size: int = 100, num_burnin: int = 1) -> pd.DataFrame:
        def target_log_prob_fn(intercept, slope, sigma):
            return self.joint_log_prob(intercept, slope, sigma)

        initial_chain_state = [
            tf.constant(0., dtype=tf.float32),
            tf.constant(0., dtype=tf.float32),
            tf.constant(1., dtype=tf.float32)
        ]

        unconstraining_bijectors = [
            tfb.Identity(),
            tfb.Identity(),
            tfb.Softplus()
        ]

        kernel = tfp.mcmc.TransformedTransitionKernel(
            inner_kernel=tfp.mcmc.HamiltonianMonteCarlo(
                target_log_prob_fn=target_log_prob_fn,
                step_size=0.01,
                num_leapfrog_steps=5
            ),
            bijector=unconstraining_bijectors
        )

        chain = tfp.mcmc.sample_chain(
            num_results=size,
            num_burnin_steps=num_burnin,
            current_state=initial_chain_state,
            kernel=kernel,
            trace_fn=None
        )

        intercept_samples, slope_samples, sigma_samples = chain

        return pd.DataFrame({
            'intercept': intercept_samples.numpy(),
            'slope': slope_samples.numpy(),
            'sigma2': sigma_samples.numpy()
        })

    def calculate_percentiles(self, x: Union[float, np.ndarray], percentiles: List[int] = [5, 25, 50, 75, 95]) -> pd.DataFrame:
        if isinstance(x, (float, int)):
            x = np.array([x])

        log_x = np.log10(x)
        results = pd.DataFrame({'TEM_kg': x})

        # for p in percentiles:
        #     percentile_values = []
        #     for _, row in self.posterior_samples.iterrows():
        #         y_pred = row['intercept'] + row['slope'] * log_x
        #         percentile_values.append(10 ** y_pred)

        #     results[f'MERPercentile_{p}'] = np.percentile(percentile_values, p, axis=0)
        
        for p in percentiles:
            percentile_values = []
            for _, row in self.posterior_samples.iterrows():
                y_pred = row['intercept'] + row['slope'] * log_x
                percentile_values.append(10**(y_pred))
            percentiles_array = np.percentile(percentile_values, p, axis=0)
            results[f'MERPercentile_{p}'] = percentiles_array

            # # Uncertainty estimation
            # results[f'Uncertainty_Lower_{p}'] = np.percentile(percentile_values, max(p - 5, 0), axis=0)
            # results[f'Uncertainty_Upper_{p}'] = np.percentile(percentile_values, min(p + 5, 100), axis=0)

            # Calculate 90%_interpercentile_MERrange_km from the 95th and 5th percentiles
        if 'MERPercentile_95' in results and 'MERPercentile_5' in results:
            results['90%_interpercentile_MERrange_kg/s'] = (results['MERPercentile_95'] - results['MERPercentile_5'])
            
            
            # Calculate 90%_interpercentile_MERrange_km_Uncertainty
        if 'Uncertainty_Upper_95' in results and 'Uncertainty_Upper_5' in results:
            results['90%_interpercentile_MERrange_kg/s_Uncertainty'] = (
                (results['Uncertainty_Upper_95'] - results['Uncertainty_Upper_5'])
            )
            
            results['90%_interpercentile_MER_2std_kg/s'] = (results['90%_interpercentile_MERrange_kg/s'] - results['90%_interpercentile_MERrange_kg/s_Uncertainty'])
        
        return results

    
    def convert_percentiles_to_duration(self) -> pd.DataFrame:
        """
        Convert calculated MER percentiles to eruption duration in hours.

        :param tem_values: Single TEM value or a list of TEM values.
        :return: DataFrame with TEM values and corresponding durations for each percentile.
        """
        # if isinstance(tem_values, (float, int)):
        #     tem_values = [tem_values]
        # tem_values = np.array(tem_values)

        #results = self.calculate_percentiles(tem_values)
        results=self.predictions

        duration_results = pd.DataFrame({'TEM_kg': results['TEM_kg']})
        for col in results.columns:
            if col.startswith('MERPercentile_'):
                percentile_name = col.split('_')[-1]
                duration_results[f'Duration_hr_P{percentile_name}'] = duration_results['TEM_kg'] / results[col] / 3600

        for col in results.columns:
            if col=='90%_interpercentile_MERrange_kg/s':
                duration_results['Duration_hr_90%_interpercentile'] = duration_results['TEM_kg'] / results[col] / 3600
            elif col=="90%_interpercentile_MERrange_kg/s_Uncertainty":
                duration_results['Duration_hr_90%_interpercentile_Uncertainty'] = duration_results['TEM_kg'] / results[col] / 3600
        
        return duration_results
    
    
    def predict_mer(self, tem_values: Union[float, List[float]], output_file: str = 'predicted_mer.csv', percentiles=[5,25,50,75,95]) -> pd.DataFrame:
        if isinstance(tem_values, (float, int)):
            tem_values = [tem_values]
        tem_values = np.array(tem_values)

        predictions = self.calculate_percentiles(tem_values, percentiles=percentiles)
        self.predictions = predictions
        predictions.to_csv(output_file, index=False)
        print(f"Predictions saved to {output_file}")
        
        self.plot_percentiles_vs_tem(percentiles=percentiles)
        durations=self.convert_percentiles_to_duration()
        
        # Merge predictions with durations
        merged_results = pd.merge(predictions, durations, on='TEM_kg')
        merged_results.to_csv(output_file, index=False)
        
        return merged_results

    def plot_percentiles_vs_tem(self, percentiles=[5, 25, 50, 75, 95]):
        if self.predictions is None:
            raise ValueError("No predictions available. Run predict_mer() first.")

        plt.figure(figsize=(12, 8))
        for p in percentiles:
            plt.plot(self.predictions['TEM_kg'], self.predictions[f'MERPercentile_{p}'], label=f'{p}th Percentile')

        plt.yscale('log')
        plt.xscale('log')
        plt.xlabel('TEM_kg')
        plt.ylabel('MER (kg/s)')
        plt.title('MER Percentiles vs TEM_kg')
        plt.legend()
        plt.grid(alpha=0.5)
        plt.tight_layout()
        plt.show()

        # Generate contour plot
        x_vals = np.logspace(np.log10(self.data[self.xvar].min()), np.log10(self.data[self.xvar].max()), 100)
        percentiles = np.array(percentiles)
        
        # x_vals = self.predictions['TEM_kg'].values
        # percentiles = np.array(percentiles)

        Z = np.array([
            np.interp(x_vals, self.predictions['TEM_kg'], self.predictions[f'MERPercentile_{p}'])
            for p in percentiles
        ])

        X, Y = np.meshgrid(x_vals, percentiles)

        # Determine log scale for axes if needed
        x_scale = 'log' if (self.data[self.xvar].max() / self.data[self.xvar].min() > 100) else 'linear'
        y_scale = 'log' if (self.data[self.yvar].max() / self.data[self.yvar].min() > 100) else 'linear'

        plt.figure(figsize=(12, 8))
        levels = np.logspace(np.log10(Z.min()), np.log10(Z.max()), num=20) if x_scale == 'log' else np.linspace(Z.min(), Z.max(), num=20)

        contour = plt.contourf(X, Y, Z, levels=levels, cmap='viridis', alpha=0.8, norm=LogNorm(vmin=Z.min(), vmax=Z.max()) ) # norm=LogNorm(vmin=Z.min(), vmax=Z.max())
        contour_lines = plt.contour(X, Y, Z, levels=levels, colors='black', linewidths=0.5 , norm=LogNorm(vmin=Z.min(), vmax=Z.max()))
        fmt = lambda x: f"{x:.1f} kg/s"  # Formatting contour labels to include "km"
        labels = plt.clabel(contour_lines, inline=True, fontsize=10, fmt=fmt)  # Add contour labels
        for label in labels:
            label.set_color('white')  # Set label font color to white

        

        cbar = plt.colorbar(contour)
        cbar.set_label('MER (kg/s)', weight='bold')

        #plt.xscale(x_scale)
        #plt.yscale(y_scale)
        plt.xlabel('TEM_kg')
        plt.ylabel('Percentiles')
        plt.title('MER Contour Plot')
        plt.tight_layout()
        plt.show()



