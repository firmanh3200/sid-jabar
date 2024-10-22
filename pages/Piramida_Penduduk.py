import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px

# Ambil tanggal hari ini
tanggal_hari_ini = datetime.now().strftime("%d-%m-%Y")

st.title("Piramida Penduduk")
st.warning(f"Sumber: https://sid.kemendesa.go.id/profile, Kondisi: {tanggal_hari_ini}")
st.subheader("", divider='green')

mfd = pd.read_csv('data/mfd_23_1_32.csv', dtype={'kdkab':'str', 'kdkec':'str', 'iddesa':'str'})
mfd['idkab'] = '32' + mfd['kdkab']
mfd['idkec'] = mfd['idkab'] + mfd['kdkec']

datakab = mfd['idkab'].unique().tolist()
kabterpilih = st.selectbox("Filter ID Kabupaten/Kota", datakab, key='idkab')

if kabterpilih:

    # URL data
    url = f"https://sid.kemendesa.go.id/region/selected?code={kabterpilih}&param=district"

    # Mengambil data dari URL
    response = requests.get(url)
    data = response.json()

    # Mengonversi data menjadi DataFrame
    df = pd.DataFrame(data)
    df = df.sort_values(by='kdkecamatan')
    
    st.dataframe(df, use_container_width=True, hide_index=True)

datakec = st.selectbox("Filter Kecamatan", df['nmkecamatan_kemendesa'])
kecterpilih = df.loc[df['nmkecamatan_kemendesa'] == datakec, 'kdkecamatan'].values[0]

if kecterpilih:
    # URL data
    url = f"https://sid.kemendesa.go.id/region/selected?code={kecterpilih}&param=village"

    # Mengambil data dari URL
    response = requests.get(url)
    data = response.json()

    # Mengonversi data menjadi DataFrame
    df2 = pd.DataFrame(data)
    df2 = df2.sort_values(by='kddesa')
    
    st.dataframe(df2, use_container_width=True, hide_index=True)

pilihandesa = st.selectbox("Filter Desa", df2['nmdesa_kemendesa'])
desaterpilih = df2.loc[df2['nmdesa_kemendesa'] == pilihandesa, 'kddesa'].values[0]

if pilihandesa:
   # URL data
    url = f"https://sid.kemendesa.go.id/population-statistic/data?location_code=&province_id=32&city_id={kabterpilih}&district_id={kecterpilih}&village_id={desaterpilih}&on=population"

    # Mengambil data dari URL
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            data = response.json()
            
            # Extracting the required data
            age_groups = ["0_4", "5_9", "10_14", "15_19", "20_24", 
                          "25_29", "30_34", "35_39", "40_44", "45_49", 
                          "50_54", "55_59", "60_64", "65_69", "70_74", "75_plus"]
            male_data = [-data[f"l_{age}"] for age in age_groups]
            female_data = [data[f"p_{age}"] for age in age_groups]
            
            # Extracting the required data
            age_groups2 = ["0_4", "5_9", "10_14", "15_19", "20_24", 
                          "25_29", "30_34", "35_39", "40_44", "45_49", 
                          "50_54", "55_59", "60_64", "65_69", "70_74", "75_plus"]
            male_data2 = [data[f"l_{age}"] for age in age_groups]
            female_data2 = [data[f"p_{age}"] for age in age_groups]
            
            # Creating the DataFrame
            df5 = pd.DataFrame({
                "umur": age_groups,
                "laki-laki": male_data,
                "perempuan": female_data
            })
            
            # Creating the DataFrame
            df6 = pd.DataFrame({
                "umur": age_groups2,
                "laki-laki": male_data2,
                "perempuan": female_data2
            })
            
            # Mengonversi data menjadi DataFrame
            df3 = pd.DataFrame([data])
            variabel = ['total_data', 'gender_men', 'gender_women', 'belum_kawin', 
                        'kawin', 'cerai_hidup', 'cerai_mati', 'wni', 'wna', 'last_update']
            df4 = df3[variabel]
            df4 = df4.rename(columns={'total_data':'Jumlah Penduduk', 
                                      'gender_men':'Laki-laki',
                                      'gender_women':'Perempuan',
                                      'last_update':'Pemutakhiran Data'})
            st.success(f"Jumlah Penduduk {pilihandesa}")
            
            kolom1, kolom2 = st.columns([3,2])
            with kolom1:
                # Membuat piramida penduduk
                fig = px.bar(df5,
                            x=['laki-laki', 'perempuan'],
                            y='umur',
                            orientation='h',
                            title='Piramida Penduduk',
                            labels={'value': 'Jumlah', 'umur': 'Umur'},
                            barmode='relative')
                
                st.plotly_chart(fig, use_container_width=True)
                
            with kolom2:
                st.dataframe(df6, hide_index=True, use_container_width=True)
                        
            st.dataframe(df4, hide_index=True, use_container_width=True)
        except ValueError:
            st.error("Tidak dapat mengonversi respons menjadi JSON.")
    else:
        st.error(f"Data Belum Tersedia")
    
    
        