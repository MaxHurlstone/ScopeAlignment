# import numpy as np
# import scipy.signal
# from scipy.signal import savgol_filter
# import statistics as st
# from pykalman import KalmanFilter
# import matplotlib.pyplot as plt
#
# n = 15
# b = [1.0/n]*n
# a = 1
#
# #arr = np.array([236.68947874, 236.69055429, 236.69003118, 236.68957031, 236.68948841, 236.68962522, 236.68949849, 236.68936057, 236.68996224, 236.69036775, 236.69090387])
# arr = np.array([[236.68947874, 43.09476042],
#  [236.69055429, 43.09580639],
#  [236.69003118, 43.09528689],
#  [236.68957031, 43.09543004],
#  [236.68948841, 43.09580445],
#  [236.68962522, 43.09546449],
#  [236.68949849, 43.09571235],
#  [236.68936057, 43.09575446],
#  [236.68996224, 43.09539884],
#  [236.69036775, 43.09509253],
#  [236.69090387, 43.09631919]])
# # print(arr)
# # print(st.stdev(arr))
# #
# # #noiseRedArr = scipy.signal.lfilter(b, a, arr, axis=0)
# # noiseRedArr = savgol_filter(arr, 9, 1, axis = 0) # no.ravel(arr)
# # print(noiseRedArr)
# # print(st.stdev(noiseRedArr))
#
# measurements = arr
# initial_state_mean = [measurements[0, 0],
#                       0,
#                       measurements[0, 1],
#                       0]
#
# transition_matrix = [[1, 1, 0, 0],
#                      [0, 1, 0, 0],
#                      [0, 0, 1, 1],
#                      [0, 0, 0, 1]]
#
# observation_matrix = [[1, 0, 0, 0],
#                       [0, 0, 1, 0]]
#
# kf1 = KalmanFilter(transition_matrices = transition_matrix,
#                   observation_matrices = observation_matrix,
#                   initial_state_mean = initial_state_mean)
#
# kf1 = kf1.em(measurements, n_iter=5)
# (smoothed_state_means, smoothed_state_covariances) = kf1.smooth(measurements)
#
# plt.figure(1)
# plt.ylim(43.09,43.1)
# times = range(measurements.shape[0])
# plt.plot(times, measurements[:, 0], 'bo',
#          times, measurements[:, 1], 'ro',
#          times, smoothed_state_means[:, 0], 'b--',
#          times, smoothed_state_means[:, 2], 'r--',)
#
# kf2 = KalmanFilter(transition_matrices = transition_matrix,
#                   observation_matrices = observation_matrix,
#                   initial_state_mean = initial_state_mean,
#                   observation_covariance = 10*kf1.observation_covariance,
#                   em_vars=['transition_covariance', 'initial_state_covariance'])
#
# kf2 = kf2.em(measurements, n_iter=5)
# (smoothed_state_means, smoothed_state_covariances)  = kf2.smooth(measurements)
#
# plt.figure(2)
# plt.ylim(43.094,43.098)
# times = range(measurements.shape[0])
# plt.plot(times, measurements[:, 0], 'bo',
#          times, measurements[:, 1], 'ro',
#          times, smoothed_state_means[:, 0], 'b--',
#          times, smoothed_state_means[:, 2], 'r--',)
# plt.show()

import datetime

currentDay = datetime.datetime.now().day
currentMonth = datetime.datetime.now().month
currentYear = datetime.datetime.now().year

print(type(currentDay))
