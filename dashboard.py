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
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e1e5e9;
    }
    .plot-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
        df_jumlah_penduduk = pd.read_csv("dataset/Penduduk, Laju Pertumbuhan Penduduk, Distribusi Persentase Penduduk, Kepadatan Penduduk, Rasio Jenis Kelamin Penduduk Menurut Provinsi, 2023 - Penduduk, Laju Pertumbuhan Penduduk, Distribusi Persentase Penduduk, Kepadatan Penduduk, Rasio Je.csv")
        
        # Load crime data
        df_tindak_pidana_2021_2023 = pd.read_csv("dataset/Risiko Penduduk Terkena Tindak Pidana (Per 100.000 Penduduk) , 2021-2023.csv")
        df_tindak_pidana_2018_2020 = pd.read_csv("dataset/Risiko Penduduk Terkena Tindak Pidana (Per 100.000 Penduduk) , 2018-2020.csv")
        df_tindak_pidana_2015_2017 = pd.read_csv("dataset/Risiko Penduduk Terkena Tindak Pidana (Per 100.000 Penduduk) , 2015-2017.csv")
        df_tindak_pidana_2012_2014 = pd.read_csv("dataset/Risiko Penduduk Terkena Tindak Pidana (Per 100.000 Penduduk) , 2012-2014.csv")
        
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
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv')
    return df

# Load geojson data function
@st.cache_data
def load_geojson():
    """Load Indonesia provinces geojson data"""
    with open('map/indonesia-prov.geojson', 'r') as f:
        geojson_data = json.load(f)
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

def create_bubble_chart(df, x_col, y_col, size_col, color_col=None, title="Bubble Chart"):
    """Create an interactive bubble chart using Plotly"""
    
    if color_col and color_col in df.columns:
        fig = px.scatter(
            df, 
            x=x_col, 
            y=y_col, 
            size=size_col,
            color=color_col,
            hover_name="Provinsi",
            hover_data={"Region": True},
            title=title,
            size_max=60
        )
    else:
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
        hovermode='closest'
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
        
        fig.update_layout(height=600)
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
                        yaxis_title="Crime Rate (per 100,000 population)"
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

def create_choropleth_map(df, metric, geojson_data, province_mapping):
    """Create a choropleth map using folium"""
    
    # Prepare data based on selected metric
    if metric == 'Crime Rate 2023':
        map_data = df[['Provinsi', 'Tindak Pidana 2023']].dropna()
        metric_col = 'Tindak Pidana 2023'
        title = 'Crime Rate per 100,000 Population (2023)'
    elif metric == 'Population':
        map_data = df[['Provinsi', 'Jumlah Penduduk']].dropna()
        metric_col = 'Jumlah Penduduk'
        title = 'Population by Province (thousands)'
    elif metric == 'Gini Ratio':
        map_data = df[['Provinsi', 'gini_ratio_2023']].dropna()
        metric_col = 'gini_ratio_2023'
        title = 'Gini Ratio by Province (2023)'
    elif metric == 'Income':
        map_data = df[['Provinsi', 'Pendapatan Agustus']].dropna()
        metric_col = 'Pendapatan Agustus'
        title = 'Average Income by Province (August 2023)'
    else:
        # Default to crime rate
        map_data = df[['Provinsi', 'Tindak Pidana 2023']].dropna()
        metric_col = 'Tindak Pidana 2023'
        title = 'Crime Rate per 100,000 Population (2023)'
    
    # Create reverse mapping for geojson (CSV province name -> GeoJSON province name)
    reverse_mapping = {v: k for k, v in province_mapping.items()}
    
    # Create a map centered on Indonesia
    m = folium.Map(
        location=[-2.5, 118.0],  # Center of Indonesia
        zoom_start=5,
        tiles='CartoDB positron'
    )
    
    # Create color scale
    if len(map_data) > 0:
        min_val = map_data[metric_col].min()
        max_val = map_data[metric_col].max()
        
        # Create a colormap
        colormap = cm.LinearColormap(
            colors=['#ffffcc', '#ff4444'],
            vmin=min_val,
            vmax=max_val
        )
        
        # Create a dictionary for the choropleth
        province_data = {}
        for _, row in map_data.iterrows():
            geojson_name = reverse_mapping.get(row['Provinsi'])
            if geojson_name:
                province_data[geojson_name] = row[metric_col]
        
        # Add choropleth layer
        folium.GeoJson(
            geojson_data,
            style_function=lambda feature: {
                'fillColor': colormap(province_data.get(feature['properties']['Propinsi'], min_val)),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7,
            },
            tooltip=folium.features.GeoJsonTooltip(
                fields=['Propinsi'],
                aliases=['Province:'],
                localize=True
            ),
            popup=folium.features.GeoJsonPopup(
                fields=['Propinsi'],
                aliases=['Province:'],
                localize=True
            )
        ).add_to(m)
        
        # Add colormap to map
        colormap.caption = title
        colormap.add_to(m)
    
    return m

def main():
    st.title("🇮🇩 Indonesia Socioeconomic Dashboard")
    st.markdown("### Interactive Analysis of Provincial Data (2023)")
    
    # Load data
    with st.spinner("Loading and processing data..."):
        df_main, df_time_series = load_and_process_data()
    
    if df_main is None or df_main.empty:
        st.error("Failed to load data. Please check your dataset files.")
        return
    
    # Sidebar for filters and controls
    st.sidebar.header("Dashboard Controls")
    
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
    
    # Main dashboard layout
    col1, col2, col3, col4 = st.columns(4)
    
    # Key metrics
    with col1:
        if 'Jumlah Penduduk' in df_filtered.columns:
            total_pop = df_filtered['Jumlah Penduduk'].sum()
            st.metric("Total Population (thousands)", f"{total_pop:,.0f}")
    
    with col2:
        if 'Tindak Pidana 2023' in df_filtered.columns:
            avg_crime = df_filtered['Tindak Pidana 2023'].mean()
            st.metric("Avg Crime Rate", f"{avg_crime:.1f}")
    
    with col3:
        if 'gini_ratio_2023' in df_filtered.columns:
            avg_gini = df_filtered['gini_ratio_2023'].mean()
            st.metric("Avg Gini Ratio", f"{avg_gini:.3f}")
    
    with col4:
        if 'Pendidikan Terakhir SMA/PT' in df_filtered.columns:
            avg_education = df_filtered['Pendidikan Terakhir SMA/PT'].mean()
            st.metric("Avg Higher Education %", f"{avg_education:.1f}%")
    
    st.markdown("---")
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Main Analysis", "🔗 Correlations", "📈 Trends", "🗺️ Regional View"])
    
    with tab1:
        st.subheader("Socioeconomic Relationships")
        
        # Bubble chart controls
        col1, col2, col3 = st.columns(3)
        
        numeric_cols = [col for col in df_filtered.select_dtypes(include=[np.number]).columns 
                       if col != 'Provinsi']
        
        with col1:
            x_axis = st.selectbox("X-axis:", numeric_cols, 
                                index=numeric_cols.index('Pendapatan Agustus') if 'Pendapatan Agustus' in numeric_cols else 0)
        
        with col2:
            y_axis = st.selectbox("Y-axis:", numeric_cols, 
                                index=numeric_cols.index('Pendidikan Terakhir SMA/PT') if 'Pendidikan Terakhir SMA/PT' in numeric_cols else 1)
        
        with col3:
            size_axis = st.selectbox("Bubble size:", numeric_cols, 
                                   index=numeric_cols.index('Tindak Pidana 2023') if 'Tindak Pidana 2023' in numeric_cols else 2)
        
        # Create and display bubble chart
        if len(numeric_cols) >= 3:
            bubble_fig = create_bubble_chart(
                df_filtered, x_axis, y_axis, size_axis, 
                title=f"{y_axis} vs {x_axis} (Bubble size: {size_axis})"
            )
            st.plotly_chart(bubble_fig, use_container_width=True)
        
        # Scatter plot with regression line
        if len(numeric_cols) >= 2:
            st.subheader("Relationship Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Pendidikan Terakhir SMA/PT' in df_filtered.columns and 'Tindak Pidana 2023' in df_filtered.columns:
                    fig1 = px.scatter(
                        df_filtered, 
                        x='Pendidikan Terakhir SMA/PT', 
                        y='Tindak Pidana 2023',
                        color='Region',
                        hover_name='Provinsi',
                        title="Education vs Crime Rate",
                        trendline="ols"
                    )
                    st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                if 'gini_ratio_2023' in df_filtered.columns and 'Tindak Pidana 2023' in df_filtered.columns:
                    fig2 = px.scatter(
                        df_filtered, 
                        x='gini_ratio_2023', 
                        y='Tindak Pidana 2023',
                        color='Region',
                        hover_name='Provinsi',
                        title="Income Inequality vs Crime Rate",
                        trendline="ols"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        st.subheader("Correlation Analysis")
        
        # Correlation heatmap
        corr_fig = create_correlation_heatmap(df_filtered)
        if corr_fig:
            st.plotly_chart(corr_fig, use_container_width=True)
        
        # Correlation table
        numeric_cols = df_filtered.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            st.subheader("Correlation Coefficients")
            corr_matrix = df_filtered[numeric_cols].corr()
            st.dataframe(corr_matrix.style.background_gradient(cmap='RdBu'))
    
    with tab3:
        st.subheader("Time Series Analysis")
        
        # Crime trend chart
        trend_fig = create_trend_chart(df_time_series)
        if trend_fig:
            st.plotly_chart(trend_fig, use_container_width=True)
        else:
            st.info("Time series data not available or incomplete.")
        
        # Crime data by province over time
        if df_time_series is not None and not df_time_series.empty:
            st.subheader("Crime Rate by Province (2021-2023)")
            
            # Prepare data for line chart
            provinces_sample = df_filtered['Provinsi'].head(10).tolist()  # Show top 10 provinces
            
            if 'Tindak Pidana 2021' in df_filtered.columns:
                crime_data = df_filtered[df_filtered['Provinsi'].isin(provinces_sample)]
                
                # Melt data for line chart
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
                    
                    st.plotly_chart(fig_trend, use_container_width=True)
    
    with tab4:
        st.subheader("Regional Analysis & Choropleth Map")
        
        # Regional statistics
        regional_stats = create_regional_comparison(df_filtered)
        if regional_stats is not None:
            st.subheader("Average Values by Region")
            st.dataframe(regional_stats)
            
            # Bar chart of regional averages
            if 'Tindak Pidana 2023' in regional_stats.columns:
                fig_regional = px.bar(
                    x=regional_stats.index,
                    y=regional_stats['Tindak Pidana 2023'],
                    title="Average Crime Rate by Region (2023)",
                    labels={'x': 'Region', 'y': 'Crime Rate'}
                )
                st.plotly_chart(fig_regional, use_container_width=True)
        
        st.markdown("---")
        
        # Choropleth map section
        st.subheader("Interactive Choropleth Map")
        
        # Load geojson data
        try:
            geojson_data = load_geojson()
            province_mapping = create_province_mapping()
            
            # Metric selection
            metric_options = ['Crime Rate 2023', 'Population', 'Gini Ratio', 'Income']
            selected_metric = st.selectbox("Select Metric to Visualize:", metric_options)
            
            # Create and display choropleth map
            if selected_metric and geojson_data and province_mapping:
                with st.spinner("Creating choropleth map..."):
                    folium_map = create_choropleth_map(df_filtered, selected_metric, geojson_data, province_mapping)
                    
                    # Display the map
                    map_data = st_folium(folium_map, width=700, height=500)
                
                # Show interpretation
                if selected_metric == 'Crime Rate 2023':
                    st.info("🔍 **Map Interpretation**: Darker red areas indicate higher crime rates per 100,000 population.")
                elif selected_metric == 'Population':
                    st.info("🔍 **Map Interpretation**: Darker red areas indicate higher population density.")
                elif selected_metric == 'Gini Ratio':
                    st.info("🔍 **Map Interpretation**: Darker red areas indicate higher income inequality (Gini ratio closer to 1).")
                elif selected_metric == 'Income':
                    st.info("🔍 **Map Interpretation**: Darker red areas indicate higher average income levels.")
            
        except Exception as e:
            st.error(f"Error loading map data: {str(e)}")
            st.info("Please ensure the GeoJSON file is available in the map/ directory.")
        
        st.markdown("---")
        
        # Data table
        st.subheader("Detailed Provincial Data")
        st.dataframe(df_filtered, use_container_width=True)

if __name__ == "__main__":
    main()
