from __future__ import print_function

import glob
import json
import os
import shutil
import subprocess
import tempfile

import csv
import numpy as np
import pandas as pd

SELF_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
# STORAGE_PATH = SELF_DIR_PATH + '/../../storage/imputedb'
STORAGE_PATH = SELF_DIR_PATH + '/app/storage/imputedb'

IMPUTEDB_PATH = SELF_DIR_PATH + '/imputedb/imputedb'
DB_PATH = STORAGE_PATH + '/tmp.db'
INPUT_PATH = STORAGE_PATH + '/inputs'
OUTPUT_PATH = STORAGE_PATH + '/out.csv'

########################################################################
#
#   New API (Oct. 2018)
#
########################################################################

'''
@author: giovnani@csail.mit.edu


TODO: this function will receive only params as input, which is a JSON with all the information stored there
The forllowing implementation is to be compieant with the old api
# def executeService(params):


'''
def executeService(source, out_path, q, r, params={}):
    dir_in = source['CSV']['dir']
    dir_out = out_path['CSV']['dir']
    
    dir_metadata = dir_in+"metadata_imputeBD/"

    out_path['CSV']['dir']=dir_metadata # The output is redirected to the metadata folder
                                        # TODO: this will be a paramenter passed though the JSON input file

    if not os.path.exists(dir_metadata):
        os.makedirs(dir_metadata)

    execute_imputedb(source, out_path, q, r)

    transform_null_to_imVal(dir_in+ source['CSV']['table']+".csv", dir_metadata+"out.csv", dir_out, params)


def transform_null_to_imVal(dir_in, dir_metadata, dir_out, params={}):
    data_in = pd.read_csv(dir_in, encoding='iso-8859-1')
    imputed_values = pd.read_csv(dir_metadata, encoding='iso-8859-1')
    cc = list(imputed_values.columns)
    cols = list(map(lambda c: c.split(".")[1], cc))
    imputed_values.columns= cols
    for c in cols:
        data_in[c] = imputed_values[c]

    data_in.to_csv(dir_out + (dir_in.split("/")[-1]),
                    sep=',',index=False,
                    quoting = csv.QUOTE_NONNUMERIC,
                    header=True
                    )


########################################################################
#
#   Old APIs
#
########################################################################

def execute_imputedb(src, dst, query, alpha):
    try:
        csv_paths = []
        if 'CSV' in src:
            csv_paths += get_csv_paths(src)
        if 'postgres' in src:
            csv_paths += get_postgres_paths(src)

        load_cmd = [IMPUTEDB_PATH, 'load', '--db', DB_PATH] + csv_paths
        subprocess.check_call(load_cmd)

        query_cmd = [IMPUTEDB_PATH, 'query', '--db', DB_PATH, '--csv', '-c', query]
        with open(OUTPUT_PATH, 'w') as f:
            subprocess.check_call(query_cmd, stdout=f)

        if 'CSV' in dst:
            put_csv_output(dst)
        if 'postgres' in dst:
            put_postgres_output(dst)

    finally:
        for f in glob.glob(INPUT_PATH + '/*csv'):
            os.remove(f)
        if os.path.isdir(DB_PATH):
            shutil.rmtree(DB_PATH)
        if os.path.isfile(OUTPUT_PATH):
            os.remove(OUTPUT_PATH)


def get_csv_paths(src):
    csv_dir = src['CSV']['dir'] + '/'
    csv_tables = src['CSV']['table']

    assert os.path.isdir(csv_dir)

    if csv_tables == '':
        return glob.glob(csv_dir + '/*.csv')
    else:
        csv_paths = []
        for table in csv_tables.split(';'):
            csv_fn = csv_dir + table + '.csv'
            assert os.path.isfile(csv_fn), '{} must be a CSV file'.format(csv_fn)
            csv_paths += [csv_fn]
        return csv_paths


def get_postgres_paths(src):
    csv_paths = []
    pg_db = src['postgres']['database']
    pg_tables = src['postgres']['table'].split(';')
    pg_user = src['postgres']['user']
    pg_password = src['postgres']['password']
    pg_host = src['postgres']['host']
    pg_port = src['postgres']['port']

    cmd = [
        'psql',
        '-d', str(pg_db),
        '-h', str(pg_host),
        '-p', str(pg_port),
        '-U', str(pg_user),
        '--no-align', '--field-separator=","'
    ]
    env = os.environ.copy()
    env['PGPASSWORD'] = pg_password

    for table in pg_tables:
        table_cmd = cmd + [
            '-c', 'select * from {}'.format(table)
        ]
        csv_fn = '{}/{}.csv'.format(INPUT_PATH, table)
        with open(csv_fn, 'w') as f:
            p = subprocess.Popen(table_cmd, env=env, stdout=f)
            p.wait()
            if p.returncode < 0:
                raise RuntimeError('psql failed with return code {}'\
                                   .format(p.returncode))
        csv_paths += [csv_fn]
    return csv_paths


def put_csv_output(dst):
    out_dir = dst['CSV']['dir']
    shutil.copy(OUTPUT_PATH, out_dir)


def put_postgres_output(dst):
    raise RuntimeError('Not implemented.')


def execute_imputedb_file(src_json, dst_json, query, alpha):
    with open(src_json, 'r') as f:
        src = json.load(f)
    with open(dst_json, 'r') as f:
        dst = json.load(f)

    try:
        csv_paths = []
        if 'CSV' in src:
            csv_paths += get_csv_paths(src)
        if 'postgres' in src:
            csv_paths += get_postgres_paths(src)

        load_cmd = [IMPUTEDB_PATH, 'load', '--db', DB_PATH] + csv_paths
        subprocess.check_call(load_cmd)

        query_cmd = [IMPUTEDB_PATH, 'query', '--db', DB_PATH, '--csv', '-c', query]
        with open(OUTPUT_PATH, 'w') as f:
            subprocess.check_call(query_cmd, stdout=f)

        if 'CSV' in dst:
            put_csv_output(dst)
        if 'postgres' in dst:
            put_postgres_output(dst)

    finally:
        for f in glob.glob(INPUT_PATH + '/*csv'):
            os.remove(f)
        if os.path.isdir(DB_PATH):
            shutil.rmtree(DB_PATH)
        if os.path.isfile(OUTPUT_PATH):
            os.remove(OUTPUT_PATH)


if __name__ == '__main__':
    src = 'src_test.json'
    dst = 'dst_test.json'
    execute_imputedb(src, dst, 'select white_blood_cell_ct from labs;', 0)

