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
