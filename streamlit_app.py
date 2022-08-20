import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import streamlit.components.v1 as components
from src.helpers import (
    calculate_points_per_player,
    calculate_value_per_result,
    get_points_per_team_each_round,
    join_team_points,
    load_data,
    opening_white_black_win_ratio_and_elo_diff_scatterplot,
    player_values_for_team,
    best_players_per_team,
)
from src.plots import *

st.title("Chess Olympiad 2022")


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
raw_data = load_data()
team_points = get_points_per_team_each_round(raw_data)
df = join_team_points(raw_data, team_points)
df = calculate_value_per_result(df)

st.subheader("Raw data")
st.write(df.head())

st.subheader("Counts team points")

st.dataframe(team_points)

team_points_per_color_plot = team_points_per_color_distribution_plot(team_points)
st.plotly_chart(team_points_per_color_plot)

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
mvp_plot = most_valuable_players_plot(player_stats)
st.plotly_chart(mvp_plot)

st.markdown("### Best performing players for each team")
team = st.selectbox("Select a team!", set(df["whiteteam"].to_list()))
players_per_team = best_players_per_team(df, player_stats)
team_players = player_values_for_team(players_per_team, team)
st.dataframe(team_players)


st.subheader("Opening stats")
min_games = st.slider("Minimum number of games", 0, 300)
df1 = games_per_openings(df, min_games)
df2 = opening_average_and_median_elo_diff(df)
df3 = pd.merge(df1, df2, "left", on="opening")
df3 = df3.reset_index()
# df3.index.names = ["opening"]
st.write(df3)


stats = opening_win_ratio_plot(df3)
st.plotly_chart(stats)

# elo_result_scatterplot = elo_result_scatterplot(df)
# st.plotly_chart(elo_result_scatterplot)
rounds = df.groupby(["round", "result"]).size().reset_index(name="counts")
st.write(rounds)

rounds_plot = game_result_each_round_plot(df)
st.plotly_chart(rounds_plot)

board_plot = board_win_ratio(df)
st.plotly_chart(board_plot)

op_win_scatterplot = opening_win_ratio_and_elo_diff_scatterplot(df3)
st.markdown("## Elo diff and win ratio scatterplots")
st.plotly_chart(op_win_scatterplot)

op_black_scatterplot = opening_black_ratio_and_elo_diff_scatterplot(df3)
st.markdown("## Elo diff and black ratio scatterplots")
st.plotly_chart(op_black_scatterplot)

op_draw_scatterplot = opening_draw_ratio_and_elo_diff_scatterplot(df3)
st.markdown("## Elo diff and draw ratio scatterplots")
st.plotly_chart(op_draw_scatterplot)

op_win_ratios_scatterplot = opening_white_black_win_ratio_and_elo_diff_scatterplot(df3)
st.markdown("## White and Black win ratios scatterplots")
st.plotly_chart(op_win_ratios_scatterplot)
