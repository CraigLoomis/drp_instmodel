#!/usr/bin/env python

import glob
import os
import re
import sys
import numpy as np
import pyfits

def readSpotDir(dir, verbose=False):
    """ Read all the spot files generated by the zemax people. 

    There is a summary file, but we use the filenames to yield the fiber# and wavelength.
    """
    
    dt = np.dtype([('fiberIdx','i2'),
                   ('lambda','f4'),
                   ('spot','(256,256)f4')])

    names = glob.glob(os.path.join(dir, "fiber_*.asc"))
    
    spots = []
    for n in names:
        m = re.match('fiber_0*(\d+)_0*(\d+)\.asc', 
                     os.path.basename(n))
        fno = int(m.group(1))
        flam = float(m.group(2))
        if verbose:
          sys.stderr.write('reading %s (%d, %0.1f)\n' % (n, fno, flam))  
        spot = np.genfromtxt(n, dtype='f4',
                             skip_header=11)
        spots.append((fno, flam, spot))
    arr = np.array(spots, dtype=dt)
    
    return arr

def writeSpotFITS(spotDir, data):

    cols = []
    cols.append(pyfits.Column(name='fiberIdx',
                              format='I',
                              array=data['fiberIdx']))
    cols.append(pyfits.Column(name='lambda',
                              format='D',
                              array=data['lambda']))
    spots = data['spot'][:]
    spots.shape = (len(spots), 256*256)
    cols.append(pyfits.Column(name='spot',
                              format='%dE' % (256*256),
                              dim='(256,256)',
                              array=spots))
    colDefs = pyfits.ColDefs(cols)
    hdu = pyfits.new_table(colDefs)
    hdu.writeto(os.path.join(spotDir, 'spots.fits'), 
                checksum=True, clobber=True)
    
def main(argv):
    """ Convert a directory of zemax spot files into a slightly more convenient FITS table. """
    
    spotDir = argv[0]

    data = readSpotDir(spotDir)
    writeSpotFITS(spotDir, data)
    
if __name__ == "__main__":
    main(sys.argv[1:])