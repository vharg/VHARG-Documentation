import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re

class VEP_TVAAC_VAAText:
    
    """
    Class VEP_TVAAC_VAAText
    ------------------------

    This class is designed to scrape and process volcanic ash advisory (VAA) data from a specified webpage. 
    It includes methods for fetching the webpage, extracting tables, searching the data, and downloading advisory text files.

    Attributes
    ----------
    url : str
        The URL of the webpage to scrape.
    soup : BeautifulSoup or None
        Parsed HTML content of the webpage.
    dataframes : list of pd.DataFrame
        List of DataFrames containing table data from the webpage.

    Methods
    -------
    __init__(url="https://www.data.jma.go.jp/svd/vaac/data/Archives/2020_vaac_list.html")
        Initializes the scraper with the provided URL.

    set_url(url)
        Updates the URL for the scraper.

    fetch_webpage()
        Fetches and parses the webpage content.

    extract_all_tables()
        Extracts all HTML tables from the webpage and converts them into pandas DataFrames.

    search(query, date_time=None, advisory_number=None)
        Searches the extracted DataFrames for rows matching a query string, with optional filters.

    download_vaa_text(output_dir=".", filtered_results=None, csv=True)
        Downloads VAA text files from the links in the "VAA Text" column and optionally saves the data as a CSV.

    Examples
    --------
    # Initialize the scraper
    scraper = VEP_TVAAC_VAAText()

    # Fetch webpage content
    scraper.fetch_webpage()

    # Extract all tables
    tables = scraper.extract_all_tables()

    # Search for entries containing "Taal" in any column, filtered by date
    search_results = scraper.search(query="Taal", date_time="02 Feb. 2020")

    # Download VAA text files and save as a CSV
    scraper.download_vaa_text(output_dir="./vaa_texts", filtered_results=search_results, csv=True)
    """
    
    
    
    def __init__(self, url="https://www.data.jma.go.jp/svd/vaac/data/Archives/2020_vaac_list.html"):
        """
        Initializes the scraper with the provided URL.
        :param url: URL of the webpage to scrape.
        
        # Example Usage
         
        url = "https://www.data.jma.go.jp/svd/vaac/data/Archives/2020_vaac_list.html" 
        
        change url to https://www.data.jma.go.jp/svd/vaac/data/vaac_list.html to search for latest  data
        
        scraper = VEP_TVAAC_VAAText()
        
        scraper.fetch_webpage()
        
        tables = scraper.extract_all_tables()
        
        # Perform a search
        
        search_results = scraper.search("taal", date_time='02 Feb. 2020')  # Replace with your query string

        search_results = scraper.search("TAAL", date_time='2020')  # Replace with your query string
        
        scraper.download_vaa_text(output_dir="./vaa_texts", filtered_results=search_results, csv=True)
        
        search_results.head(5)
        
        
        """
        self.url = url
        self.soup = None
        self.dataframes = []

    def set_url(self, url):
        """
        Updates the URL for the scraper.
        :param url: New URL to set.
        """
        self.url = url
        
    def fetch_webpage(self):
        """
        Fetches the webpage content and initializes the BeautifulSoup object.
        Raises an exception if the request fails.
        """
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to fetch the webpage: {e}")

    def extract_all_tables(self):
        """
        Extracts all tables from the webpage and converts them to DataFrames.
        Handles special cases for columns with links.
        :return: List of DataFrames representing all tables on the webpage.
        """
        if not self.soup:
            raise ValueError("Webpage content not fetched. Please call fetch_webpage() first.")

        tables = self.soup.find_all("table")
        self.dataframes = []  # Clear any existing DataFrames

        for idx, table in enumerate(tables):
            headers = [th.get_text(strip=True) for th in table.find("tr").find_all("th")] if table.find("tr") else []
            rows = table.find_all("tr")[1:]  # Skip the header row

            table_data = []
            for row in rows:
                cells = row.find_all("td")[1:]
                row_data = {}
                for header, cell in zip(headers or range(len(cells)), cells):
                    if isinstance(header, str) and header in {"VAA Text", "VA Graphic", "VA Initial", "VA Forecast"}:
                        link = cell.find("a", href=True)
                        row_data[header] = requests.compat.urljoin(self.url, link['href']) if link else cell.get_text(strip=True)
                    else:
                        link = cell.find("a", href=True)
                        cell_value = cell.get_text(strip=True)
                        row_data[header if isinstance(header, str) else f"Column {header}"] = (
                            f"{cell_value} ({requests.compat.urljoin(self.url, link['href'])})" if link else cell_value
                        )
                table_data.append(row_data)

            df = pd.DataFrame(table_data)
            if not df.empty:
                self.dataframes.append(df)

        return self.dataframes

    def search(self, query, date_time=None, advisory_number=None):
        """
        Searches all DataFrames for a specific query string.
        :param query: The string to search for.
        :param date_time: Optional filter for the "Date Time" column.
        :param advisory_number: Optional filter for the "Advisory Number" column.
        :return: DataFrame containing matching rows across all tables.
        
        
        """
        if not self.dataframes:
            raise ValueError("No DataFrames available. Please call extract_all_tables() first.")

        
        if query is None:
            # Combine all DataFrames into one without filtering by query
            matches = pd.concat(self.dataframes, ignore_index=True)
        else:
        
            matches = pd.concat([
                df[df.apply(lambda row: row.astype(str).str.contains(query, case=False, na=False).any(), axis=1)]
                for df in self.dataframes
            ], ignore_index=True)
            
        
         # Apply additional filters if provided
        if date_time:
            matches = matches[matches['Date Time'].str.contains(date_time, case=False, na=False)]
        if advisory_number:
            matches = matches[matches['Advisory Number'].str.contains(advisory_number, case=False, na=False)]

        return matches
    
    
    



    
    def download_vaa_text(self, output_dir=".", filtered_results=None, csv=True, gdf=None, get_latest_date_data_option=True):
        """
        Downloads text files linked in the "VAA Text" column for filtered results.
        Creates the output directory if it does not exist.
        :param output_dir: Directory to save the downloaded files.
        :param filtered_results: DataFrame containing filtered rows to download.
        :param gdf: GeoDataFrame contianing coordinate bounds to only return VAA reports relevant to Area of Interest
        """
        latest_date_data = None
        
        def search_and_convert_flight_level_and_coordinates(df, column='OBS VA CLD', flight_pattern="SFC/FL\\d{3}", coord_pattern="N\\d{4} E\\d{5}"):
            """
            Search a DataFrame for a specified flight level pattern and coordinates pattern in a given column,
            convert the altitude to meters, extract latitude and longitude, and update the DataFrame.

            Parameters:
            df (pd.DataFrame): Input DataFrame containing the data to search.
            column (str): The name of the column to search for the flight level and coordinate patterns.
            flight_pattern (str): Regex pattern to identify flight levels (default is 'SFC/FL\\d{3}').
            coord_pattern (str): Regex pattern to identify coordinates (default is 'N\\d{4} E\\d{5}').

            Returns:
            pd.DataFrame: DataFrame with original rows and additional columns for altitude, latitude, and longitude.
            """
            def extract_altitude(text):
                if pd.isnull(text):  # Handle None or NaN values
                    return None
                match = re.search(flight_pattern, str(text))
                if match:
                    # Extract the flight level number and convert to meters (1 FL = 100 feet, 1 foot = 0.3048 meters)
                    flight_level = int(match.group(0).split("/FL")[-1])  # Extract flight level
                    return flight_level * 100 * 0.3048  # Convert to meters
                return None

            def extract_coordinates(text):
                if pd.isnull(text):  # Handle None or NaN values
                    return []
                matches = re.findall(coord_pattern, str(text))
                coordinates = []
                for match in matches:
                    lat, lon = match.split(" ")
                    lat = float(lat[1:]) / 100  # Convert N#### to decimal degrees
                    lon = float(lon[1:]) / 1000  # Convert E##### to decimal degrees
                    coordinates.append((lat, lon))
                return coordinates

            # Apply functions to identify matches
            df["Altitude_Meters"] = df[column].apply(extract_altitude)
            df["Coordinates"] = df[column].apply(extract_coordinates)

            # Check if any matches were found
            if df["Altitude_Meters"].isnull().all() and df["Coordinates"].apply(len).sum() == 0:
                # If no matches, drop temporary columns and return original DataFrame
                df = df.drop(columns=["Altitude_Meters", "Coordinates"])
                return df

            # Expand coordinates into separate latitude and longitude columns
            expanded_coords = df["Coordinates"].apply(lambda coords: coords[0] if coords else (None, None))
            df["Latitude"] = expanded_coords.apply(lambda x: x[0] if x else None)
            df["Longitude"] = expanded_coords.apply(lambda x: x[1] if x else None)

            # Drop intermediate 'Coordinates' column
            df = df.drop(columns=["Coordinates"])
            
            return df

        
        def parse_coordinates(coord):
            """
            Converts a coordinate string in the format 'N1400 E12100' to decimal degrees.
            """
            lat_raw, lon_raw = coord.split()
            
            # Parse latitude
            lat_dir = lat_raw[0]
            lat_deg = int(lat_raw[1:3])
            lat_min = int(lat_raw[3:])
            lat = lat_deg + (lat_min / 60.0)
            if lat_dir == 'S':
                lat = -lat
            
            # Parse longitude
            lon_dir = lon_raw[0]
            lon_deg = int(lon_raw[1:4])
            lon_min = int(lon_raw[4:])
            lon = lon_deg + (lon_min / 60.0)
            if lon_dir == 'W':
                lon = -lon
            
            return lat, lon
        
        if filtered_results is None or filtered_results.empty:
            raise ValueError("No filtered results provided or the DataFrame is empty.")

        os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist
        raw_dir=output_dir + '/raw_text_dir'
        os.makedirs(raw_dir, exist_ok=True)

        # predefined_columns = [
        #     "DTG", "VAAC", "VOLCANO", "PSN", "AREA", "SUMMIT ELEV", "ADVISORY NR", "INFO SOURCE",
        #     "AVIATION COLOUR CODE", "ERUPTION DETAILS", "OBS VA DTG", "OBS VA CLD", "FCST VA CLD +6 HR",
        #     "FCST VA CLD +12 HR", "FCST VA CLD +18 HR", "RMK", "NXT ADVISORY"
        # ]
        predefined_columns = [
            "DTG", "VAAC", "VOLCANO", "VOLCANO CODE", "PSN", "AREA", "SUMMIT ELEV", "ADVISORY NR", "INFO SOURCE",
            "AVIATION COLOUR CODE", "ERUPTION DETAILS", "OBS VA DTG", "OBS VA CLD", "FCST VA CLD +6 HR",
            "FCST VA CLD +12 HR", "FCST VA CLD +18 HR", "RMK", "NXT ADVISORY"
        ]

        data = []

        if "VAA Text" in filtered_results.columns:
            for idx, link in filtered_results["VAA Text"].items():
                if link.startswith("http"):
                    try:
                        response = requests.get(link, timeout=10)
                        response.raise_for_status()

                        # Parse HTML content to extract text
                        soup = BeautifulSoup(response.content, 'html.parser')
                        text_content = soup.get_text(separator="\n").strip()

                        # Save text content to file
                        file_name = link.split("/")[-1]
                        if not file_name.endswith(".txt"):
                            file_name += ".txt"
                        with open(f"{raw_dir}/{file_name}", "w", encoding="utf-8") as file:
                            file.write(text_content)
                        #print(f"Downloaded and saved: {file_name}")

                        # If csv=True, parse text into a structured format
                        if csv:
                            row = {}
                            for line in text_content.split("\n"):
                                if ":" in line:
                                    key, value = line.split(":", 1)
                                    key = key.strip().upper()
                                    value = value.strip()
                                    if key in predefined_columns:
                                        row[key] = value
                            
                            # Split VOLCANO into VOLCANO and VOLCANO CODE
                            if "VOLCANO" in row and row["VOLCANO"]:
                                volcano_parts = row["VOLCANO"].split()
                                row["VOLCANO"] = " ".join([p for p in volcano_parts if not p.isdigit()])
                                row["VOLCANO CODE"] = " ".join([p for p in volcano_parts if p.isdigit()])

                            data.append(row)

                    except requests.exceptions.RequestException as e:
                        print(f"Failed to download {link}: {e}")

        if csv and data:
            df = pd.DataFrame(data, columns=predefined_columns )
            
            # Apply the function to extract latitude and longitude
            df[['Latitude', 'Longitude']] = df['PSN'].apply(
                lambda x: pd.Series(parse_coordinates(x))
            )
            
            if gdf is not None and not gdf.empty:
                # Get the bounding box of the GeoDataFrame
                minx, miny, maxx, maxy = gdf.total_bounds  # min Longitude, min Latitude, max Longitude, max Latitude

                # Filter the DataFrame based on the bounding box
                df = df[
                    (df['Longitude'] >= minx) & (df['Longitude'] <= maxx) &
                    (df['Latitude'] >= miny) & (df['Latitude'] <= maxy)
                ]
                
            
            
            #################
            # Split 'ADVISORY NR' to extract the year and report number
            df[['ADVISORY_YEAR', 'REPORT_NUMBER']] = df['ADVISORY NR'].str.split('/', expand=True)

            # Convert 'REPORT_NUMBER' to integer for comparison
            df['REPORT_NUMBER'] = df['REPORT_NUMBER'].astype(int)

            # Find the latest advisory report for each volcano by year and report number
            latest_VAA_report = df.loc[df.groupby('VOLCANO')['REPORT_NUMBER'].idxmax()]

            # Drop helper columns if not needed
            latest_VAA_report = latest_VAA_report.drop(columns=['ADVISORY_YEAR', 'REPORT_NUMBER'])
            
            ########
            
            def get_latest_date_data(df, dtg_column='DTG', volcano_column='VOLCANO'):
                """
                Process the DataFrame to find and return rows corresponding to the latest advisory date.

                Parameters:
                df (pd.DataFrame): Input DataFrame containing the advisory data.
                dtg_column (str): Column name for DTG values in '%Y%m%d/%H%MZ' format.
                volcano_column (str): Column name for volcano identifiers.

                Returns:
                pd.DataFrame: Filtered DataFrame with rows matching the latest advisory date.
                """
                # Convert the 'DTG' column to a datetime object for sorting
                df['DTG_DATETIME'] = pd.to_datetime(df[dtg_column], format='%Y%m%d/%H%MZ', errors='coerce')

                # Group by 'VOLCANO' and find the row with the latest advisory by 'DTG_DATETIME'
                latest_advisories = df.loc[
                    df.groupby(volcano_column)['DTG_DATETIME'].idxmax()
                ]

                # Find the latest date in the 'DTG_DATETIME' column
                latest_date = latest_advisories['DTG_DATETIME'].max()

                # Filter the DataFrame for rows that match the latest date
                latest_date_data = latest_advisories[latest_advisories['DTG_DATETIME'] == latest_date]

                return latest_date_data
            
            if get_latest_date_data_option is True and latest_date_data is None:
                # Ensure the `get_latest_date_data` is a callable function
                if callable(get_latest_date_data):
                    # Call the function to retrieve the latest date data
                    latest_date_data = get_latest_date_data(df)
                    
                    # Ensure that the function's output is not None or empty
                    if latest_date_data is not None and not latest_date_data.empty:
                        # Process the retrieved data with the search_and_convert function
                        latest_date_data_flight = search_and_convert_flight_level_and_coordinates(latest_date_data, column="OBS VA CLD")
                        latest_date_data=latest_date_data_flight
                    else:
                        print("Warning: No data found for the latest date.")
                else:
                    raise TypeError("get_latest_date_data is not callable. Ensure it's a function.")
                
            
            csv_file = os.path.join(output_dir, "vaa_texts.csv")
            df.to_csv(csv_file, index=False)
            print(f"CSV file created: {csv_file}")
            
           
            
            return df , latest_VAA_report, latest_date_data

                            
# # Example Usage
# #url = "https://www.data.jma.go.jp/svd/vaac/data/Archives/2020_vaac_list.html"
# scraper = VEP_TVAAC_VAAText()
# scraper.fetch_webpage()
# tables = scraper.extract_all_tables()
# # Perform a search
# search_results = scraper.search("TAAL", date_time=None, advisory_number=None)  # Replace with your query string
# scraper.download_vaa_text(output_dir="./vaa_texts", filtered_results=search_results, csv=True)
# search_results.head(5)