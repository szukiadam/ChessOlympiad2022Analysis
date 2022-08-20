from distutils.log import info
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.express as px


# TODO: biggest upsets
# TODO: plot colors: white=green, draw=orange, black=red
# TODO: calculate relative opponent rating for players (how much weaker opponents did he play against)

plt.style.use("fivethirtyeight")


def total_games_per_opening_plot(df):
    ax = sns.countplot(x="opening", data=df)
    return ax


def opening_win_ratio_plot(df):

    if df.shape[0] > 8:
        barmode = "stack"
    else:
        barmode = "group"

    fig = px.bar(
        df,
        x="opening",
        y=["white_win_ratio", "draw_ratio", "black_win_ratio"],
        barmode=barmode,
    )

    return fig


def elo_result_scatterplot(df):
    fig = px.scatter(df, x="whiteelo", y="blackelo", color="result", trendline="ols")
    return fig


def game_result_circle_plot(df):
    pass


def game_result_each_round_plot(df):
    rounds = df.groupby(["round", "result"]).size().reset_index(name="counts")
    rounds = rounds.sort_values("round", ascending=True)
    fig = px.line(rounds, x="round", y="counts", color="result", markers=True)
    return fig


def board_win_ratio(df):
    board_results = df.groupby(["board", "result"]).size().reset_index(name="counts")
    fig = px.bar(board_results, x="board", y="counts", color="result")
    return fig


def opening_win_ratio_and_elo_diff_scatterplot(df):
    fig = px.scatter(
        df,
        x="elo_difference_mean",
        y="white_win_ratio",
        text="opening",
        trendline="ols",
    )
    fig.update_traces(textposition="top left")
    return fig


def opening_black_ratio_and_elo_diff_scatterplot(df):
    fig = px.scatter(
        df,
        x="elo_difference_mean",
        y="black_win_ratio",
        text="opening",
        trendline="ols",
    )
    fig.update_traces(textposition="top right")
    return fig


def opening_draw_ratio_and_elo_diff_scatterplot(df):
    fig = px.scatter(
        df,
        x="elo_difference_mean",
        y="draw_ratio",
        text="opening",
        trendline="ols",
    )
    fig.update_traces(textposition="top right")
    return fig


def team_points_per_color_distribution_plot(points_per_team_df):
    points_per_team_df.groupby("team").agg(
        {"white_points": "sum", "black_points": "sum"}
    )
    points_per_team_df = points_per_team_df.rename(
        columns={
            "white_points": "total_white_points",
            "black_points": "total_black_points",
        }
    )

    fig = px.bar(
        points_per_team_df, x="team", y=["total_white_points", "total_black_points"]
    )
    return fig


def most_valuable_players_plot(df):
    df = df.sort_values(by="total_value_score", ascending=False)
    fig = px.scatter(
        df[:10],
        x="total_value_score",
        y="total_points",
        text="player_name",
    )
    fig.update_traces(textposition="top center")

    return fig
