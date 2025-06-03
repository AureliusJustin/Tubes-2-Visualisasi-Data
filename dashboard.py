import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
import warnings
import json
import folium
from folium import plugins
from folium import Element
import branca.colormap as cm
from streamlit_folium import st_folium
import uuid
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="Dashboard Kriminalitas Indonesia",
    page_icon="🇮🇩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stApp {
        background-color: #31393e;
    }
    .main > div {
        padding-top: 2rem;
        background-color: #31393e;
    }
    .stMetric {
        background-color: #25262d;
        padding: 1rem;
        border-radius: 0.5rem;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* Ensure metric containers have consistent height */
    div[data-testid="metric-container"] {
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: stretch;
    }
    
    /* Chart containers - single container approach */
    div[data-testid="stPlotlyChart"] {
        background-color: #25262d;
        border-radius: 0.75rem;
        margin: 1rem 0;
        padding: 0.75rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        overflow: hidden;
    }
    
    /* Remove extra styling from plotly elements to prevent double containers */
    .js-plotly-plot, .plotly {
        background-color: transparent !important;
        border-radius: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
        height: 100% !important;
    }
    
    /* Folium map containers - enhanced styling */
    .stFolium {
        background-color: #25262d !important;
        border-radius: 0.75rem !important;
        overflow: hidden !important;
        margin: 1rem 0 !important;
        padding: 0 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        border: none !important;
    }
    
    /* Map iframe styling with perfect rounded corners */
    .stFolium iframe {
        border-radius: 0.75rem !important;
        border: none !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
        height: 100% !important;
        background-color: #25262d !important;
        outline: none !important;
    }
    
    /* Enhanced leaflet container styling */
    .leaflet-container {
        background-color: #25262d !important;
        border-radius: 0.75rem !important;
        margin: 0 !important;
        padding: 0 !important;
        outline: none !important;
        border: none !important;
    }
    
    /* Force all leaflet panes to have dark background and prevent black squares */
    .leaflet-pane, 
    .leaflet-tile-pane, 
    .leaflet-map-pane,
    .leaflet-overlay-pane,
    .leaflet-shadow-pane,
    .leaflet-marker-pane,
    .leaflet-tooltip-pane,
    .leaflet-popup-pane {
        background-color: #25262d !important;
    }
    
    /* Hide any tile layers that might show black background */
    .leaflet-tile-pane {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Style leaflet controls to match dark theme */
    .leaflet-control-attribution {
        background-color: rgba(37, 38, 45, 0.9) !important;
        color: white !important;
        border-radius: 4px !important;
        font-size: 10px !important;
        border: none !important;
    }
    
    .leaflet-control-attribution a {
        color: #ccc !important;
    }
    
    .leaflet-control-zoom {
        border: none !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
    }
    
    .leaflet-control-zoom a {
        background-color: #25262d !important;
        color: white !important;
        border: 1px solid #444 !important;
        text-decoration: none !important;
    }
    
    .leaflet-control-zoom a:hover {
        background-color: #3a3b42 !important;
        color: white !important;
    }
    
    /* Force any div containing folium maps to use dark theme */
    div[data-testid="stFolium"] {
        background-color: #25262d !important;
        border-radius: 0.75rem !important;
        overflow: hidden !important;
        border: none !important;
    }
    
    /* Additional protection against black backgrounds */
    .leaflet-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #25262d;
        z-index: -1;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_process_data():
    """Load and preprocess all datasets"""
    
    # Load datasets from local CSV files
    try:
        df_gini_ratio = pd.read_csv("dataset/Gini Ratio Menurut Provinsi dan Daerah 2023.csv")
        df_pendapatan_bersih = pd.read_csv("dataset/Rata-rata Pendapatan Bersih Pekerja Bebas Menurut Provinsi dan Kelompok Umur, 2023.csv")
        df_penyelesaian_pendidikan = pd.read_csv("dataset/Tingkat Penyelesaian Pendidikan Menurut Jenjang Pendidikan dan Provinsi, 2021-2023.csv")
        df_jumlah_penduduk = pd.read_csv("dataset/Penduduk.csv")
        
        # Load crime data
        df_tindak_pidana_2021_2023 = pd.read_csv("dataset/Risiko Penduduk Terkena Tindak Pidana (Per 100.000 Penduduk) , 2021-2023.csv")
        df_tindak_pidana_2018_2020 = pd.read_csv("dataset/Risiko Penduduk Terkena Tindak Pidana (Per 100.000 Penduduk) , 2018-2020.csv")
        df_tindak_pidana_2015_2017 = pd.read_csv("dataset/Risiko Penduduk Terkena Tindak Pidana (Per 100.000 Penduduk) , 2015-2017.csv")
        df_tindak_pidana_2012_2014 = pd.read_csv("dataset/Risiko Penduduk Terkena Tindak Pidana (Per 100.000 Penduduk) , 2012-2014.csv")
        
        # Load OC Index data for global crime rankings
        df_oc_index_2023 = pd.read_csv("dataset/oc_index_2023.csv", sep=';')
        df_oc_index_2021 = pd.read_csv("dataset/oc_index_2021.csv", sep=';')
        
    except FileNotFoundError as e:
        st.error(f"File not found: {e}")
        st.stop()
    
    # Standardization function
    def standardize_number(value):
        value = str(value)
        if ',' in value and '.' in value:
            if value.index(',') < value.index('.'):
                value = value.replace(',', '')
            else:
                value = value.replace('.', '').replace(',', '.')
        elif ',' in value:
            value = value.replace(',', '.')
        
        try:
            return float(value)
        except ValueError:
            return None
    
    # Preprocess crime data - handle different column names
    # Standardize all crime data to use 'Provinsi' column
    crime_datasets = [
        df_tindak_pidana_2012_2014,
        df_tindak_pidana_2015_2017,
        df_tindak_pidana_2018_2020,
        df_tindak_pidana_2021_2023
    ]
    
    for df in crime_datasets:
        if 'Kepolisian Daerah' in df.columns:
            df.rename(columns={'Kepolisian Daerah': 'Provinsi'}, inplace=True)
        elif df.columns[0] != 'Provinsi' and 'Provinsi' not in df.columns:
            # Use first column as Provinsi if it's not already named correctly
            df.rename(columns={df.columns[0]: 'Provinsi'}, inplace=True)
    
    # Clean province names in all crime datasets
    for df in crime_datasets:
        if 'Provinsi' in df.columns:
            df['Provinsi'] = df['Provinsi'].str.replace("METRO JAYA", "DKI JAKARTA", regex=False)
            df['Provinsi'] = df['Provinsi'].str.replace("KEP.", "KEPULAUAN", regex=False)
    
    # Merge crime data
    df_tindak_pidana_time_series = df_tindak_pidana_2012_2014.merge(df_tindak_pidana_2015_2017, on='Provinsi', how='outer')
    df_tindak_pidana_time_series = df_tindak_pidana_time_series.merge(df_tindak_pidana_2018_2020, on='Provinsi', how='outer')
    df_tindak_pidana_time_series = df_tindak_pidana_time_series.merge(df_tindak_pidana_2021_2023, on='Provinsi', how='outer')
    
    # Preprocess education data
    provinces_to_drop = ['PAPUA BARAT DAYA', 'PAPUA SELATAN', 'PAPUA TENGAH', 'PAPUA PEGUNUNGAN']
    df_penyelesaian_pendidikan = df_penyelesaian_pendidikan[~df_penyelesaian_pendidikan['Provinsi'].isin(provinces_to_drop)]
    df_penyelesaian_pendidikan = df_penyelesaian_pendidikan.replace(re.escape("KEP."), "KEPULAUAN", regex=True)
    
    # Preprocess income data
    if 'Unnamed: 1' in df_pendapatan_bersih.columns:
        df_pendapatan_bersih = df_pendapatan_bersih.drop(columns='Unnamed: 1')
    df_pendapatan_bersih['Provinsi'] = df_pendapatan_bersih['Provinsi'].str.upper().str.strip()
    
    # Preprocess Gini ratio data
    df_gini_ratio = df_gini_ratio.replace(re.escape("KEP."), "KEPULAUAN", regex=True)
    df_gini_ratio = df_gini_ratio.rename(columns={'2023': 'gini_ratio_2023'})
    
    # Preprocess population data
    df_jumlah_penduduk["Provinsi"] = df_jumlah_penduduk["Provinsi"].str.upper().str.strip()
    
    # Merge all 2023 data
    df_2023 = df_pendapatan_bersih.merge(df_penyelesaian_pendidikan, on='Provinsi', how='outer')
    df_2023 = df_2023.merge(df_tindak_pidana_2021_2023, on='Provinsi', how='outer')
    df_2023 = df_2023.merge(df_gini_ratio, on='Provinsi', how='outer')
    df_2023 = df_2023.merge(df_jumlah_penduduk, on='Provinsi', how='outer')
    
    df_2023 = df_2023.dropna(subset=['Provinsi'])
    
    # Clean and convert data types
    if 'Rata-rata Feb 2023' in df_2023.columns:
        df_2023['Rata-rata Feb 2023'] = df_2023['Rata-rata Feb 2023'].astype(str).str.replace(' ', '', regex=False)
        df_2023['Rata-rata Feb 2023'] = pd.to_numeric(df_2023['Rata-rata Feb 2023'], errors='coerce')
    
    df_2023 = df_2023.apply(pd.to_numeric, errors="ignore")
    
    # Rename columns for clarity
    rename_dict = {
        "2021": "Tindak Pidana 2021", 
        "2022": "Tindak Pidana 2022", 
        "2023": "Tindak Pidana 2023"
    }
    
    if 'Rata-rata Feb 2023' in df_2023.columns:
        rename_dict["Rata-rata Feb 2023"] = "Pendapatan Februari"
    if 'Rata-rata Aug 2023' in df_2023.columns:
        rename_dict["Rata-rata Aug 2023"] = "Pendapatan Agustus"
    if 'Jumlah Penduduk (Ribu)' in df_2023.columns:
        rename_dict["Jumlah Penduduk (Ribu)"] = "Jumlah Penduduk"
    
    df_2023 = df_2023.rename(columns=rename_dict)
    
    # Select and organize final columns
    final_columns = ["Provinsi"]
    
    # Add available columns
    possible_columns = [
        "Pendapatan Februari", "Pendapatan Agustus", "SD_2023", "SMP_2023", "SMA_2023",
        "Tindak Pidana 2021", "Tindak Pidana 2022", "Tindak Pidana 2023", 
        "gini_ratio_2023", "Jumlah Penduduk"
    ]
    
    for col in possible_columns:
        if col in df_2023.columns:
            final_columns.append(col)
    
    df_asli = df_2023[final_columns].copy()
    
    # Create education categories if education data exists
    if all(col in df_asli.columns for col in ["SD_2023", "SMP_2023", "SMA_2023"]):
        df_asli["Tidak Tamat SD"] = 100 - df_asli["SD_2023"]
        df_asli["Pendidikan Terakhir SD"] = df_asli["SD_2023"] - df_asli["SMP_2023"]
        df_asli["Pendidikan Terakhir SMP"] = df_asli["SMP_2023"] - df_asli["SMA_2023"]
        df_asli["Pendidikan Terakhir SMA/PT"] = df_asli["SMA_2023"]
    
    # Add region information
    region_map = {
        "ACEH": "Sumatra",
        "SUMATERA UTARA": "Sumatra",
        "SUMATERA BARAT": "Sumatra",
        "RIAU": "Sumatra",
        "KEPULAUAN RIAU": "Sumatra",
        "JAMBI": "Sumatra",
        "SUMATERA SELATAN": "Sumatra",
        "BENGKULU": "Sumatra",
        "LAMPUNG": "Sumatra",
        "KEPULAUAN BANGKA BELITUNG": "Sumatra",
        "DKI JAKARTA": "Jawa",
        "JAWA BARAT": "Jawa",
        "JAWA TENGAH": "Jawa",
        "DI YOGYAKARTA": "Jawa",
        "JAWA TIMUR": "Jawa",
        "BANTEN": "Jawa",
        "KALIMANTAN BARAT": "Kalimantan",
        "KALIMANTAN TENGAH": "Kalimantan",
        "KALIMANTAN SELATAN": "Kalimantan",
        "KALIMANTAN TIMUR": "Kalimantan",
        "KALIMANTAN UTARA": "Kalimantan",
        "SULAWESI UTARA": "Sulawesi",
        "SULAWESI TENGAH": "Sulawesi",
        "SULAWESI SELATAN": "Sulawesi",
        "SULAWESI TENGGARA": "Sulawesi",
        "GORONTALO": "Sulawesi",
        "SULAWESI BARAT": "Sulawesi",
        "BALI": "Bali & Nusa Tenggara",
        "NUSA TENGGARA BARAT": "Bali & Nusa Tenggara",
        "NUSA TENGGARA TIMUR": "Bali & Nusa Tenggara",
        "MALUKU": "Maluku",
        "MALUKU UTARA": "Maluku",
        "PAPUA": "Papua",
        "PAPUA BARAT": "Papua",
    }
    
    df_asli["Region"] = df_asli["Provinsi"].map(region_map)
    
    return df_asli, df_tindak_pidana_time_series

# Load data function
# @st.cache_data
# def load_data():
#     df = pd.read_csv('data.csv')
#     return df

# Load geojson data function
@st.cache_data
def load_geojson():
    """Load Indonesia provinces geojson data and filter to only Indonesian provinces (robust version)"""
    with open('map/indonesia-prov.geojson', 'r') as f:
        geojson_data = json.load(f)
    # List of valid Indonesian provinces (matching your mapping)
    indonesian_provinces = set([
        'ACEH', 'SUMATERA UTARA', 'SUMATERA BARAT', 'RIAU', 'KEPULAUAN RIAU',
        'JAMBI', 'SUMATERA SELATAN', 'BENGKULU', 'LAMPUNG', 'KEPULAUAN BANGKA BELITUNG',
        'DKI JAKARTA', 'JAWA BARAT', 'JAWA TENGAH', 'DI YOGYAKARTA', 'JAWA TIMUR', 'BANTEN',
        'BALI', 'NUSA TENGGARA BARAT', 'NUSA TENGGARA TIMUR',
        'KALIMANTAN BARAT', 'KALIMANTAN TENGAH', 'KALIMANTAN SELATAN', 'KALIMANTAN TIMUR', 'KALIMANTAN UTARA',
        'SULAWESI UTARA', 'SULAWESI TENGAH', 'SULAWESI SELATAN', 'SULAWESI TENGGARA', 'GORONTALO', 'SULAWESI BARAT',
        'MALUKU', 'MALUKU UTARA', 'PAPUA', 'PAPUA BARAT'
    ])
    filtered_features = []
    for feature in geojson_data['features']:
        props = feature.get('properties', {})
        prov_name = props.get('Propinsi') or props.get('NAME_1') or props.get('name')
        if prov_name in indonesian_provinces:
            filtered_features.append(feature)
    geojson_data['features'] = filtered_features
    return geojson_data

# Province name mapping function
def create_province_mapping():
    """Create mapping between geojson province names and CSV province names"""
    geojson_to_csv = {
        # Most provinces match exactly, but these need mapping
        'KEPULAUAN BANGKA BELITUNG': 'KEP. BANGKA BELITUNG',
        'KEPULAUAN RIAU': 'KEP. RIAU',
        # All other provinces should match exactly
        'DKI JAKARTA': 'DKI JAKARTA',
        'JAWA BARAT': 'JAWA BARAT',
        'JAWA TENGAH': 'JAWA TENGAH',
        'DI YOGYAKARTA': 'DI YOGYAKARTA',
        'JAWA TIMUR': 'JAWA TIMUR',
        'BANTEN': 'BANTEN',
        'BALI': 'BALI',
        'NUSA TENGGARA BARAT': 'NUSA TENGGARA BARAT',
        'NUSA TENGGARA TIMUR': 'NUSA TENGGARA TIMUR',
        'KALIMANTAN BARAT': 'KALIMANTAN BARAT',
        'KALIMANTAN TENGAH': 'KALIMANTAN TENGAH',
        'KALIMANTAN SELATAN': 'KALIMANTAN SELATAN',
        'KALIMANTAN TIMUR': 'KALIMANTAN TIMUR',
        'KALIMANTAN UTARA': 'KALIMANTAN UTARA',
        'SULAWESI UTARA': 'SULAWESI UTARA',
        'SULAWESI TENGAH': 'SULAWESI TENGAH',
        'SULAWESI SELATAN': 'SULAWESI SELATAN',
        'SULAWESI TENGGARA': 'SULAWESI TENGGARA',
        'GORONTALO': 'GORONTALO',
        'SULAWESI BARAT': 'SULAWESI BARAT',
        'MALUKU': 'MALUKU',
        'MALUKU UTARA': 'MALUKU UTARA',
        'PAPUA': 'PAPUA',
        'PAPUA BARAT': 'PAPUA BARAT',
        'SUMATERA UTARA': 'SUMATERA UTARA',
        'SUMATERA BARAT': 'SUMATERA BARAT',
        'RIAU': 'RIAU',
        'JAMBI': 'JAMBI',
        'SUMATERA SELATAN': 'SUMATERA SELATAN',
        'BENGKULU': 'BENGKULU',
        'LAMPUNG': 'LAMPUNG',
        'ACEH': 'ACEH'
    }
    return geojson_to_csv

# Create a function to merge geojson data with CSV data
@st.cache_data
def merge_geojson_csv(geojson_data, csv_data):
    """Merge geojson data with CSV data on province name"""
    geojson_df = pd.json_normalize(geojson_data['features'])
    geojson_df = geojson_df.rename(columns={"properties.Propinsi": "Provinsi"})
    
    # Create province name mapping
    province_mapping = create_province_mapping()
    geojson_df['Provinsi'] = geojson_df['Provinsi'].map(province_mapping)
    
    # Merge with CSV data
    merged_df = geojson_df.merge(csv_data, on='Provinsi', how='left')
    
    return merged_df

def create_bubble_chart(df, x_col, y_col, size_col, color_col=None, title="Bubble Chart", region_filter=None, province_filter=None):
    """Create an interactive bubble chart using Plotly with dynamic coloring based on region/province filter"""
    # If province_filter is set to a specific province, color by province (legend shows province)
    if province_filter and province_filter != 'Semua' and 'Provinsi' in df.columns:
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            size=size_col,
            color='Provinsi',
            hover_name="Provinsi",
            hover_data={"Region": True},
            title=title,
            size_max=60
        )
    # If region_filter is set to a specific region, color by province
    elif region_filter and region_filter != 'Semua' and 'Provinsi' in df.columns:
        fig = px.scatter(
            df, 
            x=x_col, 
            y=y_col, 
            size=size_col,
            color='Provinsi',
            hover_name="Provinsi",
            hover_data={"Region": True},
            title=title,
            size_max=60
        )
    else:
        # Color by region (default behavior)
        fig = px.scatter(
            df, 
            x=x_col, 
            y=y_col, 
            size=size_col,
            color="Region",
            hover_name="Provinsi",
            title=title,
            size_max=60
        )
    fig.update_layout(
        height=600,
        showlegend=True,
        hovermode='closest',
        plot_bgcolor='#25262d',
        paper_bgcolor='#25262d',
        font_color='white',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_correlation_heatmap(df):
    """Create correlation heatmap for numeric columns"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    numeric_cols = [col for col in numeric_cols if col != 'Provinsi']
    
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            title="Matriks Korelasi Indikator Sosial Ekonomi",
            color_continuous_scale="RdBu"
        )
        
        fig.update_layout(
            height=600,
            plot_bgcolor='#25262d',
            paper_bgcolor='#25262d',
            font_color='white',
            margin=dict(l=20, r=20, t=40, b=20)
        )
        return fig
    return None

def create_trend_chart(df_time_series):
    """Create trend chart for crime data over time"""
    if df_time_series is not None and not df_time_series.empty:
        # Get Indonesia data
        indonesia_data = df_time_series[df_time_series['Provinsi'] == 'INDONESIA']
        
        if not indonesia_data.empty:
            years = [str(year) for year in range(2012, 2024)]
            available_years = [year for year in years if year in indonesia_data.columns]
            
            if available_years:
                trend_data = []
                for year in available_years:
                    value = indonesia_data[year].iloc[0]
                    if pd.notna(value):
                        trend_data.append({'Year': int(year), 'Crime_Rate': float(value)})
                
                if trend_data:
                    trend_df = pd.DataFrame(trend_data)
                    
                    fig = px.line(
                        trend_df, 
                        x='Year', 
                        y='Crime_Rate',
                        title="Tren Tingkat Kriminalitas Indonesia (2012-2023)",
                        markers=True
                    )
                    
                    fig.update_layout(
                        height=400,
                        xaxis_title="Tahun",
                        yaxis_title="Tingkat Kriminalitas (per 100.000 penduduk)",
                        plot_bgcolor='#25262d',
                        paper_bgcolor='#25262d',
                        font_color='white',
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    
                    return fig
    
    return None

def create_regional_comparison(df):
    """Create regional comparison charts"""
    if 'Region' in df.columns:
        # Group by region and calculate means
        regional_stats = df.groupby('Region').agg({
            col: 'mean' for col in df.select_dtypes(include=[np.number]).columns
            if col not in ['Provinsi']
        }).round(2)
        
        return regional_stats
    return None

def create_choropleth_map(df, metric, geojson_data, province_mapping, region_filter=None, province_filter=None):
    """Create a choropleth map using folium, with dynamic zoom to provinces/regions when filtered"""
    # Prepare data based on selected metric
    if metric == 'Crime Rate 2023':
        map_data = df[['Provinsi', 'Tindak Pidana 2023', 'Region']].dropna(subset=['Provinsi'])
        metric_col = 'Tindak Pidana 2023'
        title = 'Tindak Pidana per 100,000 Penduduk (2023)'
    elif metric == 'Population':
        map_data = df[['Provinsi', 'Jumlah Penduduk', 'Region']].dropna(subset=['Provinsi'])
        metric_col = 'Jumlah Penduduk'
        title = 'Populasi berdasarkan Provinsi (ribu jiwa, 2023)'
    elif metric == 'Gini Ratio':
        map_data = df[['Provinsi', 'gini_ratio_2023', 'Region']].dropna(subset=['Provinsi'])
        metric_col = 'gini_ratio_2023'
        title = 'Gini Ratio berdasarkan Provinsi (2023)'
    elif metric == 'Income':
        map_data = df[['Provinsi', 'Pendapatan Agustus', 'Region']].dropna(subset=['Provinsi'])
        metric_col = 'Pendapatan Agustus'
        title = 'Average Income by Province (August 2023)'
    elif metric == 'Education':
        map_data = df[['Provinsi', 'Pendidikan Terakhir SMA/PT', 'Region']].dropna(subset=['Provinsi'])
        metric_col = 'Pendidikan Terakhir SMA/PT'
        title = 'Tingkat Penyelesaian Pendidikan SMA berdasarkan Provinsi (2023)'
    else:
        map_data = df[['Provinsi', 'Tindak Pidana 2023', 'Region']].dropna(subset=['Provinsi'])
        metric_col = 'Tindak Pidana 2023'
        title = 'Tindak Pidana per 100,000 Penduduk (2023)'

    reverse_mapping = {v: k for k, v in province_mapping.items()}

    # Calculate map bounds and zoom based on filter
    def get_bounds_for_features(features):
        """Calculate bounds for a list of GeoJSON features"""
        if not features:
            return None
        
        all_coords = []
        for feature in features:
            geom = feature['geometry']
            if geom['type'] == 'Polygon':
                coords = geom['coordinates'][0]
                all_coords.extend(coords)
            elif geom['type'] == 'MultiPolygon':
                for polygon in geom['coordinates']:
                    coords = polygon[0]
                    all_coords.extend(coords)
        
        if not all_coords:
            return None
            
        lngs = [coord[0] for coord in all_coords]
        lats = [coord[1] for coord in all_coords]
        
        return {
            'min_lat': min(lats),
            'max_lat': max(lats),
            'min_lng': min(lngs),
            'max_lng': max(lngs)
        }

    # Determine map center, zoom, and bounds based on filters
    indonesia_sw = [-11.0, 94.0]
    indonesia_ne = [6.0, 141.0]
    map_center = [-2.5, 118.0]
    zoom_level = 4
    map_bounds = [[indonesia_sw[0], indonesia_sw[1]], [indonesia_ne[0], indonesia_ne[1]]]
    
    if province_filter and province_filter != 'Semua':
        # Find the specific province in geojson
        province_geojson_name = reverse_mapping.get(province_filter)
        if province_geojson_name:
            province_features = [f for f in geojson_data['features'] 
                               if f['properties']['Propinsi'] == province_geojson_name]
            if province_features:
                bounds = get_bounds_for_features(province_features)
                if bounds:
                    map_center = [(bounds['min_lat'] + bounds['max_lat']) / 2, 
                                 (bounds['min_lng'] + bounds['max_lng']) / 2]
                    zoom_level = 7
                    # Add padding to bounds
                    padding = 0.5
                    map_bounds = [[bounds['min_lat'] - padding, bounds['min_lng'] - padding],
                                 [bounds['max_lat'] + padding, bounds['max_lng'] + padding]]
    
    elif region_filter and region_filter != 'Semua':
        # Find all provinces in the region
        region_provinces = map_data[map_data['Region'] == region_filter]['Provinsi'].unique()
        region_geojson_names = [reverse_mapping.get(prov) for prov in region_provinces if reverse_mapping.get(prov)]
        
        if region_geojson_names:
            region_features = [f for f in geojson_data['features'] 
                             if f['properties']['Propinsi'] in region_geojson_names]
            if region_features:
                bounds = get_bounds_for_features(region_features)
                if bounds:
                    map_center = [(bounds['min_lat'] + bounds['max_lat']) / 2, 
                                 (bounds['min_lng'] + bounds['max_lng']) / 2]
                    zoom_level = 6
                    # Add padding to bounds
                    padding = 1.0
                    map_bounds = [[bounds['min_lat'] - padding, bounds['min_lng'] - padding],
                                 [bounds['max_lat'] + padding, bounds['max_lng'] + padding]]

    # Create map with dynamic center and zoom
    m = folium.Map(
        location=map_center,
        zoom_start=zoom_level,
        tiles=None,
        min_zoom=4,
        max_zoom=10,
        zoom_control=False,
        scrollWheelZoom=True,
        doubleClickZoom=True,
        prefer_canvas=True,
        attributionControl=True
    )
    
    # Add custom CSS to force dark background and fix styling issues
    custom_css = """
    <style>
    /* Force all map containers to have dark background */
    .folium-map, .leaflet-container {
        background-color: #25262d !important;
        border-radius: 0.75rem !important;
        overflow: hidden !important;
    }
    
    /* Hide all tile layers and ensure dark background */
    .leaflet-tile-pane {
        display: none !important;
    }
    
    /* Style all panes with dark background */
    .leaflet-pane, 
    .leaflet-map-pane,
    .leaflet-overlay-pane,
    .leaflet-shadow-pane,
    .leaflet-marker-pane,
    .leaflet-tooltip-pane,
    .leaflet-popup-pane {
        background-color: #25262d !important;
    }
    
    /* Style zoom controls */
    .leaflet-control-zoom {
        border: none !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
    }
    
    .leaflet-control-zoom a {
        background-color: #25262d !important;
        color: white !important;
        border: 1px solid #444 !important;
        text-decoration: none !important;
    }
    
    .leaflet-control-zoom a:hover {
        background-color: #3a3b42 !important;
        color: white !important;
    }
    
    /* Style attribution */
    .leaflet-control-attribution {
        background-color: rgba(37, 38, 45, 0.9) !important;
        color: white !important;
        border-radius: 4px !important;
        font-size: 10px !important;
    }
    
    .leaflet-control-attribution a {
        color: #ccc !important;
    }
    
    /* Remove any black backgrounds */
    .leaflet-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #25262d;
        z-index: -1;
    }
    
    /* Style colormap legend with light text - Selective targeting */
    .colormap-container, .legend, 
    div.legend, div.colormap-container {
        background-color: rgba(37, 38, 45, 0.95) !important;
        border-radius: 8px !important;
        padding: 8px !important;
        border: none !important;
        color: #ffffff !important;
        font-family: 'Arial', sans-serif !important;
    }
    
    /* Don't style .colormap directly - preserve gradients */
    
    /* Super specific legend text targeting - exclude colormap */
    .leaflet-control-container .legend,
    .leaflet-control-container .colormap-container,
    .leaflet-control .legend,
    .leaflet-control .colormap-container {
        background-color: rgba(37, 38, 45, 0.95) !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    /* Target only text elements in legends, NOT the colormap gradient */
    .legend *, .colormap-container *,
    .leaflet-control .legend *, .leaflet-control .colormap-container *,
    .legend div, .colormap-container div,
    .legend span, .colormap-container span,
    .legend p, .colormap-container p,
    .legend text, .colormap-container text {
        color: #ffffff !important;
    }
    
    /* Target SVG text elements specifically */
    .legend text, .colormap-container text {
        fill: #ffffff !important;
    }
    
    /* Preserve colormap gradient - DO NOT override colors for these */
    .colormap .leaflet-control-colorpicker,
    .colormap .leaflet-control-colorpicker *,
    .colormap img,
    .colormap canvas,
    .colormap svg rect,
    .colormap svg path,
    .colormap .leaflet-control-colorpicker-gradient {
        color: inherit !important;
        fill: inherit !important;
        background: inherit !important;
    }
    
    /* Specific element targeting - only text elements */
    .colormap-container .caption, .legend .caption,
    .legend-title, .colormap-container-title {
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 12px !important;
        margin-bottom: 4px !important;
    }
    
    .colormap-container .colorbar, .legend .colorbar {
        border: none !important;
        border-radius: 4px !important;
    }
    
    .colormap-container .tick, .legend .tick,
    .legend-scale, .colormap-container-scale {
        color: #ffffff !important;
        font-size: 10px !important;
        font-weight: normal !important;
    }
    
    /* Nuclear option - but EXCLUDE colormap gradients */
    [class*="legend"] *:not(img):not(canvas):not([class*="gradient"]):not([class*="colorpicker"]) {
        color: #ffffff !important;
    }
    
    [class*="legend"] text, .legend text, .colormap-container text {
        fill: #ffffff !important;
    }
    </style>
    """
    m.get_root().html.add_child(folium.Element(custom_css))

    # Add JavaScript to properly configure the map with dynamic bounds
    map_config_js = f'''
        <script>
        // Wait for map to be ready
        document.addEventListener('DOMContentLoaded', function() {{
            setTimeout(function() {{
                var mapContainer = document.querySelector('.folium-map');
                if (mapContainer && window[mapContainer.id]) {{
                    var map = window[mapContainer.id];
                    
                    // Set bounds based on filter
                    var bounds = [[{map_bounds[0][0]}, {map_bounds[0][1]}], [{map_bounds[1][0]}, {map_bounds[1][1]}]];
                    map.setMaxBounds(bounds);
                    
                    // Set zoom level and limits based on filter
                    map.setZoom({zoom_level});
                    map.setMinZoom({max(4, zoom_level - 2)});
                    map.setMaxZoom({zoom_level + 3});
                    
                    // Enable appropriate controls based on filter
                    {"// Province/region filtered - enable some zoom controls" if (province_filter and province_filter != 'Semua') or (region_filter and region_filter != 'Semua') else "// All Indonesia - disable zoom controls"}
                    {"map.scrollWheelZoom.enable();" if (province_filter and province_filter != 'Semua') or (region_filter and region_filter != 'Semua') else "map.scrollWheelZoom.disable();"}
                    {"map.doubleClickZoom.enable();" if (province_filter and province_filter != 'Semua') or (region_filter and region_filter != 'Semua') else "map.doubleClickZoom.disable();"}
                    map.touchZoom.{"enable" if (province_filter and province_filter != 'Semua') or (region_filter and region_filter != 'Semua') else "disable"}();
                    map.boxZoom.disable();
                    map.keyboard.disable();
                    
                    // Force dark background
                    var container = map.getContainer();
                    if (container) {{
                        container.style.backgroundColor = '#25262d';
                        container.style.borderRadius = '0.75rem';
                    }}
                    
                    // Ensure map stays within bounds and cannot be dragged outside
                    map.on('drag', function() {{
                        map.panInsideBounds(bounds, {{animate: false}});
                    }});
                    
                    // Control zoom limits
                    map.on('zoom', function(e) {{
                        var currentZoom = map.getZoom();
                        if (currentZoom < {max(4, zoom_level - 2)}) {{
                            map.setZoom({max(4, zoom_level - 2)});
                        }} else if (currentZoom > {zoom_level + 3}) {{
                            map.setZoom({zoom_level + 3});
                        }}
                    }});
                    
                    // Ultra-aggressive legend styling for white text
                    function applyLegendStyling() {{
                        // Style all legend containers
                        var legendContainers = document.querySelectorAll('.legend, .colormap, .colormap-container');
                        legendContainers.forEach(function(container) {{
                            container.style.backgroundColor = 'rgba(37, 38, 45, 0.95)';
                            container.style.color = '#ffffff';
                            container.style.border = 'none';
                            container.style.borderRadius = '8px';
                            container.style.padding = '8px';
                        }});
                        
                        // Force white color on text elements only, preserve colormap gradients
                        var textSelectors = [
                            '.legend', 
                            '.colormap-container',
                            '[class*="legend"]:not([class*="gradient"]):not([class*="colorpicker"])'
                        ];
                        
                        textSelectors.forEach(function(selector) {{
                            try {{
                                var containers = document.querySelectorAll(selector);
                                containers.forEach(function(container) {{
                                    // Only target text nodes and text elements, not gradient elements
                                    var textElements = container.querySelectorAll('div, span, p, text, *:not(img):not(canvas):not([class*="gradient"]):not([class*="colorpicker"])');
                                    textElements.forEach(function(element) {{
                                        // Skip elements that are likely colormap gradients
                                        if (!element.classList.contains('leaflet-control-colorpicker') && 
                                            !element.classList.contains('gradient') &&
                                            element.tagName !== 'IMG' &&
                                            element.tagName !== 'CANVAS') {{
                                            
                                            // Set text color
                                            element.style.color = '#ffffff';
                                            element.style.setProperty('color', '#ffffff', 'important');
                                            
                                            // Set SVG fill for text elements only
                                            if (element.tagName === 'text' || element.tagName === 'TEXT') {{
                                                element.style.fill = '#ffffff';
                                                element.style.setProperty('fill', '#ffffff', 'important');
                                                element.setAttribute('fill', '#ffffff');
                                            }}
                                        }}
                                    }});
                                }});
                            }} catch(e) {{
                                // Ignore selector errors
                            }}
                        }});
                        
                        // Specifically handle caption and tick elements
                        var specificElements = document.querySelectorAll('.caption, .legend-title, .tick, .legend-scale');
                        specificElements.forEach(function(element) {{
                            element.style.color = '#ffffff';
                            element.style.setProperty('color', '#ffffff', 'important');
                        }});
                    }}
                    
                    // Apply styling multiple times with increasing delays
                    setTimeout(applyLegendStyling, 100);
                    setTimeout(applyLegendStyling, 500);
                    setTimeout(applyLegendStyling, 1000);
                    setTimeout(applyLegendStyling, 2000);
                    
                    // Set up a mutation observer to catch any dynamically added legend elements
                    if (typeof MutationObserver !== 'undefined') {{
                        var observer = new MutationObserver(function(mutations) {{
                            var shouldRestyle = false;
                            mutations.forEach(function(mutation) {{
                                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {{
                                    for (var i = 0; i < mutation.addedNodes.length; i++) {{
                                        var node = mutation.addedNodes[i];
                                        if (node.nodeType === Node.ELEMENT_NODE && 
                                            (node.classList.contains('legend') || 
                                             node.classList.contains('colormap') || 
                                             node.classList.contains('colormap-container') ||
                                             node.querySelector('.legend, .colormap, .colormap-container'))) {{
                                            shouldRestyle = true;
                                            break;
                                        }}
                                    }}
                                }}
                            }});
                            if (shouldRestyle) {{
                                setTimeout(applyLegendStyling, 50);
                            }}
                        }});
                        
                        observer.observe(document.body, {{
                            childList: true,
                            subtree: true
                        }});
                    }}
                    
                    // Store map reference
                    window._last_folium_map = map;
                }}
            }}, 200);
        }});
        </script>
    '''
    m.get_root().html.add_child(Element(map_config_js))
    
    # Add dark background rectangle to cover visible area
    # Adjust background size based on zoom level
    bg_padding = 5.0 if zoom_level <= 5 else 2.0
    background_bounds = [
        [map_bounds[0][0] - bg_padding, map_bounds[0][1] - bg_padding],
        [map_bounds[1][0] + bg_padding, map_bounds[1][1] + bg_padding]
    ]
    
    folium.Rectangle(
        bounds=background_bounds,
        color="#25262d",
        fill=True,
        fillColor="#25262d",
        fillOpacity=1.0,
        weight=0,
        popup=None,
        tooltip=None,
        interactive=False
    ).add_to(m)

    if len(map_data) > 0:
        # Always exclude 'INDONESIA' (national aggregate) from all province-based calculations and coloring
        map_data = map_data[map_data['Provinsi'] != 'INDONESIA'] if 'INDONESIA' in map_data['Provinsi'].values else map_data
        
        min_val = map_data[metric_col].min()
        max_val = map_data[metric_col].max()
        
        # Choose appropriate color scheme based on metric
        if metric == 'Crime Rate 2023':
            # Red scale for crime (bad = high values = red)
            colormap = cm.LinearColormap(
                colors=['#ffffcc', '#ff4444'],
                vmin=min_val,
                vmax=max_val
            )
        elif metric == 'Gini Ratio':
            # Red scale for inequality (bad = high values = red)
            colormap = cm.LinearColormap(
                colors=['#ffffcc', '#ff4444'],
                vmin=min_val,
                vmax=max_val
            )
        elif metric == 'Education':
            # Green scale for education (good = high values = green)
            colormap = cm.LinearColormap(
                colors=['#ffcccc', '#44ff44'],
                vmin=min_val,
                vmax=max_val
            )
        elif metric == 'Income':
            # Blue scale for income (neutral metric)
            colormap = cm.LinearColormap(
                colors=['#ccccff', '#4444ff'],
                vmin=min_val,
                vmax=max_val
            )
        elif metric == 'Population':
            # Purple scale for population (neutral metric)
            colormap = cm.LinearColormap(
                colors=['#e6ccff', '#8844ff'],
                vmin=min_val,
                vmax=max_val
            )
        else:
            # Default to yellow-red scale
            colormap = cm.LinearColormap(
                colors=['#ffffcc', '#ff4444'],
                vmin=min_val,
                vmax=max_val
            )
        colormap.caption = title  # Add a caption to the legend
        # Add the colormap legend to the map
        colormap.add_to(m)
        province_data = {}
        region_data = {}
        for _, row in map_data.iterrows():
            geojson_name = reverse_mapping.get(row['Provinsi'])
            if geojson_name:
                province_data[geojson_name] = row[metric_col]
                region_data[geojson_name] = row['Region']
        # print(f"[DEBUG] province_data sample: {list(province_data.items())[:5]}")
        # Determine which provinces to highlight
        def highlight_feature(feature):
            prov_name = feature['properties']['Propinsi']
            region_name = region_data.get(prov_name)
            
            # Get the appropriate maximum color based on metric
            if metric == 'Education':
                max_color = '#44ff44'  # Green for education
            elif metric == 'Income':
                max_color = '#4444ff'  # Blue for income
            elif metric == 'Population':
                max_color = '#8844ff'  # Purple for population
            else:  # Crime Rate, Gini Ratio, and default
                max_color = '#ff4444'  # Red for crime/inequality
            
            # Province filter takes precedence
            if province_filter and province_filter != 'Semua':
                if prov_name == reverse_mapping.get(province_filter):
                    # Use the colormap's maximum color for the selected province
                    return {
                        'fillColor': max_color,
                        'color': 'black',
                        'weight': 3,
                        'fillOpacity': 1.0,
                    }
                else:
                    return {
                        'fillColor': '#cccccc',
                        'color': '#bbbbbb',
                        'weight': 1,
                        'fillOpacity': 0.2,
                    }
            elif region_filter and region_filter != 'Semua':
                if region_name == region_filter:
                    return {
                        'fillColor': colormap(province_data.get(prov_name, min_val)),
                        'color': 'black',
                        'weight': 1.5,
                        'fillOpacity': 0.8,
                    }
                else:
                    return {
                        'fillColor': '#cccccc',
                        'color': '#bbbbbb',
                        'weight': 1,
                        'fillOpacity': 0.3,
                    }
            else:
                return {
                    'fillColor': colormap(province_data.get(prov_name, min_val)),
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7,
                }

        # Add tooltip with value for each province
        folium.GeoJson(
            geojson_data,
            style_function=highlight_feature,
            tooltip=folium.features.GeoJsonTooltip(
                fields=['Propinsi'],
                aliases=['Province:'],
                localize=True,
                labels=False,
                sticky=True,
                toLocaleString=True,
                style=("background-color: white; color: #333; font-weight: bold; border-radius: 4px; padding: 4px;"),
                parse_html=True,
                # Custom function for tooltip content is not supported directly, so we use the following workaround:
                # We'll add the value to the feature properties before passing to GeoJson
            ),
            popup=None
        ).add_to(m)

        # Workaround: Add value to each feature's properties for tooltip
        for feature in geojson_data['features']:
            prov_name = feature['properties']['Propinsi']
            value = province_data.get(prov_name, None)
            if value is not None:
                feature['properties']['_tooltip'] = f"<b>{prov_name}</b><br>{value:,.2f}"
            else:
                feature['properties']['_tooltip'] = f"<b>{prov_name}</b><br>N/A"

        # Now re-add the GeoJson with the custom tooltip field
        folium.GeoJson(
            geojson_data,
            style_function=highlight_feature,
            tooltip=folium.features.GeoJsonTooltip(
                fields=['_tooltip'],
                aliases=[''],
                localize=True,
                labels=False,
                sticky=True,
                parse_html=True,
                style=("background-color: white; color: #333; font-weight: bold; border-radius: 4px; padding: 4px;")
            ),
            popup=folium.features.GeoJsonPopup(
                fields=['_tooltip'],
                aliases=[''],
                localize=True,
                labels=False,
                parse_html=True,
                style=("background-color: white; color: #333; font-weight: bold; border-radius: 4px; padding: 4px;")
            )
        ).add_to(m)
    
    # Add CSS to make iframe body transparent (targeting from inside the iframe)
    iframe_transparency_css = """
    <style>
    /* Target the body element that contains the folium map root */
    body {
        background-color: transparent !important;
        background: transparent !important;
    }
    
    /* Ensure the html element is also transparent */
    html {
        background-color: transparent !important;
        background: transparent !important;
    }
    
    /* Make sure the folium map container itself maintains the dark theme */
    .folium-map {
        background-color: #25262d !important;
    }
    </style>
    """
    m.get_root().html.add_child(folium.Element(iframe_transparency_css))
    
    return m

# --- Visualization Components Modularization ---

def render_key_metrics(df_filtered, selected_province, oc_data=None, selected_region=None, df_main=None):
    # Check if province or region filter is active
    is_filtered = selected_province != 'Semua' or selected_region != 'Semua'
    
    if is_filtered and df_main is not None:
        # Show provincial/regional data instead of OC Index
        render_provincial_metrics(df_filtered, selected_province, selected_region, df_main)
    elif oc_data and oc_data['indonesia_2023'] is not None:
        # Create columns for horizontal layout of metrics
        col1, col2, col3, col4 = st.columns(4)
        
        indonesia_2023 = oc_data['indonesia_2023']
        indonesia_2021 = oc_data['indonesia_2021']
        
        # Crime Rate from OC Index
        crime_rate_2023 = indonesia_2023['Criminality']
        crime_rate_2021 = indonesia_2021['Criminality'] if indonesia_2021 is not None else None
        
        with col1:
            if crime_rate_2021 is not None:
                crime_rate_change = crime_rate_2023 - crime_rate_2021  # Positive = worse (crime increased), Negative = better (crime decreased)
                if abs(crime_rate_change) >= 0.01: # Only show change if significant (>= 0.01)
                    st.metric(
                        "Tingkat Kriminalitas (OC Index)", 
                        f"{crime_rate_2023:.2f}",
                        delta=f"{crime_rate_change:.2f} dari 2021",
                        delta_color="inverse",  # inverse because higher crime rate is worse
                        help="Skor Indeks Kejahatan Terorganisir (0-10, Semakin tinggi semakin buruk)"
                    )
                else:
                    st.metric(
                        "Tingkat Kriminalitas (OC Index)", 
                        f"{crime_rate_2023:.2f}",
                        delta="Sama dengan 2021",
                        delta_color="off",
                        help="Skor Indeks Kejahatan Terorganisir (0-10, Semakin tinggi semakin buruk)"
                    )
            else:
                st.metric(
                    "Tingkat Kriminalitas (OC Index)", 
                    f"{crime_rate_2023:.2f}",
                    help="Skor Indeks Kejahatan Terorganisir (0-10, Semakin tinggi semakin buruk)"
                )
        
        # World Rank
        world_rank_2023 = int(indonesia_2023['World_Rank'])
        world_rank_2021 = int(indonesia_2021['World_Rank']) if indonesia_2021 is not None else None
        
        with col2:
            if world_rank_2021 is not None:
                rank_change = -(world_rank_2023 - world_rank_2021)  # Positive = worse (rank increased), Negative = better (rank decreased)
                if rank_change != 0:
                    st.metric(
                        "Peringkat Dunia", 
                        f"#{world_rank_2023} / 193",
                        delta=f"{rank_change} dari 2021",
                        delta_color="inverse",  # inverse because lower rank is better
                        help="Peringkat global di antara semua negara (Peringkat rendah lebih baik)"
                    )
                else:
                    st.metric(
                        "Peringkat Dunia", 
                        f"#{world_rank_2023} / 193",
                        delta="Sama dengan 2021",
                        delta_color="off",
                        help="Peringkat global di antara semua negara (Peringkat rendah lebih baik)"
                    )
            else:
                st.metric(
                    "Peringkat Dunia", 
                    f"#{world_rank_2023} / 193",
                    help="Peringkat global di antara semua negara (Peringkat rendah lebih baik)"
                )
        
        # Asia Rank
        asia_rank_2023 = int(indonesia_2023['Asia_Rank']) if pd.notna(indonesia_2023['Asia_Rank']) else None
        asia_rank_2021 = int(indonesia_2021['Asia_Rank']) if indonesia_2021 is not None and pd.notna(indonesia_2021['Asia_Rank']) else None
        
        with col3:
            if asia_rank_2023 is not None:
                if asia_rank_2021 is not None:
                    asia_change = asia_rank_2023 - asia_rank_2021  # Positive = worse (rank increased), Negative = better (rank decreased)
                    if asia_change != 0:
                        st.metric(
                            "Peringkat Asia", 
                            f"#{asia_rank_2023} / 46",
                            delta=f"{asia_change} dari 2021",
                            delta_color="inverse",  # inverse because lower rank is better
                            help="Peringkat di antara negara-negara Asia (Peringkat rendah lebih baik)"
                        )
                    else:
                        st.metric(
                            "Peringkat Asia", 
                            f"#{asia_rank_2023} / 46",
                            delta="Sama dengan 2021",
                            delta_color="off",
                            help="Peringkat di antara negara-negara Asia (Peringkat rendah lebih baik)"
                        )
                else:
                    st.metric(
                        "Peringkat Asia", 
                        f"#{asia_rank_2023} / 46",
                        help="Peringkat di antara negara-negara Asia (Peringkat rendah lebih baik)"
                    )
        
        # ASEAN Rank
        asean_rank_2023 = int(indonesia_2023['ASEAN_Rank']) if pd.notna(indonesia_2023['ASEAN_Rank']) else None
        asean_rank_2021 = int(indonesia_2021['ASEAN_Rank']) if indonesia_2021 is not None and pd.notna(indonesia_2021['ASEAN_Rank']) else None
        
        with col4:
            if asean_rank_2023 is not None:
                if asean_rank_2021 is not None:
                    asean_change = asean_rank_2023 - asean_rank_2021  # Positive = worse (rank increased), Negative = better (rank decreased)
                    if asean_change != 0:
                        st.metric(
                            "Peringkat ASEAN", 
                            f"#{asean_rank_2023} / 10",
                            delta=f"{asean_change} dari 2021",
                            delta_color="inverse",  # inverse because lower rank is better
                            help="Peringkat di antara negara-negara ASEAN (Peringkat rendah lebih baik)"
                        )
                    else:
                        st.metric(
                            "Peringkat ASEAN", 
                            f"#{asean_rank_2023} / 10",
                            delta="Sama dengan 2021",
                            delta_color="off",
                            help="Peringkat di antara negara-negara ASEAN (Peringkat rendah lebih baik)"
                        )
                else:
                    st.metric(
                        "Peringkat ASEAN", 
                        f"#{asean_rank_2023} / 10",
                        help="Peringkat di antara negara-negara ASEAN (Peringkat rendah lebih baik)"
                    )
    else:
        st.warning("Data Indeks OC tidak tersedia")



def render_provincial_data_table(df_filtered):
    st.subheader("Data Provinsi Terperinci")
    df_display = df_filtered.reset_index(drop=True)
    df_display.index = df_display.index + 1
    st.dataframe(df_display, use_container_width=True)

@st.cache_data
def load_oc_index_data():
    """Load and process OC Index data for global crime rankings"""
    try:
        # Load OC Index data
        df_oc_2023 = pd.read_csv("dataset/oc_index_2023.csv", sep=';')
        df_oc_2021 = pd.read_csv("dataset/oc_index_2021.csv", sep=';')
        
        # Clean criminality column - replace comma with dot for proper float conversion
        df_oc_2023['Criminality'] = df_oc_2023['Criminality'].astype(str).str.replace(',', '.').astype(float)
        df_oc_2021['Criminality'] = df_oc_2021['Criminality'].astype(str).str.replace(',', '.').astype(float)
        
        # Sort by criminality (higher = worse ranking)
        df_oc_2023_sorted = df_oc_2023.sort_values('Criminality', ascending=False).reset_index(drop=True)
        df_oc_2021_sorted = df_oc_2021.sort_values('Criminality', ascending=False).reset_index(drop=True)
        
        # Add rank columns (1 = highest criminality/worst)
        df_oc_2023_sorted['World_Rank'] = df_oc_2023_sorted.index + 1
        df_oc_2021_sorted['World_Rank'] = df_oc_2021_sorted.index + 1
        
        # Calculate Asia rankings
        asia_2023 = df_oc_2023_sorted[df_oc_2023_sorted['Continent'] == 'Asia'].reset_index(drop=True)
        asia_2023['Asia_Rank'] = asia_2023.index + 1
        
        asia_2021 = df_oc_2021_sorted[df_oc_2021_sorted['Continent'] == 'Asia'].reset_index(drop=True)
        asia_2021['Asia_Rank'] = asia_2021.index + 1
        
        # Calculate ASEAN rankings (Indonesia's region)
        asean_countries = ['Indonesia', 'Malaysia', 'Thailand', 'Vietnam', 'Philippines', 
                          'Singapore', 'Myanmar', 'Cambodia', 'Laos', 'Brunei', 'Timor-Leste']
        
        asean_2023 = df_oc_2023_sorted[df_oc_2023_sorted['Country'].isin(asean_countries)].reset_index(drop=True)
        asean_2023['ASEAN_Rank'] = asean_2023.index + 1
        
        asean_2021 = df_oc_2021_sorted[df_oc_2021_sorted['Country'].isin(asean_countries)].reset_index(drop=True)
        asean_2021['ASEAN_Rank'] = asean_2021.index + 1
        
        # Merge Asia rankings back to main dataframes
        df_oc_2023_sorted = df_oc_2023_sorted.merge(
            asia_2023[['Country', 'Asia_Rank']], on='Country', how='left'
        )
        df_oc_2021_sorted = df_oc_2021_sorted.merge(
            asia_2021[['Country', 'Asia_Rank']], on='Country', how='left'
        )
        
        # Merge ASEAN rankings back to main dataframes
        df_oc_2023_sorted = df_oc_2023_sorted.merge(
            asean_2023[['Country', 'ASEAN_Rank']], on='Country', how='left'
        )
        df_oc_2021_sorted = df_oc_2021_sorted.merge(
            asean_2021[['Country', 'ASEAN_Rank']], on='Country', how='left'
        )
        
        # Get Indonesia data
        indonesia_2023 = df_oc_2023_sorted[df_oc_2023_sorted['Country'] == 'Indonesia'].iloc[0] if len(df_oc_2023_sorted[df_oc_2023_sorted['Country'] == 'Indonesia']) > 0 else None
        indonesia_2021 = df_oc_2021_sorted[df_oc_2021_sorted['Country'] == 'Indonesia'].iloc[0] if len(df_oc_2021_sorted[df_oc_2021_sorted['Country'] == 'Indonesia']) > 0 else None
        
        return {
            'indonesia_2023': indonesia_2023,
            'indonesia_2021': indonesia_2021,
            'df_2023': df_oc_2023_sorted,
            'df_2021': df_oc_2021_sorted
        }
    except Exception as e:
        st.error(f"Error loading OC Index data: {e}")
        return None

def create_crime_trend_2012_2023(df_time_series, selected_province='All', selected_region='All'):
    """Create crime rate trend chart for 2012-2023 with filtering support"""
    if df_time_series is None or df_time_series.empty:
        return None
    
    # Determine what data to show based on filters
    if selected_province != 'Semua':
        # Show specific province trend
        title = f"Tren Tingkat Kriminalitas {selected_province} (2016-2023)"
        df_to_analyze = df_time_series[df_time_series['Provinsi'] == selected_province]
        line_name = selected_province
        line_color = '#ff6b6b'
    elif selected_region != 'Semua':
        # Show regional average trend
        title = f"Tren Tingkat Kriminalitas Wilayah {selected_region} (2016-2023)"
        # Filter time series data by region (need to add region mapping)
        region_mapping = {
            "ACEH": "Sumatra", "SUMATERA UTARA": "Sumatra", "SUMATERA BARAT": "Sumatra",
            "RIAU": "Sumatra", "KEPULAUAN RIAU": "Sumatra", "JAMBI": "Sumatra",
            "SUMATERA SELATAN": "Sumatra", "BENGKULU": "Sumatra", "LAMPUNG": "Sumatra",
            "KEPULAUAN BANGKA BELITUNG": "Sumatra", "DKI JAKARTA": "Jawa", "JAWA BARAT": "Jawa",
            "JAWA TENGAH": "Jawa", "DI YOGYAKARTA": "Jawa", "JAWA TIMUR": "Jawa", "BANTEN": "Jawa",
            "KALIMANTAN BARAT": "Kalimantan", "KALIMANTAN TENGAH": "Kalimantan",
            "KALIMANTAN SELATAN": "Kalimantan", "KALIMANTAN TIMUR": "Kalimantan",
            "KALIMANTAN UTARA": "Kalimantan", "SULAWESI UTARA": "Sulawesi",
            "SULAWESI TENGAH": "Sulawesi", "SULAWESI SELATAN": "Sulawesi",
            "SULAWESI TENGGARA": "Sulawesi", "GORONTALO": "Sulawesi", "SULAWESI BARAT": "Sulawesi",
            "BALI": "Bali & Nusa Tenggara", "NUSA TENGGARA BARAT": "Bali & Nusa Tenggara",
            "NUSA TENGGARA TIMUR": "Bali & Nusa Tenggara", "MALUKU": "Maluku", "MALUKU UTARA": "Maluku",
            "PAPUA": "Papua", "PAPUA BARAT": "Papua"
        }
        regional_provinces = [prov for prov, region in region_mapping.items() if region == selected_region]
        df_to_analyze = df_time_series[df_time_series['Provinsi'].isin(regional_provinces)]
        line_name = f"{selected_region} Average"
        line_color = '#ff6b6b'
    else:
        # Show national average trend
        title = "Tren Tingkat Kriminalitas Indonesia (2016-2023)"
        df_to_analyze = df_time_series[df_time_series['Provinsi'] != 'INDONESIA'] if 'INDONESIA' in df_time_series['Provinsi'].values else df_time_series
        line_name = 'National Average'
        line_color = '#ff6b6b'
    
    # Calculate trend data
    years = []
    crime_rates = []
    
    year_columns = [col for col in df_time_series.columns if col.isdigit() and int(col) >= 2016 and int(col) <= 2023]
    
    for year_col in sorted(year_columns):
        year = int(year_col)
        
        # Clean and convert the data to numeric, handling errors
        try:
            if selected_province != 'Semua' and not df_to_analyze.empty:
                # For province, get specific value
                numeric_data = pd.to_numeric(df_to_analyze[year_col], errors='coerce')
                avg_crime = numeric_data.iloc[0] if len(numeric_data) > 0 else None
            else:
                # For region/national, calculate average
                numeric_data = pd.to_numeric(df_to_analyze[year_col], errors='coerce')
                avg_crime = numeric_data.mean()
            
            if not pd.isna(avg_crime):
                years.append(year)
                crime_rates.append(avg_crime)
        except Exception as e:
            print(f"Error processing year {year}: {e}")
            continue
    
    if len(years) > 0 and len(crime_rates) > 0:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years,
            y=crime_rates,
            mode='lines+markers',
            name=line_name,
            line=dict(color=line_color, width=3),
            marker=dict(size=8, color=line_color)
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Tahun",
            yaxis_title="Tingkat Kriminalitas (per 100.000 Penduduk)",
            plot_bgcolor='#25262d',
            paper_bgcolor='#25262d',
            font_color='white',
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )
        
        return fig
    
    return None

def create_top_provinces_chart(df_filtered):
    """Create chart showing top provinces by crime rate"""
    if 'Tindak Pidana 2023' not in df_filtered.columns:
        return None
    
    # Get top 10 provinces with highest crime rates
    top_provinces = df_filtered.nlargest(10, 'Tindak Pidana 2023')
    
    fig = px.bar(
        top_provinces,
        x='Tindak Pidana 2023',
        y='Provinsi',
        orientation='h',
        title="Provinsi dengan Tingkat Kriminalitas Tertinggi",
        color='Tindak Pidana 2023',
        color_continuous_scale='Reds',
    )
    
    # Hide the color scale/colorbar
    fig.update_coloraxes(showscale=False)
    
    fig.update_layout(
        plot_bgcolor='#25262d',
        paper_bgcolor='#25262d',
        font_color='white',
        margin=dict(l=0, r=20, t=40, b=20),
        height=400,
        yaxis={'categoryorder': 'total ascending', 'title': ''},
        showlegend=False
    )
    
    return fig

def create_scatter_plot(df_filtered, x_col, y_col, title, region_filter=None, province_filter=None):
    """Create scatter plot with dynamic coloring and legend based on region/province filter"""
    if x_col not in df_filtered.columns or y_col not in df_filtered.columns:
        return None

    # Determine coloring and legend
    if province_filter and province_filter != 'Semua' and 'Provinsi' in df_filtered.columns:
        color_col = 'Provinsi'
    elif region_filter and region_filter != 'Semua' and 'Provinsi' in df_filtered.columns:
        color_col = 'Provinsi'
    else:
        color_col = 'Region' if 'Region' in df_filtered.columns else None

    fig = px.scatter(
        df_filtered,
        x=x_col,
        y=y_col,
        hover_name='Provinsi' if 'Provinsi' in df_filtered.columns else None,
        title=title,
        color=color_col
    )

    fig.update_layout(
        plot_bgcolor='#25262d',
        paper_bgcolor='#25262d',
        font_color='white',
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
    )

    return fig

def render_provincial_metrics(df_filtered, selected_province, selected_region, df_main):
    """Render metrics for provincial/regional data instead of OC Index"""
    
    if selected_province != 'Semua':
        # Provincial view - show specific province data
        province_data = df_filtered[df_filtered['Provinsi'] == selected_province].iloc[0] if not df_filtered.empty else None
        
        if province_data is not None and 'Tindak Pidana 2023' in province_data and 'Tindak Pidana 2022' in province_data:
            # Create columns for horizontal layout of metrics
            col1, col2, col3 = st.columns(3)
            
            # Crime Rate 2023 vs 2022
            crime_2023 = province_data['Tindak Pidana 2023']
            crime_2022 = province_data['Tindak Pidana 2022']
            
            with col1:
                if pd.notna(crime_2023) and pd.notna(crime_2022):
                    crime_change = crime_2023 - crime_2022
                    if abs(crime_change) >= 0.1:  # Show change if significant
                        st.metric(
                            "Tingkat Kriminalitas 2023",
                            f"{crime_2023:.1f}",
                            delta=f"{crime_change:+.1f} dari 2022",
                            delta_color="inverse",  # inverse because higher crime is worse
                            help="Insiden kejahatan per 100.000 penduduk"
                        )
                    else:
                        st.metric(
                            "Tingkat Kriminalitas 2023",
                            f"{crime_2023:.1f}",
                            delta="Mirip dengan 2022",
                            delta_color="off",
                            help="Insiden kejahatan per 100.000 penduduk"
                        )
                else:
                    st.metric(
                        "Tingkat Kriminalitas 2023",
                        f"{crime_2023:.1f}" if pd.notna(crime_2023) else "N/A",
                        help="Insiden kejahatan per 100.000 penduduk"
                    )
            
            # Regional ranking (rank within region)
            with col2:
                if 'Region' in province_data and pd.notna(province_data['Region']):
                    region_provinces = df_main[df_main['Region'] == province_data['Region']]
                    if 'Tindak Pidana 2023' in region_provinces.columns:
                        region_sorted = region_provinces.dropna(subset=['Tindak Pidana 2023']).sort_values('Tindak Pidana 2023', ascending=True).reset_index(drop=True)
                        regional_rank = region_sorted[region_sorted['Provinsi'] == selected_province].index[0] + 1 if selected_province in region_sorted['Provinsi'].values else None
                        total_in_region = len(region_sorted)
                        
                        # Calculate 2022 regional ranking for delta
                        regional_rank_2022 = None
                        if 'Tindak Pidana 2022' in region_provinces.columns:
                            region_sorted_2022 = region_provinces.dropna(subset=['Tindak Pidana 2022']).sort_values('Tindak Pidana 2022', ascending=True).reset_index(drop=True)
                            regional_rank_2022 = region_sorted_2022[region_sorted_2022['Provinsi'] == selected_province].index[0] + 1 if selected_province in region_sorted_2022['Provinsi'].values else None
                        
                        if regional_rank:
                            if regional_rank_2022 is not None:
                                rank_change = -(regional_rank - regional_rank_2022)  # Positive = worse (rank increased), Negative = better (rank decreased)
                                if rank_change != 0:
                                    st.metric(
                                        f"Peringkat di {province_data['Region']}",
                                        f"#{regional_rank} / {total_in_region}",
                                        delta=f"{rank_change} dari 2022",
                                        delta_color="inverse",  # inverse because lower rank is better
                                        help="Peringkat wilayah berdasarkan tingkat kriminalitas (Peringkat rendah lebih baik)"
                                    )
                                else:
                                    st.metric(
                                        f"Peringkat di {province_data['Region']}",
                                        f"#{regional_rank} / {total_in_region}",
                                        delta="Sama dengan 2022",
                                        delta_color="off",
                                        help="Peringkat wilayah berdasarkan tingkat kriminalitas (Peringkat rendah lebih baik)"
                                    )
                            else:
                                st.metric(
                                    f"Peringkat di {province_data['Region']}",
                                    f"#{regional_rank} / {total_in_region}",
                                    help="Peringkat wilayah berdasarkan tingkat kriminalitas (Peringkat rendah lebih baik)"
                                )
            
            # National ranking (rank among all provinces)
            with col3:
                if 'Tindak Pidana 2023' in df_main.columns:
                    national_sorted = df_main.dropna(subset=['Tindak Pidana 2023']).sort_values('Tindak Pidana 2023', ascending=True).reset_index(drop=True)
                    national_rank = national_sorted[national_sorted['Provinsi'] == selected_province].index[0] + 1 if selected_province in national_sorted['Provinsi'].values else None
                    total_provinces = len(national_sorted)
                    
                    # Calculate 2022 national ranking for delta
                    national_rank_2022 = None
                    if 'Tindak Pidana 2022' in df_main.columns:
                        national_sorted_2022 = df_main.dropna(subset=['Tindak Pidana 2022']).sort_values('Tindak Pidana 2022', ascending=True).reset_index(drop=True)
                        national_rank_2022 = national_sorted_2022[national_sorted_2022['Provinsi'] == selected_province].index[0] + 1 if selected_province in national_sorted_2022['Provinsi'].values else None
                    
                    if national_rank:
                        if national_rank_2022 is not None:
                            rank_change = -(national_rank - national_rank_2022)  # Positive = worse (rank increased), Negative = better (rank decreased)
                            if rank_change != 0:
                                st.metric(
                                    "Peringkat Nasional",
                                    f"#{national_rank} / {total_provinces}",
                                    delta=f"{rank_change} dari 2022",
                                    delta_color="inverse",  # inverse because lower rank is better
                                    help="Peringkat nasional berdasarkan tingkat kriminalitas (Peringkat rendah lebih baik)"
                                )
                            else:
                                st.metric(
                                    "Peringkat Nasional",
                                    f"#{national_rank} / {total_provinces}",
                                    delta="Sama dengan 2022",
                                    delta_color="off",
                                    help="Peringkat nasional berdasarkan tingkat kriminalitas (Peringkat rendah lebih baik)"
                                )
                        else:
                            st.metric(
                                "Peringkat Nasional",
                                f"#{national_rank} / {total_provinces}",
                                help="Peringkat nasional berdasarkan tingkat kriminalitas (Peringkat rendah lebih baik)"
                            )
                    
    elif selected_region != 'All':
        # Regional view - show regional average
        regional_data = df_filtered
        
        if not regional_data.empty and 'Tindak Pidana 2023' in regional_data.columns:
            # Create columns for horizontal layout of regional metrics
            col1, col2, col3 = st.columns(3)
            
            # Regional average crime rate
            avg_crime_2023 = regional_data['Tindak Pidana 2023'].mean()
            avg_crime_2022 = regional_data['Tindak Pidana 2022'].mean() if 'Tindak Pidana 2022' in regional_data.columns else None
            
            with col1:
                if pd.notna(avg_crime_2023) and pd.notna(avg_crime_2022):
                    crime_change = avg_crime_2023 - avg_crime_2022
                    if abs(crime_change) >= 0.1:
                        st.metric(
                            f"Tingkat Kriminalitas {selected_region}",
                            f"{avg_crime_2023:.1f}",
                            delta=f"{crime_change:+.1f} from 2022",
                            delta_color="inverse",
                            help="Rata-rata tingkat kriminalitas per 100.000 penduduk untuk wilayah"
                        )
                    else:
                        st.metric(
                            f"Tingkat Kriminalitas {selected_region}",
                            f"{avg_crime_2023:.1f}",
                            delta="Mirip dengan 2022",
                            delta_color="off",
                            help="Rata-rata tingkat kriminalitas per 100.000 penduduk untuk wilayah"
                        )
                else:
                    st.metric(
                        f"Tingkat Kriminalitas {selected_region}",
                        f"{avg_crime_2023:.1f}" if pd.notna(avg_crime_2023) else "N/A",
                        help="Rata-rata tingkat kriminalitas per 100.000 penduduk untuk wilayah"
                    )
            
            # Regional rank among all regions
            with col2:
                region_averages = df_main.groupby('Region')['Tindak Pidana 2023'].mean().dropna().sort_values(ascending=True)
                regional_rank = list(region_averages.index).index(selected_region) + 1 if selected_region in region_averages.index else None
                total_regions = len(region_averages)
                
                # Calculate 2022 regional ranking for delta
                regional_rank_2022 = None
                if 'Tindak Pidana 2022' in df_main.columns:
                    region_averages_2022 = df_main.groupby('Region')['Tindak Pidana 2022'].mean().dropna().sort_values(ascending=True)
                    regional_rank_2022 = list(region_averages_2022.index).index(selected_region) + 1 if selected_region in region_averages_2022.index else None
                
                if regional_rank:
                    if regional_rank_2022 is not None:
                        rank_change = -(regional_rank - regional_rank_2022)  # Positive = worse (rank increased), Negative = better (rank decreased)
                        if rank_change != 0:
                            st.metric(
                                "Peringkat Wilayah",
                                f"#{regional_rank} / {total_regions}",
                                delta=f"{rank_change} dari 2022",
                                delta_color="inverse",  # inverse because lower rank is better
                                help="Peringkat wilayah berdasarkan rata-rata tingkat kriminalitas (Peringkat rendah lebih baik)"
                            )
                        else:
                            st.metric(
                                "Peringkat Wilayah",
                                f"#{regional_rank} / {total_regions}",
                                delta="Sama dengan 2022",
                                delta_color="off",
                                help="Peringkat wilayah berdasarkan rata-rata tingkat kriminalitas (Peringkat rendah lebih baik)"
                            )
                    else:
                        st.metric(
                            "Peringkat Wilayah",
                            f"#{regional_rank} / {total_regions}",
                            help="Peringkat wilayah berdasarkan rata-rata tingkat kriminalitas (Peringkat rendah lebih baik)"
                        )
            
            # Number of provinces in region
            with col3:
                num_provinces = len(regional_data)
                st.metric(
                    "# Provinsi dalam Wilayah",
                    f"{num_provinces} Provinsi",
                    help="Jumlah provinsi di wilayah ini"
                )

def main():
    st.title("🇮🇩 Dashboard Kriminalitas Indonesia")
    # st.markdown("### Interactive Analysis of Provincial Crime Data")
    
    # Load data
    with st.spinner("Memuat dan memproses data..."):
        df_main, df_time_series = load_and_process_data()
        oc_data = load_oc_index_data()
    
    if df_main is None or df_main.empty:
        st.error("Gagal memuat data. Silakan periksa file dataset Anda.")
        return
    
    # Exclude 'INDONESIA' from all dataframes at the start of main analysis
    if 'Provinsi' in df_main.columns:
        df_main = df_main[df_main['Provinsi'] != 'INDONESIA']
    
    # Sidebar for filters and controls
    st.sidebar.header("Kriminalitas Indonesia")
    
    # Initialize filter variables
    selected_region = 'All'
    selected_province = 'All'
    
    # Region filter
    if 'Region' in df_main.columns:
        regions = ['Semua'] + sorted(df_main['Region'].dropna().unique().tolist())
        selected_region = st.sidebar.selectbox("Pilih Wilayah:", regions)
        if selected_region != 'Semua':
            df_filtered = df_main[df_main['Region'] == selected_region]
        else:
            df_filtered = df_main
    else:
        df_filtered = df_main
    
    # Province filter
    if 'Provinsi' in df_filtered.columns:
        available_provinces = df_filtered['Provinsi'].dropna().unique().tolist()
        provinces = ['Semua'] + sorted(available_provinces)
        selected_province = st.sidebar.selectbox("Pilih Provinsi:", provinces)
        if selected_province != 'Semua':
            df_filtered = df_filtered[df_filtered['Provinsi'] == selected_province]
    
    # Display active filters
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filter Aktif")
    if 'Region' in df_main.columns and selected_region != 'Semua':
        st.sidebar.write(f"🌍 **Wilayah:** {selected_region}")
    if 'Provinsi' in df_main.columns and selected_province != 'Semua':
        st.sidebar.write(f"📍 **Provinsi:** {selected_province}")
    if (selected_region == 'Semua' and selected_province == 'Semua'):
        st.sidebar.write("🌐 Menampilkan semua data")
    
    # Show number of provinces in current selection
    num_provinces = len(df_filtered['Provinsi'].unique()) if 'Provinsi' in df_filtered.columns else 0
    st.sidebar.write(f"📊 **Provinsi ditampilkan:** {num_provinces}")
    
    # Dynamic header based on selection
    if selected_province != 'Semua':
        st.markdown("## Tinjauan Provinsi")
    elif selected_region != 'Semua':
        st.markdown("## Tinjauan Wilayah")
    else:
        st.markdown("## Tinjauan Nasional")
    
    # First row: Key metrics
    render_key_metrics(df_filtered, selected_province, oc_data, selected_region, df_main)
    
    trend_col, top_col = st.columns([3, 2])
    
    with trend_col:
        trend_fig = create_crime_trend_2012_2023(df_time_series, selected_province, selected_region)
        if trend_fig:
            st.plotly_chart(trend_fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Data runtun waktu tidak tersedia")
    
    with top_col:
        top_fig = create_top_provinces_chart(df_filtered)
        if top_fig:
            st.plotly_chart(top_fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Data kriminalitas tidak tersedia")
    
    # Third row: Crime choropleth map
    geojson_data = load_geojson()
    province_mapping = create_province_mapping()
    
    if geojson_data and province_mapping:
        with st.spinner("Membuat peta kriminalitas choropleth..."):
            folium_map = create_choropleth_map(
                df_filtered, 'Crime Rate 2023', geojson_data, province_mapping,
                region_filter=selected_region, province_filter=selected_province
            )
        st_folium(folium_map, width="100%", height=350, returned_objects=[], key="crime_map")
        # st.info("🔍 **Map Interpretation**: Darker red areas indicate higher crime rates per 100,000 population.")
    else:
        st.warning("GeoJSON or province mapping not loaded.")
    
    # Second row: Detailed analysis
    st.markdown("---")
    st.markdown("## 🔍 Analisis Sosial Ekonomi")
    
    # Second row: Gini + scatter and Education + scatter
    gini_col, education_col = st.columns(2)
    
    with gini_col:
        st.subheader("Analisis Ketimpangan Pendapatan")
        
        # Gini ratio choropleth
        if geojson_data and province_mapping:
            with st.spinner("Membuat peta choropleth rasio Gini..."):
                gini_map = create_choropleth_map(
                    df_filtered, 'Gini Ratio', geojson_data, province_mapping,
                    region_filter=selected_region, province_filter=selected_province
                )
            st_folium(gini_map, width="100%", height=400, returned_objects=[], key="gini_map")
        
        # Gini vs Crime scatter plot
        if 'gini_ratio_2023' in df_filtered.columns and 'Tindak Pidana 2023' in df_filtered.columns:
            gini_scatter = create_scatter_plot(
                df_filtered,
                'gini_ratio_2023',
                'Tindak Pidana 2023',
                "Ketimpangan Pendapatan vs Tingkat Kriminalitas",
                region_filter=selected_region,
                province_filter=selected_province
            )
            if gini_scatter:
                st.plotly_chart(gini_scatter, use_container_width=True, config={'displayModeBar': False})
    
    with education_col:
        st.subheader("Analisis Pendidikan")
        
        # Education choropleth (using SMA/PT completion rate)
        if geojson_data and province_mapping and 'Pendidikan Terakhir SMA/PT' in df_filtered.columns:
            with st.spinner("Membuat peta choropleth pendidikan..."):
                edu_map = create_choropleth_map(
                    df_filtered, 'Education', geojson_data, province_mapping,
                    region_filter=selected_region, province_filter=selected_province
                )
            st_folium(edu_map, width="100%", height=400, returned_objects=[], key="education_map")
        
        # Education vs Crime scatter plot
        if 'Pendidikan Terakhir SMA/PT' in df_filtered.columns and 'Tindak Pidana 2023' in df_filtered.columns:
            edu_scatter = create_scatter_plot(
                df_filtered,
                'Pendidikan Terakhir SMA/PT',
                'Tindak Pidana 2023',
                "Tingkat Pendidikan vs Tingkat Kriminalitas",
                region_filter=selected_region,
                province_filter=selected_province
            )
            if edu_scatter:
                st.plotly_chart(edu_scatter, use_container_width=True, config={'displayModeBar': False})
    
    # Data table at the bottom
    st.markdown("---")
    render_provincial_data_table(df_filtered)

if __name__ == "__main__":
    main()
