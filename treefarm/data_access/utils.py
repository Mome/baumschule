import numpy as np
import scipy.io  # this is the SciPy module that loads mat-files
from datetime import datetime, date, time
import pandas as pd
import os
import subprocess
from collections import namedtuple
from itertools import chain
import mimetypes
import json

import logging
logger = logging.getLogger(__name__)

try:
    import magic
except Exception as e:
    logger.debug('No magic module available: %s' % e)
    magic_available = False
else:
    magic_available = True

# add mimetypes
module_path = os.path.dirname(__file__)
custom_types_file = os.path.join(module_path, 'mime.types')
mimetypes.init(mimetypes.knownfiles + [custom_types_file])

def read_mat(path):
    """Reads a pandas.DataFrame from a matfile"""
    # source http://poquitopicante.blogspot.de/2014/05/loading-matlab-mat-file-into-pandas.html
    mat = scipy.io.loadmat(path)  # load mat-file
    mdata = mat['measuredData']  # variable in mat file
    mdtype = mdata.dtype  # dtypes of structures are "unsized objects"
    # * SciPy reads in structures as structured NumPy arrays of dtype object
    # * The size of the array is the size of the structure array, not the number
    #   elements in any particular field. The shape defaults to 2-dimensional.
    # * For convenience make a dictionary of the data using the names from dtypes
    # * Since the structure has only one element, but is 2-D, index it at [0, 0]
    ndata = {n: mdata[n][0, 0] for n in mdtype.names}
    # Reconstruct the columns of the data table from just the time series
    # Use the number of intervals to test if a field is a column or metadata
    columns = [n for n, v in ndata.iteritems() if v.size == ndata['numIntervals']]
    # now make a data frame, setting the time stamps as the index
    df = pd.DataFrame(np.concatenate([ndata[c] for c in columns], axis=1),
                      index=[datetime(*ts) for ts in ndata['timestamps']],
                      columns=columns)
    return df


def mat_to_csv(path):
    d = scipy.io.loadmat(path)
    x = pd.DataFrame(d['X'], columns=['x'])
    y = pd.DataFrame(d['y'], columns=['y'])
    df = pd.concat([x,y], axis=1)
    df = y
    new_name = os.path.splitext(os.path.basename(path))[0] + '.csv'
    df.to_csv(new_name)


def mat_to_hdf(path):
    d = scipy.io.loadmat(path)
    x = pd.DataFrame(d['X'])
    y = pd.DataFrame(d['y'])
    new_name = os.path.splitext(os.path.basename(path))[0] + '.hdf'
    x.to_hdf(new_name, 'X')
    y.to_hdf(new_name, 'y')


def read_json(path):
    with open(path, 'r') as f:
        jdict = json.load(f)
    return jdict


def write_json(path, jdict):
    with open(path, 'w') as f:
        json.dump(jdict, f)


def read_text(path):
    with open(path, 'r') as f:
        string = f.read()
    return string


def write_text(path, string):
    with open(path, 'w') as f:
        f.write(string)


def get_filetype(path):

    # get mimetype of file
    if not os.path.exists(path):
        mime_type = 'text/plain'
    elif magic_available:
        if os.path.isdir(path):
            mime_type = 'inode/directory'
        else:
            mime_type = magic.from_file(path, mime=True)
    else:
        cmd = 'file -b --mime-type'.split()
        cmd.append(path)
        mime_type = subprocess.check_output(cmd)

    # for unknown and text type, try to determine by file extension
    if mime_type in ['application/octet-stream', 'text/plain']:
        type_, encoding = mimetypes.guess_type(path)
        if type_:
            mime_type = type_

        print('try to guess type', type_, encoding)

    return mime_type
