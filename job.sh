#!/bin/bash

for i in {6..10};
do
    python3 preprocess/porto.py --res "$i"
done
