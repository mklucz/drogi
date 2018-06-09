#! /bin/bash
cd /home/maciek/Documents/newprog/drogi
sudo python3 setup.py sdist bdist_wheel
sudo sudo pip3 install --upgrade .
echo
python3 tests/graph_test.py
