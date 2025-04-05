
# Project README

## Project Overview
This project focuses on developing a probabilistic framework for defining eruption source parameters critical for volcanic ash hazard assessment. The methodology integrates various datasets, statistical models, and Python scripts to address key challenges in volcanic monitoring, particularly during the early stages of an eruption.

### Key Objectives
1. **Define Probability Density Functions (PDFs):** 
   - PDFs describe inputs required by the NAME model at different stages:
     - **First VONA:** Only location and time are known.
     - **Infrasound data:** Plume height range and duration are also known.
     - **Satellite data:** Provides refined details.
2. **Stochastic Parameter Sampling:** 
   - Parameters include mass eruption rate (MER), eruption duration, plume height, and grain size distribution.
   - Weighted by probabilities derived from VEI data.
3. **Automated Data Processing:**
   - Real-time data collection from Volcanic Ash Advisory Centers (VAACs).
   - Integration of empirical relationships and Bayesian models for parameter estimation.

### Deliverables
1. Python scripts for probabilistic sampling of eruption parameters.
2. Automated tools for scraping and processing VAAC reports.
3. Statistical models for parameter estimation using Bayesian principles.
4. Probabilistic maps and distributions for volcanic ash concentration.

## Methodology

### Workflow Summary
| Step | Action | Output |
|------|--------|--------|
| 1    | Parse location and volcano name from VAAC. | Volcano name and location |
| 2    | Calculate weighted VEI using Whelley et al. (2015). | Weighted VEI |
| 3    | Estimate total volume using VEI. | Total Volume (km³ or m³) |
| 4    | Calculate Total Erupted Mass (TEM). | TEM (kg) |
| 5    | Determine MER using TEM and eruption duration. | MER (kg/s) |
| 6    | Estimate eruption duration. | Duration (hours) |
| 7    | Derive plume height and fine debris mass fraction. | Plume Height (km), Fine Debris |

### Data Sources
1. **Whelley et al. (2015):** Annual VEI probabilities.
2. **IVESPA Database:** Tephra density and eruption statistics.
3. **VAAC Reports:** Real-time eruption notifications.
4. **Empirical Relationships:** For volume, mass, and plume height.

## Python Scripts Overview

### VAAC Data Parser
- **Class Name:** `VEP_TVAAC_VAAText`
- **Features:**
  - Extracts HTML tables from VAAC advisories.
  - Processes volcano name, location, and ash cloud height.
  - Outputs structured data (CSV, raw text).

### Probabilistic VEI Calculation
- **Functionality:** Integrates Whelley et al. (2015) database for VEI probabilities.
- **Outputs:** Weighted VEI for each volcano.

### Volume and Mass Calculations
- **Method:**
  - Converts VEI to erupted volume using historical data.
  - Computes TEM using density estimates and Bayesian techniques.
- **Outputs:** Probabilistic distributions for volume and mass.

### Mass Eruption Rate and Duration
- **Input:** TEM and duration relationships.
- **Output:** MER estimates using Bayesian statistics and IVESPA data.

### Plume Height Estimation
- **Method:**
  - Bayesian linear regression on MER and plume height.
  - Generates posterior distributions for uncertainty quantification.

## Figures and Visual Outputs
The scripts generate various plots to visualize relationships between eruption parameters:
1. **VEI vs. Volume:** Empirical and probabilistic estimates.
2. **VEI vs. Total Erupted Mass:** Percentile-based contours.
3. **MER vs. Plume Height:** Predictive distributions and posterior estimates.
4. **Mass Fraction of Fine Debris:** Probabilistic relationships with MER.

## References
1. Aubry, T.J. et al., 2023, *New Insights Into the Relationship Between Mass Eruption Rate and Volcanic Column Height.*
2. Mastin, L.G., et al., 2009, *Preliminary Spreadsheet of Eruption Source Parameters for Volcanoes of the World.*
3. Whelley, P.L., et al., 2015, *The Frequency of Explosive Volcanic Eruptions in Southeast Asia.*

For more details, visit the [GitHub Repository](https://github.com/vharg/Eruption-Source-Parameters/tree/main).
## Contact
For further details or questions, please reach out to:
**Dr. Mahmud Muhammad**  
Email: [mahmud.geology@hotmail.com](mailto:mahmud.geology@hotmail.com)  
Website: [mahmudm.com](http://mahmudm.com)
