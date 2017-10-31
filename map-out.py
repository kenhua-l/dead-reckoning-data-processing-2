import matplotlib.pyplot as plt
import matplotlib.image as mpimg

origin = (367, 1293) # in pixels (y is 1654-359)
scale = 27

# in meters
start_point = (63.5, 11.3) # in meters
# start_point = (2100, 1000)
# start_point = (700, 1175)

wifi_location_m = [(-0.759, 19.445), (12.421, 4.654), (25.054, 11.834),
                   (45.324, 12.734), (51.224, 20.68), (51.003, 14.772),
                   (55.69, 13.281), (60.598, 15.077), (60.577, 20.072)]

wifi_location_px = [(346.507, 767.985), (702.367, 1167.342), (1043.458, 973.482),
                    (1590.748, 949.182), (1750.048, 734.64), (1744.081, 894.156),
                    (1870.63, 934.413), (2003.146, 885.921), (2002.579, 751.056)]

def convert_m_to_px((x,y)):
    real_x = x * scale + origin[0]
    real_y = origin[1] - y * scale
    return real_x, real_y

def main():
    # set up IDMI lab layout
    img=mpimg.imread('map.png')
    fig, ax = plt.subplots()
    ax.imshow(img)

    # Draw the origin point
    plt.plot(origin[0], origin[1], 'r^')
    # Draw the APs
    for ap in wifi_location_px:
        plt.plot(ap[0], ap[1], 'go')

    plt.show()

main()
