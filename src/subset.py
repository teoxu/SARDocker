#!/usr/bin/env python
#******************************************************************************
#  Name:     subset.py
#  Purpose:  spatial and spectral subsetting
#  Usage:     
#    import subset
#    subset.subset(filename,dims,pos,outfile) 
#          or        
#    python subset.py [OPTIONS] filename
# MIT License
# 
# Copyright (c) 2016 Mort Canty
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import numpy as np
import os, sys, getopt, time
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly,GDT_Float32

def subset(infile, dims=None, pos=None, outfile=None): 
    gdal.AllRegister()
    if outfile is None:
        path = os.path.dirname(infile)
        basename = os.path.basename(infile)
        root, ext = os.path.splitext(basename)
        outfile = path+'/'+root+'_sub'+ext    
    print '==========================='
    print 'Spatial/spectral subsetting'
    print '==========================='
    print time.asctime()  
    try:   
        print 'Input %s'%infile
        start = time.time()    
        inDataset = gdal.Open(infile,GA_ReadOnly)                        
        cols = inDataset.RasterXSize
        rows = inDataset.RasterYSize    
        bands = inDataset.RasterCount
        if dims:
            x0,y0,cols,rows = dims
        else:
            x0 = 0
            y0 = 0       
        if pos is not None:
            bands = len(pos)
        else:
            pos = range(1,bands+1)     
    #   subset
        G = np.zeros((rows,cols,bands)) 
        k = 0                               
        for b in pos:
            band = inDataset.GetRasterBand(b)
            G[:,:,k] = band.ReadAsArray(x0,y0,cols,rows)\
                                  .astype(float)
            k += 1         
    #  write to disk       
        driver = inDataset.GetDriver() 
        outDataset = driver.Create(outfile,
                    cols,rows,bands,GDT_Float32)
        projection = inDataset.GetProjection()
        geotransform = inDataset.GetGeoTransform()
        if geotransform is not None:
            gt = list(geotransform)
            gt[0] = gt[0] + x0*gt[1]
            gt[3] = gt[3] + y0*gt[5]
            outDataset.SetGeoTransform(tuple(gt))
        if projection is not None:
            outDataset.SetProjection(projection)        
        for k in range(bands):        
            outBand = outDataset.GetRasterBand(k+1)
            outBand.WriteArray(G[:,:,k],0,0) 
            outBand.FlushCache() 
        outDataset = None    
        inDataset = None        
        print 'elapsed time: %s'%str(time.time()-start) 
        return outfile
    except Exception as e:
        print 'subset failed: %s'%e    
        return None     
    
def main(): 
    usage = '''
Usage:
------------------------------------------------

python %s [OPTIONS] filename
    
    
Perform spatial subsetting
    
Options:

   -h    this help
   -d    spatial subset list e.g. -d [0,0,500,500]
   -p    band position list e.g. -p [1,2,3,4,5,7]
   
--------------------------------------------'''%sys.argv[0]
    options,args = getopt.getopt(sys.argv[1:],'hd:p:')
    dims = None
    pos = None
    for option, value in options: 
        if option == '-h':
            print usage
            return 
        elif option == '-d':
            dims = eval(value)  
        elif option == '-p':
            pos = eval(value)
    infile = args[0] 
    outfile = subset(infile,dims,pos)
    print 'Subset image written to: %s' % outfile 
     
if __name__ == '__main__':
    main() 