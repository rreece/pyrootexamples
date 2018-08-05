/*
 * loader.C - A file for helping PyROOT deal. Kinda black magic.
 */
#include <vector>
#include <string>
#include <set>
#include "TLorentzVector.h"

#ifdef __CINT__
#pragma link C++ class vector<vector<int> >;
#pragma link C++ class vector<vector<unsigned int> >;
#pragma link C++ class vector<vector<float> >;
#pragma link C++ class vector<vector<double> >;
#pragma link C++ class vector<string>;
#pragma link C++ class vector<vector<string> >;
//#pragma link C++ class pair<set<int>::iterator, bool >;
#pragma link C++ class pair<string, string >;
#pragma link C++ class vector<TLorentzVector>;
#else
template class std::vector<std::vector<int> >;
template class std::vector<std::vector<unsigned int> >;
template class std::vector<std::vector<float> >;
template class std::vector<std::vector<double> >;
template class std::vector<std::string>;
template class std::vector<std::vector<std::string> >;
//template class std::pair<std::set<int>::iterator, bool >;
template class std::pair<std::string, std::string >;
template class std::vector<TLorentzVector >;
template class std::vector<std::vector<TLorentzVector> >;
#endif
