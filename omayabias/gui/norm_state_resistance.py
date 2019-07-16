import numpy as np
def norm_state_res(data_array, vmin, vmax):
    '''
    Performs line fit to calculate normal state resistance of SIS junctions.
    Averages the fit from the positive and negative voltages of the IV curve
    input:
        data_array: array containing sensed voltage and current measurements
    returns:
       params: [slope, intercept]
       err: covariance matrix for fit
       x,y: points used in fitting
    ''' 
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
    #fit_pos, err_pos=np.polyfit(x_pos, y_pos, 1, cov=True)
    
    params, err = np.polyfit(x_pos, y_pos, 1, cov=True)




    #y_fit = fit_func(x, slope, intercept)


    
    #return params,cov

    return [params, err,x,y]
    
