import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import subprocess
import datetime
from mpl_toolkits.axes_grid1 import host_subplot
import pandas as pd
import matplotlib.dates as mdates
import pytz

from query import get_sensor_data

# === 🎨 Define Colors === #
FACE_COLOR = "#020713"
AXES_COLOR = "#E5E7EB"
TEMP_COLOR = "#3b7ec4"
MOTION_COLOR = "#f3590c"
LIGHT_COLOR = "#484cb7"

PLOT_PATH = "../../static/charts/"
tz_LA = pytz.timezone("America/Los_Angeles")


def analyze_data(df):
    if df.empty:
        print("No data found for the given time range.")
        return

    print(df)
    # df["hour_bin"] = df["timestamp"].dt.floor("h")
    # df["hour_bin"] = pd.to_datetime(df["timestamp"], format="%H:%M:%S").apply(
    #     lambda x: x.replace(minute=0, second=0)
    # )
    # print(pd.to_datetime(df["timestamp"], format="%H:%M:%S"))
    df_hourly = (
        df.groupby("hour_bin")
        .agg({"temperature": "mean", "motion": "mean", "light": "mean"})
        .reset_index()
    )
    # print(df_hourly["temperature"])
    # df_hourly["timestamp"] = pd.to_datetime(df_hourly["timestamp"])

    # print(df_hourly["timestamp"])

    # Print the result
    # print("hourly:", df_hourly[["hour_bin"], ["light"], ["temperature"], ["motion"]])
    # print(
    #     "times only", pd.to_datetime(df_hourly["hour_bin"], format="%H:%M:%S").dt.time
    # )
    # df_hourly = pd.to_datetime(df_hourly["hour_bin"], format="%H:%M:%S").dt.time
    time_values = df_hourly["hour_bin"]
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
    plt.rcParams["figure.figsize"] = (26, 12)
    plt.tight_layout()
    host = host_subplot(111)
    plt.subplots_adjust(right=0.75)
    fig = plt.gcf()
    fig.patch.set_facecolor(FACE_COLOR)
    host.set_facecolor(FACE_COLOR)
    ax1 = host.twinx()  # temp
    ax2 = host.twinx()  # motion
    ax2.spines["right"].set_position(("outward", 65))  # Offset third axis
    # df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%H:%M")
    # time_labels = df_hourly["hour_bin"]

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

    (p1,) = host.plot(
        time_labels,
        light_values,
        color=LIGHT_COLOR,
        linewidth=2,
        label="Light Intensity",
    )

    (p2,) = ax1.plot(time_labels, temp_values, label="Temperature", color=TEMP_COLOR)
    p3 = ax2.scatter(
        time_labels, motion_values, label="Motion", color=MOTION_COLOR, marker="o"
    )
    ax1.xaxis.set_major_formatter(
        mdates.DateFormatter("%H:%M")
    )  # Only show hour and minute

    # Alternatively, if you have strings and just need to extract the time portion:
    new_tick_labels = [
        str(label).split(" ")[1] for label in time_labels
    ]  # Assuming format like "02-28 00"
    ax1.set_xticklabels(new_tick_labels, fontsize=12)

    # Set Labels & Ranges
    host.set_xlabel("Time", color=AXES_COLOR, fontweight="bold", fontsize=14)
    host.set_ylabel("Light Intensity (Lx)", fontsize=14)
    host.set_ylim(light_min, light_max)

    ax1.set_ylabel("Temperature (°C)", fontsize=14)
    ax1.set_ylim(temp_min, temp_max)

    ax2.set_ylabel("Motion (Boolean)", fontsize=14)
    ax2.set_ylim(0, 1)

    # Optionally, adjust tick label sizes
    host.tick_params(axis="both", labelsize=12)
    ax1.tick_params(axis="both", labelsize=12)
    ax2.tick_params(axis="both", labelsize=12)

    host.legend(loc="best")
    host.tick_params(axis="x", colors=AXES_COLOR, labelsize=14, rotation=0)
    host.tick_params(axis="y", colors=LIGHT_COLOR)
    ax1.tick_params(axis="y", colors=TEMP_COLOR)
    ax2.tick_params(axis="y", colors=MOTION_COLOR)
    host.yaxis.label.set_color(LIGHT_COLOR)
    ax1.yaxis.label.set_color(TEMP_COLOR)
    ax2.yaxis.label.set_color(MOTION_COLOR)
    file_name = datetime.datetime.now(tz_LA).strftime("%Y-%m-%d")
    plt.savefig(f"{PLOT_PATH+file_name}.png")
    print(f"Plot saved as {PLOT_PATH+file_name}.png")
    subprocess.run(["code", f"{PLOT_PATH+file_name}.png"])


if __name__ == "__main__":
    main()
