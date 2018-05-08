"""-------------Shimming Functions------------------"""

def convert_bit_voltage(data_vector):
    vec=[]
    for data in data_vector:
        if data < 32767.0:
            vec.append(data*10.0/32767.0)
        else:
            vec.append(-10*(65535.0-data)/32767.0)
    return vec
            
    
