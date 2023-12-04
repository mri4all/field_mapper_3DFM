import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

path_file = "movement_paths/cube_2p5cm_path.csv"
measurements_files = [
    "measurements/10cmcube_5steps_per_axis_measurements_b0.csv",
    "measurements/10cmcube_5steps_per_axis_measurements_gx.csv"
]

dfs = []
for measurements_file in measurements_files:
    df_path = pd.read_csv(path_file)
    df_meas = pd.read_csv(measurements_file)

    df = pd.merge(df_meas,
                  df_path[["index", "x", "y", "z"]],
                  on="index")

    # Re-orient to the magnet field
    df["newz"] = df["x"]
    df["newx"] = -df["z"]
    df.drop(columns=["z", "x"], inplace=True)
    df.rename(columns={"newz": "z", "newx": "x"}, inplace=True)
    dfs.append(df)

# Subtract grads from reference measurement:
df_ref = dfs[0]
df_ref.rename(columns={"Bx": "Bxref",
                       "By": "Byref",
                       "Bz": "Bzref",
                       "Bmod": "Bmodref"}, inplace=True)
df = pd.merge(df_ref[["index", "x", "y", "z", "Bxref", "Byref", "Bzref", "Bmodref"]],
         dfs[1][["index", "x", "y", "z", "Bx", "By", "Bz", "Bmod"]],
         on = ["index", "x", "y", "z"])
df["Bx"] = df["Bx"] - df["Bxref"]
df["By"] = df["By"] - df["Byref"]
df["Bz"] = df["Bz"] - df["Bzref"]
df["Bmod"] = df["Bmod"] - df["Bmodref"]


# Plot all data
fig = plt.figure(figsize=(6, 6))

idx = 0
vmax = np.max(df[["Bx", "By", "Bz", "Bmod"]])
vmin = np.min(df[["Bx", "By", "Bz", "Bmod"]])
for plt_type in ["x", "y", "z", "mod"]:
    idx += 1
    ax = fig.add_subplot(2, 2, idx, projection='3d')
    im_ax = ax.scatter(df["x"], df["y"], df["z"], c=df[f"B{plt_type}"], cmap="coolwarm"
                       # , vmax=vmax, vmin=vmin
                       )
    plt.colorbar(im_ax)
    ax.set_title(f"B{plt_type}")
    ax.set_xlabel("x (up/down)")
    ax.set_ylabel("y (left/right)")
    ax.set_zlabel("z (along bore)")

fig.tight_layout()
fig.show()
