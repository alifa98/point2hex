#!/bin/bash

for i in {6..10};
do
    python3 preprocess/geolife.py --res "$i"
    python3 preprocess/rome.py --res "$i"
    python3 preprocess/porto.py --res "$i"
    python3 preprocess/tdrive.py --res "$i"
    python3 preprocess/preprocess.py --res "$i"
done
