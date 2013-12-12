import time
import unicodecsv as ucsv

## Functions
def read_manuscript_points(infile):
    """Return raw data array from csv file"""
    with open(infile,'rU') as inf:
        return [line for line in ucsv.reader(inf)]

def denormalize_dataset(raw_data):
    """Return one manuscript point per line"""
    # denormalize rows
    denormalized_data = []
    for row in raw_data:
        # put place copied
        place_copied = [row[0] , row[57], row[58], row[60], 
                        row[59], row[68], row[61], row[62], 
                        row[69], row[70], '', '']

        denormalized_data.append(place_copied)
        
        # put in intermediate stages
        for x in xrange(76, len(row), 12):
            constr = []
            constr.append(row[0])
            for item in row[x:x+11]:
                constr.append(item)
            denormalized_data.append(constr)

        # put current library
        current_library = [row[0], row[4], row[3], '', 
                           '', 'Current', row[5], row[6], row[7],
                           '', row[13], row[14] ]
        denormalized_data.append(current_library)

    return denormalized_data

def write_output(final_data):
    """Write line segments to CSV file"""
    with open('denorm_test.csv', 'w') as outf:
        wr = ucsv.writer(outf, delimiter=',')
        for movement in final_data:
            wr.writerow(movement) 

def write_wkt_geometry(database):
	for idx, row in enumerate(database):
		if idx == 0: row.append('WKT')
		else: row.append('LINESTRING({0} {1}, {2} {3})'.format(row[7], row[6], row[19], row[18]))

	return database

## Classes
class Manuscript(object):
    def __init__(self, movements, ms_number):
        self.data = movements
        self.uid = ms_number
        self.segments = []

    def __repr__(self):
        return 'Processing CLA ID {0}'.format(self.uid)

    def parse_manuscript_record(self):
        self.data.sort(key = lambda row:row[8])
        for x in xrange(0, len(self.data)-1):
            seg = self.data[x] + self.data[x+1]
            self.segments.append(seg)
        # return bool to evaluate whether there are valid segments
        return True if len(self.segments) > 0 else False

## Main
if __name__ == '__main__':
    start = time.time()

    # read in data
    raw_data = read_manuscript_points('cla_volume_1.csv')[1:]
    
    # denormalize
    denormalized_data = denormalize_dataset(raw_data) 

    # create database of MS movements
    headers = ['FR_MISD', 'FR_N', 'FR_REG', 'FR_CENT',
               'FR_CERT', 'FR_RLXN', 'FR_LAT', 'FR_LONG', 
               'FR_ORD', 'FR_COMMENT', 'FR_ST', 'FR_END',
               'TO_MISD', 'TO_N', 'TO_REG', 'TO_CENT', 
               'TO_CERT', 'TO_RLXN', 'TO_LAT', 'TO_LONG',
               'TO_ORD', 'TO_COMMENT', 'TO_ST', 'TO_END']
    
    # exclude rows without two coordinate pairs
    valid_data = [x for x in denormalized_data if x[6] != '' and x[7] != '']
    
    # all data with a rel code
    #valid_data = [x for x in denormalized_data if x[5] != '']
    ms_movements = []
    for ms in set([x[0] for x in valid_data]):
        m = Manuscript([p for p in valid_data if p[0] == ms], ms)
        if m.parse_manuscript_record():
            for segment in m.segments:
                ms_movements.append(segment)

    # add headers and write CSV file
    ms_movements.insert(0, headers)
    ms_movements = write_wkt_geometry(ms_movements)
    write_output(ms_movements)
    print 'Runtime: {0:.4}'.format(time.time() - start)
