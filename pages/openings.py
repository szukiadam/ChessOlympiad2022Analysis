import streamlit as st
from src.helpers import load_data

df = load_data()

openings = set(df["opening"].to_list())

st.markdown("# Page 2 ❄️")
st.sidebar.markdown("# Page 2 ❄️")

opening = st.selectbox("Choose a player!", openings)
st.write(df[df["opening"] == opening])
