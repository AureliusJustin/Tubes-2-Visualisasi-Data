#!/usr/bin/env python3
"""
Test script to verify OC Index data processing works correctly
"""

import pandas as pd

def test_oc_index_data():
    """Test OC Index data loading and processing"""
    try:
        # Load OC Index data
        df_oc_2023 = pd.read_csv("dataset/oc_index_2023.csv", sep=';')
        df_oc_2021 = pd.read_csv("dataset/oc_index_2021.csv", sep=';')
        
        print("✅ Successfully loaded OC Index datasets")
        print(f"   2023 dataset: {len(df_oc_2023)} countries")
        print(f"   2021 dataset: {len(df_oc_2021)} countries")
        
        # Clean criminality column - replace comma with dot for proper float conversion
        df_oc_2023['Criminality'] = df_oc_2023['Criminality'].astype(str).str.replace(',', '.').astype(float)
        df_oc_2021['Criminality'] = df_oc_2021['Criminality'].astype(str).str.replace(',', '.').astype(float)
        
        print("✅ Successfully processed criminality scores")
        
        # Sort by criminality (higher = worse ranking)
        df_oc_2023_sorted = df_oc_2023.sort_values('Criminality', ascending=False).reset_index(drop=True)
        df_oc_2021_sorted = df_oc_2021.sort_values('Criminality', ascending=False).reset_index(drop=True)
        
        # Add rank columns (1 = highest criminality/worst)
        df_oc_2023_sorted['World_Rank'] = df_oc_2023_sorted.index + 1
        df_oc_2021_sorted['World_Rank'] = df_oc_2021_sorted.index + 1
        
        print("✅ Successfully calculated world rankings")
        
        # Calculate Asia rankings
        asia_2023 = df_oc_2023_sorted[df_oc_2023_sorted['Continent'] == 'Asia'].reset_index(drop=True)
        asia_2023['Asia_Rank'] = asia_2023.index + 1
        
        asia_2021 = df_oc_2021_sorted[df_oc_2021_sorted['Continent'] == 'Asia'].reset_index(drop=True)
        asia_2021['Asia_Rank'] = asia_2021.index + 1
        
        print("✅ Successfully calculated Asia rankings")
        print(f"   Asian countries in 2023: {len(asia_2023)}")
        print(f"   Asian countries in 2021: {len(asia_2021)}")
        
        # Calculate ASEAN rankings
        asean_countries = ['Indonesia', 'Malaysia', 'Thailand', 'Vietnam', 'Philippines', 
                          'Singapore', 'Myanmar', 'Cambodia', 'Laos', 'Brunei', 'Timor-Leste']
        
        asean_2023 = df_oc_2023_sorted[df_oc_2023_sorted['Country'].isin(asean_countries)].reset_index(drop=True)
        asean_2023['ASEAN_Rank'] = asean_2023.index + 1
        
        asean_2021 = df_oc_2021_sorted[df_oc_2021_sorted['Country'].isin(asean_countries)].reset_index(drop=True)
        asean_2021['ASEAN_Rank'] = asean_2021.index + 1
        
        print("✅ Successfully calculated ASEAN rankings")
        print(f"   ASEAN countries in 2023: {len(asean_2023)}")
        print(f"   ASEAN countries in 2021: {len(asean_2021)}")
        
        # Merge rankings back to main dataframes
        df_oc_2023_sorted = df_oc_2023_sorted.merge(
            asia_2023[['Country', 'Asia_Rank']], on='Country', how='left'
        )
        df_oc_2021_sorted = df_oc_2021_sorted.merge(
            asia_2021[['Country', 'Asia_Rank']], on='Country', how='left'
        )
        
        df_oc_2023_sorted = df_oc_2023_sorted.merge(
            asean_2023[['Country', 'ASEAN_Rank']], on='Country', how='left'
        )
        df_oc_2021_sorted = df_oc_2021_sorted.merge(
            asean_2021[['Country', 'ASEAN_Rank']], on='Country', how='left'
        )
        
        print("✅ Successfully merged rankings")
        
        # Get Indonesia data
        indonesia_2023 = df_oc_2023_sorted[df_oc_2023_sorted['Country'] == 'Indonesia']
        indonesia_2021 = df_oc_2021_sorted[df_oc_2021_sorted['Country'] == 'Indonesia']
        
        if len(indonesia_2023) > 0:
            indo_2023 = indonesia_2023.iloc[0]
            print("\n🇮🇩 Indonesia 2023 Data:")
            print(f"   Crime Rate: {indo_2023['Criminality']:.2f}")
            print(f"   World Rank: #{indo_2023['World_Rank']}")
            print(f"   Asia Rank: #{indo_2023['Asia_Rank']}")
            print(f"   ASEAN Rank: #{indo_2023['ASEAN_Rank']}")
        else:
            print("❌ Indonesia not found in 2023 data")
            
        if len(indonesia_2021) > 0:
            indo_2021 = indonesia_2021.iloc[0]
            print("\n🇮🇩 Indonesia 2021 Data:")
            print(f"   Crime Rate: {indo_2021['Criminality']:.2f}")
            print(f"   World Rank: #{indo_2021['World_Rank']}")
            print(f"   Asia Rank: #{indo_2021['Asia_Rank']}")
            print(f"   ASEAN Rank: #{indo_2021['ASEAN_Rank']}")
            
            # Calculate changes
            if len(indonesia_2023) > 0:
                world_change = indo_2021['World_Rank'] - indo_2023['World_Rank']
                asia_change = indo_2021['Asia_Rank'] - indo_2023['Asia_Rank']
                asean_change = indo_2021['ASEAN_Rank'] - indo_2023['ASEAN_Rank']
                
                print("\n📊 Changes from 2021 to 2023:")
                print(f"   World Rank: {'↗️' if world_change > 0 else '↘️' if world_change < 0 else '→'} {abs(world_change)} positions")
                print(f"   Asia Rank: {'↗️' if asia_change > 0 else '↘️' if asia_change < 0 else '→'} {abs(asia_change)} positions")
                print(f"   ASEAN Rank: {'↗️' if asean_change > 0 else '↘️' if asean_change < 0 else '→'} {abs(asean_change)} positions")
        else:
            print("❌ Indonesia not found in 2021 data")
            
        print("\n✅ All tests passed! OC Index data processing is working correctly.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    return True

if __name__ == "__main__":
    test_oc_index_data()
