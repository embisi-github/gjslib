#a Imports
from gjslib.math.line_sets import c_set_of_lines
from gjslib.math.quaternion import c_quaternion

#a c_point_mapping
class c_point_mapping(object):
    #f __init__
    def __init__(self):
        self.reset()
        pass
    #f reset
    def reset(self):
        self.image_mappings = {}
        self.descriptions = {}
        self.reference_positions = {}
        self.positions = {}
        self.images = {}
        pass
    #f get_images
    def get_images(self):
        return self.images.keys()
    #f get_image_data
    def get_image_data(self, image_name):
        return self.images[image_name]
    #f load_data_add_image
    def load_data_add_image(self, data):
        image_name = data[0]
        image_filename = data[1]
        image_size = (int(data[2])+0.0,int(data[3])+0.0)
        self.add_image(image=data[0], filename=image_filename, size=image_size)
        pass
    #f load_data_add_point
    def load_data_add_point(self, data):
        self.add_named_point(data[0],data[1])
        pass
    #f load_data_add_reference
    def load_data_add_reference(self, data):
        self.add_named_point(data[0])
        pass
    #f load_data_add_mapping
    def load_data_add_mapping(self, data):
        image = data[0]
        point = data[1]
        xy = (float(data[2]),float(data[3]))
        self.add_named_point(data[1])
        self.add_image_location(point, image, xy)
        pass
    #f load_data
    def load_data(self, data_filename):
        data_load_callbacks = {}
        data_load_callbacks["Images"] = (self.load_data_add_image,4)
        data_load_callbacks["Points"] = (self.load_data_add_point,2)
        data_load_callbacks["References"] = (self.load_data_add_reference,4)
        data_load_callbacks["Mapping"] = (self.load_data_add_mapping,4)
        f = open(data_filename,"r")
        if not f:
            raise Exception("Failed to read point mapping file '%s'"%data_filename)
        data_stage = "Images"
        for l in f:
            l = l.strip()
            if len(l)==0: continue
            if l[0]=='#': continue
            if l[1]=='-':
                if l[2:-1] in ["Images", "Points", "References", "Mapping"]:
                    data_stage = l[2:-1]
                    pass
                else:
                    raise Exception("Bad separator '%s' in mapping file"%l)
                continue
            data = l.split(',')
            for i in range(len(data)):
                data[i] = data[i].strip()
                pass
            (cb,min_args) = data_load_callbacks[data_stage]
            if len(data)<min_args:
                raise Exception("Needed more arguments (at least %d) in line '%s' of mapping file for '%s'"%(min_args,l,data_stage))
            cb(data)
            pass
        f.close()

        # This is initial, references points only
        self.images['left']['projection'] = {'fov': 90, 'camera': [0.012699999999999979, -30.0, 30.0], 'orientation': c_quaternion({'r':-0.2153, 'i':-0.1943, 'j':-0.1821, 'k':-0.9395}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [30, -30.0, 30.0], 'orientation': c_quaternion({'r':-0.2153, 'i':-0.1943, 'j':-0.1821, 'k':-0.9395}), 'aspect': 1.0}

        # After initial quaternions (pretty rubbish camera guesses)
        self.images['left']['projection'] = {'fov': 90, 'camera': [0.012699999999999979, -30.0, 30.0], 'orientation': c_quaternion({'r': 0.8800, 'i': 0.4484, 'j':-0.0710, 'k':-0.1394}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [30, -30.0, 30.0], 'orientation': c_quaternion({'r': 0.8803, 'i': 0.4211, 'j': 0.2078, 'k': 0.0675}), 'aspect': 1.0}

        # Optimize based on reference points using delta_scale=0.3
        self.images['left']['projection'] = {'fov': 90, 'camera': [0.6067000000000005, -29.405999999999977, 30.0], 'orientation': c_quaternion({'r': 0.8615, 'i': 0.4506, 'j':-0.0312, 'k':-0.2320}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [1.2066999999999934, -28.805999999999955, 30.0], 'orientation': c_quaternion({'r': 0.8639, 'i': 0.4462, 'j':-0.0266, 'k':-0.2324}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [1.8066999999999718, -28.205999999999932, 30.0], 'orientation': c_quaternion({'r': 0.8667, 'i': 0.4413, 'j':-0.0224, 'k':-0.2316}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [2.4066999999999803, -27.60599999999991, 30.0], 'orientation': c_quaternion({'r': 0.8691, 'i': 0.4371, 'j':-0.0180, 'k':-0.2309}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [3.006700000000003, -27.005999999999887, 30.0], 'orientation': c_quaternion({'r': 0.8718, 'i': 0.4320, 'j':-0.0132, 'k':-0.2305}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [3.6067000000000258, -26.405999999999864, 30.0], 'orientation': c_quaternion({'r': 0.8743, 'i': 0.4269, 'j':-0.0087, 'k':-0.2308}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [4.2067000000000485, -25.80599999999984, 30.0], 'orientation': c_quaternion({'r': 0.8769, 'i': 0.4218, 'j':-0.0039, 'k':-0.2304}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [4.806700000000071, -25.20599999999982, 30.0], 'orientation': c_quaternion({'r': 0.8795, 'i': 0.4166, 'j': 0.0010, 'k':-0.2299}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [5.406700000000094, -24.605999999999796, 30.0], 'orientation': c_quaternion({'r': 0.8821, 'i': 0.4114, 'j': 0.0058, 'k':-0.2295}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [6.006700000000117, -24.005999999999773, 30.0], 'orientation': c_quaternion({'r': 0.8848, 'i': 0.4054, 'j': 0.0111, 'k':-0.2293}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [6.6067000000001395, -23.40599999999975, 30.0], 'orientation': c_quaternion({'r': 0.8872, 'i': 0.4000, 'j': 0.0166, 'k':-0.2291}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [7.206700000000162, -22.805999999999727, 30.0], 'orientation': c_quaternion({'r': 0.8901, 'i': 0.3941, 'j': 0.0216, 'k':-0.2280}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [7.806700000000185, -22.205999999999705, 30.0], 'orientation': c_quaternion({'r': 0.8927, 'i': 0.3879, 'j': 0.0269, 'k':-0.2278}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [8.406700000000207, -21.605999999999682, 30.0], 'orientation': c_quaternion({'r': 0.8952, 'i': 0.3818, 'j': 0.0322, 'k':-0.2276}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [9.00670000000023, -21.00599999999966, 30.0], 'orientation': c_quaternion({'r': 0.8981, 'i': 0.3749, 'j': 0.0377, 'k':-0.2267}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [9.606700000000252, -20.405999999999636, 30.0], 'orientation': c_quaternion({'r': 0.9005, 'i': 0.3685, 'j': 0.0436, 'k':-0.2267}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [10.206700000000275, -19.805999999999614, 30.0], 'orientation': c_quaternion({'r': 0.9031, 'i': 0.3616, 'j': 0.0488, 'k':-0.2265}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [10.806700000000298, -19.20599999999959, 30.0], 'orientation': c_quaternion({'r': 0.9057, 'i': 0.3545, 'j': 0.0549, 'k':-0.2258}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.40670000000032, -18.605999999999568, 30.0], 'orientation': c_quaternion({'r': 0.9081, 'i': 0.3473, 'j': 0.0607, 'k':-0.2258}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.628700000000329, -18.005999999999545, 30.0], 'orientation': c_quaternion({'r': 0.9104, 'i': 0.3413, 'j': 0.0619, 'k':-0.2256}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.625700000000329, -17.405999999999523, 30.0], 'orientation': c_quaternion({'r': 0.9124, 'i': 0.3358, 'j': 0.0606, 'k':-0.2260}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.622700000000329, -16.8059999999995, 30.0], 'orientation': c_quaternion({'r': 0.9147, 'i': 0.3296, 'j': 0.0590, 'k':-0.2264}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.616700000000328, -16.205999999999477, 30.0], 'orientation': c_quaternion({'r': 0.9166, 'i': 0.3241, 'j': 0.0577, 'k':-0.2267}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.613700000000328, -15.605999999999455, 30.0], 'orientation': c_quaternion({'r': 0.9188, 'i': 0.3179, 'j': 0.0561, 'k':-0.2271}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.607700000000328, -15.305999999999443, 29.69999999999999], 'orientation': c_quaternion({'r': 0.9190, 'i': 0.3173, 'j': 0.0560, 'k':-0.2272}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.604700000000328, -15.065999999999434, 29.339999999999975], 'orientation': c_quaternion({'r': 0.9190, 'i': 0.3173, 'j': 0.0560, 'k':-0.2272}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.601700000000328, -14.789999999999424, 29.015999999999963], 'orientation': c_quaternion({'r': 0.9193, 'i': 0.3166, 'j': 0.0558, 'k':-0.2272}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.595700000000328, -14.546999999999414, 28.65899999999995], 'orientation': c_quaternion({'r': 0.9193, 'i': 0.3166, 'j': 0.0558, 'k':-0.2272}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.592700000000328, -14.273999999999404, 28.331999999999937], 'orientation': c_quaternion({'r': 0.9195, 'i': 0.3159, 'j': 0.0556, 'k':-0.2272}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.586700000000327, -14.033999999999395, 27.971999999999923], 'orientation': c_quaternion({'r': 0.9195, 'i': 0.3159, 'j': 0.0556, 'k':-0.2272}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.583700000000327, -13.760999999999385, 27.64499999999991], 'orientation': c_quaternion({'r': 0.9197, 'i': 0.3152, 'j': 0.0555, 'k':-0.2273}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.577700000000327, -13.520999999999376, 27.284999999999897], 'orientation': c_quaternion({'r': 0.9197, 'i': 0.3152, 'j': 0.0555, 'k':-0.2273}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.610700000000328, -13.220999999999364, 26.987999999999886], 'orientation': c_quaternion({'r': 0.9202, 'i': 0.3136, 'j': 0.0558, 'k':-0.2276}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.604700000000328, -12.980999999999355, 26.627999999999872], 'orientation': c_quaternion({'r': 0.9202, 'i': 0.3136, 'j': 0.0558, 'k':-0.2276}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.598700000000328, -12.710999999999345, 26.29799999999986], 'orientation': c_quaternion({'r': 0.9204, 'i': 0.3129, 'j': 0.0556, 'k':-0.2276}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.595700000000328, -12.443999999999335, 25.964999999999847], 'orientation': c_quaternion({'r': 0.9206, 'i': 0.3122, 'j': 0.0555, 'k':-0.2277}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.586700000000327, -12.176999999999325, 25.631999999999834], 'orientation': c_quaternion({'r': 0.9209, 'i': 0.3115, 'j': 0.0553, 'k':-0.2277}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.580700000000327, -11.909999999999314, 25.298999999999822], 'orientation': c_quaternion({'r': 0.9211, 'i': 0.3108, 'j': 0.0551, 'k':-0.2278}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.574700000000327, -11.642999999999304, 24.96599999999981], 'orientation': c_quaternion({'r': 0.9213, 'i': 0.3102, 'j': 0.0549, 'k':-0.2278}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.568700000000327, -11.348999999999293, 24.659999999999798], 'orientation': c_quaternion({'r': 0.9218, 'i': 0.3088, 'j': 0.0546, 'k':-0.2279}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.559700000000326, -11.084999999999283, 24.323999999999785], 'orientation': c_quaternion({'r': 0.9220, 'i': 0.3081, 'j': 0.0544, 'k':-0.2279}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.553700000000326, -10.793999999999272, 24.014999999999773], 'orientation': c_quaternion({'r': 0.9225, 'i': 0.3067, 'j': 0.0541, 'k':-0.2280}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.544700000000326, -10.505999999999261, 23.70299999999976], 'orientation': c_quaternion({'r': 0.9230, 'i': 0.3053, 'j': 0.0538, 'k':-0.2281}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.538700000000325, -10.21499999999925, 23.39399999999975], 'orientation': c_quaternion({'r': 0.9234, 'i': 0.3039, 'j': 0.0534, 'k':-0.2282}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.529700000000325, -9.902999999999238, 23.10599999999974], 'orientation': c_quaternion({'r': 0.9241, 'i': 0.3018, 'j': 0.0529, 'k':-0.2283}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.520700000000325, -9.587999999999226, 22.820999999999728], 'orientation': c_quaternion({'r': 0.9248, 'i': 0.2998, 'j': 0.0524, 'k':-0.2284}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.526700000000325, -9.278999999999215, 22.529999999999717], 'orientation': c_quaternion({'r': 0.9252, 'i': 0.2975, 'j': 0.0523, 'k':-0.2295}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.517700000000325, -8.969999999999203, 22.238999999999706], 'orientation': c_quaternion({'r': 0.9259, 'i': 0.2955, 'j': 0.0518, 'k':-0.2296}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.508700000000324, -8.63699999999919, 21.971999999999696], 'orientation': c_quaternion({'r': 0.9268, 'i': 0.2927, 'j': 0.0511, 'k':-0.2297}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.496700000000324, -8.300999999999178, 21.707999999999686], 'orientation': c_quaternion({'r': 0.9279, 'i': 0.2892, 'j': 0.0503, 'k':-0.2299}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.487700000000324, -7.949999999999164, 21.458999999999676], 'orientation': c_quaternion({'r': 0.9287, 'i': 0.2864, 'j': 0.0496, 'k':-0.2301}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.475700000000323, -7.56899999999915, 21.239999999999668], 'orientation': c_quaternion({'r': 0.9300, 'i': 0.2822, 'j': 0.0485, 'k':-0.2303}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.463700000000323, -7.193999999999136, 21.01499999999966], 'orientation': c_quaternion({'r': 0.9313, 'i': 0.2780, 'j': 0.0475, 'k':-0.2305}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.454700000000322, -6.794999999999121, 20.813999999999652], 'orientation': c_quaternion({'r': 0.9327, 'i': 0.2731, 'j': 0.0463, 'k':-0.2308}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.442700000000322, -6.374999999999105, 20.633999999999645], 'orientation': c_quaternion({'r': 0.9344, 'i': 0.2675, 'j': 0.0449, 'k':-0.2310}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.39470000000032, -5.936999999999088, 20.47199999999964], 'orientation': c_quaternion({'r': 0.9362, 'i': 0.2614, 'j': 0.0426, 'k':-0.2311}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.256700000000315, -5.477999999999071, 20.330999999999634], 'orientation': c_quaternion({'r': 0.9380, 'i': 0.2549, 'j': 0.0386, 'k':-0.2315}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [11.11870000000031, -4.991999999999052, 20.21699999999963], 'orientation': c_quaternion({'r': 0.9398, 'i': 0.2484, 'j': 0.0346, 'k':-0.2320}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [10.917700000000302, -4.463999999999032, 20.144999999999627], 'orientation': c_quaternion({'r': 0.9421, 'i': 0.2402, 'j': 0.0286, 'k':-0.2321}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [10.683700000000293, -3.9419999999990125, 20.066999999999624], 'orientation': c_quaternion({'r': 0.9440, 'i': 0.2326, 'j': 0.0226, 'k':-0.2328}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [10.266700000000277, -3.3929999999989917, 20.01599999999962], 'orientation': c_quaternion({'r': 0.9460, 'i': 0.2244, 'j': 0.0126, 'k':-0.2334}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [9.80770000000026, -2.849999999998971, 19.95899999999962], 'orientation': c_quaternion({'r': 0.9477, 'i': 0.2171, 'j': 0.0020, 'k':-0.2338}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [9.315700000000241, -2.29499999999895, 19.913999999999618], 'orientation': c_quaternion({'r': 0.9492, 'i': 0.2093, 'j':-0.0097, 'k':-0.2347}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [8.874700000000225, -1.9379999999989412, 19.856999999999616], 'orientation': c_quaternion({'r': 0.9501, 'i': 0.2048, 'j':-0.0194, 'k':-0.2343}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [8.874700000000225, -1.9379999999989412, 19.856999999999616], 'orientation': c_quaternion({'r': 0.9501, 'i': 0.2048, 'j':-0.0194, 'k':-0.2343}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [8.874700000000225, -1.9379999999989412, 19.856999999999616], 'orientation': c_quaternion({'r': 0.9501, 'i': 0.2048, 'j':-0.0194, 'k':-0.2343}), 'aspect': 1.0}
        self.images['left']['projection'] = {'fov': 90, 'camera': [8.874700000000225, -1.9379999999989412, 19.856999999999616], 'orientation': c_quaternion({'r': 0.9501, 'i': 0.2048, 'j':-0.0194, 'k':-0.2343}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [29.405999999999977, -29.405999999999977, 30.0], 'orientation': c_quaternion({'r': 0.8592, 'i': 0.4833, 'j': 0.1443, 'k': 0.0859}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [28.805999999999955, -28.805999999999955, 30.0], 'orientation': c_quaternion({'r': 0.8617, 'i': 0.4800, 'j': 0.1403, 'k': 0.0852}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [28.205999999999932, -28.205999999999932, 30.0], 'orientation': c_quaternion({'r': 0.8646, 'i': 0.4762, 'j': 0.1364, 'k': 0.0844}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [27.60599999999991, -27.60599999999991, 30.0], 'orientation': c_quaternion({'r': 0.8668, 'i': 0.4734, 'j': 0.1320, 'k': 0.0849}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [27.005999999999887, -27.005999999999887, 30.0], 'orientation': c_quaternion({'r': 0.8696, 'i': 0.4695, 'j': 0.1278, 'k': 0.0834}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [26.405999999999864, -26.405999999999864, 30.0], 'orientation': c_quaternion({'r': 0.8721, 'i': 0.4661, 'j': 0.1235, 'k': 0.0838}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [25.80599999999984, -25.80599999999984, 30.0], 'orientation': c_quaternion({'r': 0.8749, 'i': 0.4621, 'j': 0.1188, 'k': 0.0833}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [25.20599999999982, -25.20599999999982, 30.0], 'orientation': c_quaternion({'r': 0.8776, 'i': 0.4581, 'j': 0.1146, 'k': 0.0819}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [24.605999999999796, -24.605999999999796, 30.0], 'orientation': c_quaternion({'r': 0.8805, 'i': 0.4540, 'j': 0.1093, 'k': 0.0818}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [24.005999999999773, -24.005999999999773, 30.0], 'orientation': c_quaternion({'r': 0.8832, 'i': 0.4499, 'j': 0.1047, 'k': 0.0814}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [23.40599999999975, -23.40599999999975, 30.0], 'orientation': c_quaternion({'r': 0.8859, 'i': 0.4457, 'j': 0.0994, 'k': 0.0813}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [22.805999999999727, -22.805999999999727, 30.0], 'orientation': c_quaternion({'r': 0.8886, 'i': 0.4415, 'j': 0.0941, 'k': 0.0812}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [22.205999999999705, -22.205999999999705, 30.0], 'orientation': c_quaternion({'r': 0.8916, 'i': 0.4368, 'j': 0.0892, 'k': 0.0800}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [21.605999999999682, -21.605999999999682, 30.0], 'orientation': c_quaternion({'r': 0.8945, 'i': 0.4319, 'j': 0.0836, 'k': 0.0792}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [21.00599999999966, -21.00599999999966, 30.0], 'orientation': c_quaternion({'r': 0.8974, 'i': 0.4270, 'j': 0.0784, 'k': 0.0790}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [20.405999999999636, -20.405999999999636, 30.0], 'orientation': c_quaternion({'r': 0.9002, 'i': 0.4219, 'j': 0.0724, 'k': 0.0791}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [19.805999999999614, -19.805999999999614, 30.0], 'orientation': c_quaternion({'r': 0.9031, 'i': 0.4170, 'j': 0.0669, 'k': 0.0783}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [19.20599999999959, -19.20599999999959, 30.0], 'orientation': c_quaternion({'r': 0.9062, 'i': 0.4113, 'j': 0.0607, 'k': 0.0777}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [18.605999999999568, -18.605999999999568, 30.0], 'orientation': c_quaternion({'r': 0.9088, 'i': 0.4062, 'j': 0.0547, 'k': 0.0778}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [18.005999999999545, -18.005999999999545, 30.0], 'orientation': c_quaternion({'r': 0.9118, 'i': 0.4004, 'j': 0.0485, 'k': 0.0771}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [17.405999999999523, -17.405999999999523, 30.0], 'orientation': c_quaternion({'r': 0.9150, 'i': 0.3939, 'j': 0.0423, 'k': 0.0765}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [16.8059999999995, -16.8059999999995, 30.0], 'orientation': c_quaternion({'r': 0.9178, 'i': 0.3880, 'j': 0.0354, 'k': 0.0761}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [16.205999999999477, -16.205999999999477, 30.0], 'orientation': c_quaternion({'r': 0.9205, 'i': 0.3821, 'j': 0.0292, 'k': 0.0755}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [15.605999999999455, -15.605999999999455, 30.0], 'orientation': c_quaternion({'r': 0.9235, 'i': 0.3755, 'j': 0.0224, 'k': 0.0751}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [15.005999999999432, -15.005999999999432, 30.0], 'orientation': c_quaternion({'r': 0.9264, 'i': 0.3688, 'j': 0.0155, 'k': 0.0747}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [14.405999999999409, -14.405999999999409, 30.0], 'orientation': c_quaternion({'r': 0.9291, 'i': 0.3620, 'j': 0.0087, 'k': 0.0743}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [13.841999999999388, -13.841999999999388, 29.964], 'orientation': c_quaternion({'r': 0.9315, 'i': 0.3560, 'j': 0.0020, 'k': 0.0746}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [13.62299999999938, -13.62299999999938, 29.582999999999984], 'orientation': c_quaternion({'r': 0.9316, 'i': 0.3557, 'j':-0.0010, 'k': 0.0750}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [13.424999999999372, -13.424999999999372, 29.18099999999997], 'orientation': c_quaternion({'r': 0.9314, 'i': 0.3563, 'j':-0.0030, 'k': 0.0741}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [13.259999999999366, -13.259999999999366, 28.745999999999952], 'orientation': c_quaternion({'r': 0.9312, 'i': 0.3569, 'j':-0.0054, 'k': 0.0742}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [13.10399999999936, -13.10399999999936, 28.301999999999936], 'orientation': c_quaternion({'r': 0.9307, 'i': 0.3581, 'j':-0.0072, 'k': 0.0741}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [12.956999999999354, -12.956999999999354, 27.84899999999992], 'orientation': c_quaternion({'r': 0.9302, 'i': 0.3594, 'j':-0.0090, 'k': 0.0739}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [12.782999999999348, -12.782999999999348, 27.422999999999902], 'orientation': c_quaternion({'r': 0.9300, 'i': 0.3599, 'j':-0.0114, 'k': 0.0740}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [12.620999999999341, -12.620999999999341, 26.984999999999886], 'orientation': c_quaternion({'r': 0.9295, 'i': 0.3611, 'j':-0.0139, 'k': 0.0741}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [12.440999999999335, -12.440999999999335, 26.56499999999987], 'orientation': c_quaternion({'r': 0.9292, 'i': 0.3617, 'j':-0.0163, 'k': 0.0742}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [12.281999999999329, -12.281999999999329, 26.123999999999853], 'orientation': c_quaternion({'r': 0.9287, 'i': 0.3629, 'j':-0.0188, 'k': 0.0743}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [12.092999999999321, -12.092999999999321, 25.712999999999838], 'orientation': c_quaternion({'r': 0.9285, 'i': 0.3634, 'j':-0.0214, 'k': 0.0737}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.933999999999315, -11.933999999999315, 25.27199999999982], 'orientation': c_quaternion({'r': 0.9279, 'i': 0.3646, 'j':-0.0239, 'k': 0.0738}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.747999999999308, -11.747999999999308, 24.857999999999805], 'orientation': c_quaternion({'r': 0.9277, 'i': 0.3651, 'j':-0.0266, 'k': 0.0732}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.732999999999308, -11.5259999999993, 24.47999999999979], 'orientation': c_quaternion({'r': 0.9277, 'i': 0.3651, 'j':-0.0266, 'k': 0.0732}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.732999999999308, -11.294999999999291, 24.110999999999777], 'orientation': c_quaternion({'r': 0.9277, 'i': 0.3651, 'j':-0.0266, 'k': 0.0732}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.732999999999308, -11.066999999999283, 23.738999999999763], 'orientation': c_quaternion({'r': 0.9277, 'i': 0.3651, 'j':-0.0266, 'k': 0.0732}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.732999999999308, -10.781999999999272, 23.42399999999975], 'orientation': c_quaternion({'r': 0.9283, 'i': 0.3637, 'j':-0.0265, 'k': 0.0732}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.735999999999308, -10.499999999999261, 23.10599999999974], 'orientation': c_quaternion({'r': 0.9288, 'i': 0.3623, 'j':-0.0264, 'k': 0.0733}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.735999999999308, -10.19399999999925, 22.811999999999728], 'orientation': c_quaternion({'r': 0.9296, 'i': 0.3602, 'j':-0.0262, 'k': 0.0733}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.735999999999308, -9.893999999999238, 22.511999999999716], 'orientation': c_quaternion({'r': 0.9304, 'i': 0.3581, 'j':-0.0261, 'k': 0.0734}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.735999999999308, -9.587999999999226, 22.217999999999705], 'orientation': c_quaternion({'r': 0.9312, 'i': 0.3560, 'j':-0.0259, 'k': 0.0735}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.735999999999308, -9.284999999999215, 21.920999999999694], 'orientation': c_quaternion({'r': 0.9320, 'i': 0.3539, 'j':-0.0257, 'k': 0.0735}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.717999999999307, -8.960999999999203, 21.644999999999683], 'orientation': c_quaternion({'r': 0.9331, 'i': 0.3511, 'j':-0.0258, 'k': 0.0729}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.717999999999307, -8.61599999999919, 21.389999999999674], 'orientation': c_quaternion({'r': 0.9344, 'i': 0.3476, 'j':-0.0255, 'k': 0.0730}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.717999999999307, -8.270999999999177, 21.134999999999664], 'orientation': c_quaternion({'r': 0.9357, 'i': 0.3441, 'j':-0.0252, 'k': 0.0731}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.717999999999307, -7.904999999999163, 20.900999999999655], 'orientation': c_quaternion({'r': 0.9373, 'i': 0.3399, 'j':-0.0249, 'k': 0.0732}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.717999999999307, -7.541999999999149, 20.663999999999646], 'orientation': c_quaternion({'r': 0.9388, 'i': 0.3357, 'j':-0.0246, 'k': 0.0733}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.720999999999307, -7.157999999999134, 20.447999999999638], 'orientation': c_quaternion({'r': 0.9406, 'i': 0.3307, 'j':-0.0242, 'k': 0.0734}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.720999999999307, -6.749999999999119, 20.25599999999963], 'orientation': c_quaternion({'r': 0.9425, 'i': 0.3251, 'j':-0.0237, 'k': 0.0736}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.720999999999307, -6.323999999999103, 20.081999999999624], 'orientation': c_quaternion({'r': 0.9447, 'i': 0.3187, 'j':-0.0232, 'k': 0.0737}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.699999999999307, -5.852999999999085, 19.95299999999962], 'orientation': c_quaternion({'r': 0.9473, 'i': 0.3109, 'j':-0.0229, 'k': 0.0732}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.699999999999307, -5.384999999999067, 19.820999999999614], 'orientation': c_quaternion({'r': 0.9499, 'i': 0.3031, 'j':-0.0223, 'k': 0.0734}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.699999999999307, -4.883999999999048, 19.72199999999961], 'orientation': c_quaternion({'r': 0.9526, 'i': 0.2945, 'j':-0.0216, 'k': 0.0736}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.696999999999306, -4.352999999999028, 19.652999999999608], 'orientation': c_quaternion({'r': 0.9556, 'i': 0.2845, 'j':-0.0208, 'k': 0.0738}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.693999999999306, -3.791999999999007, 19.613999999999606], 'orientation': c_quaternion({'r': 0.9587, 'i': 0.2737, 'j':-0.0200, 'k': 0.0741}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.690999999999306, -3.2009999999989844, 19.604999999999606], 'orientation': c_quaternion({'r': 0.9620, 'i': 0.2622, 'j':-0.0191, 'k': 0.0743}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.687999999999306, -2.6009999999989617, 19.604999999999606], 'orientation': c_quaternion({'r': 0.9652, 'i': 0.2499, 'j':-0.0182, 'k': 0.0745}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.669999999999305, -2.000999999998939, 19.604999999999606], 'orientation': c_quaternion({'r': 0.9684, 'i': 0.2376, 'j':-0.0174, 'k': 0.0740}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.663999999999305, -1.499999999998957, 19.70399999999961], 'orientation': c_quaternion({'r': 0.9708, 'i': 0.2274, 'j':-0.0166, 'k': 0.0742}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.663999999999305, -1.4639999999989584, 19.72799999999961], 'orientation': c_quaternion({'r': 0.9710, 'i': 0.2267, 'j':-0.0166, 'k': 0.0742}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.663999999999305, -1.4639999999989584, 19.72799999999961], 'orientation': c_quaternion({'r': 0.9710, 'i': 0.2267, 'j':-0.0166, 'k': 0.0742}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.663999999999305, -1.4639999999989584, 19.72799999999961], 'orientation': c_quaternion({'r': 0.9710, 'i': 0.2267, 'j':-0.0166, 'k': 0.0742}), 'aspect': 1.0}

        # Then delta_scale of 0.03 - eventually to these
        self.images['left']['projection'] = {'fov': 90, 'camera': [7.342600000001848, -1.967999999998938, 19.46610000000052], 'orientation': c_quaternion({'r': 0.9469, 'i': 0.2140, 'j':-0.0482, 'k':-0.2347}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 90, 'camera': [11.655899999999317, -1.147799999998991, 19.829399999999396], 'orientation': c_quaternion({'r': 0.9727, 'i': 0.2195, 'j':-0.0161, 'k': 0.0745}), 'aspect': 1.0}

        # Then try optimizing all - adjust points to match first...
        self.images['left']['projection'] = {'fov': 91.25042050666212, 'camera': [7.226200000001775, -1.6517999999989728, 19.040100000001512], 'orientation': c_quaternion({'r': 0.9479, 'i': 0.2122, 'j':-0.0545, 'k':-0.2310}), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 88.71309491219532, 'camera': [12.11369999999825, -1.5233999999989496, 20.141699999998668], 'orientation': c_quaternion({'r': 0.9720, 'i': 0.2239, 'j':-0.0064, 'k': 0.0715}), 'aspect': 1.0}

        # optimizing to get it in euler format
        self.images['left']['projection'] = {'fov': 91.35997029635297, 'camera': [7.2223000000017725, -1.6367999999989744, 19.01070000000158], 'orientation': c_quaternion(euler=(-27.4649,-0.3220,25.3080),degrees=True), 'aspect': 1.0}
        self.images['middle']['projection'] = {'fov': 88.60668709379165, 'camera': [12.134099999998202, -1.5395999999989478, 20.169299999998604], 'orientation': c_quaternion(euler=( 7.8401,-2.5141,25.7756),degrees=True), 'aspect': 1.0}

        return
        # horizontal FOV for 35mm camera: 12.5mm:110 15mm:100 18mm:90 20mm:85 23mm:75 28mm:65 31mm:60 35mm:55 40mm:50 50mm:40 54mm:35 65mm:30 80mm:35 100mm:20
        # yaw is left-right (-ve,+ve)
        # pitch is -ve up
        # roll is clockwise +ve
        # Can now do initial plus optimization (at delta_scale 0.1)
        # This you do with the reference objects
        self.images['img_1']['projection'] = {'fov': 68.33999999999999, 'camera': [5.303600000000904, -8.318100000001156, 9.881700000000029], 'orientation': c_quaternion({'r': 0.7545, 'i': 0.5657, 'j': 0.2373, 'k': 0.2330}), 'aspect': 1.3}
        self.images['main']['projection'] = {'fov': 84.575, 'camera': [-4.695799999997939, -14.592999999998563, 2.773999999999937], 'orientation': c_quaternion({'r': 0.6208, 'i': 0.7191, 'j':-0.2353, 'k':-0.2052}), 'aspect': 1.5}

        # Refine img_1 with delta_scale 0.01 on reference objects
        self.images['img_1']['projection'] = {'fov': 68.33999999999999, 'camera': [5.200500000001144, -8.421200000000916, 9.918599999999943], 'orientation': c_quaternion({'r': 0.7575, 'i': 0.5655, 'j': 0.2342, 'k': 0.2269}), 'aspect': 1.3}
        self.images['main']['projection'] = {'fov': 84.575, 'camera': [-4.29609999999887, -14.992699999997631, 2.773999999999937], 'orientation': c_quaternion({'r': 0.6243, 'i': 0.7206, 'j':-0.2353, 'k':-0.1888}), 'aspect': 1.5}
        # Now change FOV delta - made it bigger, fov does not change (obviously) - so move it down to 0.01
        self.images['main']['projection'] = {'fov': 84.575, 'camera': [-3.9960999999995517, -15.292699999996932, 2.773999999999937], 'orientation': c_quaternion({'r': 0.6278, 'i': 0.7215, 'j':-0.2301, 'k':-0.1802}), 'aspect': 1.5}

        # Now one-then-other optimization
        self.images['main']['projection'] = {'fov': 84.575, 'camera': [-3.7760999999990874, -15.51269999999642, 2.773999999999937], 'orientation': c_quaternion({'r': 0.6305, 'i': 0.7222, 'j':-0.2243, 'k':-0.1751}), 'aspect': 1.5}
        self.images['img_1']['projection'] = {'fov': 68.33999999999999, 'camera': [5.100500000001377, -8.321200000001149, 9.918599999999943], 'orientation': c_quaternion({'r': 0.7589, 'i': 0.5645, 'j': 0.2363, 'k': 0.2225}), 'aspect': 1.3}

        #After moving some points - main is still moving in the same old direction
        self.images['img_1']['projection'] = {'fov': 68.33999999999999, 'camera': [4.993600000001626, -8.472800000000795, 9.90229999999998], 'orientation': c_quaternion({'r': 0.7607, 'i': 0.5670, 'j': 0.2328, 'k': 0.2133}), 'aspect': 1.3}        
        self.images['main']['projection'] = {'fov': 84.575, 'camera': [-3.5760999999986653, -15.712699999995953, 2.773999999999937], 'orientation': c_quaternion({'r': 0.6330, 'i': 0.7226, 'j':-0.2194, 'k':-0.1705}), 'aspect': 1.5}
        pass
    #f save_data
    def save_data(self, data_filename):
        f = open(data_filename,"w")

        point_names = self.image_mappings.keys()
        point_names.sort()

        image_names = self.images.keys()
        image_names.sort()

        print >>f, "--Images:"
        for name in image_names:
            image = self.images[name]
            print >>f,"%s,%s,%d,%d"%(name,image["filename"],image["size"][0],image["size"][1])
            pass
        print >>f, "\n"

        print >>f, "--Points:"
        for name in point_names:
            desc = ""
            if name in self.descriptions:
                desc = self.descriptions[name]
            print >>f, "%s,%s"%(name,desc)
            pass
        print >>f, "\n"

        print >>f, "--References:"
        print >>f, "\n"

        print >>f, "--Mapping:"
        for name in point_names:
            for image in image_names:
                if image in self.image_mappings[name]:
                    xy = self.image_mappings[name][image]
                    print >>f, "%s,%s,%f,%f"%(image,name,xy[0],xy[1])
                    pass
                pass
            pass
        print >>f, "\n"
        f.close()
        pass
    #f add_named_point
    def add_named_point(self,name,description=None):
        if name not in self.image_mappings:
            self.image_mappings[name] = {}
            pass
        if description is not None:
            self.descriptions[name]=description
            pass
        pass
    #f add_image
    def add_image(self,image, filename=None, size=(1.0,1.0), projection=None):
        if image not in self.images:
            self.images[image] = {}
            self.images[image]["filename"] = filename
            self.images[image]["projection"] = projection
            self.images[image]["size"] = size
            pass
        pass
    #f add_image_location
    def add_image_location(self,name,image,xy,uniform=False,verbose=False):
        if uniform:
            if uniform: xy = ((xy[0]+1.0)/2.0, (1.0-xy[1])/2.0)
            size = self.images[image]["size"]
            xy = (xy[0]*size[0],xy[1]*size[1])
            pass
        if verbose:
            v = "Setting point %s in image %s to %s"
            if image in self.image_mappings[name]:
                v = "Moving point %s in image %s to %s"
                pass
            print v%(name,image,str(xy))
            pass
        undo_op = (name,image,None)
        if image in self.image_mappings[name]:
            old_xy = self.image_mappings[name][image]
            undo_op = (name,image,(old_xy[0],old_xy[1]))
            pass
        self.image_mappings[name][image] = xy
        return undo_op
    #f delete_image_location
    def delete_image_location(self,name,image,verbose=False):
        if image not in self.image_mappings[name]:
            if verbose:
                print "Requested deleting point %s that is not in image %s"%(name,image)
                pass
            return None
        if verbose:
            print "Deleting point %s in image %s"%(name,image)
            pass
        undo_op = (name,image,self.image_mappings[name][image])
        del(self.image_mappings[name][image])
        return undo_op
    #f undo_add_image_location
    def undo_add_image_location(self, undo_op, verbose=False):
        (name, image, xy) = undo_op
        if xy is None:
            self.delete_image_location(name,image,verbose=verbose)
            pass
        else:
            self.add_image_location(name,image,xy,verbose=verbose)
            pass
        pass
    #f undo_delete_image_location
    def undo_delete_image_location(self, undo_op, verbose=False):
        if undo_op is None:
            return
        (name, image, xy) = undo_op
        self.add_image_location(name,image,xy,verbose=verbose)
        pass
    #f set_projection
    def set_projection(self,image,projection):
        self.images[image]["projection"] = projection
        pass
    #f get_mapping_names
    def get_mapping_names(self):
        return self.image_mappings.keys()
    #f get_xy
    def get_xy(self, name, image ):
        if name not in self.image_mappings:
            return None
        if image not in self.image_mappings[name]:
            return None
        return self.uniform_mapping(name,image)
    #f uniform_mapping
    def uniform_mapping(self, name, image):                                
        xy = self.image_mappings[name][image]
        scaled_xy = (-1.0+2.0*xy[0]/(self.images[image]["size"][0]+0.0), 1.0-2.0*xy[1]/(self.images[image]["size"][1]+0.0))
        return scaled_xy
    #f find_line_sets
    def find_line_sets(self):
        line_sets = {}
        for n in self.image_mappings:
            line_sets[n] = c_set_of_lines()
            for img_name in self.image_mappings[n].keys():
                ##if img_name not in ["main", "img_1"]: continue
                p = self.images[img_name]["projection"]
                if p is not None:
                    xy = self.uniform_mapping(n,img_name)
                    line = p.model_line_for_image(xy)
                    line_sets[n].add_line(line[0],line[1])
                    pass
                pass
            line_sets[n].generate_meeting_points()
            #print n, line_sets[n].line_meetings
            pass
        self.line_sets = line_sets
        pass
    #f approximate_positions
    def approximate_positions(self):
        for n in self.line_sets:
            self.positions[n] = self.line_sets[n].posn
            pass
        pass
    #f get_approx_position
    def get_approx_position(self, name ):
        if name not in self.positions:
            return None
        return self.positions[name]
    #f get_xyz
    def get_xyz(self, name, use_references=False ):
        # clk.center (  0.0, -0.2,   8.4)  error 7.421E-5
        # clk.center (  0.0, -0.25,  8.4)  error 7.265E-5
        # clk.center (  0.0, -0.30,  8.4)  error 0.8185E-5
        # clk.center (  0.0, -0.32,  8.4)  error 0.1824E-5
        # That was with tower spikes +-3.0
        object_guess_locations = {}
        object_guess_locations["clk.center"] = (  0.0, -0.32,  8.4)
        object_guess_locations["lspike.t"]   = ( -3.3,  0.0, 10.9)
        object_guess_locations["rspike.t"]   = (  3.3,  0.0, 10.9)

        object_guess_locations["calc.t.bl"]   = ( 10.2, 19.0, 2.0)
        object_guess_locations["calc.b.fr"]   = ( 24.0,  0.0, 0.0)
        object_guess_locations["clips.b.fr"]  = ( 0.0,   0.0, 0.0)
        if use_references:
            return None
        if name in object_guess_locations:
            return object_guess_locations[name]
        return self.get_approx_position(name)
    #f initial_orientation
    def initial_orientation(self, image=None, **kwargs):
        for image_name in self.images.keys():
            if (image is not None) and image!=image_name:
                continue
            proj = self.images[image_name]["projection"]
            projection = proj.guess_initial_orientation(point_mappings=self, **kwargs)
            print "self.images['%s']['projection'] = %s"%(image_name,str(projection))
            pass
    #f optimize_projections
    def optimize_projections(self, image=None, **kwargs):
        for image_name in self.images.keys():
            if (image is not None) and image!=image_name:
                continue
            proj = self.images[image_name]["projection"]
            projection = proj.optimize_projection(point_mappings=self, **kwargs)
            print "self.images['%s']['projection'] = %s"%(image_name,str(projection))
            pass
        pass
    #f Done
    pass

