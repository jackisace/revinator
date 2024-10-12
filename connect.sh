#!/bin/bash

clear

ip=$(pwd | rev | cut -d "/" -f 1 | rev)

/bin/bash -s -i -l -c "(printf $ip ; cat) | nc 127.0.0.1 4444" --
