import numpy as np

def compareArray(target_arr, lower_arr , upper_arr):
    flag1=target_arr[0]<=upper_arr[0] and target_arr[1]<=upper_arr[1] and target_arr[2]<=upper_arr[2]
    flag2= target_arr[0]>=lower_arr[0] and target_arr[1]>=lower_arr[1] and target_arr[2]>=lower_arr[2]
    if flag1 and flag2:
        return True
    else:
        return False


if __name__=='__main__':
    lower_arr = np.array([156, 43, 46])
    upper_arr = np.array([180, 255, 255])
    target_arr = np.array([130,200,200])
    print(compareArray(target_arr,lower_arr,upper_arr))