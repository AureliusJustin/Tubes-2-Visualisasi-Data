# Indonesia Socioeconomic Dashboard 🇮🇩

An interactive Streamlit dashboard for analyzing socioeconomic indicators across Indonesian provinces, based on 2023 data including income, education, crime rates, and inequality measures.

## Features

- **Interactive Visualizations**: Bubble charts, scatter plots, correlation heatmaps, and trend analysis
- **Multi-dimensional Analysis**: Explore relationships between income, education, crime, and inequality
- **Regional Filtering**: Compare data across different regions of Indonesia
- **Time Series Analysis**: Track crime rate trends from 2012-2023
- **Responsive Design**: Mobile-friendly interface with modern styling

## Dataset Overview

The dashboard analyzes the following datasets:

1. **Gini Ratio by Province (2023)** - Income inequality measurements
2. **Average Income by Province (2023)** - Monthly income data for Feb and Aug
3. **Education Completion Rates (2021-2023)** - SD, SMP, SMA completion percentages
4. **Population Data (2023)** - Population counts by province
5. **Crime Rate Data (2012-2023)** - Risk of crime per 100,000 population

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd "Tubes-2-Visualisasi-Data"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv dashboard_env
   source dashboard_env/bin/activate  # On macOS/Linux
   # or
   dashboard_env\Scripts\activate     # On Windows
   ```

3. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify dataset structure**
   Ensure the following structure exists:
   ```
   project_root/
   ├── dashboard.py
   ├── requirements.txt
   ├── README.md
   └── dataset/
       ├── Gini Ratio Menurut Provinsi dan Daerah 2023.csv
       ├── Rata-rata Pendapatan Bersih Pekerja Bebas Menurut Provinsi dan Kelompok Umur, 2023.csv
       ├── Tingkat Penyelesaian Pendidikan Menurut Jenjang Pendidikan dan Provinsi, 2021-2023.csv
       ├── Penduduk, Laju Pertumbuhan Penduduk, Distribusi Persentase Penduduk, Kepadatan Penduduk, Rasio Jenis Kelamin Penduduk Menurut Provinsi, 2023 - Penduduk, Laju Pertumbuhan Penduduk, Distribusi Persentase Penduduk, Kepadatan Penduduk, Rasio Je.csv
       ├── Risiko Penduduk Terkena Tindak Pidana (Per 100.000 Penduduk) , 2021-2023.csv
       ├── Risiko Penduduk Terkena Tindak Pidana (Per 100.000 Penduduk) , 2018-2020.csv
       ├── Risiko Penduduk Terkena Tindak Pidana (Per 100.000 Penduduk) , 2015-2017.csv
       └── Risiko Penduduk Terkena Tindak Pidana (Per 100.000 Penduduk) , 2012-2014.csv
   ```

## Running the Dashboard

1. **Start the Streamlit application**
   ```bash
   streamlit run dashboard.py
   ```

2. **Access the dashboard**
   - The dashboard will automatically open in your default web browser
   - Default URL: `http://localhost:8501`
   - If it doesn't open automatically, copy and paste the URL from the terminal

## Dashboard Navigation

### Main Features

1. **Dashboard Controls (Sidebar)**
   - Region filter to focus on specific areas of Indonesia
   - Interactive controls for customizing visualizations

2. **Key Metrics (Top Bar)**
   - Total Population
   - Average Crime Rate
   - Average Gini Ratio (Income Inequality)
   - Average Higher Education Percentage

3. **Analysis Tabs**

   **📊 Main Analysis**
   - Interactive bubble charts with customizable axes
   - Relationship analysis between education, income, and crime
   - Regional color coding for geographic insights

   **🔗 Correlations**
   - Correlation heatmap showing relationships between all variables
   - Correlation coefficient table with color coding

   **📈 Trends**
   - Time series analysis of crime rates (2012-2023)
   - Provincial trend comparisons (2021-2023)

   **🗺️ Regional View**
   - Regional comparison statistics
   - Bar charts of regional averages
   - Detailed data table with all variables

### How to Use

1. **Explore Relationships**: Use the bubble chart to explore three-dimensional relationships between variables
2. **Filter by Region**: Use the sidebar to focus on specific regions (Sumatra, Jawa, Kalimantan, etc.)
3. **Analyze Correlations**: Check the correlation tab to understand statistical relationships
4. **Track Trends**: Use the trends tab to see how crime rates have changed over time
5. **Compare Regions**: Use the regional view to compare different areas of Indonesia

## Data Insights

The dashboard reveals several key insights:

- **Education-Crime Relationship**: Generally, provinces with higher education levels tend to have different crime patterns
- **Income Inequality**: Gini ratio varies significantly across provinces and regions
- **Regional Patterns**: Different regions show distinct socioeconomic characteristics
- **Temporal Trends**: Crime rates show various trends over the 2012-2023 period

## Troubleshooting

### Common Issues

1. **Module Import Errors**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **File Not Found Errors**
   - Verify all CSV files are in the `dataset/` folder
   - Check file names match exactly (including spaces and special characters)

3. **Port Already in Use**
   ```bash
   streamlit run dashboard.py --server.port 8502
   ```

4. **Performance Issues**
   - The dashboard uses caching for better performance
   - Restart the application if data seems outdated

### Data Requirements

- CSV files must be properly formatted with consistent column names
- Missing data is handled gracefully, but may affect some visualizations
- Province names must be consistent across datasets

## Technical Details

- **Framework**: Streamlit
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Data Processing**: Pandas, NumPy
- **Styling**: Custom CSS for enhanced appearance
- **Caching**: Streamlit caching for improved performance

## Contributing

To extend the dashboard:

1. Add new datasets to the `dataset/` folder
2. Update the `load_and_process_data()` function in `dashboard.py`
3. Create new visualization functions following the existing patterns
4. Add new tabs or sections as needed

## License

This project is for educational purposes. Please ensure you have proper rights to use the datasets.

---

For questions or issues, please refer to the original Jupyter notebook analysis or contact the development team.
