import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math
import sys
from PIL import Image

folder = str(sys.argv[1])
path = []
start_point = (2100, 1000)
scale = 15 #1 meter is about 25 pixels
north = 30.0

def main():
    img=mpimg.imread('map.png')
    fig, ax = plt.subplots()
    ax.imshow(img)

    with open(folder+'/output/path.txt', 'r') as f:
        f.readline()
        for line in f:
            xy = line.split()
            deg = float(xy[0].split('.')[0][1:]) - north
            path.append(tuple((deg, float(xy[1]))))

    x_axis = [start_point[0]]
    y_axis = [start_point[1]]
    for deg, dis in path:
        x_axis.append(x_axis[-1] + scale * (dis) * math.sin(math.radians(deg)))
        y_axis.append(y_axis[-1] + scale * (dis) * math.cos(math.radians(deg)))

    plt.plot(x_axis, y_axis, 'o')
    plt.plot(x_axis, y_axis)
    plt.ylabel('y-axis')
    plt.xlabel('x-axis')
    plt.show()

main()
