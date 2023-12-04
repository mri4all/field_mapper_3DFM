import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

path_file = "movement_paths/sphere_35radius_64points_1perPos.csv"
measurements_file = "measurements/sphere_35radius_64points_1perPos_measurements_passiveShim.csv"
plot_spheres = False

# ################################################
# Load data
# df_path = pd.read_csv(path_file)
df = pd.read_csv(measurements_file)
# df = pd.merge(df_meas,
#               df_path[["index", "x", "y", "z"]],
#               on="index")
# Re-orient to the magnet field
df["newz"] = df["x"]
df["newx"] = -df["z"]
df.drop(columns=["z", "x"], inplace=True)
df.rename(columns={"newz": "z", "newx": "x"}, inplace=True)
# Convert to mT
for c in ["Bx", "By", "Bz", "Bmod"]:
    df[c] /= 10000


# ################################################
# Plotting helper function:
def plot_measurements(df, title_str=""):
    fig = plt.figure(figsize=(6, 6))
    idx = 0
    for plt_type in ["x", "y", "z", "mod"]:
        idx += 1
        ax = fig.add_subplot(2, 2, idx, projection='3d')
        im_ax = ax.scatter(df["x"], df["y"], df["z"], c=df[f"B{plt_type}"], cmap="coolwarm")
        plt.colorbar(im_ax, ax=ax)

        ax.set_title(f"B{plt_type}{title_str}")
        ax.set_xlabel("x (up/down)")
        ax.set_ylabel("y (left/right)")
        ax.set_zlabel("z (along bore)")

    return fig


# Plot all data
if plot_spheres:
    # Look at sphere homoegeneity
    df_small = df[np.sqrt(df["x"]**2 + df["y"]**2 + df["z"]**2) <= 60]
    df_small = df_small[np.sqrt(df_small["x"]**2 + df_small["y"]**2 + df_small["z"]**2) > 0]
    fig = plot_measurements(df_small)
    fig.suptitle("Small sphere")
    fig.tight_layout()
    fig.show()
    print("small sphere", np.std(df_small["Bmod"])/np.mean(df_small["Bmod"])*1e6)

    # Look at large sphere homoegeneity
    df_large = df[np.sqrt(df["x"]**2 + df["y"]**2 + df["z"]**2) >= 60]
    fig = plot_measurements(df_large)
    fig.suptitle("Large sphere")
    fig.tight_layout()
    fig.show()
    print("large sphere", np.std(df_large["Bmod"])/np.mean(df_large["Bmod"])*1e6)
else:
    fig = plot_measurements(df)
    fig.tight_layout()
    fig.show()
