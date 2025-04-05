## Contact Details

For questions or support, feel free to reach out to the author or create an issue on the project's repository.

**Dr. Mahmud Muhammad**  
(PhD, MSc, and BSc in Geology)  
Email: [mahmud.geology@hotmail.com](mailto:mahmud.geology@hotmail.com)  
Website: [mahmudm.com](http://mahmudm.com)


# VEP_TVAAC_VAAText

The `VEP_TVAAC_VAAText` Python module is designed to scrape and process Volcanic Ash Advisory (VAA) data from web archives. It provides functionality for downloading advisory text files, extracting tabular data, searching for relevant information, and saving results in CSV format for further analysis.

## Features

- **Webpage Scraping:** Fetch content from a specified webpage.
- **Table Extraction:** Parse and extract all tables from the webpage into pandas DataFrames.
- **Search Capability:** Search extracted data based on keywords and apply optional filters such as date and advisory number.
- **File Downloading:** Download VAA advisory text files and save structured data in CSV format.

## Installation

This module requires the following Python packages:

- `requests`
- `BeautifulSoup` (from `bs4`)
- `pandas`

Install the required dependencies using pip:

```bash
pip install requests beautifulsoup4 pandas
```

## Usage

Below is a step-by-step guide to using the module.

### 1. Initialization

Create an instance of the `VEP_TVAAC_VAAText` class by providing the URL of the webpage containing VAA data:

```python
from vep_vaa_text import VEP_TVAAC_VAAText

scraper = VEP_TVAAC_VAAText(
    url="https://www.data.jma.go.jp/svd/vaac/data/Archives/2020_vaac_list.html"
)
```

### 2. Fetch Webpage Content

Download the webpage content and prepare it for further processing:

```python
scraper.fetch_webpage()
```

### 3. Extract Tables

Extract all tables from the webpage and convert them into pandas DataFrames:

```python
tables = scraper.extract_all_tables()
print(tables)  # View the extracted tables
```

### 4. Search for Specific Entries

Search the extracted data for specific keywords, optionally filtering by date or advisory number:

```python
search_results = scraper.search(
    query="Taal",
    date_time="02 Feb. 2020",
    advisory_number=None
)
print(search_results)
```

### 5. Download Advisory Text Files

Download the advisory text files linked in the search results and save them to a specified directory. You can also save the structured data in CSV format:

```python
scraper.download_vaa_text(
    output_dir="./vaa_texts",
    filtered_results=search_results,
    csv=True
)
```

## Methods

### `__init__(url)`
Initializes the scraper with the given URL.

- **Parameters:**
  - `url` (str): The URL of the webpage to scrape.

### `set_url(url)`
Updates the URL for the scraper.

- **Parameters:**
  - `url` (str): The new URL to scrape.

### `fetch_webpage()`
Fetches and parses the content of the webpage.

- **Raises:**
  - `ConnectionError`: If the webpage cannot be fetched.

### `extract_all_tables()`
Extracts all HTML tables from the webpage and converts them to pandas DataFrames.

- **Returns:**
  - `list`: A list of pandas DataFrames representing the extracted tables.

### `search(query, date_time=None, advisory_number=None)`
Searches all extracted tables for entries matching a query string, with optional filters.

- **Parameters:**
  - `query` (str): The keyword to search for.
  - `date_time` (str, optional): Filter results by the "Date Time" column.
  - `advisory_number` (str, optional): Filter results by the "Advisory Number" column.
- **Returns:**
  - `DataFrame`: A pandas DataFrame containing the filtered results.

### `download_vaa_text(output_dir=".", filtered_results=None, csv=True)`
Downloads text files linked in the "VAA Text" column and optionally saves the data in CSV format.

- **Parameters:**
  - `output_dir` (str): Directory to save downloaded files.
  - `filtered_results` (DataFrame): Filtered rows containing links to download.
  - `csv` (bool): Whether to save structured data in CSV format.

## Example Workflow

```python
from vep_vaa_text import VEP_TVAAC_VAAText

# Initialize the scraper
scraper = VEP_TVAAC_VAAText()

# Fetch webpage content
scraper.fetch_webpage()

# Extract all tables
tables = scraper.extract_all_tables()

# Search for entries containing "Taal"
search_results = scraper.search(query="Taal", date_time="02 Feb. 2020")

# Download VAA text files and save as CSV
scraper.download_vaa_text(output_dir="./vaa_texts", filtered_results=search_results, csv=True)
```

## Notes

- Ensure you have an active internet connection to scrape webpages and download files.
- The module is designed for the Japan Meteorological Agency's VAA archives but can be adapted for other similar webpages.
- Use appropriate query strings and filters to narrow down results.

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for bugs and feature requests.

