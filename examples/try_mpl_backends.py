import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from numpy import linspace

for back in matplotlib.rcsetup.all_backends:
     print('switch:', back)
     try:
         plt.switch_backend(back)
         plt.plot(linspace(0,1,100), linspace(0,1,100)**2); plt.show()
     except Exception as e:
         print('Failed:', e)
     input('press')

