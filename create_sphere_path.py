import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd

radii = [35]  # mm
num_points_theta = 20
num_points_phi = 20
mirror_sphere = False
dfs = []

# def define_sensor_points_on_sphere(num_pts,r,base_coord):
#     indices = np.arange(0, num_pts, dtype=float) + 0.5
#     phi = np.arccos(1 - 2*indices/num_pts)
#     theta = np.pi * (1 + 5**0.5) * indices
#     x, y, z = r*np.cos(theta) * np.sin(phi), r*np.sin(theta) * np.sin(phi), r*np.cos(phi);
#     # pp.figure().add_subplot(111, projection='3d').scatter(x, y, z);
#     # pp.show()
#     arr = np.stack((x,y,z),axis=1)
#     arr = np.vstack([arr, np.array([0,0,0])])
#     arr[:,0] = arr[:,0]+base_coord[0]
#     arr[:,1] = arr[:,1]+base_coord[1]
#     arr[:,2] = arr[:,2]+base_coord[2]

for radius in radii:
    thetas = np.linspace(0, 360, num_points_theta+1)[:-1]
    phis = np.linspace(0, 180, num_points_phi+1)[:-1]

    xs = []
    ys = []
    zs = []
    for theta in thetas:
        for phi in phis:
            theta_rad = theta * math.pi/180
            phi_rad = phi * math.pi/180
            z = math.cos(phi_rad)*radius
            x = math.cos(theta_rad) * math.sin(phi_rad) * radius
            y = math.sin(theta_rad) * math.sin(phi_rad) * radius
            # print(theta, phi, x, y, z)
            # print(x % 1, y % 1, z % 1)
            # print(math.fmod(x, 1), math.fmod(y, 1), math.fmod(z, 1))

            # int_threshold = 0.25
            # if ((np.abs(math.fmod(x, 1)) < int_threshold) &
            #         (np.abs(math.fmod(y, 1)) < int_threshold) &
            #         (np.abs(math.fmod(z, 1)) < int_threshold)):
            #     print("yes")
            #     xs.append(int(np.round(x)))
            #     ys.append(int(np.round(y)))
            #     zs.append(int(np.round(z)))
            xs.append(x)
            ys.append(y)
            zs.append(z)

    if mirror_sphere:
        df = pd.DataFrame({"x": xs + ys + zs,
                           "y": ys + zs + xs,
                           "z": zs + xs + ys})
        df = df.drop_duplicates()
    else:
        df = pd.DataFrame({"x": xs,
                           "y": ys,
                           "z": zs})
    dfs.append(df)

df = pd.concat(dfs)
df_with_center = pd.DataFrame({
    "x": [0] + df["x"].to_list() + [0],
    "y": [0] + df["y"].to_list() + [0],
    "z": [0] + df["z"].to_list() + [0],
})
df_diff = pd.DataFrame({
    "dx": [0] + list(np.diff(df_with_center["x"])),
    "dy": [0] + list(np.diff(df_with_center["y"])),
    "dz": [0] + list(np.diff(df_with_center["z"])),
    "x": df_with_center["x"].values,
    "y": df_with_center["y"].values,
    "z": df_with_center["z"].values
})
df_diff["delay"] = 1
df_diff.loc[(np.abs(df_diff["dx"]) > 10) |
            (np.abs(df_diff["dy"]) > 10) |
            (np.abs(df_diff["dz"]) > 10), "delay"] = 3
df_diff["index"] = np.arange(len(df_diff))
df_diff.to_csv(f"movement_paths/sphere_{num_points_phi}phi_{num_points_theta}theta.csv", index=False)

fig = plt.figure(figsize=(12, 12))
ax = fig.add_subplot(projection='3d')
ax.scatter(df["x"], df["y"], df["z"])
fig.show()

print("done")
