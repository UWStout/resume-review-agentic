#!/bin/bash
for file in input/*.pdf; do
    python resume_agent.py "$file" ./output
done
