import math

ORIGIN = (367, 1293) # in pixels (y is 1654-359)
SCALE = 27

wifi_location_m = [(-0.759, 19.445), (12.421, 4.654), (25.054, 11.834),
                   (45.324, 12.734), (51.224, 20.68), (51.003, 14.772),
                   (55.69, 13.281), (60.598, 15.077), (60.577, 20.072)]

wifi_location_px = [(346.507, 767.985), (702.367, 1167.342), (1043.458, 973.482),
                    (1590.748, 949.182), (1750.048, 734.64), (1744.081, 894.156),
                    (1870.63, 934.413), (2003.146, 885.921), (2002.579, 751.056)]

wifi_mac_id_common = ['00:27:0d:8b:8b:', '00:27:0d:8b:d6:', '00:27:0d:49:49:',
                      'd4:d7:48:44:c7:', 'xx', 'xx',
                      '00:27:0d:49:4b:', 'xx', 'xx']

def convert_m_to_px((x,y)):
    real_x = x * SCALE + ORIGIN[0]
    real_y = ORIGIN[1] - y * SCALE
    return real_x, real_y

def convert_px_to_meters((x,y)):
    m_x = (x - ORIGIN[0]) / SCALE
    m_y = (ORIGIN[1] - y) / SCALE
    return m_x, m_y

def convert_image_deg(deg):
    ans = (deg - 180) * -1
    if ans < 0:
        ans = ans + 360
    return ans

def get_mid_and_edge(step_range):
    mid = step_range[len(step_range)/2]
    steps_away = len(step_range)/2
    return mid, steps_away

def get_wifi(dict_of_range, step_number):
    for key, value in dict_of_range.items():
        if step_number in value:
            return key

def map_id_with_ap(wifi_name):
    for i, id_common in enumerate(wifi_mac_id_common):
        if id_common in wifi_name:
            return i+1

# pseudo algorithm for all the map matching method
class WifiArea(object): # a 21 x 21 matrix
    def __init__(self, folder, expected_wifi):
        self.max_step = 0.0
        self.min_step = 0.0
        self.ave_step = 0.0
        self.stride_length = []
        self.time_index, self.steps_to_correct, self.steps_in_range = self.set_wifi_bands(folder, expected_wifi)


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
        step_length = []
        with open(file_name, 'r') as f:
            f.readline()
            for line in f:
                line_segment = line.split()
                step_time.append((int(line_segment[1]), float(line_segment[0])))
                step_length.append(float(line_segment[4]))
        self.ave_step = sum(step_length) / len(step_length)
        self.max_step = max(step_length)
        self.min_step = min(step_length)
        return step_time

    def merge_wifi_step(self, step_time, ap_strength_with_time, expected_wifi):
        steps_in_range = dict()
        steps_to_correct = []
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
                        if step not in steps_affected: #avoid overlap
                            steps_affected.append(step)
                steps_in_range[wifi] = steps_affected
                steps_to_correct = steps_to_correct + steps_affected
        return steps_in_range, steps_to_correct

    def set_wifi_bands(self, folder, expected_wifi):
        wifi_bands, time_index, order_of_appearance = self.read_wifi_file(folder+'/Wifi.txt')
        ap_strength_with_time = self.compress_wifi_signal(wifi_bands, order_of_appearance, time_index)
        step_time = self.read_steps_file(folder+'/steps.txt')
        steps_in_range, steps_to_correct = self.merge_wifi_step(step_time, ap_strength_with_time, expected_wifi)
        return time_index, steps_to_correct, steps_in_range

    def evaluate_error_steps(self, start, path_reference):
        wifi_steps = [start]
        for i in range(len(path_reference)):
            (angle, length) = path_reference[i]
            angle = convert_image_deg(angle)
            pred_next_x = wifi_steps[-1][0] + length * math.sin(math.radians(angle))
            pred_next_y = wifi_steps[-1][1] + length * math.cos(math.radians(angle))
            pred_next_step = (pred_next_x, pred_next_y) # in meters
            if i in self.steps_to_correct:
                wifi_focus = get_wifi(self.steps_in_range, i)
                wifi_position = wifi_location_m[wifi_focus-1]
                wifi_mid, wifi_step_range = get_mid_and_edge(self.steps_in_range[wifi_focus])
                allowed_range = abs(wifi_mid - i) * self.ave_step + self.ave_step # for tolerance
                wifi_dr_step_distance = math.sqrt(pow(pred_next_step[0] - wifi_position[0],2) + pow(pred_next_step[1] - wifi_position[1],2))
                if wifi_dr_step_distance > allowed_range:
                    wifi_next_x, wifi_next_y = 0, 0
                    if i <= wifi_mid:   # too slow
                        wifi_next_x = wifi_steps[-1][0] + (self.ave_step + 0.15) * math.sin(math.radians(angle))
                        wifi_next_y = wifi_steps[-1][1] + (self.ave_step + 0.15) * math.cos(math.radians(angle))
                        self.stride_length.append(self.max_step)
                    elif i > wifi_mid:
                        wifi_next_x = wifi_steps[-1][0] + (self.ave_step - 0.15) * math.sin(math.radians(angle))
                        wifi_next_y = wifi_steps[-1][1] + (self.ave_step - 0.15) * math.cos(math.radians(angle))
                        self.stride_length.append(self.min_step)
                    wifi_next_step = (wifi_next_x, wifi_next_y)
                    wifi_steps.append(wifi_next_step)
                else:
                    self.stride_length.append(length)
                    wifi_steps.append(pred_next_step)
            else:
                self.stride_length.append(length)
                wifi_steps.append(pred_next_step)

        wifi_step_in_px = map(lambda coord: tuple(convert_m_to_px(coord)), wifi_steps)
        return wifi_step_in_px
