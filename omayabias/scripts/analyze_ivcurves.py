import pandas as pd
from omayabias.sisdb.datamodel import GelPack, SISDimensions, \
    IVCurveFile
from omayabias.utils.norm_state_resistance import norm_state_res
import os
import datetime
from dateutil.parser import parse

def process_iv_files(csvfile='junction_testing_jul16_2019.csv'):
    df = pd.read_csv(csvfile)
    resistances = {}
    for i, row in df.iterrows():
        filename = row['File Name']
        if not IVCurveFile.select().where(IVCurveFile.filename==filename).exists():
            date = parse(row.Date)
            if os.path.exists(filename):
                junction_id = row['Junction ID']
                args = junction_id.split(':')
                gelpack_number = args[0][-1]
                gelpack = GelPack.select().where(GelPack.description==gelpack_number).get()
                sisargs = args[1].strip().split(' ')
                sis2letter = sisargs[0]
                sisrowcol = ' '.join([sisargs[1], sisargs[2]])
                gelpack_label = sisargs[3]
                sisd_query = SISDimensions.select().where(SISDimensions.gelpack==gelpack,
                                                          SISDimensions.sis2letter==sis2letter,
                                                          SISDimensions.sisrowcol==sisrowcol,
                                                          SISDimensions.gelpack_label==gelpack_label)
                if sisd_query.exists():
                    sisdimensions = sisd_query.get()
                    if date.date() >= datetime.date(2019, 6, 1):
                        dfd = pd.read_csv(filename, skiprows=3)
                    else:
                        dfd = pd.read_csv(filename)
                    res = norm_state_res(dfd, 0.015, 0.025)
                    print filename, res[0]
                    ivcurve_file = IVCurveFile(sis=sisdimensions, filename=filename,
                                               measured_time=date,
                                               resistance=res[0][0],
                                               resistance_error=res[0][1],
                                               slope=res[1][0],
                                               slope_error=res[1][1],
                                               intercept=res[2][0],
                                               intercept_error=res[2][1])
                    ivcurve_file.save()
                    resistances[filename] = res[0][0]
        else:
            print "Filename %s already exists in database" % filename
    return resistances
