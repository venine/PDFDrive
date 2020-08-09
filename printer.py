import sys
from termcolor import colored, cprint
from functools import partial

def PRINT(color, attr, text):
    t = colored(text, color, attrs = attr)
    print(t)

use = {'alert' : 'red', 'notice' : 'blue', 'good' : 'green', 'degraded' : 'magenta', 'comment' : 'grey', 'ok' : 'yellow', 'text' : 'white'}

class printer:
    def __init__(self):
        pass

at = [ 'bold', 'underline', ]
for i in at:
    for color in use.keys():
        if i == 'bold':
            k = color.upper()
        else:
            k = 'u' + color

        setattr(printer, k, partial(PRINT,use[color],[i]))
        setattr(printer, color, partial(PRINT, use[color], None))

     
        
            

                
            
    
