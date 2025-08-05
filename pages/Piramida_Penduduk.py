import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

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
            age_groups = ["0_4", "5_9", "10_14", "15_19", "20_24", "25_29", "30_34", "35_39", "40_44", "45_49", "50_54", "55_59", "60_64", "65_69", "70_74", "75_plus"]
            male_data = [data[f"l_{age}"] for age in age_groups]
            female_data = [data[f"p_{age}"] for age in age_groups]
            
            # Creating the DataFrame
            df = pd.DataFrame({
                "umur": age_groups,
                "laki-laki": male_data,
                "perempuan": female_data
            })
            
            # Mengonversi data menjadi DataFrame
            df3 = pd.DataFrame([data])
            
            df4 = df3.T
            tanggal = df3['last_update']
            st.success(f"Jumlah Penduduk {pilihandesa}, Tanggal {tanggal}")
            
            st.dataframe(df, hide_index=True)
            
            df['laki-laki'] = df['laki-laki'] * -1
            
            fig = px.bar(df, x=['laki-laki', 'perempuan'], y='umur', labels={'variable':''},
                             orientation='h', color_discrete_map={'laki-laki':'brown', 'perempuan':'orange'})
            
            # Menempatkan legenda di bawah tengah
            fig.update_layout(
                xaxis_title="",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                )
            )
            st.info(f"Piramida Penduduk")
            st.plotly_chart(fig)
            
            st.dataframe(df4, hide_index=False)
        except ValueError:
            st.error("Tidak dapat mengonversi respons menjadi JSON.")
    else:
        st.error(f"Data Belum Tersedia")
        
    url2 = f"https://sid.kemendesa.go.id/sdgs/searching/score-sdgs?location_code=&province_id=32&city_id={kabterpilih}&district_id={kecterpilih}&village_id={desaterpilih}"
    
    response2 = requests.get(url2)