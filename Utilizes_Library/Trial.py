from cmath import cos, pi, sin, sqrt
import SR830_Lib
import pyvisa
import instrument
import pymeasure
import visa
import math
import matplotlib.pyplot as plt
import time
import csv
import datetime
import numpy as np
#from pymeasure.instruments.srs import SR830



######################################################################
# Connect to the lock-in amplifier
######################################################################

# connect to the SR830 Lock In Amplifier
sr830 = SR830_Lib.SR830()
sr830.connect('ASRL3::INSTR')
sr830.enable_debug_output()

# Reset the device
sr830.reset()

print('Hello Peter')

######################################################################
# Setup of the SR830 Lock-in Amplifier
######################################################################

# Use internal reference for this measurement
sr830.use_internal_reference()

# enable line filters
sr830.enable_line_filters()

# set the input to measure 
sr830.set_input_mode_I_100M()
sr830.set_input_shield_to_floating()
sr830.set_input_coupling_dc()
sr830.set_filter_slope(12)

# set the reserve
sr830.set_reserve_normal()

# time constant and sensitivity
sr830.set_time_constant(1)
sr830.set_sensitivity(.2)


# set the displays to interesting things
sr830.display_ch1_x()
sr830.display_ch2_y()

######################################################################
# define the parameters for the measurement
######################################################################


'''
f_s = np.logspace(100,100000,10)

# Just get one measurement to work
amplitude = .004
sr830.set_sine_output_level(amplitude)
sr830.set_reference_frequency(1000)
sr830.auto_phase()

time.sleep(5)
value_x = sr830.read_x()
value_y = sr830.read_y()
value_r = sr830.read_r()
value_phi = sr830.read_phi()

time.sleep(5)

print('Value X' , value_x)
print('Value Y' , value_y)
print('Value phi' , value_phi)
print('Value r' , value_r)


print('Cap? ',value_r/(2*pi*1000*amplitude)*10**12)

sr830.disconnect()
'''
f_s = [1000,2500,5000,7500,10000,25000,50000,75000,100000]
amplitude = .004
sr830.set_sine_output_level(amplitude)

c_vals = np.zeros(len(f_s))

for i in range(len(f_s)):
    # Just get one measurement to work

    sr830.set_reference_frequency(f_s[i])
    sr830.auto_phase()
    time.sleep(4)

    value_x = sr830.read_x()
    value_y = sr830.read_y()
    value_r = sr830.read_r()
    value_phi = sr830.read_phi()
    time.sleep(4)

    print('Value X' , value_x)
    print('Value Y' , value_y)
    print('Value phi' , value_phi)
    print('Value r' , value_r)
    print('Ic? ', sqrt(value_x**2 + value_y**2))

    c = value_r/(2*pi*f_s[i]*amplitude)*10**12
    c_vals[i] = c

    print(c)

print(c_vals)

sr830.disconnect()