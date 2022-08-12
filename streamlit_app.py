import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import streamlit.components.v1 as components
from src.helpers import load_data
from src.plots import *

st.title("Chess Olympiad 2022")


@st.cache
def calculate_points_per_player(df):
    white_points = df.groupby("white", as_index=False).agg(
        {"white_score": ["sum", "count"]}
    )
    white_points.columns = list(map("_".join, white_points.columns.values))
    white_points = white_points.rename(
        columns={
            "white_": "player_name",
            "white_score_sum": "white_points",
            "white_score_count": "white_games",
        }
    )

    black_points = df.groupby("black", as_index=False).agg(
        {"black_score": ["sum", "count"]}
    )
    black_points.columns = list(map("_".join, black_points.columns.values))
    black_points = black_points.rename(
        columns={
            "black_": "player_name",
            "black_score_sum": "black_points",
            "black_score_count": "black_games",
        }
    )

    merged_points = pd.merge(white_points, black_points, how="outer", on="player_name")
    merged_points["total_points"] = (
        merged_points["white_points"] + merged_points["black_points"]
    )
    merged_points["total_games_played"] = (
        merged_points["white_games"] + merged_points["black_games"]
    )

    return merged_points


def games_per_openings(df, minimum_game_count: int):
    opening_count = pd.pivot_table(
        df, index=["opening"], columns=["result"], aggfunc="size", fill_value=0
    )

    opening_count["total_games"] = opening_count.sum(axis=1)
    opening_count["white_win_ratio"] = (
        opening_count["1-0"] / opening_count["total_games"]
    )
    opening_count["draw_ratio"] = (
        opening_count["1/2-1/2"] / opening_count["total_games"]
    )
    opening_count["black_win_ratio"] = (
        opening_count["0-1"] / opening_count["total_games"]
    )
    opening_count = opening_count.drop(columns=["0-1", "1-0", "1/2-1/2"])
    opening_count = opening_count[opening_count["total_games"] > minimum_game_count]
    return opening_count.sort_values("total_games", ascending=False)


def opening_average_and_median_elo_diff(df):
    opening_elo_diff = df.groupby("opening").agg({"elo_difference": ["mean", "median"]})
    opening_elo_diff.columns = list(map("_".join, opening_elo_diff.columns.values))
    return opening_elo_diff


# Create a text element and let the reader know the data is loading.
data_load_state = st.text("Loading data...")

# Load data into the dataframe.
df = load_data()

st.subheader("Raw data")
st.write(df.head())

players = set(df["white"].to_list() + df["black"].to_list())

option = st.selectbox("Choose a player!", players)
st.write(df[(df["white"] == option) | (df["black"] == option)])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total games played", df.shape[0])
col2.metric("White wins: ", df[df["result"] == "1-0"].shape[0])
col3.metric("Draws: ", df[df["result"] == "1/2-1/2"].shape[0])
col4.metric("Black wins: ", df[df["result"] == "0-1"].shape[0])

st.markdown("### Best performing players")
player_stats = calculate_points_per_player(df)
st.dataframe(player_stats)

st.subheader("Opening stats")
min_games = st.slider("Minimum number of games", 0, 300)
df1 = games_per_openings(df, min_games)
df2 = opening_average_and_median_elo_diff(df)
df3 = pd.merge(df1, df2, "left", on="opening")
st.write(df3)
