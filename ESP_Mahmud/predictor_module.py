import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_probability as tfp
import matplotlib.pyplot as plt

tfd = tfp.distributions
tfb = tfp.bijectors


class AutoMERPredictor:
    def __init__(self, data: pd.DataFrame):
        """
        Automatically find the best relationship between x and y variables.
        :param data: Input dataset as a DataFrame.
        """
        self.data = data.copy()
        self.xvar = 'TEM_kg'
        self.yvar = 'MER_kg/s'
        self.models = []
        self.selected_model = None
        self._prepare_data()

    def _prepare_data(self):
        """
        Prepares the dataset by ensuring the necessary columns exist and converting to log space.
        """
        if self.xvar not in self.data.columns or self.yvar not in self.data.columns:
            raise ValueError(f"Columns {self.xvar} and {self.yvar} must exist in the dataset.")
        self.data = self.data.dropna(subset=[self.xvar, self.yvar])
        self.data['log_x'] = np.log10(self.data[self.xvar])
        self.data['log_y'] = np.log10(self.data[self.yvar])
        self.data['x_squared'] = self.data['log_x'] ** 2
        self.data['x_cubed'] = self.data['log_x'] ** 3

    def _build_model(self, relationship: str):
        """
        Build the Bayesian model based on the specified relationship.
        :param relationship: The type of relationship (e.g., 'linear', 'logarithmic', 'polynomial').
        """
        x = tf.convert_to_tensor(self.data['log_x'].values.astype(np.float32))
        y = tf.convert_to_tensor(self.data['log_y'].values.astype(np.float32))

        if relationship == 'linear':
            predictors = tf.reshape(x, [-1, 1])  # Ensure 2D
        elif relationship == 'logarithmic':
            predictors = tf.reshape(tf.math.log(x), [-1, 1])  # Ensure 2D
        elif relationship == 'polynomial':
            predictors = tf.stack(
                [x, tf.pow(x, 2), tf.pow(x, 3)], axis=1
            )  # Polynomial terms in 2D
        else:
            raise ValueError(f"Unsupported relationship: {relationship}")

        # Define priors
        prior_intercept = tfd.Normal(loc=0., scale=10.)
        prior_slope = tfd.Normal(loc=tf.zeros(predictors.shape[1], dtype=tf.float32),
                                scale=tf.ones(predictors.shape[1], dtype=tf.float32) * 2.)
        prior_sigma = tfd.HalfNormal(scale=1.)

        # Joint log probability
        def joint_log_prob(intercept, slope, sigma):
            y_pred = intercept + tf.reduce_sum(slope * predictors, axis=-1)
            return (prior_intercept.log_prob(intercept) +
                    tf.reduce_sum(prior_slope.log_prob(slope)) +
                    prior_sigma.log_prob(sigma) +
                    tf.reduce_sum(tfd.Normal(loc=y_pred, scale=sigma).log_prob(y)))

        return joint_log_prob




    def _evaluate_model(self, relationship: str) -> float:
        """
        Evaluate the model using Bayesian Information Criterion (BIC).
        :param relationship: The type of relationship (e.g., 'linear', 'logarithmic', 'polynomial').
        :return: BIC score for the model.
        """
        joint_log_prob = self._build_model(relationship)
        num_parameters = {
            'linear': 2,  # intercept + slope
            'logarithmic': 2,
            'polynomial': 4  # intercept + 3 slopes
        }[relationship]

        # Sample from the posterior to estimate log likelihood
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

        # Calculate log likelihood
        intercept_samples, slope_samples, sigma_samples = chain
        log_likelihood = target_log_prob_fn(
            intercept_samples.numpy().mean(),
            slope_samples.numpy().mean(axis=0),
            sigma_samples.numpy().mean()
        )

        # Calculate BIC
        n = len(self.data)
        bic = -2 * log_likelihood + num_parameters * np.log(n)
        return bic

    def find_best_model(self):
        """
        Find the best relationship between x and y variables.
        """
        relationships = ['linear', 'logarithmic', 'polynomial']
        scores = {rel: self._evaluate_model(rel) for rel in relationships}
        self.selected_model = min(scores, key=scores.get)
        print(f"Selected model: {self.selected_model} with BIC = {scores[self.selected_model]}")

    def fit_selected_model(self):
        """
        Fit the selected model and sample posterior.
        """
        if not self.selected_model:
            raise ValueError("No model has been selected. Run find_best_model() first.")
        self.joint_log_prob = self._build_model(self.selected_model)
        self.posterior_samples = self.sample_posterior()

    def sample_posterior(self, num_samples: int = 100, num_burnin: int = 2) -> pd.DataFrame:
        """
        Sample from the posterior using Hamiltonian Monte Carlo (HMC).
        """
        def target_log_prob_fn(intercept, slope, sigma):
            return self.joint_log_prob(intercept, slope, sigma)

        # Initial values
        initial_chain_state = [
            tf.constant(0., dtype=tf.float32),  # Intercept
            tf.constant(0., dtype=tf.float32),  # Slope
            tf.constant(1., dtype=tf.float32)   # Sigma
        ]

        # HMC transition kernel
        unconstraining_bijectors = [
            tfb.Identity(),
            tfb.Identity(),
            tfb.Softplus()  # For sigma (positive-only)
        ]
        kernel = tfp.mcmc.TransformedTransitionKernel(
            inner_kernel=tfp.mcmc.HamiltonianMonteCarlo(
                target_log_prob_fn=target_log_prob_fn,
                step_size=0.01,  # Smaller step size for better sampling 0.01
                num_leapfrog_steps=5
            ),
            bijector=unconstraining_bijectors
        )

        # Run MCMC
        chain = tfp.mcmc.sample_chain(
            num_results=num_samples,
            num_burnin_steps=num_burnin,
            current_state=initial_chain_state,
            kernel=kernel,
            trace_fn=None  # Suppress tracing kernel results
        )

        # Unpack the chain samples
        intercept_samples, slope_samples, sigma_samples = chain

        # Convert to DataFrame
        self.posterior_samples = pd.DataFrame({
            'intercept': intercept_samples.numpy(),
            'slope': slope_samples.numpy(),
            'sigma': sigma_samples.numpy()
        })
        return self.posterior_samples

    def plot_posterior_predictive(self, num_posterior_samples_to_visualize=100, confidence=0.95):
        """
        Plot posterior predictive samples, mean posterior line, and credible intervals.
        X-axis: Linear scale, Y-axis: Logarithmic scale.
        """
        posterior_samples = self.posterior_samples.sample(n=num_posterior_samples_to_visualize)
        x_vals = np.logspace(np.log10(self.data[self.xvar].min()), np.log10(self.data[self.xvar].max()), 100)
        log_x_vals = np.log10(x_vals)

        # Compute posterior predictive samples
        posterior_predictive_points = []
        for _, row in posterior_samples.iterrows():
            noise = np.random.normal(0, row['sigma'], len(x_vals))
            y_pred = row['intercept'] + row['slope'] * log_x_vals + noise
            posterior_predictive_points.append(10**y_pred)
        posterior_predictive_points = np.array(posterior_predictive_points)

        # Flatten arrays for scatter plotting
        x_repeated = np.tile(x_vals, posterior_predictive_points.shape[0])  # Repeat x_vals for each sample
        y_pred_flat = posterior_predictive_points.flatten()

        # Compute mean posterior line
        mean_intercept = posterior_samples['intercept'].mean()
        mean_slope = posterior_samples['slope'].mean()
        mean_y_pred = mean_intercept + mean_slope * log_x_vals

        # Compute credible intervals
        lower_percentile = (1 - confidence) / 2 * 100
        upper_percentile = (1 + confidence) / 2 * 100
        credible_intervals = np.percentile(posterior_predictive_points, [lower_percentile, upper_percentile], axis=0)

        # Plot observed data
        plt.figure(figsize=(10, 6))
        plt.scatter(self.data[self.xvar], self.data[self.yvar], color="black", label="Observed Data")

        # Plot posterior predictive scatter
        plt.scatter(x_repeated, y_pred_flat, color="blue", alpha=0.1,
                    label="Posterior Predictive Samples", s=10)

        # Plot mean posterior line
        plt.plot(x_vals, 10**mean_y_pred, color="red", label="Mean Posterior Prediction", linewidth=2)

        # Fill credible interval
        plt.fill_between(x_vals, credible_intervals[0], credible_intervals[1], color="gray", alpha=0.3,
                         label=f"{int(confidence * 100)}% Credible Interval")

        # Set axes scales and labels
        plt.yscale("log")
        plt.xscale("log")
        plt.xlabel(self.xvar)
        plt.ylabel(self.yvar)
        plt.legend()
        plt.title("Posterior Predictive Plot with Logarithmic Model")
        plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)
        plt.tight_layout()
        plt.show()