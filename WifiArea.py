ORIGIN = (367, 1293) # in pixels (y is 1654-359)

# pseudo algorithm for all the map matching method
class WifiArea(object): # a 21 x 21 matrix
    def __init__(self):
        self.wifi_bands = dict()
        pass

    def set_wifi_bands(self, file):
        wifi_bands = dict()
        with open(file, 'r') as f:
            wifi_ap = f.readline().split()[1:]
            for ap in wifi_ap:
                wifi_bands[ap] = []
            for i, line in enumerate(f):
                line_segment = line.split()
                time = float(line_segment[0])
                aps_rss = line_segment[1:]
                for j, rss in enumerate(aps_rss):
                    if int(rss) != -100:
                        wifi_bands[wifi_ap[j]].append((i, time, int(rss)))
            print wifi_bands
