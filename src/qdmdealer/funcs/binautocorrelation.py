import numpy as np 

def auto_corr(data, min_bin_num = 16, bin_threshold = 16.0):
	data_size = len(data)
	bin_size = 1
	bin_num = data_size
	tmp = data

	var_origin = np.var(data)
	#print('var_origin = {}'.format(var_origin))
	act_val = 1.0

	bin_size = 2
	while (data_size // bin_size >= min_bin_num):
		bin_num = data_size // bin_size
		#print(bin_num)
		tmp = np.average(np.reshape(tmp[:(bin_num * 2)], (-1, 2)), axis = 1)
		act_val = bin_size * np.var(tmp) / var_origin
		#print(act_val)
		#print(act_val)
		if (act_val * bin_threshold < 1.0 * bin_size):
		#	print('Finish calculating autocorrelation time')
			return act_val, var_origin * data_size / (1.0 * (data_size - 1))

		bin_size *= 2


	print("Not enough data for calculating autocorrelation time")
	return act_val, var_origin * data_size / (1.0 * (data_size - 1))

def auto_corr_from_bin(bin_sum_input, bin_sqr_input, data_size, min_bin_num = 16, bin_threshold = 16.0):
	#print(bin_sum_input.shape)
	data_shape = bin_sum_input[0].shape 
	data_n = 1
	for x in data_shape:
		data_n *= x
	n = len(bin_sum_input)
	act_val = []
	bin_size_lst = []
	bin_var_lst = []
	bin_num_lst = []
	bin_sum = []
	bin_sqr = []
	for i in range(n):
		bin_sum.append(np.reshape(bin_sum_input[i], (data_n, )))
		bin_sqr.append(np.reshape(bin_sqr_input[i], (data_n, )))
		bin_var_lst.append(bin_sqr[i] - bin_sum[i] * bin_sum[i])

		bin_size_lst.append(2 ** i)
		bin_num_lst.append(n // (2 ** i))
	#for var_value in bin_var_lst:
		#print(np.reshape(var_value, data_shape))

	var_origin = bin_var_lst[0]
	act_val = np.ones(data_n)
	bin_size = 2
	bin_cur = 1
	var_eps = 1e-10

	while (data_size // bin_size >= min_bin_num):
		#print('begin loop!')
		# bin_num = data_size // bin_size
		#print(bin_num)
		#tmp = np.average(np.reshape(tmp[:(bin_num * 2)], (-1, 2)), axis = 1)
		for i in range(data_n):
			if (np.abs(var_origin[i]) > var_eps):
				act_val[i] = bin_size * bin_var_lst[bin_cur][i] / var_origin[i]
			else:
				act_val[i] = 0.0
		#print(act_val)
		#for i in range(data_n):
		#	if (np.isnan(act_val[i])):
		#		act_val[i] = 0.0
		#print(np.average(act_val))
		#print(act_val)
		#print(act_val)
		if (np.average(act_val) * bin_threshold < 1.0 * bin_size):
		#	print('Finish calculating autocorrelation time')
			return np.reshape(act_val, data_shape)

		bin_size *= 2
		bin_cur += 1

	print("Not enough data for calculating autocorrelation time by bin value")
	return np.reshape(act_val, data_shape)

def binder_cumulant(psi4, psi2):
	return 1.0 - (psi4 / (3.0 * (psi2 ** 2)))
	# return psi4 / (3.0 * (psi2 ** 2))
	# return psi4 / (3.0 * (psi2 ** 2))




