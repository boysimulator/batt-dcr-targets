d = {}
print()

#Cell Design Inputs:
#*********************************************************************************************************************************************

#Cathode Design
d['cat_active_percent'] = 0.97 #%
d['cat_chg_s_cap'] = 214.33 #mAh/g
d['cat_dchg_s_cap'] = 179.69 #mAh/g
d['cat_density_targ'] = 3.42 #g/cc

#Anode Design
d['an_active_percent'] = 0.948 #%
d['an_chg_s_cap'] = 386 #mAh/g
d['an_dchg_s_cap'] = 337 #mAh/g
d['an_density_targ'] = 1.7 #g/cc

#Cell Design
d['ac_ratio'] = 1.04

#Cell Program Requirements
d['capacity_target'] = 78 #Ah
d['cell_thickness_target'] = 8.5 #mm
d['cell_DCR_target'] = 1.35 #mOhm

#Empirical Data/Properties
d['cat_swelling'] = 1.06
d['an_swelling'] = 1.210
d['DCR_a_coefficient'] = 0.0006 #DCR = ax2+bx+c
d['DCR_b_coefficient'] = -0.0401 #DCR = ax2+bx+c
d['DCR_c_coefficient'] = 1.9773 #DCR = ax2+bx+c
d['large_cell_DCR_factor'] = 1

#Product-Level Cell Componentry
d['al_foil_length'] = 497 #mm
d['al_foil_width'] = 95 #mm
d['al_foil_thickness'] = 12 #um
d['al_tab_length'] = 45 #mm
d['al_tab_width'] = 45 #mm
d['al_tab_thickness'] = 0.4 #mm
d['cu_foil_length'] = 501.5 #mm
d['cu_foil_width'] = 98 #mm
d['cu_foil_thickness'] = 6 #um
d['cu_tab_length'] = 45 #mm
d['cu_tab_width'] = 45 #mm
d['cu_tab_thickness'] = 0.3 #mm
d['pouch_thickness'] = 153 #um
d['separator_thickness'] = 17 #um

#Research-Level Cell Componentry
d['SLP_al_foil_length'] = 44 #mm
d['SLP_al_foil_width']= 30.4 #mm
d['SLP_al_foil_thickness'] = 20 #um
d['SLP_al_tab_length'] = 26 #mm
d['SLP_al_tab_width'] = 10 #mm
d['SLP_al_tab_thickness'] = 0.098 #mm
d['SLP_cu_foil_length'] = 46 #mm
d['SLP_cu_foil_width'] = 32.4 #mm
d['SLP_cu_foil_thickness'] = 6 #um
d['SLP_ni_tab_length'] = 26 #mm
d['SLP_ni_tab_width'] = 10 #mm
d['SLP_ni_tab_thickness'] = 0.1 #mm

#Physical Quantities
d['al_resistivity'] = 0.0000029 #ohm-cm
d['cu_resistivity'] = .00000172 #ohm-cm
d['ni_resistivity'] = 0.00000699 #ohm-cm

#*********************************************************************************************************************************************

def set_limiting_weight_by_cap(d):
	'''
	specific funtion returning limiting electrode weight needed to hit minimum capacity
	
	
	takes in dictionary of cell design values
	does not mutate dictionary
	returns float of weight of limiting electrode
	'''
	
	return d['capacity_target']*1000/(d['cat_dchg_s_cap']*d['cat_active_percent']) #g
	
	
def optimize_loading_by_cell_thickness(d):
	'''
	specific function that finds the maximum layer count that will fit in the target cell geometry
	
	takes in dictionary of cell parameters
	iterates through increasing layer count until design will exceed maximum allowable geometry
	!!!MUTATES DICTIONARY!!!
	
	per cell design, there is one additional anode than cathode.
	at low layer counts, electrode loading per layer is usually very high to meet capacity target.
	when evaulating overall cell thickness, this function begins with the passed layer count and associated loadings.
	if passed layer count is the practical minimum of 1 for cathode, it is possible that initial loading is very high to meet capacity target.
	in this scenario, the matching anode loading is very high, and may thus cause the cell design with 1 extra anode to go far beyond allowable thickness.
	increasing layer count, and thus decreasing anode loading, should eventually fix this conundrum by decreasing cell thickness of successive layer additions, to a point.
	eventually, thickness will increase from the inactive components used: foils & separator
	
	this function first looks to see if the cell design will fit within the required geometry.
	if it doesn't, but increasing layer count will cause the thickness to be lower, this function will increase layer count by one and check again
	if it doesn't and increasing the layer count will cause the cell to continue growing, this function will return a message of failure
	if it does, this function will increase the layer count and check again to see if it still fits
	
	Mutates dictionary of parameters
	returns None
	'''
	
	#Initialization: prior to optimization, sets error flag to False, before determining if it can be set to True
	d['geometry_error'] = False
	
	#Initialization: sets anode layer count to one greater than input cathode layer count for separator quantity calculation (cell design requires 1 more anode than cathode)
	an_layer_count = d['cat_layer_count'] + 1
	
	#Initialization: calculates cathode loading level and corresponding anode loading level, and for the case the cathode layer count is one more than the passed-in case
	d['cat_loading_level'] = get_cathode_loading(d)
	d['an_loading_level'] = get_excess_loading(d)
	cat_loading_level_next_layer = get_cathode_loading_specific_var(d['cat_weight'], d['al_foil_length'], d['al_foil_width'], d['cat_layer_count']+1)
	an_loading_level_next_layer = get_excess_loading_specific_var(cat_loading_level_next_layer, d['cat_active_percent'], d['cat_chg_s_cap'], d['ac_ratio'], d['an_chg_s_cap'], d['an_active_percent'])
	
	#Initialization: calculates thickness of ***one-sided electrode coating*** for current layer and next layer
	cat_electrode_thickness = get_electrode_layer_thickness(d['cat_loading_level'], d['cat_density_targ']) #um // per side
	an_electrode_thickness = get_electrode_layer_thickness(d['an_loading_level'], d['an_density_targ']) #um // per side
	cat_electrode_thickness_next_layer = get_electrode_layer_thickness(cat_loading_level_next_layer, d['cat_density_targ']) #um // per side
	an_electrode_thickness_next_layer = get_electrode_layer_thickness(an_loading_level_next_layer, d['an_density_targ']) #um // per side
	
	#Initialization: calculates overall thickness of ***electrode*** related components in cell design passed to function when called, using electrode coating thickness values calculated above
	cat_thickness = get_electrode_thickness(cat_electrode_thickness, d['cat_swelling'], d['al_foil_thickness'], d['cat_layer_count']) #mm
	an_thickness = get_electrode_thickness(an_electrode_thickness, d['an_swelling'], d['cu_foil_thickness'], an_layer_count) #mm
	cat_thickness_next_layer = get_electrode_thickness(cat_electrode_thickness_next_layer, d['cat_swelling'], d['al_foil_thickness'], d['cat_layer_count']+1) #mm
	an_thickness_next_layer = get_electrode_thickness(an_electrode_thickness_next_layer, d['an_swelling'], d['cu_foil_thickness'], an_layer_count+1) #mm
	
	#Initialization: calculates the ***cell*** thickness for the current layer count and the next additional layer count scenario
	cell_thickness = get_cell_thickness(d, cat_thickness, an_thickness, an_layer_count)
	cell_thickness_next_layer = get_cell_thickness(d, cat_thickness_next_layer, an_thickness_next_layer, an_layer_count+1)
	
	#Print statements to display cell physical properties during optimization - initialization level
	print('______________________________')
	print('|***OPTIMIZING CELL DESIGN***|')
	print('------------------------------')
	print()
	print('Cathode Layer Count          Cathode Loading Level          Cathode Thickness          Anode Loading Level          Anode Thickness')
	print('-----------------------------------------------------------------------------------------------------------------------------------')
	if d['cat_layer_count'] < 10:
		cat_layer = ' ' + str(d['cat_layer_count'])
	else:
		cat_layer = str(d['cat_layer_count'])
	if d['cat_loading_level'] < 100:
		cat_loading = ' ' + str(round(d['cat_loading_level'], 2))
		if len(cat_loading) == 5:
			cat_loading = cat_loading + '0'
	else:
		cat_loading = str(round(d['cat_loading_level'], 2))
		if len(cat_loading) == 5:
			cat_loading = cat_loading + '0'
	if len(str(round(cat_thickness, 2))) == 3:
		cat_thickness_string = str(round(cat_thickness, 2)) + '0'
	else:
		cat_thickness_string = str(round(cat_thickness, 2))
	if d['an_loading_level'] < 100:
		an_loading = ' ' + str(round(d['an_loading_level'], 2))
		if len(an_loading) == 5:
			an_loading = an_loading + '0'
	else:
		an_loading = str(round(d['an_loading_level'], 2))
	print('        ' + cat_layer + '                          ' + cat_loading + '                         ' + cat_thickness_string + '                        ' + an_loading + '                      ' + str(round(an_thickness, 2)))
	
	#Initialization: if the cell thickness is above the target and increasing the layer count isn't shown to be a method for decreasing thickness, will skip layer count optimization
	#returns None and mutates dictionary to contain True for key 'geometry_error' and minimum cell thickness
	if cell_thickness > d['cell_thickness_target'] and cell_thickness_next_layer > cell_thickness:
		d['geometry_error'] = True
		d['cell_thickness'] = cell_thickness #mm
		return None
	
	#Optimization: If cell thickness is greater than the target, but increasing layer counts shows to be effective for decreasing layer thickness, or cell thickness is less than
	#              target and increasing the layer count by 1 is also less than target --> increase layer count by 1, redistribute active material accordingly, re-calculate
	#              thickness values, and re-test
	#
	#			   STOP: ends on layer that meets the thickness target
	while (cell_thickness > d['cell_thickness_target'] and cell_thickness_next_layer < cell_thickness) or (cell_thickness < d['cell_thickness_target'] and cell_thickness_next_layer < d['cell_thickness_target']):
		
		#increase layer count for iteration in loop
		# !!!THIS STEP MUTATES DICTIONARY!!! --> cat_layer_count will always have new value set here each time line is executed
		d['cat_layer_count'] += 1
		an_layer_count = d['cat_layer_count'] + 1
		
		#calculates cathode loading level and corresponding anode loading level, and for the case the cathode layer count is one more than the loop case
		# !!!THIS STEP MUTATES DICTIONARY!!! --> cathode and anode loading levels will always have new value set here each time line is executed
		d['cat_loading_level'] = get_cathode_loading(d) #mg/cm2
		d['an_loading_level'] = get_excess_loading(d) #mg/cm2
		cat_loading_level_next_layer = get_cathode_loading_specific_var(d['cat_weight'], d['al_foil_length'], d['al_foil_width'], d['cat_layer_count']+1) #mg/cm2
		an_loading_level_next_layer = get_excess_loading_specific_var(cat_loading_level_next_layer, d['cat_active_percent'], d['cat_chg_s_cap'], d['ac_ratio'], d['an_chg_s_cap'], d['an_active_percent']) #mg/cm2
		
		#calculates thickness of ***one-sided electrode coating***  as updated by this loop, current layer and next layer
		cat_electrode_thickness = get_electrode_layer_thickness(d['cat_loading_level'], d['cat_density_targ']) #[g/cc, um] // per side
		an_electrode_thickness = get_electrode_layer_thickness(d['an_loading_level'], d['an_density_targ']) #[g/cc, um] // per side
		cat_electrode_thickness_next_layer = get_electrode_layer_thickness(cat_loading_level_next_layer, d['cat_density_targ']) #[g/cc, um] // per side
		an_electrode_thickness_next_layer = get_electrode_layer_thickness(an_loading_level_next_layer, d['an_density_targ']) #[g/cc, um] // per side
		
		#calculates overall thickness of ***electrode*** related components in cell design as updated by this loop, using electrode coating thickness values calculated above
		cat_thickness = get_electrode_thickness(cat_electrode_thickness, d['cat_swelling'], d['al_foil_thickness'], d['cat_layer_count']) #mm
		an_thickness = get_electrode_thickness(an_electrode_thickness, d['an_swelling'], d['cu_foil_thickness'], an_layer_count) #mm
		cat_thickness_next_layer = get_electrode_thickness(cat_electrode_thickness_next_layer, d['cat_swelling'], d['al_foil_thickness'], d['cat_layer_count']+1) #mm
		an_thickness_next_layer = get_electrode_thickness(an_electrode_thickness_next_layer, d['an_swelling'], d['cu_foil_thickness'], an_layer_count+1) #mm
		
		#calculates the ***cell*** thickness for the current layer count and the next additional layer count scenario
		cell_thickness = get_cell_thickness(d, cat_thickness, an_thickness, an_layer_count)
		cell_thickness_next_layer = get_cell_thickness(d, cat_thickness_next_layer, an_thickness_next_layer, an_layer_count+1)
		
		#Print statements to display cell physical properties during optimization - loop level
		if d['cat_layer_count'] < 10:
			cat_layer = ' ' + str(d['cat_layer_count'])
		else:
			cat_layer = str(d['cat_layer_count'])
		if d['cat_loading_level'] < 100:
			cat_loading = ' ' + str(round(d['cat_loading_level'], 2))
			if len(cat_loading) == 5:
				cat_loading = cat_loading + '0'
		else:
			cat_loading = str(round(d['cat_loading_level'], 2))
			if len(cat_loading) == 5:
				cat_loading = cat_loading + '0'
		if len(str(round(cat_thickness, 2))) == 3:
			cat_thickness_string = str(round(cat_thickness, 2)) + '0'
		else:
			cat_thickness_string = str(round(cat_thickness, 2))
		if d['an_loading_level'] < 100:
			an_loading = ' ' + str(round(d['an_loading_level'], 2))
			if len(an_loading) == 5:
				an_loading = an_loading + '0'
		else:
			an_loading = str(round(d['an_loading_level'], 2))
		print('        ' + cat_layer + '                          ' + cat_loading + '                         ' + cat_thickness_string + '                        ' + an_loading + '                      ' + str(round(an_thickness, 2)))
		
		#If the cell thickness is still above the target and further increasing the layer count isn't shown to be a method for decreasing thickness, will skip further layer count optimization
		#returns None and mutates dictionary to contain True for key 'geometry_error' and minimum cell thickness
		if cell_thickness > d['cell_thickness_target'] and cell_thickness_next_layer > cell_thickness:
			d['geometry_error'] = True
			d['cell_thickness'] = cell_thickness #mm
			return None
		
	#Mutates dictionary to include all values changed as a result of optimization loop above
	d['an_layer_count'] = d['cat_layer_count']+1
	d['cat_thickness'] = cat_electrode_thickness #um
	d['an_thickness'] = an_electrode_thickness #um
	d['cell_thickness'] = cell_thickness #mm
	run_cap_calc = get_real_capacity(d) #Ah (more important when get_cathode_loading() and get_cathode_loading_specific_var() are setup to increment specific loading levels
	d['cat_weight_actual'] = get_actual_cat_weight(d) #g (more important when get_cathode_loading() and get_cathode_loading_specific_var() are setup to increment specific loading levels
	
	return None
	
	
def get_cathode_loading(d):
	'''
	specific function returning the cathode loading level corresponding to necessary cathode weight and design parameters like geometry, layer count, and material capacity
	
	takes in dictionary of cell design values
	does not mutate dictionary
	can return float of cathode loading level rounded to next highest value of 0.01 to ensure no material contributing to optimized capacity gets lost, if comments below edited
	
	returns float of cathode loading level
	'''
	full = d['cat_weight']*100000/(d['al_foil_length']*d['al_foil_width']*2*d['cat_layer_count'])
	
	#Comment out return statement below and uncomment lines below here to only look at 0.01mg/cm2 increments of loading
	#rounded = round(d['cat_weight']*100000/(d['al_foil_length']*d['al_foil_width']*2*d['cat_layer_count']), 2)
	
	#if full - rounded > 0 and full - rounded <= 0.005:
		#return rounded + 0.01
	#else:
		#return rounded
		
	return full


def get_excess_loading(d):
	'''
	specific function returning excess electrode based off limiting electrode
	
	
	takes in dictionary of cell design values
	does not mutate dictionary
	returns excess electrode loading level
	'''
	return (d['cat_loading_level']*d['cat_active_percent']*d['cat_chg_s_cap']*d['ac_ratio'])/(d['an_chg_s_cap']*d['an_active_percent']) #mg/cm2

	
def get_cathode_loading_specific_var(cat_weight, al_foil_length, al_foil_width, cat_layer_count):
	'''
	specific function returning the cathode loading level corresponding to necessary cathode weight and design parameters like geometry, layer count, and material capacity
	
	takes in variables of calculation-specific cell design values, NOT overall dictionary (therefore no chance for dictionary mutation)
	can return float of cathode loading level rounded to next highest value of 0.01 to ensure no material contributing to optimized capacity gets lost, if comments below edited
	
	returns float of cathode loading level
	'''
	full = cat_weight*100000/(al_foil_length*al_foil_width*2*cat_layer_count)
	
	#Comment out return statement below and uncomment lines below here to only look at 0.01mg/cm2 integrals of loading
	#rounded = round(cat_weight*100000/(al_foil_length*al_foil_width*2*cat_layer_count), 2)
	
	#if full - rounded > 0 and full - rounded <= 0.005:
		#return rounded + 0.01
	#else:
		#return rounded
	
	return full
	

def get_excess_loading_specific_var(cat_loading_level, cat_active_percent, cat_chg_s_cap, ac_ratio, an_chg_s_cap, an_active_percent):
	'''
	specific function returning excess electrode based off limiting electrode
	
	
	takes in variables of calculation-specific cell design values, NOT overall dictionary (therefore no chance for dictionary mutation)
	returns excess electrode loading level
	'''
	return (cat_loading_level*cat_active_percent*cat_chg_s_cap*ac_ratio)/(an_chg_s_cap*an_active_percent) #mg/cm2
	
	
def get_electrode_layer_thickness(loading_level, density_targ):
	'''
	general formula: not electrode specific
	
	takes in electrode design floats
	returns float of electrode coating thickness
	'''
	thickness = loading_level*10/density_targ
	
	return thickness #um

	
def get_electrode_thickness(electrode_thickness, swelling_factor, foil_thickness, layers):
	'''
	general formula: not electrode specific
	
	takes in electrode properties as floats to get calculate dimensional data
	returns thickness of electrode stack per cell design
	'''
	return ((electrode_thickness*swelling_factor*2+foil_thickness)/1000*layers) #mm

		
def get_cell_thickness(d, cat_thickness, an_thickness, an_layer_count):
	'''
	specific funtion that calculates total cell thickness based upon pouch_thickness and separator_thickness in data dictionary;
	cat_thickness, an_thickness, and an_layer_count from calling source
	
	takes in total cathode and anode thickness, already calculated, as well as pouch, separator, and layer info
	returns total thickness of cell per design elements as float
	'''
	return cat_thickness+an_thickness+2*d['pouch_thickness']/1000+(an_layer_count*2+2)*d['separator_thickness']/1000 #mm
	
	
def get_real_capacity(d):
	'''
	specific function that updates the real cell capacity in the dictionary based upon state of dictionary as passed
	therefore, call this function after any time there is some update to cathode loading and layer count to reassess real capacity
	
	takes in dictionary of cell values and MUTATES it to newly calculated real capacity
	
	returns None
	'''
	d['cell_capacity_real'] = d['cat_loading_level']*d['cat_active_percent']*d['al_foil_length']*d['al_foil_width']*d['cat_dchg_s_cap']*d['cat_layer_count']*2/100000000 #Ah
	return None


def get_actual_cat_weight(d):
	'''
	specific function that takes in loading level and layer count as adjusted by optimization functions and calculates the amount of cathode material in the cell
	
	takes in dictionary of all cell values
	returns float rounded to two decimals
	'''
	return round(d['cat_loading_level']*2*d['cat_layer_count']*d['al_foil_length']*d['al_foil_width']/100000, 2) #g
	
	
def get_component_resistance(length, width, thickness, resistivity):
	'''
	general function to return the resistance associated with flowing electrons in a certain direction through a cell component of certain cross-sectional area
	
	length = direction of electronic flow
	width = width of component
	thickness = thickness of component (usually smallest dimension)
	
	simplified: (length*resistivity)/area
	
	returns a resistance in ohms
	'''
	return length*resistivity*10/width/thickness #ohm

	
def get_SLP_DCR(d):
	'''
	specific function that calculates the 50% SOC DCR of the SLP made with cathode loading level optimized for large format cell
	
	THIS FUNCTION MUTATES THE DICTIONARY EACH TIME IT IS CALLED
	this function uses empirical data for the SLP DCR behavior, for example, the optimized formulation has to have been built at the SLP level and analyzed to provide the coefficients
	
	mutates dictionary to update SLP DCR at 50% SOC as equation changes (as it can due to DCR optimization step)
	returns None
	'''
	d['SLP_DCR_50_SOC'] = d['DCR_a_coefficient']*d['cat_loading_level']**2+d['DCR_b_coefficient']*d['cat_loading_level']+d['DCR_c_coefficient']	#ohm
	return None
	
	
def get_ASR_from_SLP(d):
	'''
	specific function that calculates the electrode ASR from the SLP construction case
	
	THIS FUNCTION MUTATES THE DICTIONARY EACH TIME IT IS CALLED
	
	mutates dictionary to update ASR from SLP-based calculations
	returns None
	'''
	
	#need to update SLP area of 13.3674cm2 to be calculation from drawing
	d['ASR'] = (d['SLP_DCR_50_SOC']-(d['SLP_al_foil_R']+d['SLP_cu_foil_R'])- d['SLP_al_tab_R']-d['SLP_ni_tab_R'])*13.3674 #ohm-cm2
	return None
	
	
def get_large_electrode_resistance(d):
	'''
	specific function that calculates the electrode resistance for the optimized large cell format
	
	THIS FUNCTION MUTATES THE DICTIONARY EACH TIME IT IS CALLED
	
	mutates dictionary to update electrode resistance
	return None
	'''
	d['electrode_R'] = d['ASR']/(2*d['cat_layer_count']*d['al_foil_length']*d['al_foil_width']/100)
	return None
	
	
def get_DCR(d):
	'''
	specific function that calculates the DCR of the large cell for the optimized parameters
	
	THIS FUNCTION MUTATES THE DICTIONARY EACH TIME IT IS CALLED
	
	mutates dictionary to update electrode resistance
	return None
	'''
	d['DCR'] = (d['electrode_R']+((d['al_foil_R']+d['cu_foil_R'])/2)+d['al_tab_R']+d['cu_tab_R'])*1000*d['large_cell_DCR_factor'] #mOhm
	
	
def get_SLP_DCR_target(d):
	'''
	takes in dictionary
	
	mutates as it lowers SLP DCR
	returns none
	'''
	while d['DCR'] > d['cell_DCR_target']:
		
		#translate empirical SLP DCR eqn downward
		d['DCR_c_coefficient'] -= 0.001
		
		#rerun large cell DCR math with adjusted eqn
		SLP_DCR = get_SLP_DCR(d)
		ASR = get_ASR_from_SLP(d)
		electrode_R = get_large_electrode_resistance(d)
		DCR = get_DCR(d)
		
	return None
	

#Find amount of capacity limiting electrode (cathode) needed to achieve product target capacity
d['cat_weight'] = set_limiting_weight_by_cap(d) #g

#Initialize cathode layer count to practical minimum of 1
d['cat_layer_count'] = 1

#Find maximum layer count to fit within cell geometry and set cell design parameters as a result
optimize = optimize_loading_by_cell_thickness(d)


#Calculate the resistivity of cell components (tabs, foils) for SLP and large cell
d['SLP_al_foil_R'] = get_component_resistance(d['SLP_al_foil_length'], d['SLP_al_foil_width'], d['SLP_al_foil_thickness']/1000, d['al_resistivity']) #ohm (1000: conversion from um to mm)
d['SLP_cu_foil_R'] = get_component_resistance(d['SLP_cu_foil_length'], d['SLP_cu_foil_width'], d['SLP_cu_foil_thickness']/1000, d['cu_resistivity']) #ohm (1000: conversion from um to mm)
d['SLP_al_tab_R'] = get_component_resistance(d['SLP_al_tab_length'], d['SLP_al_tab_width'], d['SLP_al_tab_thickness'], d['al_resistivity']) #ohm
d['SLP_ni_tab_R'] = get_component_resistance(d['SLP_ni_tab_length'], d['SLP_ni_tab_width'], d['SLP_ni_tab_thickness'], d['ni_resistivity']) #ohm
d['al_foil_R'] = get_component_resistance(d['al_foil_length'], d['al_foil_width']*d['cat_layer_count'], d['al_foil_thickness']/1000, d['al_resistivity']) #ohm (1000: conversion from um to mm; layer factor applied to width)
d['cu_foil_R'] = get_component_resistance(d['cu_foil_length'], d['cu_foil_width']*d['cat_layer_count'], d['cu_foil_thickness']/1000, d['cu_resistivity']) #ohm (1000: conversion from um to mm; layer factor applied to width)
d['al_tab_R'] = get_component_resistance(d['al_tab_length'], d['al_tab_width'], d['al_tab_thickness'], d['al_resistivity']) #ohm
d['cu_tab_R'] = get_component_resistance(d['cu_tab_length'], d['cu_tab_width'], d['cu_tab_thickness'], d['cu_resistivity']) #ohm

#Calculate SLP DCR (necessary because empirical data represents SLP level DCR measurements of the electrode chemistry)
SLP_DCR = get_SLP_DCR(d)

#Calculate electrode ASR at optimized loading by subtracting out SLP components
ASR = get_ASR_from_SLP(d)

#Calculate electrode resistance in large cell design
electrode_R = get_large_electrode_resistance(d)

#Calculate large cell DCR for design
DCR = get_DCR(d)

#Predict SLP DCR needed to acheive DCR target
if d['DCR'] < d['cell_DCR_target']:
	d['DCR_error'] = False
else:
	d_adjusted_DCR = d.copy() #lets program save original SLP DCR value to compare to
	d['DCR_error'] = True
	SLP_target = get_SLP_DCR_target(d_adjusted_DCR)

#additional print statements	
print()
print()
print('______________')
print('|***REPORT***|')
print('--------------')
#print()
#print('Minimum weight of cathode electrode required is:.....' + str(round(d['cat_weight'], 2)) + 'g')
print()
if d['geometry_error'] == True:
	print('Cell design will not fit within the given volume.')
	print('The minimum cell thickness is ' + str(round(d['cell_thickness'], 3)) + 'mm')
else:
	print('Actual weight of cathode material:...................' + str(round(d['cat_weight_actual'], 2)) + 'g')
	print('Cathode layer count:.................................' + str(d['cat_layer_count']))
	print('Cathode loading level:...............................' + str(round(d['cat_loading_level'], 2)) + 'mg/cm2')
	print('Anode loading level:.................................' + str(round(d['an_loading_level'], 3)) + 'mg/cm2')
	print('Cathode electrode layer thickness:...................' + str(round(d['cat_thickness'], 2)) + 'um')
	print('Anode electrode layer thickness:.....................' + str(round(d['an_thickness'], 2)) + 'um')
	print('Cell thickness:......................................' + str(round(d['cell_thickness'], 3)) + 'mm')
	print('Cell capacity:.......................................' + str(round(d['cell_capacity_real'], 3)) + 'Ah')
	print('Cell DCR:............................................' + str(round(d['DCR'], 3)) + 'mOhm')
	
	if d['DCR_error'] == True:
		print()
		print('Cell chemistry does not meet DCR requirement.')
		SLP_difference = (d['SLP_DCR_50_SOC']-d_adjusted_DCR['SLP_DCR_50_SOC'])/d['SLP_DCR_50_SOC']*100
		print('DCR at the SLP level is ' + str(round(d['SLP_DCR_50_SOC'], 2)) + 'ohm')
		print('SLP-level DCR needs to be lowered by ' + str(round(SLP_difference, 2)) + '% to meet program DCR target.')
		print('Old DCR equation is y=' + str(d['DCR_a_coefficient']) + 'x^2' + str(d['DCR_b_coefficient']) + 'x+' + str(round(d['DCR_c_coefficient'], 3)))
		print('New DCR equation is y=' + str(d['DCR_a_coefficient']) + 'x^2' + str(d['DCR_b_coefficient']) + 'x+' + str(round(d_adjusted_DCR['DCR_c_coefficient'], 3)))
print()
print('Verbose report:')		
print(d)