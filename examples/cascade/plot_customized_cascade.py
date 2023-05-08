#!/usr/bin/env python3
# Copyright (c) 2023 Intel Corporation
# SPDX-License-Identifier: 0BSD
"""
Customized Cascade
==================

A customized cascade plot.

This example demonstrates how to use the
:py:class:`p3.plot.CascadePlot` object returned by
:py:func:`p3.plot.cascade` to access underlying matplotlib objects
and use them to customize the plot.
"""

import matplotlib.pyplot as plt
import pandas as pd

import p3

# Initialize synthetic performance efficiency data
# (not shown, but available in script download)
# sphinx_gallery_start_ignore
from collections import defaultdict

data = defaultdict(list)
for (i, platform) in enumerate(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]):
    data["problem"] += ["Synthetic"] * 6
    data["platform"] += [platform] * 6
    data["application"] += [
        "Unportable",
        "Single Target",
        "Multi-Target",
        "Consistent (30%)",
        "Consistent (70%)",
        "Inconsistent",
    ]
    eff = [0] * 6
    eff[0] = 1 if i == 0 else 0
    eff[1] = 1 if i == 0 else 0.1
    eff[2] = 0.1 if i % 2 else 1
    eff[3] = 0.3
    eff[4] = 0.7
    eff[5] = (i + 1) * 0.1
    data["app eff"] += eff
    data["arch eff"] += [0] * 6
    data["fom"] += [0] * 6
# sphinx_gallery_end_ignore

# Read performance efficiency data into pandas DataFrame
df = pd.DataFrame(data)

# Generate a cascade plot
fig = plt.figure(figsize=(6, 5))
cascade = p3.plot.cascade(df)

# Customize the cascade plot
# In this example, we adjust the range of the y-axis
cascade.get_axes("eff").set_ylim([0, 0.5])
cascade.get_axes("pp").set_ylim([0, 0.5])

plt.savefig("customized-cascade.png", bbox_inches="tight")
