from cmath import cos, pi, sin
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
sr830.read_termination = '\n'
sr830.timeout = 5000

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
sr830.set_time_constant(.3)
sr830.set_sensitivity(.05)


# set the displays to interesting things
sr830.display_ch1_x()
sr830.display_ch2_y()

######################################################################
# define the parameters for the measurement
######################################################################


# amplitude = 0.004
# sr830.set_sine_output_level(amplitude)
# #sr830.set_reference_frequency(freq)

 # # define the sweep parameters
f_start = 100
f_stop =  100000
f_step = 1000       
delay = 3


# # define variables we store the measurement in
data_impedance = []                # impedance
data_BiasVoltage = []            # Bias voltage we set
data_phi = []                       # phaseshift
# #data_1_over_C_squared = []  # to save one over Capacity^2
freq = []                               # frequency

# Set the file name
filename_pdf = 'First trial' + '.pdf'

# # Header for csv
# with open(filename_csv, 'a') as csvfile:
        # writer = csv.writer(csvfile, delimiter=';',  lineterminator='\n')
# #       writer.writerow(["f / Hz :" , str(freq)])
        # writer.writerow(["Ue / V :" , str(amplitude)])
        # writer.writerow(["Frequency / Hz" , "Impedance / Ohm", "Phase / °"])

# # Some parameters for the SR830
# sr830.set_time_constant(.3)
# sr830.set_sensitivity(1)
# sr830.set_reference_frequency(f_start)
# time.sleep(delay)


# ######################################################################
# # step through the frequencies
# ######################################################################
# 
#sr830.set_sine_output_level(.004)
#f_start = 100
#f_step = 100

# Just get one measurement to work
amplitude = .04
sr830.set_sine_output_level(amplitude)
sr830.set_reference_frequency(1000)
#sr830.auto_phase()

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
'''
# positive sweep
steps = int((f_stop - f_start)/f_step)
for nr in range(steps):
    f = f_start + nr * f_step
    sr830.set_reference_frequency(f)
    time.sleep(1)
    sr830.auto_phase()

    # read the data from the SR830
    #value_x = sr830.read_x()
    #value_y = sr830.read_y()

    time.sleep(1000)
    phi = sr830.read_phi()
   
    print(value_x,value_y,phi)
'''
    
    # #sr830.set_sensitivity(2*value_r)
    # # calculate the capacity
    # # if clause in case of opern circuit measure with I = 0 A
    # if (value_r != 0):
        # freq.append(f)
        # Z = amplitude/value_r
        # data_impedance.append(Z)
        # data_phi.append(phi)

        # # Write the data in a csv
        # with open(filename_csv, 'a') as csvfile:
            # writer = csv.writer(csvfile, delimiter=';',  lineterminator='\n')
            # writer.writerow([f, Z, phi])


# ######################################################################
# # Plot the Data and save the figure as a .pdf
# ######################################################################

# # plot the data
# f, fig = plt.subplots(2, sharex = True)
# fig[0].plot(freq, data_impedance,'o-')
# fig[1].plot(freq, data_phi,'*')

# # set labels and a title
# plt.xlabel('Frequency / Hz')
# plt.axes(fig[0])
# plt.ylabel('Z / Ohm')
# plt.axes(fig[1])
# plt.ylabel('Phi / °')
# #plt.title('Characteristic curve of a diode')

# plt.savefig(filename_pdf)
# plt.show()


######################################################################
# Clean up
######################################################################

# reset and disconnect the SR830
#sr830.reset()
sr830.disconnect()




















