ORIGIN = (367, 1293) # in pixels (y is 1654-359)

wifi_location_m = [(-0.759, 19.445), (12.421, 4.654), (25.054, 11.834),
                   (45.324, 12.734), (51.224, 20.68), (51.003, 14.772),
                   (55.69, 13.281), (60.598, 15.077), (60.577, 20.072)]

wifi_location_px = [(346.507, 767.985), (702.367, 1167.342), (1043.458, 973.482),
                    (1590.748, 949.182), (1750.048, 734.64), (1744.081, 894.156),
                    (1870.63, 934.413), (2003.146, 885.921), (2002.579, 751.056)]

wifi_mac_id_common = ['00:27:0d:8b:8b:', '00:27:0d:8b:d6:', '00:27:0d:49:49:',
                      'd4:d7:48:44:c7:', 'xx', 'xx',
                      '00:27:0d:49:4b:', 'xx', 'xx']

def map_id_with_ap(wifi_name):
    for i, id_common in enumerate(wifi_mac_id_common):
        if id_common in wifi_name:
            return i+1

# pseudo algorithm for all the map matching method
class WifiArea(object): # a 21 x 21 matrix
    def __init__(self, folder, expected_wifi):
        self.wifi_bands, self.time_index, self.steps_in_range = self.set_wifi_bands(folder, expected_wifi)

    def get_ap(self):
        print self.steps_in_range
        return self.steps_in_range
        # return wifi_location_px

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

        ap_range = dict()
        for ap in ap_detected:
            min_i = min(ap_detected[ap].keys())
            min_time = time_index[min_i]
            max_i = max(ap_detected[ap].keys())
            max_time = time_index[max_i]
            ap_range[ap] = {'min':min_time, 'max':max_time}
        return ap_range

    def read_wifi_file(self, file_name):
        wifi_bands = dict()
        time_index = []
        order_of_appearance = []
        with open(file_name, 'r') as f:
            wifi_ap = f.readline().split()[1:]
            for ap in wifi_ap:
                wifi_bands[ap] = []
            for i, line in enumerate(f):
                line_segment = line.split()
                time_index.append(float(line_segment[0]))
                aps_rss = line_segment[1:]
                for j, rss in enumerate(aps_rss):
                    if int(rss) != -100:
                        wifi_bands[wifi_ap[j]].append((i, int(rss)))
                        if not wifi_ap[j] in order_of_appearance:
                            order_of_appearance.append(wifi_ap[j])
        return wifi_bands, time_index, order_of_appearance

    def read_steps_file(self, file_name):
        step_time = []
        with open(file_name, 'r') as f:
            f.readline()
            for line in f:
                line_segment = line.split()[0:2]
                step_time.append((int(line_segment[1]), float(line_segment[0])))
        return step_time

    def merge_wifi_step(self, step_time, ap_strength_with_time, expected_wifi):
        steps_in_range = dict()
        for wifi in expected_wifi:
            if wifi in ap_strength_with_time:
                min_time = ap_strength_with_time[wifi]['min']
                max_time = ap_strength_with_time[wifi]['max']
                steps_affected = []
                if min_time == max_time: # only one occurence
                    min_minus_one = step_time[0]
                    max_plus_one = step_time[-1]
                    index = 0
                    while step_time[index][1] < min_time:
                        min_minus_one = step_time[index]
                        index = index + 1
                    max_plus_one = step_time[index]
                    steps_affected.append(min_minus_one[0])
                    steps_affected.append(max_plus_one[0])
                for step, time in step_time:
                    if time >= min_time and time <= max_time:
                        steps_affected.append(step)
                steps_in_range[wifi] = steps_affected
        return steps_in_range

    def set_wifi_bands(self, folder, expected_wifi):
        wifi_bands, time_index, order_of_appearance = self.read_wifi_file(folder+'/Wifi.txt')
        ap_strength_with_time = self.compress_wifi_signal(wifi_bands, order_of_appearance, time_index)
        step_time = self.read_steps_file(folder+'/steps.txt')
        steps_to_correct = self.merge_wifi_step(step_time, ap_strength_with_time, expected_wifi)
        print "Order", map(lambda x: map_id_with_ap(x), order_of_appearance)
        print "Expected", expected_wifi
        return wifi_bands, time_index, steps_to_correct
