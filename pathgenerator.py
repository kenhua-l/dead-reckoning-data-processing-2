import math

#CONSTANT
SCALE = 27
NORTH = 20
ORIGIN = (367, 1293) # in pixels (y is 1654-359)

wifi_location_m = [(-0.759, 19.445), (12.421, 4.654), (25.054, 11.834),
                   (45.324, 12.734), (51.224, 20.68), (51.003, 14.772),
                   (55.69, 13.281), (60.598, 15.077), (60.577, 20.072)]

wifi_location_px = [(346.507, 767.985), (702.367, 1167.342), (1043.458, 973.482),
                    (1590.748, 949.182), (1750.048, 734.64), (1744.081, 894.156),
                    (1870.63, 934.413), (2003.146, 885.921), (2002.579, 751.056)]

def convert_m_to_px((x,y)):
    real_x = x * SCALE + ORIGIN[0]
    real_y = ORIGIN[1] - y * SCALE
    return real_x, real_y

def convert_image_deg(deg):
    ans = (deg - 180) * -1
    if ans < 0:
        ans = ans + 360
    return ans

class PathGen(object):
    def __init__(self, folder):
        self.folder = folder # all data needed
        self.start_point = (0, 0) # initialized but will be known from ground_path.txt
        self.ground_path = self.get_ground_truth()
        self.dr_path = self.get_dr()
        print("PATHGEN created")

    def get_ground_truth(self):
        x_axis=[]
        y_axis=[]
        with open(self.folder+'/ground_path.txt', 'r') as f:
            start = f.readline().split()
            self.start_point = (float(start[1]), float(start[2]))
            start_x, start_y = convert_m_to_px(self.start_point)
            x_axis.append(start_x)
            y_axis.append(start_y)
            start_path_x, start_path_y = (start_x, start_y)
            for line in f:
                lines = line.split()
                steps = int(lines[0])
                direction = int(lines[1])
                end_x, end_y = convert_m_to_px((float(lines[2]), float(lines[3])))
                step_length = math.sqrt(pow(end_x - start_path_x, 2) + pow(end_y - start_path_y, 2)) / steps
                for i in xrange(steps):
                    x_axis.append(x_axis[-1] + step_length * math.sin(math.radians(direction)))
                    y_axis.append(y_axis[-1] + step_length * math.cos(math.radians(direction)))
                start_path_x, start_path_y = end_x, end_y
        return (x_axis, y_axis)

    def get_dr(self):
        x_axis, y_axis = convert_m_to_px(self.start_point)
        x_axis = [x_axis]
        y_axis = [y_axis]
        with open(self.folder+'/path.txt', 'r') as f:
            f.readline()
            for line in f:
                steps = line.split()
                deg = convert_image_deg(float(steps[0]) - NORTH)
                step_length = float(steps[1])
                x_axis.append(x_axis[-1] + SCALE * step_length * math.sin(math.radians(deg)))
                y_axis.append(y_axis[-1] + SCALE * step_length * math.cos(math.radians(deg)))
        return (x_axis, y_axis)

class MapObject(object):
    def __init__(self, folder):
        self.map_size = (1770, 615) # in pixels 1770 wide, 615 tall
        self.map_size_in_m = (65.5, 22.8) # in meters
        self.path = PathGen(folder)

    def plot_important_points(self, plt):
        plt.plot(ORIGIN[0], ORIGIN[1], 'r^')
        plt.plot(ORIGIN[0]+self.map_size[0], ORIGIN[1]-self.map_size[1], 'r^')

    def plot_ground_truth(self, plt):
        (x_truth, y_truth) = self.path.ground_path
        plt.plot(x_truth, y_truth, 'bx')

    def plot_dr(self, plt):
        (x_dr, y_dr) = self.path.dr_path
        plt.plot(x_dr, y_dr, 'ro')

    # def quantize()
