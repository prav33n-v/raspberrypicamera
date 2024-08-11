# Functions to perform basic operations like increment, decrement

def increment(value,num):
    return (value+num)

def decrement(value,num):
    return (value-num)

def down(value,minval,maxval):
    if(value < maxval):
        return (value+1)
    else:
        return minval

def up(value,minval,maxval):
    if(value > minval):
        return (value-1)
    else:
        return maxval

def check_left_right(value,lower_limit,higher_limit,difference):
    left_flag = True
    right_flag = True
    if((value > (lower_limit + difference)) and (value < higher_limit - difference)):
        left_flag = True
        right_flag = True
    elif(value <= (lower_limit + difference)):
        left_flag = False
        right_flag = True
    else:
        left_flag = True
        right_flag = False
    return left_flag,right_flag

