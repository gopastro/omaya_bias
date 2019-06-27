import numpy as np
def norm_state_res(data_array, voltage):
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
    subset_pos = data_array[data_array.Vs >=voltage]
    x_pos=np.array(subset_pos['Vs'])
    y_pos=np.array(subset_pos['Is'])
    fit_pos, err_pos=np.polyfit(x_neg, y_neg, 1, cov=True)
            
    #Negative subset voltages <= -0.015 V

    subset_neg = data_array[data_array.Vs <= -voltage]
    x_neg = np.array(subset_neg['Vs'])
    y_neg = np.array(subset_neg['Is'])
    fit_neg,err_neg=np.polyfit(x_neg,y_neg,1,cov=True)

    avg_slope = (fit_pos[0]+fit_neg[0])/2
    avg_int = (fit_pos[1]+fit_neg[1])/2
    avg_slope_err=np.sqrt(err_pos[0,0]+err_neg[0,0])
    avg_int_err=np.sqrt(err_pos[1,1]+err_neg[1,1])
    resistance = 1/avg_slope
    resistance_err=avg_slope_err
    #print(avg_slope_err,avg_int_err,resistance, resistance_err)
    return [[resistance, resistance_err],[avg_slope,avg_slope_err],[avg_int, avg_int_err]]
    #return fit_pos,err_pos
