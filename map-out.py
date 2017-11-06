import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys
from pathgenerator import MapObject

folder = str(sys.argv[1])

def main():
    # set up IDMI lab layout
    img=mpimg.imread('map.png')
    fig, ax = plt.subplots()
    ax.imshow(img)

    # Draw the origin point
    map_image = MapObject(folder)
    # map_image.plot_important_points(plt)

    # Draw Ground Truth
    ground, = map_image.plot_ground_truth(plt)

    # Draw DR
    dr, = map_image.plot_dr(plt)

    # Draw map-correction
    # map_dr, = map_image.plot_map_matching(plt)

    # Draw wifi_correction
    # wifi, = map_image.plot_wifi_correction(plt)

    # Draw hybrid_correction
    hybrid, = map_image.plot_hybrid_correction(plt)

    # plt.legend([ground, dr], ['Ground Truth', 'Dead-Reckoning'])
    # plt.legend([ground, dr, map_dr], ['Ground Truth', 'Dead-Reckoning', 'Map Matching'])
    # plt.legend([ground, dr, wifi], ['Ground Truth', 'Dead-Reckoning', 'WiFi'])
    plt.legend([ground, dr, hybrid], ['Ground Truth', 'Dead-Reckoning', 'Hybrid'])
    plt.show()
    fig.savefig(folder+'/path.png', dpi=fig.dpi)


main()
