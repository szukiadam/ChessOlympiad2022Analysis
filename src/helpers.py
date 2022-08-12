import streamlit as st
import pandas as pd
import numpy as np


@st.cache
def load_data():
    df = pd.read_csv("olympiad2022.csv")
    df = df[df["result"] != "0-0"]
    df["moves"] = df["moves"].astype(str)
    df["moves_length"] = df["moves"].apply(lambda x: len(x))
    df = df[df["moves_length"] > 20]

    df["round"] = df["round"].astype(str)
    df[["round", "board"]] = df["round"].str.split(".", 1, expand=True)
    df[["whiteelo", "blackelo"]] = (
        df[["whiteelo", "blackelo"]].replace("-", 0).astype(int)
    )
    df["elo_difference"] = df["whiteelo"] - df["blackelo"]

    # Transform input data
    df["white_score"] = df["result"].apply(
        lambda x: 1 if x == "1-0" else (0.5 if x == "1/2-1/2" else 0)
    )
    df["black_score"] = df["result"].apply(
        lambda x: 0 if x == "1-0" else (0.5 if x == "1/2-1/2" else 1)
    )

    lowercase = lambda x: str(x).lower()
    df.rename(lowercase, axis="columns", inplace=True)
    return df
