import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

cube_half_length = 20  # mm
num_points_per_side = 2
num_measurements_per_position = 1
filename = f"{cube_half_length}cube_{num_points_per_side}samples_{num_measurements_per_position}measurements_per_pos"
dfs = []

# Make cube dataframe
xs = []
ys = []
zs = []
for x in np.linspace(-1 * cube_half_length, cube_half_length, num_points_per_side):
    for y in np.linspace(-1 * cube_half_length, cube_half_length, num_points_per_side):
        for z in np.linspace(-1 * cube_half_length, cube_half_length, num_points_per_side):
            print(x, y, z, "num_measurements_per_position", num_measurements_per_position)
            for t in range(num_measurements_per_position):
                xs.append(x)
                ys.append(y)
                zs.append(z)
df = pd.DataFrame({"x": xs,
                   "y": ys,
                   "z": zs})

# Make "Center point" dataframe
df_center = pd.DataFrame({
    "x": np.zeros((1, num_measurements_per_position))[0],
    "y": np.zeros((1, num_measurements_per_position))[0],
    "z": np.zeros((1, num_measurements_per_position))[0],
})

# Combine the cube and center point dataframes together
df_full = pd.concat([df_center, df, df_center])

# Create movement differences and delays
df_diff = pd.DataFrame({
    "dx": [0] + list(np.diff(df_full["x"])),
    "dy": [0] + list(np.diff(df_full["y"])),
    "dz": [0] + list(np.diff(df_full["z"])),
    "x": df_full["x"].values,
    "y": df_full["y"].values,
    "z": df_full["z"].values
})
df_diff["delay"] = 1
df_diff.loc[(np.abs(df_diff["dx"]) > 10) |
            (np.abs(df_diff["dy"]) > 10) |
            (np.abs(df_diff["dz"]) > 10), "delay"] = 3
df_diff.loc[(np.abs(df_diff["dx"]) == 0) &
            (np.abs(df_diff["dy"]) == 0) &
            (np.abs(df_diff["dz"]) == 0), "delay"] = 0
df_diff["index"] = np.arange(len(df_diff))

print("Total number of points", len(df_diff))
print("Saving to:", f"movement_paths/{filename}.csv")
df_diff.to_csv(f"movement_paths/{filename}.csv", index=False)

# Plot output for sanity check
fig = plt.figure(figsize=(12, 12))
ax = fig.add_subplot(projection='3d')
ax.scatter(df["x"], df["y"], df["z"])
fig.show()

print("Finished")
