import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math
import sys
from PIL import Image

# in meters
start_point = (63.5, 11.3) # in meters
# start_point = (2100, 1000)
# start_point = (700, 1175)
wifi1_location = (0, 19.45)
wifi2_location = (12.42, 4.65)
wifi3_location = (25.05, 11.83)
wifi4_location = (45.32, 12.73)
wifi5_location = (51.22, 20.68)
wifi6_location = (51.00, 14.77)
wifi7_location = (55.69, 13.28)
wifi8_location = (60.60, 15.07)
wifi9_location = (60.57, 20.07)

origin = (370, 1294) # in pixels (y is 1654-360)

# folder = str(sys.argv[1])
path = []
north = 40 # simplistically
scale = 27 #27 pixels : 1meter

zone_of_uncertainty = 3.5 #3.5m radius

def convert_image_deg(deg):
    ans = (deg - 180) * -1
    if ans < 0:
        ans = ans + 360
    return ans

def scale_m_to_px((x,y)):
    real_x = x * scale + origin[0]
    real_y = origin[1] - y * scale
    return (real_x, real_y)

def main():
    # set up IDMI lab layout
    img=mpimg.imread('map.png')
    fig, ax = plt.subplots()
    ax.imshow(img)

    #
    #
    # with open(folder+'/output/path.txt', 'r') as f:
    #     f.readline()
    #     for line in f:
    #         xy = line.split()
    #         deg = convert_image_deg(float(xy[0].split('.')[0][1:]) - north)
    #         path.append(tuple((deg, float(xy[1]))))
    #
    # x_axis, y_axis = scale_m_to_px(start_point)
    # x_axis = [x_axis]
    # y_axis = [y_axis]
    # prev_deg = 0
    # for deg, dis in path:
    #     x_axis.append(x_axis[-1] + scale * (dis) * math.sin(math.radians(deg)))
    #     y_axis.append(y_axis[-1] + scale * (dis) * math.cos(math.radians(deg)))
    #     prev_deg = deg
    #
    # wifi_x=[x_axis[0]]
    # wifi_y=[y_axis[1]]
    # with open(folder+'/output/StepsWiFi.txt', 'r') as f:
    #     f.readline()
    #     for line in f:
    #         parts = line.split()
    #         argtype = int(parts[0])
    #         arg1 = float(parts[1])
    #         arg2 = float(parts[2])
    #         if argtype == 2:
    #             map_x, map_y = scale_m_to_px((arg1, arg2))
    #             wifi_x.append(map_x)
    #             wifi_y.append(map_y)
    #         elif argtype == 1:
    #             deg = convert_image_deg(arg1 - north)
    #             wifi_x.append(wifi_x[-1] + scale * arg2 * math.sin(math.radians(deg)))
    #             wifi_y.append(wifi_y[-1] + scale * arg2 * math.cos(math.radians(deg)))
    #
    #
    # plt.plot(x_axis, y_axis, 'o')
    # plt.plot(x_axis, y_axis)
    # plt.plot(wifi_x, wifi_y, 'rx')
    # plt.plot(wifi_x, wifi_y)
    # plt.ylabel('y-axis')
    # plt.xlabel('x-axis')
    plt.show()
    # fig.savefig(folder+'/output/path.png', dpi=fig.dpi)

main()
