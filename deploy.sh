#!/bin/bash
echo "Creating lambda artifacts"
sleep 2
echo "Set versión for lambda artifacts"
read lambda_version
sleep 2
echo "Creating artifact folder"
mkdir artifacts/"$lambda_version"
sleep 3
lambda_layers=$(find "." -maxdepth 1 -type f -name "*.py" | sed 's/\.py$//')
for loop in $lambda_layers
do
zip artifacts/"$lambda_version"/"$loop".zip $loop.py
done
