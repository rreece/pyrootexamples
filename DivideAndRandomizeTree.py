import sys
import os
import random
import math


from argparse import ArgumentParser

parser = ArgumentParser(usage='Randomize and split root trees')

parser.add_argument('--input-dir', dest='input_dir', default=None, help='path to input directory (will walk to find all root files)')
parser.add_argument('--output-dir', dest='output_dir', default=None, help='path to output dirctory ')
parser.add_argument('--output-file-name', dest='output_file_name', default='hist.root', help='name of output file')
parser.add_argument('--filekey', dest='filekey', default='.root', help='key to match root directories')
parser.add_argument('--treename', dest='treename', default=None, help='name of tree to read and split')
parser.add_argument('--nout', dest='nout', type=int, default=1, help='number of output files to create')

parser.add_argument('--overwrite', dest='overwrite', default=False, action='store_true', help='overwrite output directory')

options = parser.parse_args()

# import ROOT after parsing args
import ROOT

# will crash without this!!
#import AthenaPython.PyAthena as PyAthena
#getattr(PyAthena, 'Anp::DiLep')


def main() :

    if options.input_dir is None :
        print 'Must provide an input directory via --input-dir'
        sys.exit(-1)

    if options.output_dir is None :
        print 'Must provide an output directory via --output-dir'
        sys.exit(-1)

    if os.path.isdir(options.output_dir) :
        if not options.overwrite :
            print 'output directory already exists.  Add --overwrite to overwrite this directory'
            sys.exit(-1)

    input_files = collect_input_files(options.input_dir, options.filekey)

    print 'Will split %d input files into %d output files' %(len(input_files), options.nout)

    proc_trees = []
    if options.treename is not None :
        proc_trees.append(options.treename)
    else :
        # get all trees in top level of the file
        testfile = ROOT.TFile.Open(input_files[0], 'READ')
        for objkey in testfile.GetListOfKeys() :
            obj = testfile.Get(objkey.GetName())
            print obj.IsA().GetName()
            if obj.IsA().GetName() == 'TTree' :
                proc_trees.append(obj.GetName())
        testfile.Close()
    
    # unique the list
    proc_trees = set(proc_trees)

    proc_chains = [ ROOT.TChain(treename) for treename in proc_trees]

    out_maps = {}

    job_dirs = make_output(options.output_dir, options.nout, options.overwrite)

    output_files = {}
    output_dirs  = {}
    #Open output files
    rootoutdir = None
    output = options.output_dir
    outname = options.output_file_name
    if options.treename is not None :
        treetok = options.treename.split('/')
        if len(treetok) > 1 :
            rootoutdir = '/'.join(treetok[:-1])

    for dir in job_dirs :
        print '%s/%s/%s' %(output, dir, outname )
        thisfile = ROOT.TFile.Open('%s/%s/%s' %(output, dir, outname), 'RECREATE')

        output_files[dir] = thisfile
        if rootoutdir is not None :
            thisfile.mkdir(rootoutdir)

    for chain in proc_chains :

        [ chain.Add(x) for x in input_files ]

        nent = chain.GetEntries()

        print 'Total entries = %d' %nent

        # randomly sample from the event list without replacement
        randent = random.sample(xrange(0, nent), nent)

        # splits list into N(=options.nout) chunks (last entry may be shorter than others)
        nEntries          = len(randent)
        nEntriesPerOutput = int(math.ceil(float(nEntries)/options.nout))
        split_entries = [randent[i:i+nEntriesPerOutput] for i in range(0, nEntries, nEntriesPerOutput)]
        
        if len(split_entries) != options.nout :
            #hack this to work
            print 'before'
            print split_entries
            n_iter = 0
            while len(split_entries) != options.nout :
                n_iter += 1
                new_entry = []
                randlist = random.sample(xrange(0, nEntriesPerOutput), nEntriesPerOutput)
                for i in randlist :
                    if len(split_entries[i]) > 1 :
                        new_entry.append(split_entries[i].pop(0))
                split_entries.append(new_entry)

                if n_iter > 10 :
                    print split_entries
                    print 'Failed to properly split events'
                    sys.exit(-1)

        print 'Split into %d event lists' %len(split_entries)

        process(chain, split_entries, output_files, rootoutdir, job_dirs, out_maps)

    for file in output_files.values() :
        file.Write()
        file.Close()

    print 'FINISHED ^.^'

#--------------------------------------------------------------
def process(chain, entry_list, output_files, root_output_dir, job_dirs, out_tree_map) :

    if len(entry_list) != len(job_dirs) :
        print 'Number of input event lists does not match number of output dirs'
        return

    outlist = ROOT.TList()
    read_entries = 0
    chain_tree_map = {}
    for dir in job_dirs :
        chain_tree_map[dir] = chain.CloneTree(0)
        if root_output_dir is None :
            chain_tree_map[dir].SetDirectory(output_files[dir])
        else :
            chain_tree_map[dir].SetDirectory(output_files[dir].Get(root_output_dir))
        chain_tree_map[dir].SetAutoSave(3000000)
        

    print chain_tree_map
    event_to_tree_map = {}

    for entries, outdir in zip(entry_list, job_dirs) :

        for entry in entries :
            event_to_tree_map[entry] = outdir

    for entry in range(0, len(event_to_tree_map) ) :

        read_entries += 1
        if read_entries %10000 == 0 :
            print event_to_tree_map[entry]
            print 'read %d entries' %read_entries

        chain.GetEntry(entry)

        chain_tree_map[event_to_tree_map[entry]].Fill()


    for dir, tree in chain_tree_map.iteritems() :
        if root_output_dir is None :
            output_files[dir].cd()
        else :
            output_files[dir].cd(root_output_dir)
        tree.Write()
            

#--------------------------------------------------------------
def collect_input_files(input_dir, filekey) :
    """ collect all input files

    Walk through input directory and find all files 
    that match the key.  Walk through soft links too.

    """

    # collect all input files.  walk
    input_files = []
    for top, dirs, files in os.walk(input_dir, followlinks=True) :

        for file in files :
            if file.find(filekey) != -1 :
                filepath = top +'/' + file
                input_files.append(filepath)

    return input_files

#--------------------------------------------------------------
def make_output(out_dir, nout, overwrite=False) :
    """ Make output directories """

    if os.path.isdir(out_dir) :
        if overwrite :
            print 'Overwriting output directory'
            os.system('rm -rf %s' %out_dir)
            os.mkdir(out_dir)
    else :
        os.makedirs(out_dir)

    job_dirs = ['Job_%04d' %x for x in range(0, nout) ]

    for jd in job_dirs :
        os.mkdir('%s/%s' %(out_dir, jd))


    return job_dirs




    

if __name__ == '__main__' :
    main()
