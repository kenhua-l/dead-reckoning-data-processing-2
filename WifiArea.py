ORIGIN = (367, 1293) # in pixels (y is 1654-359)

wifi_location_m = [(-0.759, 19.445), (12.421, 4.654), (25.054, 11.834),
                   (45.324, 12.734), (51.224, 20.68), (51.003, 14.772),
                   (55.69, 13.281), (60.598, 15.077), (60.577, 20.072)]

wifi_location_px = [(346.507, 767.985), (702.367, 1167.342), (1043.458, 973.482),
                    (1590.748, 949.182), (1750.048, 734.64), (1744.081, 894.156),
                    (1870.63, 934.413), (2003.146, 885.921), (2002.579, 751.056)]

wifi_mac_id_common = ['xx', '00:27:0d:8b:d6:', '00:27:0d:49:49:',
                      'd4:d7:48:44:c7:', 'xx', 'xx',
                      '00:27:0d:49:4b:', 'xx', 'xx']

# pseudo algorithm for all the map matching method
class WifiArea(object): # a 21 x 21 matrix
    def __init__(self):
        self.wifi_bands = dict()
        pass

    def compress_wifi_signal(self, wifi_bands, order, time_index):
        ap_detected = dict()
        for ap in order:
            for i, mac_id in enumerate(wifi_mac_id_common):
                if mac_id in ap and i+1 not in ap_detected:
                    ap_detected[i+1] = dict()

        for key in wifi_bands:
            ap = wifi_mac_id_common.index(str(key[-18:-3])) + 1
            for (index, rss) in wifi_bands[key]:
                if index not in ap_detected[ap]:
                    ap_detected[ap][index] = rss
                else:
                    curr_rss = ap_detected[ap][index]
                    ap_detected[ap][index] = max(curr_rss, rss)
        print ap_detected
            # ap_detected[ap].append(wifi_bands[key])
        return ap_detected

    def set_wifi_bands(self, file):
        wifi_bands = dict()
        time_index = []
        with open(file, 'r') as f:
            wifi_ap = f.readline().split()[1:]
            for ap in wifi_ap:
                wifi_bands[ap] = []
            order_of_appearance = []
            for i, line in enumerate(f):
                line_segment = line.split()
                time_index.append(float(line_segment[0]))
                aps_rss = line_segment[1:]
                for j, rss in enumerate(aps_rss):
                    if int(rss) != -100:
                        wifi_bands[wifi_ap[j]].append((i, int(rss)))
                        if not wifi_ap[j] in order_of_appearance:
                            order_of_appearance.append(wifi_ap[j])

        ap_strength = self.compress_wifi_signal(wifi_bands, order_of_appearance, time_index)
        print ap_strength
        # for yo in order_of_appearance:
            # print yo, wifi_bands[yo]
