#!/usr/bin/env python3
# Copyright (c) 2023 Intel Corporation
# SPDX-License-Identifier: 0BSD
"""
Simple Cascade
==============

A simple cascade plot.

This example uses the synthetic performance efficiency data introduced
in the paper "`Interpreting and Visualizing Performance Portability Metrics`_"
to demonstrate the structure and interpretation of a cascade plot.

The dataset contains application efficiency for six hypothetical applications:

1. **Unportable**: Runs on only one platform.
2. **Single Target**: Runs everywhere, but with high efficiency on one platform.
3. **Multi-Target**: Runs everywhere, with high efficiency on half of the platforms.
4. **Consistent (30%)**: Runs everywhere, with 30% efficiency.
5. **Consistent (70%)**: Runs everywhere, with 70% efficiency.
6. **Inconsistent**: Runs everywhere, with inconsistent efficiency.

The line chart shows the efficiency of each application for every platform it
supports. Platforms are sorted individually for each application, in decreasing
order of application efficiency.

The boxes underneath the line chart show which platform is associated with each
point in the line chart, for each application.

The bar chart shows the performance portability of each application.

.. _Interpreting and Visualizing Performance Portability Metrics: https://doi.org/10.1109/P3HPC51967.2020.00007
"""

import matplotlib as mpl
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
p3.plot.cascade(df)
plt.savefig("cascade.png", bbox_inches="tight")
