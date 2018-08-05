#
# file: setup.sh
# author: Ryan Reece <ryan.reece@cern.ch>
# created: August 17, 2012
#
# Setup script for a release of PennTau software
#
###############################################################################


##-----------------------------------------------------------------------------
## pre-setup, don't touch

path_of_this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#export MYMAGICDIR=${path_of_this_dir}

add_to_python_path()
{
    export PYTHONPATH=$1:$PYTHONPATH
    echo "  Added $1 to your PYTHONPATH."
}

add_to_path()
{
    export PATH=$1:$PATH
    echo "  Added $1 to your PATH."
}


##-----------------------------------------------------------------------------
## setup PYTHONPATH

echo "  Setting up your PYTHONPATH."
add_to_python_path ${path_of_this_dir}
echo "  done."


##-----------------------------------------------------------------------------
## setup PATH

#echo "  Setting up your PATH."
#add_to_path ${path_of_this_dir}/tree_trimmer
#echo "  done."


