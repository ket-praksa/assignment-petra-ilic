#!/bin/bash

export PYTHONPATH=../../src_py
python3 -m hat.orchestrator.main --conf ./data/orchestrator.yaml
