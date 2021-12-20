import math

#typical simulation values -- unquote to use instead of manual input
"""
rocket_mass = 0.036
Cd = 0.524
frontal_area = 0.000482662
parachute_area = 0.073
air_density = 1.225
time_step = 0.001
num_rockets = 1
file_path = "Estes_C6.eng"
"""

#ask user for simulation parameters
rocket_mass = float(input("Enter the rocket's mass without the motor in kg: "))
Cd = float(input("Enter the rocket's coefficient of drag: "))
frontal_area = float(input("Enter the rocket's frontal area in m^2: "))
parachute_area = float(input("Enter the parachute's area in m^2: "))
air_density = float(input("Enter the density of the air in kg/m^3: "))
time_step = float(input("Enter the simulation time step in s: "))
num_rockets = int(input("Enter the number of motors (clustered) in the rocket: "))
file_path = input("Enter the path to the RASP motor file: ")

#parse engine file
with open(file_path, "r") as f:
	data_points = []
	for line in f:
		if line.startswith(";"): #ignore comment lines
			continue
		elif line.startswith(" "): #read data points from indented lines
			data_points.append(list(map(float, line.split())))
		else: #non-indented line is the header
			header_line = line.split()

propellant_mass, total_motor_mass = float(header_line[4]), float(header_line[5]) #only extract useful data from header

#get total impulse of the motor 
total_impulse = 0
prev_time = 0
prev_thrust = 0
for data_point in data_points:
	delta_time = data_point[0]-prev_time
	delta_thrust = data_point[1]-prev_thrust
	total_impulse += ((delta_thrust*delta_time)/2) + (prev_thrust*delta_time)
	prev_time = data_point[0]
	prev_thrust = data_point[1]

#generator to get motor thrust at every time interval
def thrust():
	time = 0
	index = 0
	while True:
		time += time_step
		try:
			while time > data_points[index+1][0]: #find closest data point to the current time interval
				index += 1
		except IndexError: #return zero thrust after motor is spent
			while True:
				yield 0

		yield ((data_points[index][1] * (data_points[index+1][0]-time)) + \
			  (data_points[index+1][1] * (time-data_points[index][0]))) / \
			  (data_points[index+1][0]-data_points[index][0]) #linear interpolate with known data points

#generator to get motor mass at every time interval
def motor_mass():
	spent_impulse = 0
	prev_thrust = 0
	non_propellant_mass = total_motor_mass-propellant_mass
	while True:
		thrust = yield #wait to be sent current motor thrust
		delta_thrust = thrust - prev_thrust
		spent_impulse += ((delta_thrust*time_step)/2) + (prev_thrust*time_step) #calculate total impulse the motor has outputted
		prev_thrust = thrust

		impulse_ratio = spent_impulse/total_impulse

		yield non_propellant_mass + propellant_mass*impulse_ratio #calculate how much motor mass is still left

velocity = 0
height = 0
velocity_max = 0
acceleration_max = 0
thrust_gen = thrust()
motor_mass_gen = motor_mass()
time = 0
while velocity >= 0 or force_thrust != 0: #ascent simulation
	time += time_step
	
	#retrieve generator values
	force_thrust = next(thrust_gen) * num_rockets
	next(motor_mass_gen)
	new_motor_mass = motor_mass_gen.send(force_thrust)
	total_mass = rocket_mass + (new_motor_mass * num_rockets) 

	#calculate and apply forces to rocket body over the time interval
	force_gravity = 9.80665 * total_mass
	force_drag = Cd*air_density*(velocity**2)*frontal_area #drag equation
	net_force = force_thrust - force_gravity - force_drag
	acceleration = net_force/total_mass
	height += (velocity*time_step) + (acceleration*(time_step**2))/2
	velocity += acceleration*time_step

	velocity_max = max(velocity, velocity_max)
	acceleration_max = max(acceleration, acceleration_max)

height_max = height
ascent_duration = time
ideal_delay = ascent_duration - data_points[-1][0]

time = 0
while height > 0: #descent simulation
	time += time_step

	#calculate and apply downward forces to rocket body over the time interval
	force_drag = 1.75*air_density*(velocity**2)*parachute_area #drag equation with typical parachute coefficient
	net_force = force_drag-force_gravity #use gravity value from before
	acceleration = net_force/total_mass
	height += (velocity*time_step) + (acceleration*(time_step**2))/2
	velocity += acceleration*time_step

descent_duration = time-ascent_duration

#display values to the user
print("\nResults (NOTE - simulation assumes that parachute deploys at apogee):")
print(f"Max height: {height_max} m")
print(f"Max velocity: {velocity_max} m/s")
print(f"Max acceleration: {acceleration_max} m/s^2")
print(f"Ascent duration: {ascent_duration} s")
print(f"Descent duration: {time} s")
print(f"Ideal parachute ejection delay: {ideal_delay} s")
print(f"Speed at ground impact: {abs(velocity)} m/s")
