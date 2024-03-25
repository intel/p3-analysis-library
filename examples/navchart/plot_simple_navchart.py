#!/usr/bin/env python3
# Copyright (c) 2023 Intel Corporation
# SPDX-License-Identifier: 0BSD
"""
Simple Navigation Chart
=======================

A simple navigation chart.

The point in the top-right corner represents the ideal, where an application
achieves the best performance across all platforms of interest using a single
source code.

The point in the top-left corner represents applications that achieve the best
performance across all platforms of interest, but do so without reusing any
code.

Any point along the x-axis represents an application which is unportable (i.e.
there is at least one platform of interest where it does not run).

Real-life applications are expected to lie somewhere between these extremes.

A navigation chart is a useful way to visualize the trade-offs between
performance (portability) and programmer productivity, assisting in navigation
of the P3 space and reasoning about how to reach development goals.
"""

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
navchart = p3.plot.navchart(pp, cd, size=(5, 5))
navchart.save("navchart.png")
