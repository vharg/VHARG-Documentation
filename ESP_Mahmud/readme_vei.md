## Contact Details

For questions or support, feel free to reach out to the author or create an issue on the project's repository.

**Dr. Mahmud Muhammad**  
(PhD, MSc, and BSc in Geology)  
Email: [mahmud.geology@hotmail.com](mailto:mahmud.geology@hotmail.com)  
Website: [mahmudm.com](http://mahmudm.com)


# VEI_BulkVolume_Mass Class

The `VEI_BulkVolume_Mass` class provides a robust framework for analyzing and calculating volcanic bulk volumes and masses across various VEI (Volcanic Explosivity Index) levels. By incorporating both empirical and probabilistic approaches, this class supports advanced Bayesian updates for density estimation and offers visualization and export tools for effective data analysis and reporting.

## Key Features
- **Comprehensive Volume and Mass Calculations**: Supports empirical and probabilistic bulk volume estimation with detailed analysis.
- **Bayesian Density Updating**: Implements Bayesian probability methods to refine density bounds using predefined or user-specified data.
- **Advanced Visualization**: Creates histograms, KDE plots, boxplots, and percentile bands for detailed data insights.
- **Export Capabilities**: Facilitates exporting of results to CSV and PDF formats for further analysis and documentation.

---

## Attributes
The following attributes store the core data and results of the calculations:
- **`data`**: A DataFrame containing VEI levels, bulk volumes, and calculated masses.
- **`mass_distributions`**: A list of mass distributions corresponding to each VEI level.
- **`summary_statistics`**: Summary statistics of volumes and masses grouped by VEI levels.
- **`volume_percentiles`**: Percentile bands for bulk volumes.
- **`mass_percentiles`**: Percentile bands for masses.

---

## Parameters
The class can be initialized with the following parameters:
- **`use_default_densities`** *(bool, optional)*: Use predefined bulk density values (default: `True`).
- **`density_min`** *(int, optional)*: Minimum density value (default: `800`).
- **`density_max`** *(int, optional)*: Maximum density value (default: `1200`).
- **`num_samples`** *(int, optional)*: Number of samples for Monte Carlo simulations (default: `10000`).

---

## Methods

### Initialization
```python
vei = VEI_BulkVolume_Mass(use_default_densities=True, density_min=800, density_max=1200, num_samples=10000)
```
Initializes the class with default or custom parameters.

### Core Methods
- **`generate_probabilistic_volumes`**
  - Generates probabilistic bulk volumes ensuring consistency with the empirical PDF while maintaining a logarithmic trend with increasing VEI levels.

- **`calculate_mass`**
  - Computes masses for empirical and probabilistic bulk volumes using density values refined by Bayesian updating.
  - Parameters:
    - `calculate_empirical` *(bool)*: Whether to compute empirical masses.
    - `calculate_probabilistic` *(bool)*: Whether to compute probabilistic masses.

- **`calculate_percentile_bands`**
  - Calculates percentile probability bands for bulk volumes and masses across specified VEI ranges.

- **`generate_summary_statistics`**
  - Produces grouped summary statistics for volumes and masses by VEI levels, including mean, standard deviation, and median values.

- **`visualize_statistics`**
  - Creates detailed visualizations, including histograms, KDE plots, and boxplots, for empirical and probabilistic distributions.

### Export Methods
- **`export_volumes_and_masses`**
  - Exports volume and mass-related data to separate CSV files.
  - Parameters:
    - `volume_filename` *(str)*: Name of the CSV file for volume data.
    - `mass_filename` *(str)*: Name of the CSV file for mass data.

- **`export_statistics`**
  - Saves summary statistics to a CSV file.

- **`save_outputs_to_pdf`**
  - Consolidates all results, including tables, statistics, and visualizations, into a single PDF file.

### Utility Methods
- **`determine_best_sampling_strategy`**
  - Identifies the optimal probabilistic distribution for bulk volumes using statistical metrics such as AIC and KS tests.

- **`_estimate_density_bounds`**
  - Estimates density bounds through Bayesian probability updating based on predefined bulk density values.

- **`plot_percentile_bands`**
  - Visualizes percentile probability bands for bulk volumes and masses.

- **`summary`**
  - Displays the current dataset stored in the `data` attribute.

---

## Example Usage
```python
# Initialize the class
vei = VEI_BulkVolume_Mass()

# Generate probabilistic volumes and calculate masses
vei.generate_probabilistic_volumes()
vei.calculate_mass()

# Calculate percentile bands and generate summary statistics
vei.calculate_percentile_bands()
vei.generate_summary_statistics()

# Visualize and export results
vei.visualize_statistics()
vei.export_volumes_and_masses(volume_filename="volumes.csv", mass_filename="masses.csv")
vei.save_outputs_to_pdf(filename="results.pdf")
```

---

## Default Bulk Densities
The class utilizes a predefined set of bulk density values from the IVESPA database for Bayesian updates. These values can be overridden by specifying custom `density_min` and `density_max` parameters during initialization.

---

## Dependencies
To use the `VEI_BulkVolume_Mass` class, ensure the following libraries are installed:
- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `scipy`
- `tabulate`

Install them using pip:
```bash
pip install pandas numpy matplotlib seaborn scipy tabulate
```

---

## Detailed Workflow
### Step 1: Initialization
Begin by initializing the class with appropriate parameters. The default densities and sample size can be customized.

### Step 2: Probabilistic Volume Generation
Use `generate_probabilistic_volumes` to create probabilistic bulk volumes that align with empirical values while maintaining realistic trends.

### Step 3: Mass Calculation
Calculate masses using `calculate_mass`, leveraging Bayesian updates to refine density estimates.

### Step 4: Percentile and Statistical Analysis
Compute percentile probability bands for volumes and masses using `calculate_percentile_bands`. Generate grouped summary statistics with `generate_summary_statistics`.

### Step 5: Visualization and Export
Visualize results using `visualize_statistics` and export data or plots using `export_volumes_and_masses` or `save_outputs_to_pdf`.

---

## Additional Information
For further information, bug reports, or contributions, please contact the author or refer to the documentation for detailed descriptions of the algorithms implemented in this class.
