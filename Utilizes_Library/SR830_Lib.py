import pyvisa

# TODO: query error register to see if a fault condition exists (i.e. input overload, ...)


class SR830:
    """library to control / read out the Stanford Research Systems SR830 Lock-In Amplifier"""

    """
    ####################################################################################################################
    List of device specific commands and parameters based on 
    the programming section (5) of the manual (Starting at page 85)
    ####################################################################################################################
    """

    # general operations
    OPERATION_IDENTIFY = "*IDN?"
    OPERATION_RESET = "*RST"
    OPERATION_CLEAR = "*CLS"

    # operations concerning communication with the computer
    OPERATION_SEND_RESPONSE_TO_RS232 = "OUTX 0"
    OPERATION_SEND_RESPONSE_TO_GPIB = "OUTX 1"

    # operations / parameters for controlling the oscillator
    OPERATION_SET_TO_INTERNAL_REFERENCE = "FMOD 1"
    OPERATION_SET_TO_EXTERNAL_REFERENCE = "FMOD 0"
    OPERATION_SET_INTERNAL_REFERENCE_FREQUENCY = "FREQ"
    UPPER_FREQ_LIMIT = 102000       # Limit in Hz based on the specifications of the SR830
    LOWER_FREQ_LIMIT = 0.001

    OPERATION_SINE_OUTPUT_LEVEL = "SLVL"
    LOWER_SINE_OUTPUT_LEVEL = 0.004     # Limit in Volts based on the specifications of the SR830
    UPPER_SINE_OUTPUT_LEVEL = 5

    # operations that define the input characteristics
    OPERATION_SET_INPUT_TO_I_100M = "ISRC 3"
    OPERATION_SET_INPUT_TO_I_1M = "ISRC 2"
    OPERATION_SET_INPUT_TO_A = "ISRC 0"
    OPERATION_SET_INPUT_TO_A_MINUS_B = "ISRC 1"
    OPERATION_SET_INPUT_SHIELD_TO_FLOATING = "IGND 0"
    OPERATION_SET_INPUT_SHIELD_TO_GROUND = "IGND 1"
    OPERATION_SET_INPUT_COUPLING_AC = "ICPL 0"
    OPERATION_SET_INPUT_COUPLING_DC = "ICPL 1"

    OPERATION_DISABLE_LINE_FILTER = "ILIN 0"
    OPERATION_ENABLE_LINE_FILTER = "ILIN 3"

    # sensitivity commands
    OPERATION_SET_SENSITIVITY = "SENS"
    # Available sensitivity ranges in volts
    SENSITIVITY_RANGES = (2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9, 1000e-9,
                          2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 200e-6, 500e-6, 1000e-6,
                          2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3, 200e-3, 500e-3, 1000e-3)

    OPERATION_SET_RESERVE_MODE_HIGH_RESERVE = "RMOD 0"
    OPERATION_SET_RESERVE_MODE_NORMAL = "RMOD 1"
    OPERATION_SET_RESERVE_MODE_LOW_NOISE = "RMOD 2"
    
    OPERATION_SET_TIME_CONSTANT = "OFLT"
    # Available time constants in seconds
    TIME_CONSTANTS = (10e-6, 30e-6, 100e-6, 300e-6,
                      1e-3, 3e-3, 10e-3, 30e-3, 100e-3, 300e-3,
                      1, 3, 10, 30, 100, 300,
                      1e3, 3e3, 10e3, 30e3)

    OPERATION_LOW_PASS_FILTER_SLOPE = "OFSL"
    # Available filters slopes in dB/oct
    FILTER_SLOPES = (6, 12, 18, 24)

    # display commands
    OPERATION_SET_DISPLAY_CH1_TO_X = "DDEF 1, 0, 0"
    OPERATION_SET_DISPLAY_CH1_TO_R = "DDEF 1, 1, 0"
    OPERATION_SET_DISPLAY_CH2_TO_Y = "DDEF 2, 0, 0"
    OPERATION_SET_DISPLAY_CH2_TO_PHI = "DDEF 2, 1, 0"

    # auto functions
    OPERATION_AUTO_GAIN = "AGAN"
    OPERATION_AUTO_RESERVE = "ARSV"
    OPERATION_AUTO_PHASE = "APHS"
    OPERATION_AUTO_OFFSET_X = "AOFF 1"
    OPERATION_AUTO_OFFSET_Y = "AOFF 2"
    OPERATION_AUTO_OFFSET_R = "AOFF 3"

    # data transfer commands
    READ_X = "OUTP? 1"
    READ_Y = "OUTP? 2"
    READ_R = "OUTP? 3"
    READ_PHI = "OUTP? 4"

    # snap commands read data synchronously (important if time constant is very short)
    READ_SNAP_X_Y_R_PHI = "SNAP? 1, 2, 3, 4"

    """
    ####################################################################################################################
    General functions to communicate with the device
    ####################################################################################################################
    """

    def __init__(self, rm=None):

        # variable to store if the debug output was enabled
        self.__debug = False
        self.instrument = None

        # if we have no resource manager then get one
        if rm is None:
            self.rm = pyvisa.ResourceManager()
        else:
            self.rm = rm

    def enable_debug_output(self):
        """Enables the debug output of all communication.The messages will be printed on the console."""
        self.__debug = True

    def disable_debug_output(self):
        """Disables the debug output. Nothing will be printed to the console that you haven't specified yourself."""
        self.__debug = False

    def connect(self, visa_resource_name):

        # Connect to the device
        self.instrument = self.rm.open_resource(visa_resource_name)

        # define the termination characters as stated in the manual
        self.instrument.read_termination = '\n'
        self.instrument.write_termination = '\n'

        # clears the resource; if something was in the input buffer it gets lost
        self.instrument.clear()

        # send the appropriate command to respond to RS232 or GIPB based on the initial connection method
        if "ASRL3" in visa_resource_name:
            # we have a GPIB connection; command the device to also respond to the GPIB interface
            self._write(self.OPERATION_SEND_RESPONSE_TO_GPIB)
        else:
            # send responses to the serial interface
            self._write(self.OPERATION_SEND_RESPONSE_TO_RS232)

        # the instrument handle is returned although the user most likely doesn't need it
        return self.instrument

    def _write(self, msg):
        # if the debug output is enabled we dump the msg to the console
        if self.__debug:
            print('Write cmd: ' + str(msg))

        # send the command to the instrument
        self.instrument.write(msg)

    def _query(self, msg):
        # if the debug output is enabled we dump the msg to the console
        if self.__debug:
            print('Query cmd: ' + str(msg))

        # send the command to the instrument
        return self.instrument.query(msg)

    def _read(self):
        return self.instrument.read()

    def disconnect(self):
        self.instrument.close()

    def identify(self):
        return self._query(self.OPERATION_IDENTIFY)

    def reset(self):
        self._write(self.OPERATION_RESET)
        self._write(self.OPERATION_CLEAR)

    """
    ####################################################################################################################
    Instrument specific functions
    ####################################################################################################################
    """

    """ Oscillator / reference section """

    def use_external_reference(self):
        self._write(self.OPERATION_SET_TO_EXTERNAL_REFERENCE)

    def use_internal_reference(self):
        self._write(self.OPERATION_SET_TO_INTERNAL_REFERENCE)

    def set_reference_frequency(self, frequency_in_hz):
        if self.LOWER_FREQ_LIMIT <= frequency_in_hz <= self.UPPER_FREQ_LIMIT:
            msg = self.OPERATION_SET_INTERNAL_REFERENCE_FREQUENCY + " " + str(frequency_in_hz)
            self._write(msg)
        else:
            raise ValueError("Frequency must be within " + str(self.LOWER_FREQ_LIMIT) + " Hz to "
                             + str(self.UPPER_FREQ_LIMIT) + " Hz")

    def set_sine_output_level(self, voltage):
        if self.LOWER_SINE_OUTPUT_LEVEL <= voltage <= self.UPPER_SINE_OUTPUT_LEVEL:
            msg = self.OPERATION_SINE_OUTPUT_LEVEL + " " + str(voltage)
            self._write(msg)
        else:
            raise ValueError("Sine output voltage must be within " + str(self.LOWER_SINE_OUTPUT_LEVEL) + " V to "
                             + str(self.UPPER_SINE_OUTPUT_LEVEL) + " V")

    """ Input Mode section """

    def set_input_mode_A(self):
        self._write(self.OPERATION_SET_INPUT_TO_A)
        
    def set_input_mode_I_100M(self):
        self._write(self.OPERATION_SET_INPUT_TO_I_100M)
        
    def set_input_mode_I_1M(self):
        self._write(self.OPERATION_SET_INPUT_TO_I_1M)

    def set_input_mode_A_minus_B(self):
        self._write(self.OPERATION_SET_INPUT_TO_A_MINUS_B)

    def set_input_shield_to_floating(self):
        self._write(self.OPERATION_SET_INPUT_SHIELD_TO_FLOATING)

    def set_input_shield_to_ground(self):
        self._write(self.OPERATION_SET_INPUT_SHIELD_TO_GROUND)

    def set_input_coupling_ac(self):
        self._write(self.OPERATION_SET_INPUT_COUPLING_AC)

    def set_input_coupling_dc(self):
        self._write(self.OPERATION_SET_INPUT_COUPLING_DC)

    def enable_line_filters(self):
        self._write(self.OPERATION_ENABLE_LINE_FILTER)

    def disable_line_filters(self):
        self._write(self.OPERATION_DISABLE_LINE_FILTER)

    """ sensitivity / time constant section """

    def set_sensitivity(self, sensitivity_in_volt):

        # check the given values for a suitable range and return a value that is certainly available.
        # if the value is larger then the maximum available range, a error is raised
        value = self.find_suitable_range(sensitivity_in_volt, self.SENSITIVITY_RANGES)

        # get the index of the range. This is needed for the command that needs to be sent to the SR830
        range_index = self.SENSITIVITY_RANGES.index(value)

        # construct the command and sent it to the device
        cmd = self.OPERATION_SET_SENSITIVITY + " " + str(range_index)
        self._write(cmd)

    def set_time_constant(self, time_in_seconds):

        # check the given values for a suitable range and return a value that is certainly available.
        # if the value is larger then the maximum available range, a error is raised
        value = self.find_suitable_range(time_in_seconds, self.TIME_CONSTANTS)

        # get the index of the range. This is needed for the command that needs to be sent to the SR830
        range_index = self.TIME_CONSTANTS.index(value)

        # construct the command and sent it to the device
        cmd = self.OPERATION_SET_TIME_CONSTANT + " " + str(range_index)
        self._write(cmd)

    def set_filter_slope(self, filter_in_db):

        # check the given values for a suitable range and return a value that is certainly available.
        # if the value is larger then the maximum available range, a error is raised
        value = self.find_suitable_range(filter_in_db, self.FILTER_SLOPES)

        # get the index of the range. This is needed for the command that needs to be sent to the SR830
        range_index = self.FILTER_SLOPES.index(value)

        # construct the command and sent it to the device
        cmd = self.OPERATION_LOW_PASS_FILTER_SLOPE + " " + str(range_index)
        self._write(cmd)

    """ reserve mode section """

    def set_reserve_high_reserve(self):
        self._write(self.OPERATION_SET_RESERVE_MODE_HIGH_RESERVE)

    def set_reserve_normal(self):
        self._write(self.OPERATION_SET_RESERVE_MODE_NORMAL)

    def set_reserve_low_noise(self):
        self._write(self.OPERATION_SET_RESERVE_MODE_LOW_NOISE)

    """ display control section (what will be shown on the device display) """

    def display_ch1_x(self):
        self._write(self.OPERATION_SET_DISPLAY_CH1_TO_X)

    def display_ch1_r(self):
        self._write(self.OPERATION_SET_DISPLAY_CH1_TO_R)

    def display_ch2_y(self):
        self._write(self.OPERATION_SET_DISPLAY_CH2_TO_Y)

    def display_ch2_phi(self):
        self._write(self.OPERATION_SET_DISPLAY_CH2_TO_PHI)

    """ auto commands section """

    def auto_gain(self):
        self._write(self.OPERATION_AUTO_GAIN)

    def auto_reserve(self):
        self._write(self.OPERATION_AUTO_RESERVE)

    def auto_phase(self):
        self._write(self.OPERATION_AUTO_PHASE)

    def auto_offset_x(self):
        self._write(self.OPERATION_AUTO_OFFSET_X)

    def auto_offset_y(self):
        self._write(self.OPERATION_AUTO_OFFSET_Y)

    def auto_offset_r(self):
        self._write(self.OPERATION_AUTO_OFFSET_R)

    """ data transfer section section (to read measurement values from the device) """

    def read_x(self):
        return float(self._query(self.READ_X))

    def read_y(self):
        return float(self._query(self.READ_Y))

    def read_r(self):
        return float(self._query(self.READ_R))

    def read_phi(self):
        return float(self._query(self.READ_PHI))

    def read_snap(self):

        # query the values (the values will be read simultaneously and are transmitted together
        response = self._query(self.READ_SNAP_X_Y_R_PHI)
        [x, y, r, phi] = str(response).split(",")

        # convert values to float before returning them
        x = float(x)
        y = float(y)
        r = float(r)
        phi = float(phi)

        return [x, y, r, phi]

    """
    ####################################################################################################################
    Helper functions
    ####################################################################################################################
    """

    @staticmethod
    def find_suitable_range(value, value_list):

        # if the value is in the list directly return the given value
        if value in value_list:
            return value

        # if the value is larger then the largest range of the device raise an error.
        # This will maybe prevent the user from overloading the input
        elif value > max(value_list):
            raise ValueError("\n\nThe value " + str(value) + " is larger than the largest available range.\n\n" +
                             "Available ranges are:\n" + str(value_list))

        # in other cases just select the smallest possible range the requested value is within
        else:
            # go through the available ranges starting with the smallest and return if we reach a suitable range
            for v in sorted(value_list):
                if v > value:
                    return v
