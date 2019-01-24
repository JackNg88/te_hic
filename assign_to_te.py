#!/usr/bin/env python3

'''

Assign the BEDPE to a TE.

Basically, does one or more end overlap with a TE?

'''

import sys, os
import glbase3 # glbase3 namespace mangling!

class measureTE:
    def __init__(self, base_path):
        '''
        **Purpose**
            Constructor

        **Arguments**
            base_path (Required)
                the path we are being run in


        '''
        self.base_path = base_path

    def bind_genome(self, genelist_glb_filename):
        self.genome = glbase3.glload(genelist_glb_filename)
        print('Loaded %s' % genelist_glb_filename)

    def load_bedpe(self, filename, out_filename):
        '''
        **Purpose**
            Load in a BEDPE file, ideally output by collect_valid_pairs.py, although I guess any valid BEDPE will do

        **Arguments**
            filename (Required)
                filename of the BEDPE file
        '''
        assert filename, 'You must specify a filename'

        done = 0
        bucket_size = glbase3.config.bucket_size

        print(self.genome.buckets.keys())

        output = []

        oh = open(filename, 'r')
        for idx, line in enumerate(oh): 
            line = line.strip().split('\t')
           
            # reach into the genelist guts...
            # work out which of the buckets is required:
            loc = glbase3.location(chr=line[0], left=line[1], right=line[2])
            left_buck = int((loc["left"]-1)/bucket_size) * bucket_size
            right_buck = int((loc["right"])/bucket_size) * bucket_size
            buckets_reqd = list(range(left_buck, right_buck+bucket_size, bucket_size)) 
            result = []
            # get the ids reqd.
            loc_ids = set()
            if buckets_reqd:
                for buck in buckets_reqd:
                    if buck in self.genome.buckets[loc["chr"]]:
                        loc_ids.update(self.genome.buckets[loc["chr"]][buck]) # set = unique ids

                for index in loc_ids:
                    #print loc.qcollide(self.linearData[index]["loc"]), loc, self.linearData[index]["loc"]
                    if loc.qcollide(self.genome.linearData[index]["loc"]):
                        result.append(self.genome.linearData[index])
            
                read1_feat = []
                read1_type = []
                if result:
                    for r in result:
                        read1_feat.append(r['name'])
                        read1_type.append(r['type'])             

            output.append('\t'.join(line[0:3] + [', '.join(read1_feat), ', '.join(read1_type)] + line[4:]))# + [', '.join(read2_feat), ', '.join(read2_type)]))

            print(output[-1])
            
            done += 1
            
            if done % 1000 == 0:
                print('Processed: {:,}'.format(done)) 
                break

        print('Processed {:,} reads'.format(done))
        oh.close()
        
        out = open(out_filename, 'w')
        for o in output:
            out.write('%s\n' % o) 
        out.close()


if __name__ == '__main__':    
    if len(sys.argv) != 3:
        print('\nNot enough arguments')
        print('assign_to_te.py in.bedpe out.tsv')
        print()
        sys.exit()

    mte = measureTE(sys.argv[0])
    mte.bind_genome('mm10_glb_gencode_tes.glb')
    mte.load_bedpe(sys.argv[1], sys.argv[2])

        