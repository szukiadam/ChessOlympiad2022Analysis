import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def total_games_per_opening_plot(df):
    ax = sns.countplot(x="opening", data=df)
    return ax
