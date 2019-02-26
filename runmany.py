
# from MakeStencil import makeStencil
from SatMatchScatter import SatMatchScatter

paramfile = 'C:\\Users\\aanderson29\\Box Sync\\[VICE Lab]\\RESEARCH\\PROJECTS\\Gallo\\Madera Block 760\\METRIC\\WIP\\Andy\\Catalogs\\params.csv'
f = open(paramfile,'r')
lines = f.readlines()
for l in lines:
    p = l.split('\n')[0].split(',')
    SatMatchScatter(p[0],p[1],p[2])

print 'done'

f.close()


