import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
def knee_voltage(df,**kwargs):
    """
    Calculates the knee voltage of SIS junctions using a first derivative
    
    input:
        df : array containing sensed voltage and current measurements
    returns:
        pos_knee, neg_knee : voltage values of the positive and negative knee voltages
    """
    #dividing into regions where the knee should be
    print(df)
    pre_pos = df[df.Vs >= 0.010]
    pos = pre_pos[pre_pos.Vs <= 0.015]
    pre_neg = df[df.Vs <= -0.005]
    neg = pre_neg[pre_neg.Vs >= -0.015]
    #creating positive and negative arrays based on the region
    x_pos = np.array(pos['Vs'])
    y_pos = np.array(pos['Is'])

    #finding first derivative of positive subset
    dx_pos=np.diff(x_pos,1)

    #some dx are zero which will cause an error. Flagging these values
    bad_dx_pos=np.where(dx_pos==0)
    dx_pos[bad_dx_pos]=99999
    
    dy_pos=np.diff(y_pos,1)
    y1_pos=dy_pos/dx_pos

 
    #doing the same thing for the negative subset
    x_neg = np.array(neg['Vs'])
    y_neg = np.array(neg['Is'])
    dx_neg=np.diff(x_neg,1)
    bad_dx_neg=np.where(dx_neg==0)
    dx_neg[bad_dx_neg]=99999
    dy_neg=np.diff(y_neg,1)
    y1_neg=dy_neg/dx_neg

    #finding the index of the knee
    loc_pos = np.where(y1_pos==np.amax(y1_pos))
    loc_neg = np.where(y1_neg == np.amax(y1_neg))
    
    #finding and returning the knee voltage in Volts
    pos_knee =x_pos[loc_pos]
    neg_knee = x_neg[loc_neg]
    if 'debug' in kwargs:
        print(pre_pos,pos,pre_neg,neg)
        #print(dx_pos,dy_pos)
        #print(dx_neg,dy_neg)
        #print(y1_pos,y1_neg)
        #print(loc_pos,loc_neg)
    return pos_knee, neg_knee
