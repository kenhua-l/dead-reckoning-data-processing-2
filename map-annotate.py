import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math
import sys
from PIL import Image

folder = str(sys.argv[1])
path = []
start_point = (2100, 1000)
# start_point = (2100, 1000)
# start_point = (700, 1175)
scale = 15 #1 meter is about 25 pixels
north = 30.0

def main():
    img=mpimg.imread('map.png')
    fig, ax = plt.subplots()
    ax.imshow(img)
    # ax.imshow(img, origin='lower')

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

    # wifi_x=[start_point[0]]
    # wifi_y=[start_point[1]]
    # with open(folder+'/output/wifi_info.txt', 'r') as f:
    #     f.readline()
    #     i=0
    #     for line in f:
    #         wf = line.split()
    #         # if int(wf[1][1:-1]) > -47:
    #         if(i==9):
    #             wifi_x.append(1880)
    #             wifi_y.append(940)
    #         elif(i==27):
    #             wifi_x.append(1580)
    #             wifi_y.append(950)
    #         elif(i==57):
    #             wifi_x.append(1050)
    #             wifi_y.append(975)
    #         else:
    #             wifi_x.append(wifi_x[-1] + scale * (path[i][1]) * math.sin(math.radians(path[i][0])))
    #             wifi_y.append(wifi_y[-1] + scale * (path[i][1]) * math.cos(math.radians(path[i][0])))
    #         i = i+1

    plt.plot(x_axis, y_axis, 'o')
    plt.plot(x_axis, y_axis)
    # plt.plot(wifi_x, wifi_y, 'rx')
    plt.ylabel('y-axis')
    plt.xlabel('x-axis')
    plt.show()
    fig.savefig(folder+'/output/path.png', dpi=fig.dpi)

main()
