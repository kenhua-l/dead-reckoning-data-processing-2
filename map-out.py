import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys
from pathgenerator import MapObject

folder = str(sys.argv[1])

wifi_location_px = [(346.507, 767.985), (702.367, 1167.342), (1043.458, 973.482),
                    (1590.748, 949.182), (1750.048, 734.64), (1744.081, 894.156),
                    (1870.63, 934.413), (2003.146, 885.921), (2002.579, 751.056)]

def main():
    # set up IDMI lab layout
    img=mpimg.imread('map.png')
    fig, ax = plt.subplots()
    ax.imshow(img)

    # Draw the origin point
    map_image = MapObject(folder)
    map_image.plot_important_points(plt)

    # Draw the APs
    for ap in wifi_location_px:
        plt.plot(ap[0], ap[1], 'go')

    # Draw Ground Truth
    map_image.plot_ground_truth(plt)

    # Draw DR
    map_image.plot_dr(plt)

    # Draw map-correction
    map_image.plot_map_matching(plt)

    # Draw wifi_correction
    map_image.plot_wifi_correction(plt)
    
    plt.show()
    # # pathgenerator.PathGen()
    # fig.savefig(folder+'/path.png', dpi=fig.dpi)


main()
