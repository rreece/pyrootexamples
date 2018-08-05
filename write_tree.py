#!/usr/bin/env python
"""
NAME
    name.py - short description

SYNOPSIS
    Put synposis here.

DESCRIPTION
    Put description here.

OPTIONS
    -h, --help
        Prints this manual and exits.
        
    -n VAL
        Blah blah.

AUTHOR
    Ryan Reece  <ryan.reece@cern.ch>

COPYRIGHT
    Copyright 2010 Ryan Reece
    License: GPL <http://www.gnu.org/licenses/gpl.html>

SEE ALSO
    ROOT <http://root.cern.ch>

TO DO
    - One.
    - Two.

2011-06-15
"""

#------------------------------------------------------------------------------
# imports
#------------------------------------------------------------------------------

## std
import argparse, sys, time
import array

## ROOT
import ROOT
ROOT.gROOT.SetBatch(True)

## my modules
import rootutils
import stl_loader


#------------------------------------------------------------------------------
# globals
#------------------------------------------------------------------------------
timestamp = time.strftime('%Y-%m-%d-%Hh%M')
GeV = 1000.


#------------------------------------------------------------------------------
# options
#------------------------------------------------------------------------------
def options():
    parser = argparse.ArgumentParser()
#    parser.add_argument('infile',  default=None,
#            help='A positional argument.')
#    parser.add_argument('-x', '--option',  default=False,  action='store_true',
#            help="Some toggle option.")
#    parser.add_argument('-i', '--input',  default=None,
#            help="Path to directory of datasets")
#    parser.add_argument('-o', '--output',  default='out.txt',
#            help="Name of output file.")   
    return parser.parse_args()


#------------------------------------------------------------------------------
# main
#------------------------------------------------------------------------------
def main():
    ops = options()

    print 'Helloworld.  The time is %s.' % timestamp
#    print ops.output

    ## distributions to draw random test tree from
    f_w = ROOT.TF1('f_w', 'gaus', -2.0, 5.0)
    f_w.SetParameters(1.0, 1.0, 0.2)
    f_n = ROOT.TF1('f_n', 'TMath::Poisson(x, [0])', 0 , 20)
    f_n.SetParameter(0, 3)
    f_x = ROOT.TF1('f_x', 'TMath::CauchyDist(x, [0], [1])', 0.0, 200.0)
    f_x.SetParameters(91.0, 3.5)
    f_y = ROOT.TF1('f_y', 'expo', 0.0, 200.0)
    f_y.SetParameters(0.0, -1.0/150.0)
    f_z = ROOT.TF1('f_z', 'pol0', 0.0, 200.0)
    f_z.SetParameter(0, 1.0)


    ## build tree and declare branches
    tw = MyTreeWriter('myntuple.root', 'myntuple')

    ## fill tree
    n_events = 100
    for i_event in xrange(n_events):
        event = dict()
        event['w'] =     ( 'F',      f_w.GetRandom()                                                      )
        n = int(f_n.GetRandom())
        event['n'] =     ( 'I',      n                                                                    )
        event['x'] =     ( 'VF',     [ f_x.GetRandom() for j in xrange(n) ]                               )
        event['y'] =     ( 'VVF',    [ [ f_y.GetRandom() for k in xrange(3) ] for j in xrange(n) ]        )
        event['z'] =     ( 'VVI',    [ [ int(f_z.GetRandom()) for k in xrange(3) ] for j in xrange(n) ]   )
        tw.fill(event)

    tw.close()
    print 'Done'




#------------------------------------------------------------------------------
# MyTreeWriter class
#------------------------------------------------------------------------------
class MyTreeWriter(object):
    """
    A helper class for writing trees.
    """
    #__________________________________________________________________________
    def __init__(self, tfile='myntuple.root', tree='myntuple'):
        self._tfile_name = tfile
        self._tree_name = tree
        self._tfile = ROOT.TFile.Open(tfile, 'RECREATE')
        self._tree = ROOT.TTree(tree, tree)
        self._n_events = 0 
        self._branch_contents = dict()
        self._branch_types    = dict()

    #__________________________________________________________________________
    def fill(self, event):
        if self._n_events == 0:
            self.initialize_branches(event)
        else:
            self.update_branches(event)
        assert len(self._branch_contents) > 0
        assert len(self._branch_types) == len(self._branch_contents)
        self._tree.Fill()
        self._n_events += 1

    #__________________________________________________________________________
    def initialize_branches(self, event):
        for key, val in event.iteritems():
            branch_type, branch_data = val
            branch_content = self.convert_branch_content(branch_data, branch_type)

            ## cache branch info (keeping these contents/arrays persisently)
            self._branch_types[key] = branch_type
            self._branch_contents[key] = branch_content

            ## add new branch to the tree
            # ints, floats
            if branch_type in ('I', 'F'):
                # construct TLeaf name (eg. "RunNumber/I")
                leafname = '%s/%s' % (key, branch_type)
                self._tree.Branch(key, branch_content, leafname)
            # vectors
            else:
                self._tree.Branch(key, branch_content)

    #__________________________________________________________________________
    def update_branches(self, event):
        for key, val in event.iteritems():
            branch_type, branch_data = val
            branch_content = self.convert_branch_content(branch_data, branch_type)

            assert self._branch_types[key] == branch_type

            if branch_type in ('I', 'F'):
                self._branch_contents[key][0] = branch_content[0]
            else:
                vec = self._branch_contents[key]
                vec.clear()
                for x in branch_content:
                    vec.push_back(x)
            
    #__________________________________________________________________________
    def convert_branch_content(self, branch_data, branch_type):
        branch_content = None
        if branch_type == 'I':
            branch_content = array.array('i', [branch_data])
        elif branch_type == 'F':
            branch_content = array.array('f', [branch_data])
        else:
            branch_content = rootutils.rootify(branch_data, branch_type)
        assert not branch_content is None
        return branch_content

    #__________________________________________________________________________
    def close(self):
        self.tree.GetCurrentFile().Write()
        self.tree.GetCurrentFile().Close()


#------------------------------------------------------------------------------
# free functions
#------------------------------------------------------------------------------

#______________________________________________________________________________
def fatal(message=''):
    sys.exit("Fatal error in %s: %s" % (__file__, message))


#______________________________________________________________________________
def tprint(s, log=None):
    line = '[%s] %s' % (time.strftime('%Y-%m-%d:%H:%M:%S'), s)
    print line
    if log:
        log.write(line + '\n')
        log.flush()


#------------------------------------------------------------------------------
if __name__ == '__main__': main()

# EOF
