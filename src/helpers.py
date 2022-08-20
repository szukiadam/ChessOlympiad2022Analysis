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
    df[["round", "team_board"]] = df["round"].str.split(".", 1, expand=True)

    df["round"] = df["round"].astype(int)
    df["team_board"] = df["team_board"].astype(int)

    df["board"] = df["board"].astype(int)

    df[["whiteelo", "blackelo"]] = (
        df[["whiteelo", "blackelo"]].replace("-", 0).astype(int)
    )
    df["elo_difference"] = df["whiteelo"] - df["blackelo"]
    df["white_relative_elo_difference"] = df["elo_difference"]
    df["black_relative_elo_difference"] = df["elo_difference"] * -1

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


def get_points_per_team_each_round(df):
    white_team_points = (
        df.groupby(["round", "whiteteam"])
        .agg({"white_score": "sum"})
        .reset_index()
        .rename(
            columns={
                "whiteteam": "team",
                "white_score": "white_points",
            }
        )
    )
    black_team_points = (
        df.groupby(["round", "blackteam"])
        .agg({"black_score": "sum"})
        .reset_index()
        .rename(columns={"blackteam": "team", "black_score": "black_points"})
    )
    team_points = pd.merge(
        white_team_points, black_team_points, on=["round", "team"], how="inner"
    )
    team_points["total_points"] = (
        team_points["white_points"] + team_points["black_points"]
    )

    return team_points


def opening_white_black_win_ratio_and_elo_diff_scatterplot(df):
    fig = px.scatter(
        df,
        x="white_win_ratio",
        y="black_win_ratio",
        text="opening",
        trendline="ols",
        hover_data=["elo_difference_mean"],
    )
    fig.update_traces(textposition="top right")
    return fig


def join_team_points(original_df, team_points_df):
    df1 = pd.merge(
        original_df,
        team_points_df.add_suffix("_white"),
        how="left",
        left_on=["round", "whiteteam"],
        right_on=["round_white", "team_white"],
    )
    df = pd.merge(
        df1,
        team_points_df.add_suffix("_black"),
        how="left",
        left_on=["round", "blackteam"],
        right_on=["round_black", "team_black"],
    )

    return df


def calculate_value_per_result(df):
    # if gained points 2/1/0
    df["white_value_score"] = df.apply(
        lambda x: 2 * x["white_score"] - x["total_points_white"] / 4
        if x["total_points_white"] > 2.0
        else 1 * x["white_score"] - 0.5
        if abs(x["total_points_white"] - 2.0) < 0.1
        else 0,
        axis=1,
    )

    df["black_value_score"] = df.apply(
        lambda x: 2 * x["black_score"] - x["total_points_black"] / 4
        if x["total_points_black"] > 2.0
        else 1 * x["black_score"] - 0.5
        if abs(x["total_points_black"] - 2.0) < 0.1
        else 0,
        axis=1,
    )

    return df


@st.cache
def calculate_points_per_player(df):
    white_points = df.groupby("white", as_index=False).agg(
        {
            "white_score": ["sum", "count"],
            "white_value_score": ["sum"],
            "white_relative_elo_difference": ["mean"],
        }
    )
    white_points.columns = list(map("_".join, white_points.columns.values))
    white_points = white_points.rename(
        columns={
            "white_": "player_name",
            "white_score_sum": "white_points",
            "white_score_count": "white_games",
            "white_value_score_sum": "white_value_score",
            "white_relative_elo_difference_mean": "white_relative_elo_difference",
        }
    )

    black_points = df.groupby("black", as_index=False).agg(
        {
            "black_score": ["sum", "count"],
            "black_value_score": ["sum"],
            "black_relative_elo_difference": ["mean"],
        }
    )
    black_points.columns = list(map("_".join, black_points.columns.values))
    black_points = black_points.rename(
        columns={
            "black_": "player_name",
            "black_score_sum": "black_points",
            "black_score_count": "black_games",
            "black_value_score_sum": "black_value_score",
            "black_relative_elo_difference_mean": "black_relative_elo_difference",
        }
    )

    merged_points = pd.merge(white_points, black_points, how="outer", on="player_name")
    merged_points["total_points"] = (
        merged_points["white_points"] + merged_points["black_points"]
    )
    merged_points["total_value_score"] = (
        merged_points["white_value_score"] + merged_points["black_value_score"]
    )

    merged_points["total_games_played"] = (
        merged_points["white_games"] + merged_points["black_games"]
    )

    return merged_points


def best_players_per_team(original_data, player_stats):
    players_and_teams = original_data[["white", "whiteteam"]].drop_duplicates()
    players_per_team = pd.merge(
        players_and_teams,
        player_stats,
        how="left",
        left_on="white",
        right_on="player_name",
    )

    return players_per_team


def player_values_for_team(df, team):

    df = df[df["whiteteam"] == team]
    df = (
        df[["whiteteam", "player_name", "total_value_score"]]
        .rename(columns={"whiteteam": "team"})
        .sort_values(by="total_value_score", ascending=False)
    )

    return df
