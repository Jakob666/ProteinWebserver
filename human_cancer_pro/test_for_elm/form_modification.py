# -*- coding:utf-8 -*-
import json


modification = {"Acetylation": {"right": 7, "left": 7}, "Glycation": {"right": 7, "left": 7},
                "Malonylation": {"right": 7, "left": 7}, "Methylation": {"right": 7, "left": 7},
                "Succinylation": {"right": 7, "left": 6}, "Sumoylation": {"right": 1, "left": 2},
                "Ubiquitination": {"right": 7, "left": 7}, "other": {"right": 7, "left": 7}}

with open("C:/Users/hbs/Desktop/lysine/modification.json", "w") as f:
    json.dump(modification, f, indent=4)
