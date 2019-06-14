import numpy as np

def norm_state_res(data_array):
    '''
    Performs line fit to calculate normal state resistance of SIS junctions.
    Averages the fit from the positive and negative voltages of the IV curve
    input:
        data_array: array containing sensed voltage and current measurements
    returns:
       3x2 matrix:
           resistance, resistance error
           average slope, average slope error
           average y-intercept, average y-intercept error
    '''
    
    #Positive subset voltages >= 0.015 V
    subset_pos = data_array[data_array.Vs >= 0.015]
    x_pos=np.array(subset_pos["Vs"]/1e-3)
    y_pos=np.array(subset_pos["Is"]/1e-6)
    fit_pos,err_pos=np.polyfit(x_pos,y_pos,1,cov=True)
    
    #Negative subset voltages <= -0.015 V
    subset_neg = data_array[data_array.Vs <= -0.015]
    x_neg = np.array(subset_neg['Vs']/1e-3)
    y_neg = np.array(subset_neg['Is']/1e-6) 
    fit_neg,err_neg=np.polyfit(x_neg,y_neg,1,cov=True)
    
    
    avg_slope = (fit_pos[0]+fit_neg[0])/2
    avg_int = (fit_pos[1]+fit_neg[1])/2
    avg_slope_err=np.sqrt(err_pos[0,0]+err_neg[0,0])
    avg_int_err=np.sqrt(err_pos[1,1]+err_neg[1,1])

    #print(avg_slope_err,avg_int_err,resistance, resistance_err)
    return [[avg_slope,avg_slope_err],[avg_int, avg_int_err]]
# =============================================================================
# import pandas as pd
# import matplotlib.pyplot as plt
# test = pd.read_csv('D:/User/Documents/sis_data/channel0_june4_2019_234pm.txt',skiprows=3)
# 
# data=norm_state_res(test)
# plt.plot(test["Vs"]/1e-3,test["Is"]/1e-6)
# test_x=np.arange(-50,50,1)
# test_y=test_x*data[0][0]+data[1][1]
# plt.xlabel('Vs')
# plt.ylabel('Is')
# plt.plot(test_x,test_y)
# =============================================================================
