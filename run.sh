#!/bin/bash

source settings.sh
./run_sim.py --conv
echo "Please navigate to:  http://<IP_ADDRESS> in your browser to view the results."
# sudo python -m SimpleHTTPServer 80

