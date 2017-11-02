import math
from StepMatrix import StepMatrix

#CONSTANT
SCALE = 27 # 1 meter is 27 pixels
NORTH = 20 # north of map is 30 degree
AVERAGE_STEP = 3 # quantized blocks away
ORIGIN = (367, 1293) # in pixels (y is 1654-359)
MAP_SIZE = (1770, 615) # in pixels - (590, 205) in quantized, and (65.56, 22.78) in meters

wifi_location_m = [(-0.759, 19.445), (12.421, 4.654), (25.054, 11.834),
                   (45.324, 12.734), (51.224, 20.68), (51.003, 14.772),
                   (55.69, 13.281), (60.598, 15.077), (60.577, 20.072)]

wifi_location_px = [(346.507, 767.985), (702.367, 1167.342), (1043.458, 973.482),
                    (1590.748, 949.182), (1750.048, 734.64), (1744.081, 894.156),
                    (1870.63, 934.413), (2003.146, 885.921), (2002.579, 751.056)]

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
    if axis=="x":
        return value * 3 + ORIGIN[0]
    else:
        return ORIGIN[1] - 615 + value * 3

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
    def __init__(self, folder):
        self.folder = folder # all data needed
        self.path_reference = self.get_path_reference() # all the calculated step value from Julia - tuple of degree and distance
        self.start_point, self.ground_path = self.get_ground_truth() # start point in m, true path step value - tuple of (x,y) in m
        self.dr_path = self.get_dr() # dead-reckoning path step value as of Julia calculated

        self.wifi = []
        self.corrected_path = []
        # print self.wifi
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
            # self.wifi = f.readline().split()[1].split(',')
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
    def get_map_match_path(self):
        

    def draw_wifi_correction(self):
        pass


class MapObject(object):
    def __init__(self, folder):
        self.map_size = (1770, 615) # in pixels 1770 wide, 615 tall
        self.map_size_in_m = (65.5, 22.8) # in meters
        self.map_array_2d_obs = [[0 for x in range(590)] for y in range(205)] # quantized block - 3 x 3pixels per block
        self.path = PathGen(folder)
        self.quantize_obs_block()

    def plot_important_points(self, plt):
        plt.plot(ORIGIN[0], ORIGIN[1], 'r^')
        plt.plot(ORIGIN[0]+self.map_size[0], ORIGIN[1]-self.map_size[1], 'r^')

    def plot_ground_truth(self, plt):
        (x_truth, y_truth) = separate_tuple(self.path.ground_path)
        plt.plot(x_truth, y_truth, 'bx')

    def plot_dr(self, plt):
        (x_dr, y_dr) = separate_tuple(self.path.dr_path)
        plt.plot(x_dr, y_dr, 'ro')

    # These two are binary checks
    def inconsistent(self, coords, map_array):
        inconsistent_coords_index = []
        print coords
        for i,coord in enumerate(coords):
            if map_array[coord[1]][coord[0]] == 1:
                inconsistent_coords_index.append(i)
        return inconsistent_coords_index

    def inconsistent_point(self, coord, map_array):
        return map_array[coord[1]][coord[0]] == 1

    def plot_map(self, plt):
        dr_steps = self.path.dr_path
        dr_missteps = []
        quantized_dr_steps = map(lambda x: quantize_pixel(x), dr_steps)
        for i, step in enumerate(quantized_dr_steps):
            self.path.corrected_path.append(step)
            if self.inconsistent_point(step, self.map_array_2d_obs):
                #correction
                dr_missteps.append((step, i))
                # print step

        x_axis_right = []
        y_axis_right = []
        x_axis = []
        y_axis = []

        step1 = dr_missteps[0][0]
        refer = self.path.path_reference[dr_missteps[0][1]]
        prev_step = quantize_pixel(dr_steps[dr_missteps[0][1]-1])
        next_step = quantize_pixel(dr_steps[dr_missteps[0][1]+1])
        # print step1, prev_step, next_step
        stepobj = StepMatrix(step1, refer, prev_step, self.map_array_2d_obs)
        for i in range(step1[0]-10, step1[0]+10):
            for j in range(step1[1]-10, step1[1]+10):
                x_axis.append(convert_quantize_to_px('x', i))
                y_axis.append(convert_quantize_to_px('y', j))
        # print dr_steps
        # dr_missteps = self.inconsistent(quantize_pixels(dr_steps), self.map_array_2d_obs)
        for c in self.path.corrected_path:
            x_axis_right.append(c[0]  * 3 + ORIGIN[0])
            y_axis_right.append(ORIGIN[1] - self.map_size[1] + c[1] * 3)
        # for t in dr_missteps:
            # x_axis.append(t[0] * 3 + ORIGIN[0])
            # y_axis.append(ORIGIN[1] - self.map_size[1] + t[1] * 3)
        plt.plot(x_axis, y_axis, 'gs')
        plt.plot(x_axis_right, y_axis_right, 'yx')

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


    def quantize_obs_block(self):
        # set up obstacles based on map
        # use block (3 x 3 pixels equal one quantize block)
        for i in range(92):
            for j in range(388):
                self.map_array_2d_obs[i][j] = 1
        for i in range(109, 205):
            for j in range(0, 34):
                self.map_array_2d_obs[i][j] = 1
        for i in range(171, 205):
            for j in range(34, 164):
                self.map_array_2d_obs[i][j] = 1
        for i in range(109, 205):
            for j in range(164, 590):
                self.map_array_2d_obs[i][j] = 1
