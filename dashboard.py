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
import branca.colormap as cm
from streamlit_folium import st_folium
import uuid
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="Indonesia Socioeconomic Dashboard",
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
    
    /* Folium map containers */
    .stFolium {
        background-color: #25262d;
        border-radius: 0.75rem;
        overflow: hidden;
        margin: 1rem 0;
        padding: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Additional styling for map iframe */
    .stFolium iframe {
        border-radius: 0.75rem;
    }
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
    if province_filter and province_filter != 'All' and 'Provinsi' in df.columns:
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
    elif region_filter and region_filter != 'All' and 'Provinsi' in df.columns:
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
            title="Correlation Matrix of Socioeconomic Indicators",
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
                        title="Indonesia Crime Rate Trend (2012-2023)",
                        markers=True
                    )
                    
                    fig.update_layout(
                        height=400,
                        xaxis_title="Year",
                        yaxis_title="Crime Rate (per 100,000 population)",
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
    """Create a choropleth map using folium, strictly restricted to Indonesia bounds and zoom, and highlight only selected region/province if filtered"""
    # Prepare data based on selected metric
    if metric == 'Crime Rate 2023':
        map_data = df[['Provinsi', 'Tindak Pidana 2023', 'Region']].dropna(subset=['Provinsi'])
        metric_col = 'Tindak Pidana 2023'
        title = 'Crime Rate per 100,000 Population (2023)'
    elif metric == 'Population':
        map_data = df[['Provinsi', 'Jumlah Penduduk', 'Region']].dropna(subset=['Provinsi'])
        metric_col = 'Jumlah Penduduk'
        title = 'Population by Province (thousands)'
    elif metric == 'Gini Ratio':
        map_data = df[['Provinsi', 'gini_ratio_2023', 'Region']].dropna(subset=['Provinsi'])
        metric_col = 'gini_ratio_2023'
        title = 'Gini Ratio by Province (2023)'
    elif metric == 'Income':
        map_data = df[['Provinsi', 'Pendapatan Agustus', 'Region']].dropna(subset=['Provinsi'])
        metric_col = 'Pendapatan Agustus'
        title = 'Average Income by Province (August 2023)'
    else:
        map_data = df[['Provinsi', 'Tindak Pidana 2023', 'Region']].dropna(subset=['Provinsi'])
        metric_col = 'Tindak Pidana 2023'
        title = 'Crime Rate per 100,000 Population (2023)'

    reverse_mapping = {v: k for k, v in province_mapping.items()}

    # Debug output
    print(f"[DEBUG] map_data rows: {len(map_data)}")
    print(f"[DEBUG] map_data Provinsi unique: {map_data['Provinsi'].unique()}")
    print(f"[DEBUG] reverse_mapping keys: {list(reverse_mapping.keys())}")

    indonesia_sw = [-11.0, 94.0]
    indonesia_ne = [6.0, 141.0]

    m = folium.Map(
        location=[-2.5, 118.0],
        zoom_start=5,
        tiles='CartoDB positron',
        max_bounds=True,
        min_zoom=4,
        max_zoom=8
    )
    m.fit_bounds([indonesia_sw, indonesia_ne])

    folium.Rectangle(
        bounds=[indonesia_sw, indonesia_ne],
        color="#ff7800",
        fill=False,
        weight=2
    ).add_to(m)

    bounds_js = f'''
        <script>
        var map = window._last_folium_map || window.map;
        if (map) {{
            map.setMaxBounds([[{indonesia_sw[0]}, {indonesia_sw[1]}], [{indonesia_ne[0]}, {indonesia_ne[1]}]]);
        }}
        </script>
    '''
    from folium import Element
    m.get_root().html.add_child(Element(bounds_js))

    if len(map_data) > 0:
        # Always exclude 'INDONESIA' (national aggregate) from all province-based calculations and coloring
        map_data = map_data[map_data['Provinsi'] != 'INDONESIA'] if 'INDONESIA' in map_data['Provinsi'].values else map_data
        if metric == 'Population':
            min_val = map_data[metric_col].min()
            max_val = map_data[metric_col].max()
        else:
            min_val = map_data[metric_col].min()
            max_val = map_data[metric_col].max()
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
        print(f"[DEBUG] province_data sample: {list(province_data.items())[:5]}")
        # Determine which provinces to highlight
        def highlight_feature(feature):
            prov_name = feature['properties']['Propinsi']
            region_name = region_data.get(prov_name)
            # Province filter takes precedence
            if province_filter and province_filter != 'All':
                if prov_name == reverse_mapping.get(province_filter):
                    # Use the colormap's last color directly (force red)
                    return {
                        'fillColor': '#ff4444',  # hardcode to the highest color in the colormap
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
            elif region_filter and region_filter != 'All':
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
                feature['properties']['_tooltip'] = f"<b>{prov_name}</b><br>Value: {value:,.2f}"
            else:
                feature['properties']['_tooltip'] = f"<b>{prov_name}</b><br>Value: N/A"

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
    return m

# --- Visualization Components Modularization ---

def render_key_metrics(df_filtered, selected_province, oc_data=None):
    st.subheader("🇮🇩 Indonesia Global Crime Rankings")
    
    if oc_data and oc_data['indonesia_2023'] is not None:
        indonesia_2023 = oc_data['indonesia_2023']
        indonesia_2021 = oc_data['indonesia_2021']
        
        # Crime Rate from OC Index
        crime_rate_2023 = indonesia_2023['Criminality']
        crime_rate_2021 = indonesia_2021['Criminality'] if indonesia_2021 is not None else None
        
        if crime_rate_2021 is not None:
            crime_rate_change = crime_rate_2023 - crime_rate_2021  # Positive = worse (crime increased), Negative = better (crime decreased)
            if abs(crime_rate_change) >= 0.01:  # Only show change if significant (>= 0.01)
                st.metric(
                    "Crime Rate (OC Index)", 
                    f"{crime_rate_2023:.2f}",
                    delta=f"{crime_rate_change:+.2f} from 2021",
                    delta_color="inverse",  # inverse because higher crime rate is worse
                    help="Organized Crime Index Score (0-10, higher = worse)"
                )
            else:
                st.metric(
                    "Crime Rate (OC Index)", 
                    f"{crime_rate_2023:.2f}",
                    delta="Same as 2021",
                    delta_color="off",
                    help="Organized Crime Index Score (0-10, higher = worse)"
                )
        else:
            st.metric(
                "Crime Rate (OC Index)", 
                f"{crime_rate_2023:.2f}",
                help="Organized Crime Index Score (0-10, higher = worse)"
            )
        
        # World Rank
        world_rank_2023 = int(indonesia_2023['World_Rank'])
        world_rank_2021 = int(indonesia_2021['World_Rank']) if indonesia_2021 is not None else None
        
        if world_rank_2021 is not None:
            rank_change = -(world_rank_2023 - world_rank_2021)  # Positive = worse (rank increased), Negative = better (rank decreased)
            if rank_change != 0:
                st.metric(
                    "World Rank", 
                    f"#{world_rank_2023}",
                    delta=f"{rank_change:+d} from 2021",
                    delta_color="inverse",  # inverse because lower rank is better
                    help="Global ranking among all countries (Lower Rank = Better)"
                )
            else:
                st.metric(
                    "World Rank", 
                    f"#{world_rank_2023}",
                    delta="Same as 2021",
                    delta_color="off",
                    help="Global ranking among all countries (Lower Rank = Better)"
                )
        else:
            st.metric(
                "World Rank", 
                f"#{world_rank_2023}",
                help="Global ranking among all countries (Lower Rank = Better)"
            )
        
        # Asia Rank
        asia_rank_2023 = int(indonesia_2023['Asia_Rank']) if pd.notna(indonesia_2023['Asia_Rank']) else None
        asia_rank_2021 = int(indonesia_2021['Asia_Rank']) if indonesia_2021 is not None and pd.notna(indonesia_2021['Asia_Rank']) else None
        
        if asia_rank_2023 is not None:
            if asia_rank_2021 is not None:
                asia_change = asia_rank_2023 - asia_rank_2021  # Positive = worse (rank increased), Negative = better (rank decreased)
                if asia_change != 0:
                    st.metric(
                        "Asia Rank", 
                        f"#{asia_rank_2023}",
                        delta=f"{asia_change:+d} from 2021",
                        delta_color="inverse",  # inverse because lower rank is better
                        help="Ranking among Asian countries (Lower Rank = Better)"
                    )
                else:
                    st.metric(
                        "Asia Rank", 
                        f"#{asia_rank_2023}",
                        delta="Same as 2021",
                        delta_color="off",
                        help="Ranking among Asian countries (Lower Rank = Better)"
                    )
            else:
                st.metric(
                    "Asia Rank", 
                    f"#{asia_rank_2023}",
                    help="Ranking among Asian countries (Lower Rank = Better)"
                )
        
        # ASEAN Rank
        asean_rank_2023 = int(indonesia_2023['ASEAN_Rank']) if pd.notna(indonesia_2023['ASEAN_Rank']) else None
        asean_rank_2021 = int(indonesia_2021['ASEAN_Rank']) if indonesia_2021 is not None and pd.notna(indonesia_2021['ASEAN_Rank']) else None
        
        if asean_rank_2023 is not None:
            if asean_rank_2021 is not None:
                asean_change = asean_rank_2023 - asean_rank_2021  # Positive = worse (rank increased), Negative = better (rank decreased)
                if asean_change != 0:
                    st.metric(
                        "ASEAN Rank", 
                        f"#{asean_rank_2023}",
                        delta=f"{asean_change:+d} from 2021",
                        delta_color="inverse",  # inverse because lower rank is better
                        help="Ranking among ASEAN countries (Lower Rank = Better)"
                    )
                else:
                    st.metric(
                        "ASEAN Rank", 
                        f"#{asean_rank_2023}",
                        delta="Same as 2021",
                        delta_color="off",
                        help="Ranking among ASEAN countries (Lower Rank = Better)"
                    )
            else:
                st.metric(
                    "ASEAN Rank", 
                    f"#{asean_rank_2023}",
                    help="Ranking among ASEAN countries (Lower Rank = Better)"
                )
    else:
        st.warning("OC Index data not available")

def render_bubble_and_relationship(df_filtered, selected_region, selected_province):
    st.subheader("Socioeconomic Relationships")
    col1, col2, col3 = st.columns(3)
    numeric_cols = [col for col in df_filtered.select_dtypes(include=[np.number]).columns if col != 'Provinsi']
    with col1:
        x_axis = st.selectbox("X-axis:", numeric_cols, index=numeric_cols.index('Pendapatan Agustus') if 'Pendapatan Agustus' in numeric_cols else 0)
    with col2:
        y_axis = st.selectbox("Y-axis:", numeric_cols, index=numeric_cols.index('Pendidikan Terakhir SMA/PT') if 'Pendidikan Terakhir SMA/PT' in numeric_cols else 1)
    with col3:
        size_axis = st.selectbox("Bubble size:", numeric_cols, index=numeric_cols.index('Tindak Pidana 2023') if 'Tindak Pidana 2023' in numeric_cols else 2)
    if len(numeric_cols) >= 3:
        bubble_fig = create_bubble_chart(
            df_filtered, x_axis, y_axis, size_axis, 
            title=f"{y_axis} vs {x_axis} (Bubble size: {size_axis})",
            region_filter=selected_region,
            province_filter=selected_province
        )
        st.plotly_chart(bubble_fig, use_container_width=True)
    if len(numeric_cols) >= 2:
        st.subheader("Relationship Analysis")
        col1, col2 = st.columns(2)
        with col1:
            if 'Pendidikan Terakhir SMA/PT' in df_filtered.columns and 'Tindak Pidana 2023' in df_filtered.columns:
                color_col = 'Provinsi' if selected_province != 'All' or selected_region != 'All' else 'Region'
                fig1 = px.scatter(
                    df_filtered, 
                    x='Pendidikan Terakhir SMA/PT', 
                    y='Tindak Pidana 2023',
                    color=color_col,
                    hover_name='Provinsi',
                    title="Education vs Crime Rate",
                    trendline="ols"
                )
                fig1.update_layout(
                    plot_bgcolor='#25262d',
                    paper_bgcolor='#25262d',
                    font_color='white',
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig1, use_container_width=True)
        with col2:
            if 'gini_ratio_2023' in df_filtered.columns and 'Tindak Pidana 2023' in df_filtered.columns:
                color_col = 'Provinsi' if selected_province != 'All' or selected_region != 'All' else 'Region'
                fig2 = px.scatter(
                    df_filtered, 
                    x='gini_ratio_2023', 
                    y='Tindak Pidana 2023',
                    color=color_col,
                    hover_name='Provinsi',
                    title="Income Inequality vs Crime Rate",
                    trendline="ols"
                )
                fig2.update_layout(
                    plot_bgcolor='#25262d',
                    paper_bgcolor='#25262d',
                    font_color='white',
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig2, use_container_width=True)

def render_correlation_tab(df_filtered):
    st.subheader("Correlation Analysis")
    corr_fig = create_correlation_heatmap(df_filtered)
    if corr_fig:
        st.plotly_chart(corr_fig, use_container_width=True)

def render_trend_tab(df_time_series, df_filtered):
    st.subheader("Time Series Analysis")
    trend_fig = create_trend_chart(df_time_series)
    if trend_fig:
        st.plotly_chart(trend_fig, use_container_width=True)
    else:
        st.info("Time series data not available or incomplete.")
    if df_time_series is not None and not df_time_series.empty:
        st.subheader("Crime Rate by Province (2021-2023)")
        provinces_sample = df_filtered['Provinsi'].head(10).tolist()
        if 'Tindak Pidana 2021' in df_filtered.columns:
            crime_data = df_filtered[df_filtered['Provinsi'].isin(provinces_sample)]
            crime_cols = ['Tindak Pidana 2021', 'Tindak Pidana 2022', 'Tindak Pidana 2023']
            available_crime_cols = [col for col in crime_cols if col in crime_data.columns]
            if available_crime_cols:
                melted_data = crime_data.melt(
                    id_vars=['Provinsi', 'Region'],
                    value_vars=available_crime_cols,
                    var_name='Year',
                    value_name='Crime_Rate'
                )
                melted_data['Year'] = melted_data['Year'].str.extract(r'(\d{4})').astype(int)
                fig_trend = px.line(
                    melted_data,
                    x='Year',
                    y='Crime_Rate',
                    color='Provinsi',
                    title="Crime Rate Trends by Province (2021-2023)",
                    markers=True
                )
                fig_trend.update_xaxes(dtick=1, tickformat="d")
                fig_trend.update_yaxes(title_text="Crime Rate")
                fig_trend.update_layout(
                    plot_bgcolor='#25262d',
                    paper_bgcolor='#25262d',
                    font_color='white',
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig_trend, use_container_width=True)

def render_regional_tab(df_filtered, selected_region, selected_province):
    st.subheader("Regional Analysis & Choropleth Map")
    regional_stats = create_regional_comparison(df_filtered)
    if regional_stats is not None:
        st.subheader("Average Values by Region")
        st.dataframe(regional_stats)
        if 'Tindak Pidana 2023' in regional_stats.columns:
            fig_regional = px.bar(
                x=regional_stats.index,
                y=regional_stats['Tindak Pidana 2023'],
                title="Average Crime Rate by Region (2023)",
                labels={'x': 'Region', 'y': 'Crime Rate'}
            )
            fig_regional.update_layout(
                plot_bgcolor='#25262d',
                paper_bgcolor='#25262d',
                font_color='white',
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_regional, use_container_width=True)
    st.markdown("---")
    render_choropleth_section(df_filtered, selected_region, selected_province)

def render_choropleth_section(df_filtered, selected_region, selected_province):
    st.subheader("Interactive Choropleth Map")
    geojson_data = load_geojson()
    province_mapping = create_province_mapping()
    metric_options = ['Crime Rate 2023', 'Population', 'Gini Ratio', 'Income']
    # Use selectbox with no key and default index=0 for proper interactivity and default rendering
    selected_metric = st.selectbox(
        "Select Metric to Visualize:",
        metric_options,
        index=0
    )
    if geojson_data and province_mapping:
        with st.spinner("Creating choropleth map..."):
            folium_map = create_choropleth_map(
                df_filtered, selected_metric, geojson_data, province_mapping,
                region_filter=selected_region, province_filter=selected_province
            )
        st_folium(folium_map, width=700, height=500)
        if selected_metric == 'Crime Rate 2023':
            st.info("🔍 **Map Interpretation**: Darker red areas indicate higher crime rates per 100,000 population.")
        elif selected_metric == 'Population':
            st.info("🔍 **Map Interpretation**: Darker red areas indicate higher population density.")
        elif selected_metric == 'Gini Ratio':
            st.info("🔍 **Map Interpretation**: Darker red areas indicate higher income inequality (Gini ratio closer to 1).")
        elif selected_metric == 'Income':
            st.info("🔍 **Map Interpretation**: Darker red areas indicate higher average income levels.")
    else:
        st.warning("GeoJSON or province mapping not loaded.")

def render_provincial_data_table(df_filtered):
    st.subheader("Detailed Provincial Data")
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

def main():
    # st.title("🇮🇩 Indonesia Socioeconomic Dashboard")
    # st.markdown("### Interactive Analysis of Provincial Data (2023)")
    
    # Load data
    with st.spinner("Loading and processing data..."):
        df_main, df_time_series = load_and_process_data()
        oc_data = load_oc_index_data()
    
    if df_main is None or df_main.empty:
        st.error("Failed to load data. Please check your dataset files.")
        return
    
    # Exclude 'INDONESIA' from all dataframes at the start of main analysis
    if 'Provinsi' in df_main.columns:
        df_main = df_main[df_main['Provinsi'] != 'INDONESIA']
    
    # Sidebar for filters and controls
    st.sidebar.header("Indonesia Criminality")
    
    # Initialize filter variables
    selected_region = 'All'
    selected_province = 'All'
    
    # Region filter
    if 'Region' in df_main.columns:
        regions = ['All'] + sorted(df_main['Region'].dropna().unique().tolist())
        selected_region = st.sidebar.selectbox("Select Region:", regions)
        if selected_region != 'All':
            df_filtered = df_main[df_main['Region'] == selected_region]
        else:
            df_filtered = df_main
    else:
        df_filtered = df_main
    
    # Province filter
    if 'Provinsi' in df_filtered.columns:
        available_provinces = df_filtered['Provinsi'].dropna().unique().tolist()
        provinces = ['All'] + sorted(available_provinces)
        selected_province = st.sidebar.selectbox("Select Province:", provinces)
        if selected_province != 'All':
            df_filtered = df_filtered[df_filtered['Provinsi'] == selected_province]
    
    # Display active filters
    st.sidebar.markdown("---")
    st.sidebar.subheader("Active Filters")
    if 'Region' in df_main.columns and selected_region != 'All':
        st.sidebar.write(f"🌍 **Region:** {selected_region}")
    if 'Provinsi' in df_main.columns and selected_province != 'All':
        st.sidebar.write(f"📍 **Province:** {selected_province}")
    if (selected_region == 'All' and selected_province == 'All'):
        st.sidebar.write("🌐 Showing all data")
    
    # Show number of provinces in current selection
    num_provinces = len(df_filtered['Provinsi'].unique()) if 'Provinsi' in df_filtered.columns else 0
    st.sidebar.write(f"📊 **Provinces shown:** {num_provinces}")
    
    # Create main layout with metrics column and content column
    metrics_col, content_col = st.columns([1, 4])
    
    # Key metrics in the left column (next to sidebar)
    with metrics_col:
        render_key_metrics(df_filtered, selected_province, oc_data)
    
    # Main dashboard content in the right column
    with content_col:
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Main Analysis", "🔗 Correlations", "📈 Trends", "🗺️ Regional View"])
        
        with tab1:
            render_bubble_and_relationship(df_filtered, selected_region, selected_province)
        
        with tab2:
            render_correlation_tab(df_filtered)
        
        with tab3:
            render_trend_tab(df_time_series, df_filtered)
        
        with tab4:
            render_regional_tab(df_filtered, selected_region, selected_province)
    
    st.markdown("---")
    render_provincial_data_table(df_filtered)

if __name__ == "__main__":
    main()
