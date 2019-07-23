import numpy as np
def norm_state_res(data_array, vmin, vmax):
    """
    Performs line fit to calculate normal state resistance of SIS junctions.
    
   input:
      data_array: array containing sensed voltage and current measurements
    returns:
      3x2 matrix:
          resistance, resistance error
          average slope, average slope error
          average y-intercept, average y-intercept error
    """ 
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
    slope = params[0]
    intercept=params[1]
    resistance=1/slope
    slope_err = np.sqrt(err[0][0])
    intercept_err=np.sqrt(err[1][1])
    resistance_err=slope_err
    return [[resistance,resistance_err],[slope,slope_err],[intercept,intercept_err]]

    
