    
import sys, os
loader = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl_loader.C")

import ROOT
ROOT.gROOT.ProcessLine('.L %s+' % loader)

#ROOT.gROOT.ProcessLine("""
#include <string>
#ifdef __MAKECINT__
#pragma link C++ class vector<vector<int> >+;
#pragma link C++ class vector<vector<float> >+;
#pragma link C++ class vector<vector<double> >+;
#pragma link C++ class vector<vector<string> >+;
#endif""")

#import re
#rex_type = re.compile(r"<type '(\w+)'>\Z")
#rex_vector = re.compile(r"<class '__main__.vector\s*<([\w\s]+)\s*(,\s*allocator\s*<[\w\s]+>)?\s*>'>")
#rex_vector_vector = re.compile(r"<class '__main__.vector<\s*vector\s*<([\w\s]+)(,\s*allocator<[\w\s]+>\s*)?>\s*(,\s*allocator\s*<\s*vector\s*<[\w\s]+,\s*allocator\s*<[\w\s]+>\s+>\s+>)?\s+>'>")

