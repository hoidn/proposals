#!/bin/bash
python chain.py "$(cat context)" "inconsistency_finder.txt,recommendation_eval.txt,arch_compare.txt" "llm:o1-mini,llm:sonnet3.5,llm:sonnet3.5"
