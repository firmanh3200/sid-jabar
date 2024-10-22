import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Ambil tanggal hari ini
tanggal_hari_ini = datetime.now().strftime("%d-%m-%Y")

st.title("Skor SDG's Desa")
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
    url2 = f"https://sid.kemendesa.go.id/sdgs/searching/score-sdgs?location_code=&province_id=32&city_id={kabterpilih}&district_id={kecterpilih}&village_id={desaterpilih}"
    
    response2 = requests.get(url2)
    
    if response2.status_code == 200:
        try:
            data = response2.json()
            # Mengambil hanya goals, title, dan score
            filtered_data = [{"goals": item["goals"], "title": item["title"], "score": item["score"]} for item in data["data"]]
            # Mengonversi data menjadi DataFrame
            df = pd.DataFrame(filtered_data)
            
            st.success(f"Skor SDGs {pilihandesa}")
            st.dataframe(df, use_container_width=True, hide_index=True)
        except ValueError:
            st.error("Tidak dapat mengonversi respons menjadi JSON.")
    else:
        st.error(f"Data Belum Tersedia")