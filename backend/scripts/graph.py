import pytz
import datetime
import subprocess
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1 import host_subplot

from .query import get_sensor_data

# === 🎨 Define Colors === #
FACE_COLOR = "#020713"
AXES_COLOR = "#E5E7EB"
TEMP_COLOR = "#99b6ff"
MOTION_COLOR = "#ffc299"
LIGHT_COLOR = "#4846E2"
TEMP_TEXT_COLOR = "#4A60EB"


PLOT_PATH = "../static/charts/"
# PLOT_PATH = "../../static/charts/"
# PLOT_PATH = "../charts/"
tz_LA = pytz.timezone("America/Los_Angeles")    


def analyze_data(df):
    if df.empty:
        print("No data found for the given time range.")
        return

    df_hourly = (
        df.groupby("hour_bin")
        .agg({"temperature": "mean", "motion": "mean", "light": "mean"})
        .reset_index()
    )

    time_values = df_hourly["hour_bin"]
    time_values = [str(x).split(" ")[1][:5] for x in time_values]
    light_values = df_hourly["light"]
    temp_values = df_hourly["temperature"]
    motion_values = df_hourly["motion"]
    light_max = light_values.max()
    temp_max = temp_values.max()
    light_min = light_values.min()
    temp_min = temp_values.min()

    return (
        time_values,
        light_values,
        temp_values,
        motion_values,
        light_min,
        light_max,
        temp_min,
        temp_max,
    )


def main():
    df = get_sensor_data()
    plt.rcParams["figure.figsize"] = (14, 8)
    # plt.title("Daily Sleep Data", fontsize=40, fontweight='bold', color=AXES_COLOR)
    host = host_subplot(111)
    plt.subplots_adjust(right=0.7)
    fig = plt.gcf()
    fig.patch.set_facecolor(FACE_COLOR)
    host.set_facecolor(FACE_COLOR)
    ax1 = host.twinx()  # temp
    ax2 = host.twinx()  # motion
    ax2.spines["right"].set_position(("outward", 88))  # Offset third axis

    (
        time_labels,
        light_values,
        temp_values,
        motion_values,
        light_min,
        light_max,
        temp_min,
        temp_max,
    ) = analyze_data(df)
    print(time_labels, light_values, motion_values, temp_values)
    (p1,) = host.plot(
        time_labels,
        light_values,
        color=LIGHT_COLOR,
        linewidth=3,
        label="Light Intensity",
    )

    (p2,) = ax1.plot(time_labels, temp_values, linewidth=3, label="Temperature", color=TEMP_COLOR)
    p3 = ax2.scatter(
        time_labels, motion_values, label="Motion", color=MOTION_COLOR, marker="o", s=100
    )

    # Set Labels & Ranges
    host.set_xlabel("Time", color=AXES_COLOR, fontweight="bold", fontsize=25)
    host.set_ylabel("Light Intensity (Lx)", fontsize=25)
    host.set_ylim(light_min - 0.1, light_max + 1)
    # plt.margins(x=1, y=2)

    ax1.set_ylabel("Temperature (°C)", fontsize=25)
    ax1.set_ylim(temp_min - 0.5, temp_max + 1)

    ax2.set_ylabel("Motion (Boolean)", fontsize=25)
    ax2.set_ylim(-0.1, 1)
    host.margins(y=0.1)

    # Optionally, adjust tick label sizes
    host.tick_params(axis="both", labelsize=18)
    ax1.tick_params(axis="both", labelsize=18)
    ax2.tick_params(axis="both", labelsize=18)

    legend = host.legend(loc="best", prop={'size': 18}, labelcolor=AXES_COLOR)
    legend.get_frame().set_facecolor(FACE_COLOR)
    host.tick_params(axis="x", colors=AXES_COLOR, labelsize=16, rotation=0)
    host.tick_params(axis="y", colors=TEMP_TEXT_COLOR)
    ax1.tick_params(axis="y", colors=TEMP_COLOR)
    ax2.tick_params(axis="y", colors=MOTION_COLOR)
    host.yaxis.label.set_color(TEMP_TEXT_COLOR)
    ax1.yaxis.label.set_color(TEMP_COLOR)
    ax2.yaxis.label.set_color(MOTION_COLOR)
    file_name = datetime.datetime.now(tz_LA).strftime("%Y-%m-%d")
    plt.savefig(f"{PLOT_PATH+file_name}.png")
    print(f"Plot saved as {PLOT_PATH+file_name}.png")
    subprocess.run(["code", f"{PLOT_PATH+file_name}.png"])


if __name__ == "__main__":
    main()
