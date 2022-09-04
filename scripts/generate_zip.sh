#!/usr/bin/env bash

rm -rf lambda_function.zip
rm -rf lib

pip install -t lib -r requirements.txt
cd lib && zip ../lambda_function.zip -r . && cd ..
zip lambda_function.zip -u main.py
zip lambda_function.zip -u parse.py
zip lambda_function.zip -u -r templates/ 