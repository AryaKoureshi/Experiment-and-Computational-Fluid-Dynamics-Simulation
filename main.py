#%% Imports
import numpy as np
import matplotlib.pyplot as plt
import math
from sklearn.cluster import DBSCAN

#%% Functions
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def calculate_polygon_area(points):
    n = len(points)
    area = 0
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0

#%% Load and plot data
filenumbers = np.linspace(100, 50000, 500)
prev_cluster_centers_y = []
numBands = 50

diameters_bands = np.zeros((numBands))
areas_bands = np.zeros((numBands))
speeds_bands = np.zeros((numBands))
num_speeds_bands = np.zeros((numBands))
num_centers_bands = np.zeros((numBands))


for fnum in filenumbers:
    if fnum <1000:
        fileName = 'SYS-0'
    else:
        fileName = 'SYS-'
    with open(fileName+str(int(fnum))+'.txt', 'r') as file:
        lines = file.readlines()
    
    plt.figure(figsize=(15, 40))
    cellnumber_list = []
    x_coordinate_list = []
    y_coordinate_list = []
    cell_volume_list = []
    solid_x_velocity_list = []
    solid_y_velocity_list = []
    solid_vof_list = []
    a=[]
    
    for line in range(len(lines[1:])):
        values = lines[line+1].split()
        cellnumber_list.append(float(values[0]))
        x_coordinate_list.append(float(values[1]))
        y_coordinate_list.append(float(values[2]))
        cell_volume_list.append(float(values[3]))
        solid_x_velocity_list.append(float(values[4]))
        solid_y_velocity_list.append(float(values[5]))
        solid_vof_list.append(float(values[6]))
        if solid_vof_list[line] > 0.2:
            solid_vof_list[line] = 0
            plt.plot(x_coordinate_list[line], y_coordinate_list[line], '.b', alpha=0.6)
        else:
            solid_vof_list[line] = 1
            plt.plot(x_coordinate_list[line], y_coordinate_list[line], '.r', alpha=0.6)
    
    if fnum == 100:
        maxy = np.max(y_coordinate_list)
        miny = np.min(y_coordinate_list)
        bands = np.linspace(miny, maxy, numBands+1)
    
    #%% Find area of each seperate parts
    threshold = 0.005
    points_with_label_1 = np.array([(x, y) for x, y, label in zip(x_coordinate_list, y_coordinate_list, solid_vof_list) if label == 1])
    clusters = DBSCAN(eps=threshold, min_samples=1).fit(points_with_label_1)
    labels = clusters.labels_
    unique_labels = np.unique(labels)
    areas = []
    diameters = []
    cluster_centers_x = []
    cluster_centers_y = []
    for cluster_id in unique_labels:
        cluster_points = [p for i, p in enumerate(points_with_label_1) if labels[i] == cluster_id]
        cluster_area = calculate_polygon_area(cluster_points)
        diameter = 2*np.sqrt(cluster_area/np.pi)
        areas.append(cluster_area)
        diameters.append(diameter)
        
        x, y = zip(*cluster_points)
        plt.scatter(x, y, c='gray', alpha = 0.4) # Plot each cluster with different colors
    
        center_x = sum(x) / len(x)
        center_y = sum(y) / len(y)
        cluster_centers_x.append(center_x)
        cluster_centers_y.append(center_y)
        
        plt.text(center_x, center_y, f"Area: {cluster_area:.8f}", fontsize=12, ha='center', va='center', weight="bold")
        plt.text(center_x, center_y-0.01, f"d: {diameter:.6f}", fontsize=12, ha='center', va='center', weight="bold")
        
    print(fileName+str(fnum)+": Areas of separate clusters with label 1:", np.array(areas))
    print(fileName+str(fnum)+": Diameters of separate clusters with label 1:", np.array(diameters))
    
    speeds = []
    if prev_cluster_centers_y:
        cluster_speeds = []
        for current_center, prev_center in zip(cluster_centers_y, prev_cluster_centers_y):
            displacement = current_center - prev_center
            speed = displacement / 0.02  # Assuming time step is 0.02 seconds
            cluster_speeds.append(speed)
        
        
        if len(cluster_speeds) == len(cluster_centers_y): # Check if the number of speeds matches the number of current clusters
            print(fileName + str(int(fnum)) + ": Speeds of separate clusters with label 1:", np.array(cluster_speeds))
            for i, (x, y) in enumerate(zip(cluster_centers_x, cluster_centers_y)):
                plt.text(x, y-0.02, f"Speed: {cluster_speeds[i]:.4f}", fontsize=12, ha='center', va='center', weight="bold")
        else:
            print("Number of speeds does not match the number of clusters. Clusters might have merged or split.")
        
        for cn in range(len(cluster_centers_y)):
            for bn in range(len(bands)-1):
                if bands[bn] <= cluster_centers_y[cn] < bands[bn+1]:
                    diameters_bands[bn] += diameters[cn]
                    areas_bands[bn] += areas[cn]
                    num_centers_bands[bn] += 1
                    if len(cluster_speeds) == len(cluster_centers_y):
                        speeds_bands[bn] += cluster_speeds[cn]
                        num_speeds_bands[bn] += 1
    
    print("==================")       
    prev_cluster_centers_y = cluster_centers_y.copy()
    
    
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(fileName+str(fnum))
    plt.ylim([-0.015, 0.245])
    plt.savefig("./images/"+fileName+str(int(fnum))+'.png')
    #plt.show()
    plt.close()
    
centers_bands = bands + (bands[1]-bands[0])/2

# plot diameter versus height
plt.figure()
plt.plot(centers_bands[:-1], diameters_bands/num_centers_bands)
plt.ylabel("Diameter (m)")
plt.xlabel("Height (m)")
plt.title("Diameter versus Height")
plt.xlim([0, 0.1])
plt.ylim([0, 0.04])
plt.savefig('D_H.png')

# plot area versus height
plt.figure()
plt.plot(centers_bands[:-1], areas_bands/num_centers_bands)
plt.ylabel("Area (m^2)")
plt.xlabel("Height (m)")
plt.title("Area versus Height")
plt.xlim([0, 0.1])
plt.ylim([0, 0.0004])
plt.savefig('A_H.png')

# plot diameter versus height
plt.figure()
plt.plot(centers_bands[:-1], speeds_bands/num_speeds_bands)
plt.ylabel("Speed (m/s)")
plt.xlabel("Height (m)")
plt.title("Speed versus Height")
plt.xlim([0, 0.1])
plt.savefig('S_H.png')

