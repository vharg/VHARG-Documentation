#!/usr/bin/env python
from ecmwfapi import ECMWFDataServer
from sys import argv

west = argv[1]
east = argv[2]
south = argv[3]
north = argv[4]
res = argv[5]
sDate = argv[6]
eDate = argv[7]
scaling = argv[8]

## Added by Seb 26/02/2019
time = sDate+"/to/"+eDate
area = str(north)+"/"+str(west)+"/"+str(south)+"/"+str(east)
grid = str(res)+"/"+str(res)

# Print file containing nx and ny -> useful for fall3d input file
nx = ((float(east) - float(west)) / float(res)) * float(scaling) + 1
ny = ((float(north) - float(south)) / float(res)) * float(scaling) + 1

f = open('domain.txt', 'w')
f.write("nx: {NX}\n".format(NX=str(nx)))
f.write("ny: {NY}\n".format(NY=str(ny)))
f.close()
## End addition


server = ECMWFDataServer()

server.retrieve({
                'stream'    : "oper",
                'levtype'   : "sfc",
                'param'     : "165.128/166.128/167.128",
                'dataset'   : "interim",
                'step'      : "0",
                'grid'      : grid,
                'time'      : "00/06/12/18",
                'date'      : time,
                'type'      : "an",
                'class'     : "ei",
                'format'    : "netcdf",
                'area'      : area,
                'target'    : "sfc.nc"
                })

server.retrieve({
                'stream'    : "oper",
                'levtype'   : "sfc",
                'param'     : "159.128",
                'dataset'   : "interim",
                'step'      : "12",
                'grid'      : grid,
                'time'      : "12",
                'date'      : time,
                'type'      : "fc",
                'class'     : "ei",
                'format'    : "netcdf",
                'area'      : area,
                'target'    : "bl1.nc"
                })

server.retrieve({
                'stream'    : "oper",
                'levtype'   : "sfc",
                'param'     : "159.128",
                'dataset'   : "interim",
                'step'      : "6/12",
                'grid'      : grid,
                'time'      : "00/12",
                'date'      : time,
                'type'      : "fc",
                'class'     : "ei",
                'format'    : "netcdf",
                'area'      : area,
                'target'    : "bl2.nc"
                })

server.retrieve({
                'stream'    : "oper",
                'levtype'   : "sfc",
                'param'     : "159.128",
                'dataset'   : "interim",
                'step'      : "6/12",
                'grid'      : grid,
                'time'      : "00",
                'date'      : time,
                'type'      : "fc",
                'class'     : "ei",
                'format'    : "netcdf",
                'area'      : area,
                'target'    : "bl3.nc"
                })

server.retrieve({
                'stream'    : "oper",
                'levtype'   : "sfc",
                'param'     : "159.128",
                'dataset'   : "interim",
                'step'      : "6",
                'grid'      : grid,
                'time'      : "12",
                'date'      : time,
                'type'      : "fc",
                'class'     : "ei",
                'format'    : "netcdf",
                'area'      : area,
                'target'    : "bl4.nc"
                })

server.retrieve({
                'stream'    : "oper",
                'levtype'   : "sfc",
                'param'     : "129.128/172.128",
                'dataset'   : "interim",
                'step'      : "0",
                'expver'    : "1",
                'grid'      : grid,
                'time'      : "00/06/12/18",
                'date'      : time,
                'type'      : "an",
                'class'     : "ei",
                'format'    : "netcdf",
                'area'      : area,
                'target'    : "invariant.nc"
                })

server.retrieve({
                'stream'    : "oper",
                'levtype'   : "pl",
                'param'     : "129.128/130.128/131.128/132.128/135.128/157.128",
                'levelist'  : "1/2/3/5/7/10/20/30/50/70/100/125/150/175/200/225/250/300/350/400/450/500/550/600/650/700/750/775/800/825/850/875/900/925/950/975/1000",
                'dataset'   : "interim",
                'step'      : "0",
                'expver'    : "1",
                'grid'      : grid,
                'time'      : "00/06/12/18",
                'date'      : time,
                'type'      : "an",
                'class'     : "ei",
                'format'    : "netcdf",
                'area'      : area,
                'target'    : "prs.nc"
                })

