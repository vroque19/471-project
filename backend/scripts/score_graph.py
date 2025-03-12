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

# PLOT_PATH = "../../static/scores/"
PLOT_PATH = "../static/scores/"
FILE_NAME = datetime.datetime.now(tz_LA).strftime("%Y-%m-%d")
FACE_COLOR = "#020713"
FACE_COLOR = "#020713"
LIGHT_COLOR = "#4846E2"
AXES_COLOR = "#E5E7EB"

def main():
  data = {
      "Day": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
      "Sleep Score": [85, 78, 82, 90, 88, 76, 80]  # Scores out of 100
  }
  df = pd.DataFrame(data)
  if df.empty:
      print("No data found for the given time range. ( score_graph.py )")
      return
  sns.set_style("darkgrid")
  fig, ax = plt.subplots(figsize=(14, 7))
  fig.set_facecolor("#020713")  # Set figure background color
  ax.set_facecolor("#020713")  # Set axes background color

  ax = sns.lineplot(x="Day", y="Sleep Score", data=df, marker="o", linewidth=2.5, color=LIGHT_COLOR)

  # Customize title and labels
  # ax.set_title("Sleep Scores Throughout the Week", fontsize=16, fontweight='bold', color=AXES_COLOR)
  ax.set_ylabel("Sleep Score", fontsize=16, color=AXES_COLOR)
  ax.set_xlabel("", fontsize=16, color=AXES_COLOR)

  # Set custom y-ticks at 0, 25, 50, 75, and 100 with labels
  ax.set_yticks([0, 25, 50, 75, 100])
  ax.set_yticklabels(["", "Poor", "Fair", "Good", "Optimal"], fontsize=16, color=AXES_COLOR)

  # Rotate x-axis labels for better readability
  plt.xticks(rotation=30, fontsize=16, color=AXES_COLOR)



  plt.savefig(f"{PLOT_PATH+FILE_NAME}.png")
  print(f"Plot saved as {PLOT_PATH+FILE_NAME}.png")
  subprocess.run(["code", f"{PLOT_PATH+FILE_NAME}.png"])


if __name__ == "__main__":
  main()
