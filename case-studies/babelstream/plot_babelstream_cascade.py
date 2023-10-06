#!/usr/bin/env python3
# Copyright (c) 2023 Intel Corporation
# SPDX-License-Identifier: 0BSD
"""
BabelStream Cascade Plot
========================

A cascade plot of BabelStream data.

This example uses real application data collected with the BabelStream
benchmark. However, programming language and platform names have been removed.
The original data is available from https://github.com/UoB-HPC/BabelStream.

This example demonstrates a realistic workflow, where the original data does
not use the required naming convention, and application efficiencies are not
readily available in the dataset.
"""

# %%
# Load Data into Pandas
# ---------------------

# import libraries
import pandas as pd
import p3

#sphinx_gallery_start_ignore
import os
dpath = os.path.realpath(os.getcwd())
performance_csv = os.path.join(dpath, "performance.csv")
#sphinx_gallery_end_ignore

# Load performance data from BabelStream results
df = pd.read_csv(performance_csv)

# %%
# Project Labels into Expected Forms
# ----------------------------------
# The :py:func:`p3.data.projection` method can be used to project column names
# from the original data into names required by the P3 Analysis Library.

df = p3.data.projection(
    df, problem=["name"], platform=["arch"], application=["language"]
)

# %%
# Our BabelStream data contains only one problem, and the "name" field is
# always "BabelStream". Other BabelStream case studies may feature multiple
# array sizes, which could also be used here.
#
# The platforms can be identified by the "arch" column, which stores an
# architecture name.
#
# For this case study, we treat each implementation of BabelStream as a
# different application (consistent with the definition of "application"
# here_). Each implementation of BabelStream is identified by the language it
# is written in.
#
# .. _here: ../../introduction.html#terminology

# %%
# Calculate Application Efficiencies
# ----------------------------------
# Application efficiency values show which application(s) are most effective
# at utilizing a given platform. In the below, any row with an 'app eff' of
# 0 represents an application that did not run correctly for a given
# (problem, platform) combination; any row with an `app eff` of 1 represents
# an application achieving the best-known performance.

effs = p3.metrics.application_efficiency(df)
print(effs)

# %%
# Generate a Cascade Plot
# -----------------------

cascade = p3.plot.cascade(effs)
cascade.save("cascade.png")

# %%
# The plot shows the *application efficiency* (line chart, left) and
# *performance portability* (bar chart, right) of BabelStream across 11
# platforms (A-I).
#
# The *application efficiency* for each platform is ranked from highest to
# lowest, such that platforms on the far left have the highest efficiency, and
# platforms on the far right have the lowest efficiency. If an application does
# not run on a platform, no efficiency value will be plotted for that platform
# in the line chart.
#
# An application must run across all platforms to achieve a non-zero
# *performance portability* score. For BabelStream, Language 0 is the only
# programming model that runs across all 11 platforms, and is the only one
# without a 0 for performance portability in the bar chart.
