import pytz
import datetime
import subprocess
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1 import host_subplot

tz_LA = pytz.timezone("America/Los_Angeles")    

PLOT_PATH = "../static/scores/"
FILE_NAME = datetime.datetime.now(tz_LA).strftime("%Y-%m-%d")
FACE_COLOR = "#020713"
FACE_COLOR = "#020713"
LIGHT_COLOR = "#4846E2"
AXES_COLOR = "#E5E7EB"

from test_query import get_weekly_scores


def main():
    # Update data with the current score
    data = get_weekly_scores()
    
    # Create a DataFrame
    df = pd.DataFrame(data)
    
    if df["Sleep Score"].isna().all():
        print("No sleep scores available yet for this week.")
        return
    
    # Set up the plot
    sns.set_style("darkgrid")
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.set_facecolor(FACE_COLOR)
    ax.set_facecolor(FACE_COLOR)
    ax.yaxis.tick_right()  # Move ticks to the right side
    # ax.yaxis.set_label_position("right")  # Move the ylabel to the right
    # Plot the line, only connecting points where data exists
    ax = sns.lineplot(
        x="Day", 
        y="Sleep Score", 
        data=df, 
        marker="o", 
        markersize=10,
        linewidth=2.5, 
        color=LIGHT_COLOR,
        linestyle='-'  # Connects only consecutive non-null points
    )

    # Explicitly set x-axis to show all days
    ax.set_xticks(range(len(data["Day"])))  # Set ticks for all days
    ax.set_xticklabels(data["Day"], rotation=30, fontsize=16, color=AXES_COLOR)

    # Customize axes
    ax.set_ylabel("Sleep Score", fontsize=16, color=AXES_COLOR, labelpad=20)
    ax.set_xlabel("", fontsize=16, color=AXES_COLOR)
    ax.set_yticks([0, 25, 50, 75, 100], )
    ax.set_yticklabels(["", "Poor", "Fair", "Good", "Optimal"], fontsize=16, color=AXES_COLOR)

    # Save and open the plot
    plt.savefig(f"{PLOT_PATH}{FILE_NAME}.png")
    print(f"Plot saved as {PLOT_PATH}{FILE_NAME}.png")
    subprocess.run(["code", f"{PLOT_PATH}{FILE_NAME}.png"])

if __name__ == "__main__":
    main()
