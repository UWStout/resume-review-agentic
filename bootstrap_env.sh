#!/bin/bash
if [ ! -d "./langchain_env" ]; then
    python3.13 -m venv langchain_env
fi

if [ -d "./langchain_env/Scripts" ]; then
    source ./langchain_env/Scripts/activate
else
    source ./langchain_env/bin/activate
fi

pip install -r requirements.txt
