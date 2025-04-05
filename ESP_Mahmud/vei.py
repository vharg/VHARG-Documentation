import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import lognorm, uniform, norm, gamma, expon, ks_2samp, gaussian_kde
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import io
import sys
from matplotlib.colors import LogNorm
import textwrap
from tabulate import tabulate

import scipy.stats as stats


class VEI_BulkVolume_Mass:
    
    """
    VEI_BulkVolume_Mass Class
    -------------------------

    This class calculates volcanic bulk volumes and masses across different VEI (Volcanic Explosivity Index) levels. 
    It supports both empirical and probabilistic approaches, incorporates Bayesian updating for densities, and provides 
    visualization and export tools.

    Default Bulk Densities for Bayesian statistics are sourced from The Independent Volcanic Eruption Source Parameter 
    Archive (IVESPA, version 1.0): A new observational database to support explosive eruptive column model validation and development. 
    Alternatively, users can define custom minimum and maximum density ranges.

    **Features:**
        - Generates empirical and probabilistic bulk volumes.
        - Calculates masses using densities with Bayesian updating.
        - Visualizes results using histograms, KDE plots, and percentile bands.
        - Exports results to CSV and PDF files.

    **Attributes:**
        - `data`: DataFrame containing VEI levels, bulk volumes, and calculated masses.
        - `mass_distributions`: List of mass distributions for each VEI level.
        - `summary_statistics`: Summary statistics grouped by VEI level.
        - `volume_percentiles`: Percentile probability bands for volumes.
        - `mass_percentiles`: Percentile probability bands for masses.

    **Parameters:**
        use_default_densities : bool, optional
            Use predefined bulk density values (default is True).
        density_min : int, optional
            Minimum density value (default is 800).
        density_max : int, optional
            Maximum density value (default is 1200).
        num_samples : int, optional
            Number of samples for Monte Carlo simulations (default is 10000).

    **Example:**
        ```python
        vei = VEI_BulkVolume_Mass()
        vei.generate_probabilistic_volumes()
        vei.calculate_mass()
        vei.calculate_percentile_bands()
        vei.visualize_statistics()
        vei.export_volumes_and_masses()
        ```

    | **VEI** | **Best Estimate Volume (km³)** | **Example Eruption**                              | **Reference**                                                                                               |
    |---------|--------------------------------|--------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
    | **0**   | 0.0005                        | Kīlauea, Hawai'i (typical lava flows).           | U.S. Geological Survey (USGS). (2023). [Kīlauea Volcano Activity](https://www.usgs.gov/volcanoes/kilauea). |
    | **1**   | 0.005                         | Stromboli, Italy (frequent strombolian activity). | Rosi, M., et al. (2013). Volcanism of the Aeolian Islands. *Geological Society, London, Memoirs*, 37, 157–211. |
    | **2**   | 0.1                           | Parícutin, Mexico (1943–1952 cone formation).    | Luhr, J. F., & Simkin, T. (1993). Parícutin: The Volcano Born in a Mexican Cornfield. *Geoscience Press.*    |
    | **3**   | 3                             | Mount St. Helens, USA (1980 eruption).           | Lipman, P. W., & Mullineaux, D. R. (Eds.). (1981). The 1980 Eruptions of Mount St. Helens, Washington. *USGS Professional Paper 1250.* |
    | **4**   | 30                            | Eyjafjallajökull, Iceland (2010 eruption).       | Gudmundsson, M. T., et al. (2010). Eruption of Eyjafjallajökull Volcano, Iceland. *EOS Transactions, AGU*, 91(21), 190–191. |
    | **5**   | 100                           | Mount Pinatubo, Philippines (1991 eruption).     | Newhall, C. G., & Punongbayan, R. S. (1996). Fire and Mud: Eruptions and Lahars of Mount Pinatubo, Philippines. *University of Washington Press.* |
    | **6**   | 500                           | Krakatoa, Indonesia (1883 eruption).             | Simkin, T., & Fiske, R. S. (1983). Krakatau 1883: The Volcanic Eruption and Its Effects. *Smithsonian Institution Press.* |
    | **7**   | 1,000                         | Mount Tambora, Indonesia (1815 eruption).        | Stothers, R. B. (1984). The Great Tambora Eruption in 1815 and Its Aftermath. *Science*, 224(4654), 1191–1198. |
    | **8**   | 2,500                         | Yellowstone Caldera, USA (Lava Creek eruption ~640,000 years ago). | Smith, R. B., & Siegel, L. J. (2000). Windows into the Earth: The Geologic Story of Yellowstone and Grand Teton. *Oxford University Press.* |
  
    """

    
    
    DEFAULT_BULK_DENSITY_VALUES = [
        1040, 1040, 1400, 1400, 1000, 1000, 1000, 1000, 1750, 1750, 900, 900,
        1000, 900, 1200, 1200, 1200, 1200, 1000, 997, 997, 1250, 1600, 560,
        600, 600, 1339, 1343, 1572, 1579, 1300, 1300, 1300, 1000, 1000, 1067,
        1067, 1067, 1067, 1000, 1070, 1000, 1000, 1000, 1000, 1000, 1000, 1400,
        1400, 1400, 1226, 1350, 1140, 1190, 1190, 1000, 666, 666, 1000, 700,
        1000, 1000, 450, 450, 1030, 1250, 450, 1000, 1000, 1000, 1000, 1400,
        1000, 1000, 1000, 1400, 1400, 1100, 1000, 900, 950, 1600, 1600, 1250,
        1000, 1100, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000
    ]
    
    
    BULK_VOLUME_RANGES = [
    (0.001, 0.01),   # VEI 0
    (0.01, 0.1),     # VEI 1
    (0.1, 1),        # VEI 2
    (1, 10),         # VEI 3
    (10, 100),       # VEI 4
    (100, 1000),     # VEI 5
    (1000, 10000),   # VEI 6
    (10000, 100000), # VEI 7
    (100000, 1e6)    # VEI 8 - Large finite upper bound
]

    
    def __init__(self, use_default_densities=True, density_min=800, density_max=1200, num_samples=10000):
        
        """
        Initialize the VEI_BulkVolume_Mass class.

        Parameters:
        -----------
        use_default_densities : bool, optional
            Use predefined bulk density values.
        density_min : int, optional
            Minimum density value.
        density_max : int, optional
            Maximum density value.
        num_samples : int, optional
            Number of Monte Carlo samples.
        """
        
        
        self.summary_statistics=pd.DataFrame()
        #####
        self.vei_levels = list(range(9))
        self.bulk_volumes_km3 = [0.0005, 0.005, 0.1, 3, 30, 100, 500, 1000, 2500]
        #self.bulk_volumes_km3 = [5e-06, 4e-05, 0.0005, 0.00275, 0.0115, 0.04, 0.1, 0.5, 1.0] # Median Volume for each VEI Level
        self.num_samples = num_samples
        self.use_default_densities = use_default_densities
        self.mass_distributions = []
        self.data = pd.DataFrame({'VEI': self.vei_levels, 'Bulk_Volume_km3': self.bulk_volumes_km3})
        self.data["VEI"] = pd.to_numeric(self.data["VEI"], errors='coerce')
        self._convert_to_meters()
        
        # Set density values
        if use_default_densities:
            self._estimate_density_bounds()
        else:
            self.density_min = density_min
            self.density_max = density_max
            
        

    def _convert_to_meters(self):
        """
        Convert bulk volumes from km³ to m³.
        
        """
        self.data['emperical_Bulk_Volume_m3'] = self.data['Bulk_Volume_km3'] * 1e9
        
       

    def determine_best_sampling_strategy(self):
        """
        Determine the best probabilistic distribution for bulk volumes using AIC and KS tests.
        """
        print("Determining the best sampling strategy...")
        emperical_volumes = self.data['emperical_Bulk_Volume_m3'].values

        # Logarithmic scaling of emperical volumes
        log_volumes = np.log10(emperical_volumes)
        min_log = np.min(log_volumes)
        log_shift = 1 - min_log if min_log < 1 else 0  # Ensure positivity
        shifted_log_volumes = log_volumes + log_shift

        # Adjusted distributions with logarithmic trend
        def log_normal_shifted(size):
            samples = lognorm.rvs(s=0.5, scale=10**np.mean(shifted_log_volumes), size=size)
            return np.clip(samples, 0.1 * 10**np.mean(shifted_log_volumes), 10 * 10**np.mean(shifted_log_volumes))

        distributions = {
            'log-normal': lambda size: np.clip(lognorm.rvs(0.5, scale=np.mean(emperical_volumes), size=size), 0, None),
            'uniform': lambda size: np.clip(uniform.rvs(np.min(emperical_volumes), np.ptp(emperical_volumes), size=size), 0, None),
            'normal': lambda size: np.clip(norm.rvs(np.mean(emperical_volumes), np.std(emperical_volumes), size=size), 0, None),
            'gamma': lambda size: np.clip(gamma.rvs(2.0, scale=np.mean(emperical_volumes) / 2, size=size), 0, None),
            'exponential': lambda size: np.clip(expon.rvs(scale=np.mean(emperical_volumes), size=size), 0, None),
            'log-normal-adjusted': log_normal_shifted
        }

        best_aic, best_strategy = np.inf, None
        for name, dist in distributions.items():
            try:
                sampled_data = dist(self.num_samples)
                ks_stat, p_value = ks_2samp(emperical_volumes, sampled_data)
                log_likelihood = -np.sum(np.log(sampled_data[sampled_data > 0]))
                aic = -2 * log_likelihood + 2 * 2
                print(f"Distribution: {name}, AIC: {aic:.2f}, KS p-value: {p_value:.4f}")
                if aic < best_aic:
                    best_aic, best_strategy = aic, name
            except Exception as e:
                print(f"Error with distribution {name}: {e}")
        
        if best_strategy:
            self.best_strategy = best_strategy
            print(f"Best strategy: {self.best_strategy} (AIC: {best_aic:.2f})")
            return distributions[best_strategy]
        else:
            print("No valid strategy found. Using emperical volumes.")
            return lambda size: np.full(size, np.mean(emperical_volumes))
    #################################################################################
    
    def generate_probabilistic_volumes(self):
        """
        Generate probabilistic bulk volumes ensuring they stay within the defined range for each VEI.
        Assigns the calculated volumes to a DataFrame column 'Probabilistic_Bulk_Volume_m3'.
        """
        print("Generating probabilistic volumes...")

        # Validate required attributes
        if not hasattr(self, 'BULK_VOLUME_RANGES') or not hasattr(self, 'data'):
            raise AttributeError("Ensure 'BULK_VOLUME_RANGES' and 'data' are properly initialized.")

        if not isinstance(self.data, pd.DataFrame):
            raise TypeError("'data' must be a pandas DataFrame.")

        if not hasattr(self, 'num_samples'):
            raise AttributeError("Ensure 'num_samples' is defined.")

        # Initialize parameters
        total_samples = self.num_samples
        num_rows = len(self.data)
        samples_per_vei = total_samples // num_rows
        probabilistic_volumes = []

        # Generate probabilistic volumes for each VEI
        for idx in range(num_rows):
            min_volume, max_volume = self.BULK_VOLUME_RANGES[idx]

            # Sample volumes uniformly within the defined range
            sampled_volumes = np.random.uniform(min_volume, max_volume, samples_per_vei)
            probabilistic_volumes.extend(sampled_volumes)

        # Assign sampled volumes to the DataFrame (calculate mean per VEI for simplicity)
        self.data['Probabilistic_Bulk_Volume_m3'] = [
            np.mean(probabilistic_volumes[idx * samples_per_vei:(idx + 1) * samples_per_vei]) * 1e9
            for idx in range(num_rows)
        ]

        print("Probabilistic volumes successfully generated.")

    
    
    # def generate_probabilistic_volumes(self):
    #     """
    #     Generate probabilistic bulk volumes ensuring they stay within the defined range for each VEI.
    #     """
    #     print("Generating probabilistic volumes...")

    #     total_samples = self.num_samples
    #     num_rows = len(self.data)
    #     samples_per_vei = total_samples // num_rows
    #     probabilistic_volumes = []

    #     for idx in range(num_rows):
    #         min_volume, max_volume = self.BULK_VOLUME_RANGES[idx]
    #         sampled_volumes = np.random.uniform(min_volume, max_volume, samples_per_vei)  # Sample within the defined range
            
    #         probabilistic_volumes.extend(sampled_volumes)
        

        

    #     # Assign sampled volumes to the DataFrame (taking the mean for simplicity in this example)
    #     self.data['Probabilistic_Bulk_Volume_m3'] = [
    #         np.mean([v * 1e9 for v in probabilistic_volumes[idx * samples_per_vei:(idx + 1) * samples_per_vei]])
    #         for idx in range(num_rows)
    #     ]
    #     print("Probabilistic volumes successfully generated.")

    def _estimate_density_bounds(self):
        """Estimate density bounds using Bayesian probability updating on DEFAULT_BULK_DENSITY_VALUES."""
        sample_mean = np.mean(self.DEFAULT_BULK_DENSITY_VALUES)
        sample_std = np.std(self.DEFAULT_BULK_DENSITY_VALUES)

        # Bayesian updating: Assume weak prior centered at 1000 with high variance
        prior_mean = 1000
        prior_std = 300

        posterior_variance = 1 / ((1 / prior_std**2) + (len(self.DEFAULT_BULK_DENSITY_VALUES) / sample_std**2))
        posterior_mean = posterior_variance * ((prior_mean / prior_std**2) + (len(self.DEFAULT_BULK_DENSITY_VALUES) * sample_mean / sample_std**2))

        # Set density bounds as +/- 2 standard deviations from posterior mean
        self.density_min = max(0, posterior_mean - 2 * np.sqrt(posterior_variance))
        self.density_max = posterior_mean + 2 * np.sqrt(posterior_variance)
        print(f"Density bounds estimated using Bayesian updating:\nDensity Min: {self.density_min:.2f}, Density Max: {self.density_max:.2f}")

    
   

        
    def _best_density_strategy(self):
        """Determine the best strategy for sampling densities using log-normal, uniform, or normal."""
        densities = np.array(self.DEFAULT_BULK_DENSITY_VALUES)

        # Logarithmic scaling of densities
        log_densities = np.log10(densities)
        min_log = np.min(log_densities)
        log_shift = 1 - min_log if min_log < 1 else 0  # Ensure positivity
        shifted_log_densities = log_densities + log_shift

        # Adjusted distributions with logarithmic trend
        def log_normal_shifted(size):
            samples = lognorm.rvs(s=0.5, scale=10**np.mean(shifted_log_densities), size=size)
            return np.clip(samples, 0.1 * 10**np.mean(shifted_log_densities), 10 * 10**np.mean(shifted_log_densities))

        strategies = {
            'log-normal': lambda size: np.clip(lognorm.rvs(s=0.5, scale=np.mean(densities), size=size), 0.1, None),
            'uniform': lambda size: np.clip(uniform.rvs(np.min(densities), np.ptp(densities), size=size), 0.1, None),
            'normal': lambda size: np.clip(norm.rvs(np.mean(densities), np.std(densities), size=size), 0.1, None),
            'log-normal-adjusted': log_normal_shifted
        }

        best_strategy = None
        min_variance = float('inf')

        for name, strategy in strategies.items():
            samples = strategy(self.num_samples)
            variance = np.var(samples)
            if variance < min_variance:
                min_variance = variance
                best_strategy = name
        
        print(f"Best density sampling strategy: {best_strategy}")
        return strategies[best_strategy]

    def calculate_mass(self, calculate_emperical=True, calculate_probabilistic=True, vei_range=None):
        """
        Calculate masses using emperical and probabilistic bulk volumes and densities.

        Parameters:
        -----------
        calculate_emperical : bool, optional
            Calculate emperical masses.
        calculate_probabilistic : bool, optional
            Calculate probabilistic masses.
        """
        
        
        best_density_sampler = self._best_density_strategy()

        # Initialize mass distributions placeholders
        self.mass_distributions = [None] * len(self.data)

        if calculate_emperical:
            column = 'emperical_Bulk_Volume_m3'
            volumes = self.data[column]
            mean_masses_emp, std_masses_emp, mass_distributions_emp = [], [], []
            for idx, v in enumerate(volumes):
                sampled_densities_emp = np.random.uniform(self.density_min, self.density_max, self.num_samples)
                masses_emp = np.maximum(v * sampled_densities_emp, 1.0)  # Ensure no mass is zero or negative
                mean_masses_emp.append(np.nanmean(masses_emp))
                std_masses_emp.append(np.nanstd(masses_emp))
                mass_distributions_emp.append(masses_emp)
                self.mass_distributions[idx] = masses_emp
            self.data['Mean_Mass_emp_kg'] = mean_masses_emp
            self.data['Std_Mass_emp_kg'] = std_masses_emp

        if calculate_probabilistic:
            column = 'Probabilistic_Bulk_Volume_m3'
            if column not in self.data:
                raise ValueError("Probabilistic volumes have not been generated. Call generate_probabilistic_volumes first.")

            volumes = self.data[column]
            mean_masses_prob, std_masses_prob, mass_distributions_prob = [], [], []
            prior_mean, prior_std = np.nanmean(self.DEFAULT_BULK_DENSITY_VALUES), np.nanstd(self.DEFAULT_BULK_DENSITY_VALUES)
            
            for idx, v in enumerate(volumes):
                #iterations = 0
                valid=False 
                while not valid:
                    sampled_densities_prob = best_density_sampler(self.num_samples)
                    # Bayesian update for densities
                    evidence_mean = np.nanmean(sampled_densities_prob)
                    evidence_std = np.nanstd(sampled_densities_prob)
                    posterior_variance = 1 / ((1 / prior_std**2) + (1 / evidence_std**2))
                    posterior_mean = posterior_variance * ((prior_mean / prior_std**2) + (evidence_mean / evidence_std**2))
                    
                    # Sample updated densities
                    updated_densities = np.random.normal(loc=posterior_mean, scale=np.sqrt(posterior_variance), size=self.num_samples)
                    masses_prob = np.maximum(v * updated_densities, 1.0)
                    if idx == 0 or (np.mean(masses_prob) >= mean_masses_prob[-1]):
                        valid=True
                        #break
                    # iterations += 1
                    # if iterations > 100:  # Prevent infinite loop
                    #     break
                mean_masses_prob.append(np.mean(masses_prob))
                std_masses_prob.append(np.std(masses_prob))
                mass_distributions_prob.append(masses_prob)
                self.mass_distributions[idx] = masses_prob
            
            self.data['Mean_Mass_Prob_kg'] = mean_masses_prob
            self.data['Std_Mass_Prob_kg'] = std_masses_prob
            
            ######################
            
                    # Filter results by VEI if specified
            if vei_range is not None:
                filtered_data, filtered_mass_distributions = self._filter_by_vei(vei_range)
                self.data = filtered_data
                self.mass_distributions = filtered_mass_distributions
            
            ######################


    
    def _filter_by_vei(self, vei_range=None):
        """
        Filter the DataFrame and mass distributions for specific VEI levels or ranges.
        """
        if not self.mass_distributions:  # Check if masses have been calculated
            raise RuntimeError("Mass distributions are empty. Please run `calculate_mass` first.")

        if vei_range is None:
            return self.data, self.mass_distributions

        if isinstance(vei_range, int):
            filter_mask = self.data['VEI'] == vei_range
        elif isinstance(vei_range, (list, tuple)):
            if isinstance(vei_range, tuple):  # Range of VEI
                filter_mask = (self.data['VEI'] >= vei_range[0]) & (self.data['VEI'] <= vei_range[1])
            else:  # List of VEI values
                filter_mask = self.data['VEI'].isin(vei_range)
        else:
            raise ValueError("Invalid VEI range. Provide an int, list, tuple (range), or None.")

        filtered_data = self.data[filter_mask].reset_index(drop=True)
        filtered_mass_distributions = [
            self.mass_distributions[i] for i in filtered_data.index if self.mass_distributions[i] is not None
        ]

        return filtered_data, filtered_mass_distributions




    # def calculate_percentile_bands(self, vei_range=None):
    #     """
    #     Calculate percentile probability bands for volumes and masses.

    #     Parameters:
    #     -----------
    #     vei_range : tuple or list, optional
    #         Range of VEI levels to consider.
    #     """
    #     percentiles =[5, 25, 50, 75, 95]

    #     # Step 1: Filter data by VEI range
    #     filtered_data, filtered_masses = self._filter_by_vei(vei_range)

    #     # Debug: Check filtered data and masses
    #     print("Filtered Data:\n", filtered_data)
    #     print("Filtered Masses:\n", filtered_masses)

    #     if filtered_data.empty or not filtered_masses:
    #         print("Filtered data or masses are empty. Check VEI range or input data.")
    #         return

    #     # Debug: Check for missing or NaN columns
    #     required_columns = ['emperical_Bulk_Volume_m3', 'Probabilistic_Bulk_Volume_m3']
    #     for col in required_columns:
    #         if col not in filtered_data:
    #             print(f"Missing column in filtered data: {col}")
    #             return
    #         print(f"NaN counts in {col}:", filtered_data[col].isna().sum())
    #         if filtered_data[col].isna().all():
    #             print(f"Column {col} contains only NaN values. Cannot compute percentiles.")
    #             return

    #     # Step 2: Initialize volume percentiles DataFrame
    #     self.volume_percentiles = pd.DataFrame({'VEI': filtered_data['VEI']})

    #     # Step 3: Calculate volume percentiles
    #     for p in percentiles:
    #         emp_vol_values = filtered_data['emperical_Bulk_Volume_m3'].dropna().values
    #         prob_vol_values = filtered_data.get('Probabilistic_Bulk_Volume_m3', pd.Series()).dropna().values

    #         # Debug: Check data input for percentiles
    #         print(f"Percentile {p}: emperical Volumes:", emp_vol_values)
    #         print(f"Percentile {p}: Probabilistic Volumes:", prob_vol_values)

    #         if emp_vol_values.size == 0:
    #             print(f"No valid data for emperical volumes at percentile {p}.")
    #             self.volume_percentiles[f"emp_Volume_{p}th"] = np.nan
    #             self.volume_percentiles[f"Uncertainty_emp_Volume_{p}th"] = np.nan
    #         else:
    #             self.volume_percentiles[f"emp_Volume_{p}th"] = np.nanpercentile(emp_vol_values, p)
    #             self.volume_percentiles[f"Uncertainty_emp_Volume_{p}th"] = self.volume_percentiles[f"emp_Volume_{p}th"] * 0.1

    #         if prob_vol_values.size == 0:
    #             print(f"No valid data for probabilistic volumes at percentile {p}.")
    #             self.volume_percentiles[f"Prob_Volume_{p}th"] = np.nan
    #             self.volume_percentiles[f"Uncertainty_Prob_Volume_{p}th"] = np.nan
    #         else:
    #             self.volume_percentiles[f"Prob_Volume_{p}th"] = np.nanpercentile(prob_vol_values, p)
    #             #self.volume_percentiles[f"Uncertainty_Prob_Volume_{p}th"] = self.volume_percentiles[f"Prob_Volume_{p}th"] * 0.1

    #     # Step 4: Initialize mass percentiles DataFrame
    #     mass_percentiles = []
    #     for masses in filtered_masses:
    #         if len(masses) == 0 or np.isnan(masses).all():
    #             print("Mass data is empty or contains only NaN values.")
    #             continue

    #         masses = np.array(masses)[~np.isnan(masses)]  # Remove NaN values
    #         percentiles_dict = {f"Mass_{p}th": np.percentile(masses, p) for p in percentiles}

    #         # for p in percentiles:
    #         #     percentiles_dict[f"Uncertainty_Mass_{p}th"] = percentiles_dict[f"Mass_{p}th"] * 0.1

    #         # Calculate Best Mass Estimate and Uncertainty
    #         percentiles_dict["90%_interpercentile_Mass_Estimate"] = percentiles_dict["Mass_95th"] - percentiles_dict["Mass_5th"]
    #         # percentiles_dict["90%_interpercentile_Mass_Estimate_Uncertainty"] = (
    #         #     (percentiles_dict["Uncertainty_Mass_95th"]**2 + percentiles_dict["Uncertainty_Mass_5th"]**2) ** 0.5
    #         # )
    #         mass_percentiles.append(percentiles_dict)

    #     if not mass_percentiles:
    #         print("No valid mass data to calculate percentiles.")
    #         return

    #     self.mass_percentiles = pd.DataFrame(mass_percentiles)
    #     self.mass_percentiles.insert(0, 'VEI', filtered_data['VEI'])

    #     # Step 5: Insert results into self.data
    #     exclude_column = 'VEI'
    #     for col in self.volume_percentiles.columns:
    #         if col != exclude_column:
    #             self.data[col] = self.volume_percentiles[col]

    #     for col in self.mass_percentiles.columns:
    #         if col != exclude_column:
    #             self.data[col] = self.mass_percentiles[col]

    #     # Debug: Print final results
    #     print("### Volume Percentiles ###")
    #     print(self.volume_percentiles)
    #     print("### Mass Percentiles ###")
    #     print(self.mass_percentiles)

    def calculate_percentile_bands(self, vei_range=None):
        """
        Calculate percentile probability bands for volumes and masses.

        Parameters:
        -----------
        vei_range : tuple or list, optional
            Range of VEI levels to consider.
        """
        percentiles = [5, 25, 50, 75, 95]

        # Step 1: Filter data by VEI range
        filtered_data, filtered_masses = self._filter_by_vei(vei_range)

        if filtered_data.empty or not filtered_masses:
            print("Filtered data or masses are empty. Check VEI range or input data.")
            return

        # Step 2: Check for required columns
        required_columns = ['emperical_Bulk_Volume_m3', 'Probabilistic_Bulk_Volume_m3']
        missing_columns = [col for col in required_columns if col not in filtered_data]
        if missing_columns:
            print(f"Missing required columns: {missing_columns}")
            return

        # Step 3: Initialize volume percentiles DataFrame
        self.volume_percentiles = pd.DataFrame({'VEI': filtered_data['VEI']})

        for p in percentiles:
            emp_vol_values = filtered_data['emperical_Bulk_Volume_m3'].dropna().values
            prob_vol_values = filtered_data['Probabilistic_Bulk_Volume_m3'].dropna().values

            self.volume_percentiles[f"emp_Volume_{p}th"] = (
                np.nanpercentile(emp_vol_values, p) if emp_vol_values.size > 0 else np.nan
            )
            self.volume_percentiles[f"Uncertainty_emp_Volume_{p}th"] = (
                self.volume_percentiles[f"emp_Volume_{p}th"] * 0.1 if emp_vol_values.size > 0 else np.nan
            )

            self.volume_percentiles[f"Prob_Volume_{p}th"] = (
                np.nanpercentile(prob_vol_values, p) if prob_vol_values.size > 0 else np.nan
            )
            self.volume_percentiles[f"Uncertainty_Prob_Volume_{p}th"] = (
                self.volume_percentiles[f"Prob_Volume_{p}th"] * 0.1 if prob_vol_values.size > 0 else np.nan
            )

        # Step 4: Calculate mass percentiles
        mass_percentiles = []
        for masses in filtered_masses:
            if len(masses) == 0 or np.isnan(masses).all():
                continue

            masses = np.array(masses)[~np.isnan(masses)]  # Remove NaN values
            percentiles_dict = {f"Mass_{p}th": np.nanpercentile(masses, p) for p in percentiles}

            # Calculate interpercentile range
            percentiles_dict["90%_interpercentile_Mass_Estimate"] = (
                percentiles_dict["Mass_95th"] - percentiles_dict["Mass_5th"]
            )
            mass_percentiles.append(percentiles_dict)

        if not mass_percentiles:
            print("No valid mass data to calculate percentiles.")
            return

        self.mass_percentiles = pd.DataFrame(mass_percentiles)
        self.mass_percentiles.insert(0, 'VEI', filtered_data['VEI'])

        # Step 5: Insert results into self.data
        for col in self.volume_percentiles.columns:
            if col != 'VEI':
                self.data[col] = self.volume_percentiles[col]

        for col in self.mass_percentiles.columns:
            if col != 'VEI':
                self.data[col] = self.mass_percentiles[col]

        # Debug: Print final results
        print("### Volume Percentiles ###")
        print(self.volume_percentiles)
        print("### Mass Percentiles ###")
        print(self.mass_percentiles)

        
    

    def generate_summary_statistics(self):
        """Generate summary statistics for volumes and masses grouped by VEI level."""
        print("\n### Generating Summary Statistics Grouped by VEI Level ###")

        # Step 1: Verify and clean the VEI column
        if 'VEI' not in self.data.columns:
            raise ValueError("The column 'VEI' does not exist in the DataFrame.")
        
        # Ensure VEI is a single Series (not a DataFrame)
        print("Ensuring VEI is a Series...")
        if isinstance(self.data['VEI'], pd.DataFrame):
            self.data['VEI'] = self.data['VEI'].iloc[:, 0]

        # Flatten any lists or tuples in VEI and convert to strings
        print("Flattening and cleaning VEI column...")
        self.data['VEI'] = self.data['VEI'].apply(
            lambda x: str(x[0]).strip() if isinstance(x, (list, tuple)) else str(x).strip()
        )
        
        # Debug: Confirm unique VEI values
        print("Unique VEI values after cleaning:", self.data['VEI'].unique())

        # Step 2: Define aggregation dictionary dynamically
        agg_dict = {
            'emperical_Bulk_Volume_m3': ['mean', 'std', 'median']
        }
        if 'Probabilistic_Bulk_Volume_m3' in self.data:
            agg_dict['Probabilistic_Bulk_Volume_m3'] = ['mean', 'std', 'median']
        if 'Mean_Mass_emp_kg' in self.data:
            agg_dict['Mean_Mass_emp_kg'] = ['mean', 'std', 'median']
        if 'Mean_Mass_Prob_kg' in self.data:
            agg_dict['Mean_Mass_Prob_kg'] = ['mean', 'std', 'median']

        # Step 3: Perform groupby operation
        print("Performing groupby operation...")
        grouped = self.data.groupby('VEI', as_index=False).agg(agg_dict)

        # Step 4: Flatten column names
        grouped.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in grouped.columns]

        # Step 5: Print and store the results
        print("\n### Summary Statistics Grouped by VEI ###")
        print(tabulate(grouped, headers='keys', tablefmt='grid', showindex=False))

        # Save results to the class attribute
        self.summary_statistics = grouped

        # Optional: Provide a quick summary for the entire dataset
        print("\n### Overall Dataset Statistics ###")
        print(tabulate(self.data.describe(), headers='keys', tablefmt='grid', showindex=True))



    def visualize_statistics(self, pdf_pages=None):
        """
        Visualize volumes and masses using histograms, KDE plots, and boxplots with interpretations.
        Optionally save plots to a PDF file if `pdf_pages` is provided.
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))

        # Plot 1: Histogram for emperical Volumes
        sns.histplot(self.data['emperical_Bulk_Volume_m3'], kde=True, ax=axes[0, 0], bins=20, color="skyblue")
        axes[0, 0].set_title("emperical Bulk Volumes Distribution")
        axes[0, 0].set_yscale('log')  # Set y-axis to log scale
        # Plot 2: Histogram for Probabilistic Volumes (sampled)
        all_probabilistic_volumes = []
        for idx, (min_volume, max_volume) in enumerate(self.BULK_VOLUME_RANGES):
            samples_per_vei = self.num_samples // len(self.BULK_VOLUME_RANGES)
            sampled_volumes = np.random.uniform(min_volume, max_volume, samples_per_vei)
            all_probabilistic_volumes.extend(sampled_volumes)

        sns.histplot(all_probabilistic_volumes, kde=True, ax=axes[0, 1], bins=20, color="orange")
        axes[0, 1].set_title("Probabilistic Bulk Volumes Distribution (Sampled)")
        #axes[0, 1].set_xscale('log')  # Set x-axis to log scale
        axes[0, 1].set_yscale('log')  # Set x-axis to log scale
        axes[0,1].set_xlabel('probablistic_Bulk_Volume_m3')

        # Plot 3: Boxplot for emperical Mass
        if 'Mean_Mass_emp_kg' in self.data:
            sns.boxplot(data=self.data[['Mean_Mass_emp_kg']], ax=axes[1, 0], color="lightgreen")
            axes[1, 0].set_title("emperical Mass Distribution Boxplot")

        # Plot 4: KDE Plot for Probabilistic Mass (if available)
        if 'Mean_Mass_Prob_kg' in self.data:
            sns.kdeplot(self.data['Mean_Mass_Prob_kg'], ax=axes[1, 1], fill=True, color="green", label="Mass Density")
            mean_mass = self.data['Mean_Mass_Prob_kg'].mean()
            axes[1, 1].axvline(mean_mass, color='red', linestyle='--', label=f"Mean Mass: {mean_mass:.2e} kg")
            axes[1, 1].set_title("Probabilistic Mass KDE Plot")
            axes[1, 1].legend()

        # Layout and show or save the plot
        plt.tight_layout()
        if pdf_pages:
            pdf_pages.savefig(fig)



    def export_statistics(self, filename="summary_statistics.csv"):
        """Export summary statistics to a CSV file."""
        summary = self.data.describe().T
        summary.to_csv(filename)
        print(f"Summary statistics saved to {filename}.")

    

    def plot_percentile_bands(self, vei_range=None, pdf_pages=None):
        """
        Plot percentile probability bands for volumes and masses.
        """
        if not hasattr(self, 'volume_percentiles') or not hasattr(self, 'mass_percentiles'):
            print("Error: Percentiles have not been calculated. Run `calculate_percentile_bands()` first.")
            return

        percentiles =  [5, 25, 50, 75, 95]
        filtered_data = self.volume_percentiles if vei_range is None else self.volume_percentiles[
            self.volume_percentiles['VEI'].between(vei_range[0], vei_range[1])
        ]

        # Plot Volume Percentile Bands
        plt.figure(figsize=(10, 6))
        color_palette = sns.color_palette("coolwarm", len(percentiles))

        # Plot percentile lines
        line_handles = []
        for i, p in enumerate(percentiles):
            emperical_line, = plt.plot(
                filtered_data['VEI'], 
                filtered_data[f"emp_Volume_{p}th"],
                label=f"emperical {p}th Percentile",
                color=color_palette[i], linewidth=2
            )
            probabilistic_line, = plt.plot(
                filtered_data['VEI'], 
                filtered_data[f"Prob_Volume_{p}th"],
                linestyle='--', 
                label=f"Probabilistic {p}th Percentile",
                color=color_palette[i], linewidth=2
            )
            # Collect handles for the first legend
            if i == 0:  # Only add one pair to avoid duplicating lines in legend
                line_handles.append(emperical_line)
                line_handles.append(probabilistic_line)

        # Add title and labels
        plt.title("emperical and Probabilistic Volume Percentile Bands", fontsize=16, fontweight='bold')
        plt.xlabel("Volcanic Explosivity Index (VEI)", fontsize=14)
        plt.ylabel("Volume (m³)", fontsize=14)
        plt.yscale('log')

        # Add grid for better readability
        plt.grid(True, linestyle='--', alpha=0.7)

        # Legend 1: Plot Lines
        legend1 = plt.legend(handles=line_handles, labels=["emperical Percentile", "Probabilistic Percentile"],
                            loc="upper left", fontsize=10, title="Plot Lines")

        # Legend 2: Interpretation
        interpretation_text = [
            "emperical: Solid lines indicate modeled volumes.",
            "Probabilistic: Dashed lines show uncertainty.",
            "Percentiles: 5th, 25th, 50th (Median), 75th, 95th.",
            "Increasing VEI corresponds to larger volumes."
        ]
        interpretation_legend = plt.legend(handles=[], labels=interpretation_text,
                                        loc="upper right", fontsize=10, title="Interpretation")

        # Add both legends back to the plot
        plt.gca().add_artist(legend1)
        plt.gca().add_artist(interpretation_legend)

        # Adjust layout to ensure legends do not overlap
        fig=plt.tight_layout()
        if pdf_pages:
            pdf_pages.savefig(fig)
            plt.close(fig)
        else:
            plt.show()

        # Plot Mass Percentile Bands
        fig=plt.figure(figsize=(10, 6))
        for p in percentiles:
            plt.plot(self.mass_percentiles['VEI'], self.mass_percentiles[f"Mass_{p}th"], label=f"Mass {p}th %ile")
                
        plt.title("Mass Percentile Probability Bands")
        plt.xlabel("VEI Level")
        plt.ylabel("Mass (kg)")
        plt.legend()
        plt.grid()
        plt.yscale("log")
        
        if pdf_pages:
            pdf_pages.savefig(fig)
            plt.close(fig)
        else:
            plt.show()
        
        from scipy.interpolate import griddata
        # Prepare the original meshgrid and data
        vei_levels = self.mass_percentiles['VEI']
        mass_values = [self.mass_percentiles[f"Mass_{p}th"].values for p in percentiles]
        X, Y = np.meshgrid(vei_levels, percentiles)
        Z = np.array(mass_values)

       # Interpolate to a finer grid for smoother contours
        finer_vei = np.linspace(vei_levels.min(), vei_levels.max(), 1)  # High resolution grid
        finer_percentiles = np.linspace(min(percentiles), max(percentiles), 1)
        X_fine, Y_fine = np.meshgrid(finer_vei, finer_percentiles)
        Z_fine = griddata((X.flatten(), Y.flatten()), Z.flatten(), (X_fine, Y_fine), method='cubic')

        # Fill gaps by replacing NaN values with nearest neighbors
        Z_fine = np.nan_to_num(Z_fine, nan=np.nanmin(Z))

        # Generate filled contour plot with log scale
        fig=plt.figure(figsize=(12, 8))
        filled_contour = plt.contourf(
            X, Y, Z, levels=1, cmap="plasma", alpha=0.75 , norm=LogNorm(vmin=Z.min(), vmax=Z.max()) ) #  norm=LogNorm(vmin=Z.min(), vmax=Z.max()), 
        cbar = plt.colorbar(filled_contour, pad=0.02, aspect=30, shrink=0.8)
        cbar.set_label("Mass (kg) [Log Scale]", fontsize=12)

        # Add labeled contour lines for clarity
        contour_lines = plt.contour(
            X, Y, Z, levels=1, colors='black', linewidths=0.8, linestyles='solid', norm=LogNorm(vmin=Z.min(), vmax=Z.max())) #norm=LogNorm(vmin=Z.min(), vmax=Z.max())  
        plt.clabel(contour_lines, inline=True, fontsize=10, fmt="%.1e", colors='white')

        # Add labels, grid, and custom aesthetics
        plt.title("Mass Percentile Probability Bands with Log-Scaled Contours", fontsize=14, weight='bold')
        plt.xlabel("VEI Level", fontsize=12)
        plt.ylabel("Percentile (%)", fontsize=12)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.5)
       
       
        # Adjust layout and display the plot
        plt.tight_layout()
        if pdf_pages:
            pdf_pages.savefig(fig)
            plt.close(fig)
        else:
            plt.show()

        
        #########
        
    def summary(self):
        print(self.data)
        
    def export_data(self, filename='VEI_MASS_VolumeResults.csv'):
        """Export the current data DataFrame to a CSV file."""
        self.data.to_csv(filename, index=False)
        print(f"Data successfully exported to {filename}")
        
    

    def save_outputs_to_pdf(self, filename='output_results.pdf'):
        """
        Save all outputs, including tables, statistics, percentile bands, and visualizations, to a single PDF file.
        Ensures text does not clip and spans multiple pages if needed.

        Parameters:
        -----------
        filename : str
            Filename for the output PDF.
        """
        with PdfPages(filename) as pdf:
            # Capture printed output
            printed_output = io.StringIO()
            sys.stdout = printed_output
            
            # Generate printed outputs
            print("\n### Summary Statistics ###")
            #print(self.data.describe())
            # Convert to table
            #print(tabulate(self.data, headers='keys', tablefmt='grid', showindex=False))
            print(self.data.describe().to_string(index=False))
            
            # Reset stdout
            sys.stdout = sys.__stdout__
            full_text = printed_output.getvalue()
            
            # Paginate the text output
            max_chars_per_page = 3000  # Adjust this based on page size and font
            wrapped_text = textwrap.wrap(full_text, width=100)  # Wrap text to fit within page width
            
            # Create pages for wrapped text
            page_content = []
            temp_text = ""
            for line in wrapped_text:
                temp_text += line + "\n"
                if len(temp_text) >= max_chars_per_page:
                    page_content.append(temp_text)
                    temp_text = ""
            if temp_text:
                page_content.append(temp_text)
            
            # Save each page of text as a PDF page
            for page_text in page_content:
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.axis('off')
                ax.text(0, 1, page_text, fontsize=10, ha='left', va='top', wrap=True)
                pdf.savefig(fig)
                plt.close(fig)
            
            # Call existing visualization methods
            self.visualize_statistics(pdf_pages=pdf)
            
            # Call existing percentile band calculations
            self.plot_percentile_bands(pdf_pages=pdf)
        
        print(f"All outputs successfully saved to {filename}.")
        
    def export_volumes_and_masses(self, volume_filename='volumes_data.csv', mass_filename='masses_data.csv'):
        """
        Export volume and mass-related columns to separate CSV files.

        Parameters:
        -----------
        volume_filename : str
            Filename for volume data.
        mass_filename : str
            Filename for mass data.
        """
        # Export volume-related columns
        volume_columns = [
            col for col in self.data.columns 
            if 'Volume' in col or col == 'VEI'
        ]
        volume_data = self.data[volume_columns]
        volume_data.to_csv(volume_filename, index=False)
        print(f"Volume data successfully exported to {volume_filename}")

        # Export mass-related columns
        mass_columns = [
            col for col in self.data.columns 
            if 'Mass' in col or col == 'VEI'
        ]
        mass_data = self.data[mass_columns]
        mass_data.to_csv(mass_filename, index=False)
        print(f"Mass data successfully exported to {mass_filename}")
        
        ######################################################################
        

# Load Eruption source paramerter Datasets
import pandas as pd
import geopandas as gpd
import numpy as np

class LOADDATA:
    def __init__(self):
        self.datasets = {
            "IVESPA": pd.read_csv("./data/IVESPAData.csv"),
            "Aubry": pd.read_csv("./data/AubryData.csv"),
            "Mastin": pd.read_csv("./data/MastinData.csv"),
            "Sparks": pd.read_csv("./data/SparksData.csv"),
            "whelley_2015": pd.read_csv("./data/Whelley_2015.csv"),
            'Mastin_a': pd.read_csv("./data/volcanoExport.csv",  encoding='ISO-8859-1')
        }

    def load_IVESPA(self, as_geodataframe: bool = False):
        df = self.datasets["IVESPA"]
        
        # Ensure numeric types for calculations
        df["TEM_kg"] = pd.to_numeric(df.get("TEM_kg", np.nan), errors="coerce")
        df["Duration_hours"] = pd.to_numeric(df.get("Duration_hours", np.nan), errors="coerce")
        df["Tephra Plume Top Best estimate (km a.s.l.)"] = pd.to_numeric(
            df.get("Tephra Plume Top Best estimate (km a.s.l.)", np.nan), errors="coerce"
        )
        df["Vent altitude (m a.s.l.)"] = pd.to_numeric(
            df.get("Vent altitude (m a.s.l.)", np.nan), errors="coerce"
        )

        # Calculate MER (kg/s) safely
        df["MER_kg/s"] = df["TEM_kg"] / (df["Duration_hours"].replace(0, np.nan) * 3600)

        # Calculate Plume height safely
        df["Height_km.a.v.l"] = (
            df["Tephra Plume Top Best estimate (km a.s.l.)"]
            - df["Vent altitude (m a.s.l.)"] / 1000.0
        )

        # Combine Volcano and Event Name
        df["Name"] = df["Volcano"].fillna("").combine(
            df["Event Name"].fillna(""), lambda a, b: a + " " + b
        )
        
        # Rename Columns to standard names
        df.rename(columns={
            'TEM Best estimate (kg)': 'TEM_kg', 
            'Duration Best estimate (hours)': 'Duration_hours'
        }, inplace=True)
        
       

        # Select and return required columns
        #df = df[['VEI', 'Height_km.a.v.l', 'TEM_kg', 'MER_kg/s', 'Duration_hours']]

        if as_geodataframe:
            df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']))
            df.set_crs(epsg=4326, inplace=True)

        return df

    def load_Aubry(self, as_geodataframe: bool = False):
        df = self.datasets["Aubry"]

        

        df['MER (kg/s)'] = df['Erupted tephra mass (kg)'] / (df['Duration (hrs)'] * 3600.0)
        df['Name'] = df['Volcano'].combine(df['Eruption'], lambda a, b: a + " " + (str(b) or ""))
        
        
        
        # Rename Columns to standard names
        df.rename(columns={
            'Erupted tephra mass (kg)': 'TEM_kg',
            'Duration (hrs)': 'Duration_hours',
            'Plume height (km a.v.l.)': 'Height_km.a.v.l',
            "MER (kg/s)": "MER_kg/s"
        }, inplace=True)
        
        # if 'VEI' not in df.columns:
        #     df['VEI'] = None

        # Select and return required columns
        #df = df[['Height_km.a.v.l', 'TEM_kg', 'MER_kg/s', 'Duration_hours']]

        if as_geodataframe:
            df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']))
            df.set_crs(epsg=4326, inplace=True)

        return df

    def load_Mastin(self, as_geodataframe: bool = False):
        df = self.datasets["Mastin"]

        # Compute TEM_kg using MER and Duration
        df['TEM_kg'] = df['MER (kg/s)'] / 3600 * df['Duration (hours)']

        # Rename Columns to standard names
        df.rename(columns={
            'Duration (hours)': 'Duration_hours',
            'Plume height (km a.v.l.)': 'Height_km.a.v.l',
            "MER (kg/s)": "MER_kg/s"
        }, inplace=True)

        # Select and return required columns
        #df = df[['VEI', 'Height_km.a.v.l', 'TEM_kg', 'MER_kg/s', 'Duration_hours']]

        if as_geodataframe:
            df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']))
            df.set_crs(epsg=4326, inplace=True)

        return df
    
    def load_Mastin_a(self, as_geodataframe: bool = False):
        df = self.datasets["Mastin_a"]

        # Compute TEM_kg using MER and Duration
        df['TEM_kg'] = df['MER (kg/s)'] / 3600 * df['Duration (hours)']

        # Rename Columns to standard names
        df.rename(columns={
            'Duration (hours)': 'Duration_hours',
            'Plume height (km a.v.l.)': 'Height_km.a.v.l',
            "MER (kg/s)": "MER_kg/s"
        }, inplace=True)

        # Select and return required columns
        #df = df[['VEI', 'Height_km.a.v.l', 'TEM_kg', 'MER_kg/s', 'Duration_hours']]

        if as_geodataframe:
            df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']))
            df.set_crs(epsg=4326, inplace=True)

        return df

    def load_Sparks(self, as_geodataframe: bool = False):
        df = self.datasets["Sparks"]

        # Compute TEM_kg using MER and Duration
        df['TEM_kg'] = df['MER (kg/s)'] / 3600 * df['Duration (hours)']

        # Rename Columns to standard names
        df.rename(columns={
            'Duration (hours)': 'Duration_hours',
            'Plume height (km a.v.l.)': 'Height_km.a.v.l',
            "MER (kg/s)": "MER_kg/s"
        }, inplace=True)

        if 'VEI' not in df.columns:
            df['VEI'] = None

        # Select and return required columns
        #df = df[['VEI', 'Height_km.a.v.l', 'TEM_kg', 'MER_kg/s', 'Duration_hours']]

        if as_geodataframe:
            df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']))
            df.set_crs(epsg=4326, inplace=True)

        return df
    
    def whelley_2015(self, as_geodataframe: bool = False):
        df=self.datasets["whelley_2015"]
        
        if as_geodataframe:
            df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']))
            df.set_crs(epsg=4326, inplace=True)

        return df
    
    def search_whelley_2015(self, max_vei_returns=None, **kwargs):
        """
        Search the whelley_2015 dataframe using one or multiple columns.

        Parameters:
        max_vei_returns: int, optional
            The maximum number of VEI values to return, in descending order. Default is None (return all non-zero VEI values).
        **kwargs: Key-value pairs where keys are column names, and values are the values to search for.
            If 'coordinates' is used as a key, its value must be a tuple (lat, lon).

        Returns:
        A filtered dataframe containing matching rows and a list of VEI values in descending order.

        Example:
        # Search by Volcano Number (unique ID):
        search_whelley_2015(Volcano_Number=345060)

        # Search by Volcano name:
        search_whelley_2015(Volcano="Mount St. Helens")

        # Search by geographic coordinates:
        search_whelley_2015(coordinates=(45.1, -122.2))

        # Search by elevation range:
        search_whelley_2015(Elevation_m=(2500, 3000))

        # Search by volcano classification:
        search_whelley_2015(Classification="Stratovolcano")

        # Search by Volcanic Explosivity Index (VEI):
        search_whelley_2015(VEI_5=1)

        Columns available for search:
        - 'Volcano Number': Search by unique volcano identification number.
        - 'Volcano': Search by the volcano's name.
        - 'Latitude' and 'Longitude': Search by geographic coordinates (e.g., coordinates=(45.1, -122.2)).
        - 'Elevation (m)': Search by elevation range or specific value.
        - 'Classification': Search by volcano classification.
        - 'VEI X' (e.g., 'VEI 5'): Search by Volcanic Explosivity Index values.
        """
        df = self.datasets.get("whelley_2015")
        df = df.drop(columns=['VEI 1'])

        for column, value in kwargs.items():
            if column == 'coordinates':
                if not isinstance(value, tuple) or len(value) != 2:
                    raise ValueError("For 'coordinates', the value must be a tuple of (lat, lon).")
                lat, lon = value
                df = df[(df['Latitude'] == lat) & (df['Longitude'] == lon)]
            elif column in df.columns:
                if isinstance(value, tuple) and len(value) == 2:
                    df = df[(df[column] >= value[0]) & (df[column] <= value[1])]
                elif isinstance(value, str):
                    df = df[df[column].str.contains(value, case=False, na=False)]
                else:
                    df = df[df[column] == value]
            else:
                raise ValueError(f"Invalid column: {column}. Please use a valid column name.")

        # Identify the VEI columns with non-zero values
        vei_columns = [col for col in df.columns if col.startswith("VEI ")]
        if not vei_columns:
            print("No VEI columns found in the dataset.")
            return df, []

        vei_sums = df[vei_columns].sum()
        non_zero_vei = vei_sums[vei_sums > 0].sort_values(ascending=False)

        if max_vei_returns:
            non_zero_vei = non_zero_vei.head(max_vei_returns)

        vei_values = non_zero_vei.index.str.extract(r'(\d+)')[0].astype(int).tolist()

        print(f"Top VEI values returned: {vei_values}")
        return df, vei_values

    
        

# Initialize the LOADDATA class
data_loader = LOADDATA()


# Initialize the LOADDATA class
#data_loader = LOADDATA()


##############################################

# Explor data correlations

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def analyze_correlations(dataframe, dataset_name, threshold=0.6):
    """
    Analyze correlations among specific columns, filter based on a user-defined threshold,
    and visualize the best correlations using scatter plots.

    Parameters:
        dataframe (pd.DataFrame): Input DataFrame containing relevant columns.
        dataset_name (str): Name of the dataset for plot titles.
        threshold (float): User-defined threshold for correlation filtering (default is 0.6).

    Returns:
        pd.DataFrame: DataFrame with correlation pairs and their values above the threshold.
    """
    # Define columns of interest
    columns_of_interest = ['Height_km.a.v.l', 'TEM_kg', 'MER_kg/s', 'Duration_hours']
    columns_to_check = ["Brunt-Väisälä frequency", 'VEI', 'MASS_FRACTION_ASH_BELOW_63_micron']

    # Check if each column in `columns_to_check` exists in the dataframe
    for column in columns_to_check:
        if column in dataframe.columns:
            columns_of_interest.append(column)

    # Filter and drop rows with missing values
    filtered_data = dataframe[columns_of_interest].dropna()

    # Define correlation methods
    methods = ['pearson', 'spearman', 'kendall']
    correlation_results = {}

    # Compute correlation matrices for each method
    for method in methods:
        correlation_results[method] = filtered_data.corr(method=method)

    # Combine all correlation results
    combined_correlations = []
    for method, matrix in correlation_results.items():
        sorted_pairs = (
            matrix.unstack()
            .reset_index()
            .rename(columns={0: 'Correlation', 'level_0': 'Column1', 'level_1': 'Column2'})
        )
        sorted_pairs['Method'] = method
        combined_correlations.append(sorted_pairs)

    combined_correlations_df = pd.concat(combined_correlations)
    combined_correlations_df = combined_correlations_df[combined_correlations_df['Column1'] != combined_correlations_df['Column2']]
    combined_correlations_df['Abs_Correlation'] = combined_correlations_df['Correlation'].abs()

    # Filter correlations above the threshold
    filtered_correlations = combined_correlations_df[combined_correlations_df['Abs_Correlation'] >= threshold]

    # Select the best correlation for each unique pair
    best_correlations = (
        filtered_correlations.loc[
            filtered_correlations.groupby(['Column1', 'Column2'])['Abs_Correlation'].idxmax().dropna()
        ]
    )

    # Plot heatmap for the best method
    if not best_correlations.empty:
        best_method = best_correlations.iloc[0]['Method']
        correlation_matrix = correlation_results[best_method]

        plt.figure(figsize=(10, 8))
        heatmap = sns.heatmap(
            correlation_matrix,
            annot=True,
            cmap='coolwarm',
            fmt=".2f",
            square=True,
            cbar=True,
            linewidths=0.5,
            linecolor='black'
        )
        plt.title(f"Correlation Heatmap for {dataset_name} (Method: {best_method})", fontsize=14)
        plt.tight_layout()
        plt.show()

    # Combined scatter plots for the best pairs
    if not best_correlations.empty:
        plt.figure(figsize=(12, 8))

        plotted_pairs = set()  # Track plotted pairs to avoid duplicates

        for _, row in best_correlations.iterrows():
            col1, col2, method, corr = row['Column1'], row['Column2'], row['Method'], row['Correlation']

            # Ensure each pair is plotted only once (ignore reversed pairs)
            if (col2, col1) in plotted_pairs or (col1, col2) in plotted_pairs:
                continue

            plotted_pairs.add((col1, col2))

            x_data, y_data = filtered_data[col1], filtered_data[col2]

            # Determine if log scale is needed
            x_scale = 'log' # if (x_data.min() > 0 and x_data.max() / x_data.min() > 10) else 'linear'
            y_scale = 'log' #if (y_data.min() > 0 and y_data.max() / y_data.min() > 10) else 'linear'

            plt.scatter(
                x_data,
                y_data,
                alpha=0.7,
                label=f"{col1} vs {col2} (Corr: {corr:.2f}, {method})"
            )

            # Apply log scale if needed
            plt.xscale(x_scale)
            plt.yscale(y_scale)

        plt.legend(loc='best', fontsize=9)
        plt.title(f"Scatter Plots of Correlation Pairs for {dataset_name}", fontsize=14)
        plt.xlabel("X-axis (variable dependent)", fontsize=12)
        plt.ylabel("Y-axis (variable dependent)", fontsize=12)
        plt.tight_layout()
        plt.show()

    return best_correlations