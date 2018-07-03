#! /bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
cd ..
sudo python3 setup.py sdist bdist_wheel
sudo pip3 install --upgrade .
echo
python3 tests/graph_test.py
