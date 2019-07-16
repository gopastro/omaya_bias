import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

datadir = '/home/selah/testblock/'

df = pd.read_csv(datadir + 'channel0_july15_2019_1237_cold.txt', skiprows=3)

vmin = .015 #[V]

vmax = .02 #[V]

data_array = df

pre_pos = data_array[data_array.Vs <= vmax]
pre_neg = data_array[data_array.Vs >= -vmax]

subset_pos = pre_pos[vmin <= pre_pos.Vs]
subset_neg = pre_neg[pre_neg.Vs <= -vmin]

x_pos = np.array(subset_pos['Vs'])
y_pos = np.array(subset_pos['Is'])

x_neg = np.array(subset_neg['Vs'])
y_neg = np.array(subset_neg['Is'])

x = np.concatenate((x_neg, x_pos))
y = np.concatenate((y_neg, y_pos))
params, cov = np.polyfit(x, y, 1, cov=True)

def fit_func(x, a, b):
    return x*a + b

slope = params[0]
intercept = params[1]

y_fit = fit_func(x, slope, intercept)

plt.plot(x, y, 'o')
plt.plot(x, y_fit, '-')
plt.show()
