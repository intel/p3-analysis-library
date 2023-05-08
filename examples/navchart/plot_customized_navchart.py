#!/usr/bin/env python3
# Copyright (c) 2023 Intel Corporation
# SPDX-License-Identifier: 0BSD
"""
Customized Navigation Chart
===========================

A customized navigation chart.

This example demonstrates how to use the :py:class:`p3.plot.NavChart` object
returned by :py:func:`p3.plot.navchart` to access underlying matplotlib objects
and use them to customize the chart.
"""

import matplotlib.pyplot as plt
import pandas as pd

import p3

# Initialize synthetic data
# (not shown, but available in script download)
# sphinx_gallery_start_ignore
from collections import defaultdict

pp_data = defaultdict(list)
cd_data = defaultdict(list)
for data in [pp_data, cd_data]:
    data["problem"] += ["Synthetic"] * 5
    data["application"] += [
        "Unportable",
        "Ideal",
        "Per-Platform Source",
        "Portability Framework",
        "Specialized",
    ]
pp_data["app pp"] += [0, 1, 1, 0.5, 0.7]
cd_data["divergence"] += [1, 0, 1, 0, 0.3]
# sphinx_gallery_end_ignore

# Read performance portability and code divergence data into pandas DataFrame
pp = pd.DataFrame(pp_data)
cd = pd.DataFrame(cd_data)

# Generate a navigation chart
fig = plt.figure(figsize=(5, 5))
navchart = p3.plot.navchart(pp, cd)

# Customize the navigation chart
# In this example, we add a label and adjust the ticks
ax = navchart.get_axes()
ax.annotate("Balances performance and code re-use.",
            xy=(0.7, 0.7),
            xytext=(0.2, 0.55),
            arrowprops=dict(facecolor='black', shrink=0.05))
ax.set_xticks([x * 0.1 for x in range(0, 11)])
ax.set_yticks([y * 0.1 for y in range(0, 11)])

plt.savefig("customized-navchart.png")
