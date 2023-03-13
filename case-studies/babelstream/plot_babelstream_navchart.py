#!/usr/bin/env python3
# Copyright (c) 2023 Intel Corporation
# SPDX-License-Identifier: 0BSD
"""
BabelStream Navigation Chart
============================

A navigation chart of BabelStream data.

This example uses real application data collected with the BabelStream
benchmark. However, programming language and platform names have been removed.
The original data is available from https://github.com/UoB-HPC/BabelStream.
"""

# %%
# Load Data into Pandas
# ---------------------

# import libraries
import pandas as pd
import matplotlib.pyplot as plt
import p3

#sphinx_gallery_start_ignore
import os
dpath = os.path.realpath(os.getcwd())
performance_csv = os.path.join(dpath, "performance.csv")
coverage_csv = os.path.join(dpath, "coverage.csv")
#sphinx_gallery_end_ignore

# Load data from BabelStream results
df = pd.read_csv(performance_csv)
df_cov = pd.read_csv(coverage_csv)

# %%
# Note that, unlike a `cascade plot`_, plotting a navigation chart requires
# both performance and coverage data.
#
# .. _cascade plot: ../plot_babelstream_cascade

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
# Calculate P3 Metrics
# --------------------
#
# Application Efficiency
# ^^^^^^^^^^^^^^^^^^^^^^
# Application efficiency values show which application(s) are most effective
# at utilizing a given platform. In the below, any row with an 'app eff' of
# 0 represents an application that did not run correctly for a given
# (problem, platform) combination; any row with an `app eff` of 1 represents
# an application achieving the best-known performance.

effs = p3.metrics.application_efficiency(df)
print(effs)

# %%
# Code Divergence
# ^^^^^^^^^^^^^^^
# Code divergence values show how much code is re-used across the platforms
# targeted by a specific application. For BabelStream, only Language 0
# has a non-zero divergence, as it is the only implementation containing
# different code paths for different platforms.

div = p3.metrics.divergence(df, df_cov)
print(div)

# %%
# Performance Portability
# ^^^^^^^^^^^^^^^^^^^^^^^
# Performance portability values show the average efficiency achieved when
# using all platforms in the set. An application must run across all platforms
# to achieve a non-zero performance portability score. For BabelStream,
# Language 0 is the only programming model that runs across all 11 platforms.

pp = p3.metrics.pp(effs)
print(pp)

# %%
# Generate a Navigation Chart
# ---------------------------

fig = plt.figure(figsize=(5, 5))
ax = p3.plot.navchart(pp, div)
plt.savefig("navchart.png")

# %%
# The plot shows the performance portability and code convergence values for
# each implementation of BabelStream. Code convergence is simply (1 -- code
# divergence).
#
# The top-right corner of a navigation chart represents the ideal, where an
# application achieves the best performance across all platforms of interest
# using a single source code. The top-left corner represents an application
# that achieves the best performance but without reusing any code across
# platforms. Any points along the x-axis are unportable (i.e. there is at least
# one platform of interest where it does not run).
#
# For BabelStream, Language 0 is the only implementation that runs across all
# platforms and is therefore the only point not on the x-axis. All other
# implementations are plotted at (1, 0) because although they use exactly the
# same source code to target all platforms, there is at least one platform
# where they do not run.
