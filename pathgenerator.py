import math
from StepMatrix import StepMatrix
from WifiArea import WifiArea

#CONSTANT
SCALE = 27 # 1 meter is 27 pixels
NORTH = 31 # north of map is 30 degree
AVERAGE_STEP = 3 # quantized blocks away
ORIGIN = (367, 1293) # in pixels (y is 1654-359)
MAP_SIZE = (1770, 615) # in pixels - (590, 205) in quantized, and (65.56, 22.78) in meters

def convert_px_to_meters((x,y)):
    m_x = (x - ORIGIN[0]) / SCALE
    m_y = (ORIGIN[1] - y) / SCALE
    return m_x, m_y

# converts m to px to draw on map - returns two values, not tuple
def convert_m_to_px((x,y)):
    real_x = x * SCALE + ORIGIN[0]
    real_y = ORIGIN[1] - y * SCALE
    return real_x, real_y

# returns a normal degree we can deal with
def convert_image_deg(deg):
    ans = (deg - 180) * -1
    if ans < 0:
        ans = ans + 360
    return ans

def convert_quantize_to_px(axis, value):
    if axis == "xy":
        return (value[0] * 3 + ORIGIN[0] +1, ORIGIN[1] - 614 + value[1] * 3)
    elif axis=="x":
        return value * 3 + ORIGIN[0] - 1
    else:
        return ORIGIN[1] - 614 + value * 3

def separate_tuple(array_of_tuple):
    arr_x = []
    arr_y = []
    for x,y in array_of_tuple:
        arr_x.append(x)
        arr_y.append(y)
    return arr_x, arr_y

# represent a quantized block
def quantize_pixel(coord):
    new_x = int((coord[0] - ORIGIN[0]) / 3)
    new_y = int((coord[1] - ORIGIN[1] + 615) / 3)
    return (new_x, new_y)

class PathGen(object):
    def __init__(self, folder, obs_map):
        self.folder = folder # all data needed
        self.path_reference = self.get_path_reference() # all the calculated step value from Julia - tuple of degree and distance
        self.start_point, self.ground_path = self.get_ground_truth() # start point in m, true path step value - tuple of (x,y) in m
        self.dr_path = self.get_dr() # dead-reckoning path step value as of Julia calculated

        # for hybrid correction
        self.hybrid_path_distance = []

        # technique map_match
        self.dr_map_path = self.get_map_match_path(obs_map)

        # technique wifi_correct
        self.wifi_path = self.get_wifi_correction()

        # technique hybrid_correc
        self.hybrid_path = self.get_hybrid_correction(obs_map)

        print("Paths for 3 methods generated")

    # returns array of tuple of (angle, distance) of each step
    def get_path_reference(self):
        path = []
        with open(self.folder+'/path.txt', 'r') as f:
            f.readline()
            for line in f:
                steps = line.split()
                direction = convert_image_deg(float(steps[0]) - NORTH)
                step_length = float(steps[1])
                path.append((direction, step_length))
        return path

    # returns the start point (in m) and the pixelated steps location of ground truth - array of tuple of (x,y) for each step
    def get_ground_truth(self):
        ground_path = []
        start_point = None
        with open(self.folder+'/ground_path.txt', 'r') as f:
            start_point = tuple(map(lambda x: float(x), f.readline().split()[1:]))
            ground_path.append(convert_m_to_px(start_point))
            start_path_x, start_path_y = ground_path[0]
            self.wifi = map(lambda x: int(x), f.readline().split()[1:])
            for line in f:
                lines = line.split()
                number_of_steps = int(lines[0])
                direction = int(lines[1])
                end_x, end_y = convert_m_to_px((float(lines[2]), float(lines[3])))
                step_length = math.sqrt(pow(end_x - start_path_x, 2) + pow(end_y - start_path_y, 2)) / number_of_steps
                for i in range(number_of_steps):
                    x = ground_path[-1][0] + step_length * math.sin(math.radians(direction))
                    y = ground_path[-1][1] + step_length * math.cos(math.radians(direction))
                    ground_path.append((x,y))
                start_path_x, start_path_y = end_x, end_y
        return start_point, ground_path

    # returns the dead-reckoning path in px - array of tuple of (x,y) for each step
    def get_dr(self):
        dr_path = [tuple(convert_m_to_px(self.start_point))]
        for angle, length in self.path_reference:
            x = dr_path[-1][0] + SCALE * length * math.sin(math.radians(angle))
            y = dr_path[-1][1] + SCALE * length * math.cos(math.radians(angle))
            dr_path.append((x, y))
        return dr_path

    #returns the map-matching path in px - array of tuple of (x,y) for each step
    def get_map_match_path(self, obs_map):
        # get path in m
        (angle, length) = self.path_reference[0]
        x = self.start_point[0] + length * math.sin(math.radians(angle))
        y = self.start_point[1] + length * math.cos(math.radians(angle))
        first_step = (x, y)
        mapper_dr_in_m = [self.start_point, first_step]
        #in px
        mapped_dr_path = [convert_m_to_px(self.start_point), convert_m_to_px(first_step)]

        for i in range(1, len(self.dr_path) - 1):
            step_matrix = StepMatrix(quantize_pixel(mapped_dr_path[-1]), self.path_reference[i], quantize_pixel(mapped_dr_path[-2]), obs_map)
            map_next_step = convert_quantize_to_px("xy", step_matrix.next_step_matched)
            mapped_dr_path.append(map_next_step)
            # self.hybrid_path_angle.append(step_matrix.angle)
        return mapped_dr_path

    def get_wifi_correction(self):
        wifi_object = WifiArea(self.folder, self.wifi)
        wifi_path = wifi_object.evaluate_error_steps(self.start_point, self.path_reference)
        self.hybrid_path_distance = wifi_object.stride_length
        return wifi_path

    def get_hybrid_correction(self, obs_map):
        angle = self.path_reference[0][0]
        length = self.hybrid_path_distance[0]
        x = self.start_point[0] + length * math.sin(math.radians(angle))
        y = self.start_point[1] + length * math.cos(math.radians(angle))
        first_step = (x, y)
        #in px
        hybrid_path = [convert_m_to_px(self.start_point), convert_m_to_px(first_step)]

        for i in range(1, len(self.dr_path) - 1):
            refer = (self.path_reference[i][0], self.hybrid_path_distance[i])
            step_matrix = StepMatrix(quantize_pixel(hybrid_path[-1]), refer, quantize_pixel(hybrid_path[-2]), obs_map)
            map_next_step = convert_quantize_to_px("xy", step_matrix.next_step_matched)
            hybrid_path.append(map_next_step)
        return hybrid_path

class MapObject(object):
    def __init__(self, folder):
        self.map_size = (1770, 615) # in pixels 1770 wide, 615 tall
        self.map_size_in_m = (65.5, 22.8) # in meters
        self.map_array_2d_obs = [[0 for x in range(590)] for y in range(205)] # quantized block - 3 x 3pixels per block
        self.quantize_obs_block()
        self.path = PathGen(folder, self.map_array_2d_obs)

    def plot_important_points(self, plt):
        # print self.path.start_point
        plt.plot(ORIGIN[0], ORIGIN[1], 'r^')
        plt.plot(ORIGIN[0]+self.map_size[0], ORIGIN[1]-self.map_size[1], 'r^')

        plt.plot()

    def plot_ground_truth(self, plt):
        (x_truth, y_truth) = separate_tuple(self.path.ground_path)
        return plt.plot(x_truth, y_truth, 'bx')

    def plot_dr(self, plt):
        (x_dr, y_dr) = separate_tuple(self.path.dr_path)
        return plt.plot(x_dr, y_dr, 'ro')

    def plot_map_matching(self, plt):
        (x_map, y_map) = separate_tuple(self.path.dr_map_path)
        return plt.plot(x_map, y_map, 'ys')

    def plot_wifi_correction(self, plt):
        (x_wifi, y_wifi) = separate_tuple(self.path.wifi_path)
        return plt.plot(x_wifi, y_wifi, 'g^')

    def plot_hybrid_correction(self, plt):
        (x_hybrid, y_hybrid) = separate_tuple(self.path.hybrid_path)
        return plt.plot(x_hybrid, y_hybrid, 'k*')

    def check_map(self, plt): # don't use unless needed because takes time to draw
        # x_points = range(ORIGIN[0] + (3 * (0+1) - 1), ORIGIN[0] + (3 * (388+1) - 1))
        # y_points = [ORIGIN[1] - self.map_size[1] + (3 * (90+1) - 1)] * len(x_points)
        x_points = []
        y_points = []
        for i in range(len(self.map_array_2d_obs)): # row
            for j in range(len(self.map_array_2d_obs[i])): # col
                if self.map_array_2d_obs[i][j] == 1: # obstacle
                    x_points.append(ORIGIN[0] + (3 * (j+1) - 1))
                    y_points.append(ORIGIN[1] - self.map_size[1] + (3 * (i+1) - 1))
        # print x_points, y_points
        # print len(self.map_array_2d_obs)
        plt.plot(x_points, y_points, 'yx')
        # for row in self.map_array_2d_obs:
            # print row

    def get_result(self):
        start = self.path.start_point
        ground_end = convert_px_to_meters(self.path.ground_path[-1])
        dr_end = convert_px_to_meters(self.path.dr_path[-1])
        map_end = convert_px_to_meters(self.path.dr_map_path[-1])
        wifi_end = convert_px_to_meters(self.path.wifi_path[-1])
        hybrid_end = convert_px_to_meters(self.path.hybrid_path[-1])
        print "End", ground_end
        print "DR", dr_end
        print "Map", map_end
        print "wifi", wifi_end
        print "hybrid", hybrid_end
        print math.sqrt(pow(ground_end[0]-dr_end[0], 2) + pow(ground_end[1]-dr_end[1], 2))
        print math.sqrt(pow(ground_end[0]-map_end[0], 2) + pow(ground_end[1]-map_end[1], 2))
        print math.sqrt(pow(ground_end[0]-wifi_end[0], 2) + pow(ground_end[1]-wifi_end[1], 2))
        print math.sqrt(pow(ground_end[0]-hybrid_end[0], 2) + pow(ground_end[1]-hybrid_end[1], 2))

    def quantize_obs_block(self):
        # set up obstacles based on map
        # use block (3 x 3 pixels equal one quantize block)
        for i in range(95):
            for j in range(391):
                self.map_array_2d_obs[i][j] = 1
        for i in range(52, 95):
            for j in range(425, 490):
                self.map_array_2d_obs[i][j] = 1
        for i in range(108, 205):
            for j in range(35):
                self.map_array_2d_obs[i][j] = 1
        for i in range(170, 205):
            for j in range(34, 164):
                self.map_array_2d_obs[i][j] = 1
        for i in range(108, 205):
            for j in range(163, 590):
                self.map_array_2d_obs[i][j] = 1
        for i in range(108, 155):
            for j in range(55, 147):
                self.map_array_2d_obs[i][j] = 1
