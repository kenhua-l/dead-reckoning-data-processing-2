import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys
import pathgenerator

folder = str(sys.argv[1])

def main():
    # set up IDMI lab layout
    img=mpimg.imread('map.png')
    fig, ax = plt.subplots()
    ax.imshow(img)

    # Draw the origin point
    map_image = pathgenerator.MapObject(folder)
    map_image.plot_important_points(plt)

    # Draw the APs
    for ap in wifi_location_px:
        plt.plot(ap[0], ap[1], 'go')

    # Draw Ground Truth
    map_image.plot_ground_truth(plt)

    # Draw DR
    map_image.plot_dr(plt)

    plt.show()
    # pathgenerator.PathGen()

main()
