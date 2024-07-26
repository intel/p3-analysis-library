#!/usr/bin/env python3
# Copyright (c) 2024 Intel Corporation
# SPDX-License-Identifier: 0BSD
"""
Understanding Data Projection
=============================

Projecting data onto P3 definitions.

The P3 Analysis Library expects data to be prepared in a specific
:ref:`format <performance_data>`. This format was inspired by the
:ref:`terminology <terminology>` first introduced in "`Implications of a Metric
for Performance Portability`_":

.. _Implications of a Metric for Performance Portability:
   https://doi.org/10.1016/j.future.2017.08.007

**Problem**
  A task with a pass/fail metric for which quantitative performance may be
  measured. Multiplying an :math:`N \\times K` matrix by an :math:`K \\times M`
  matrix to the accuracy guaranteed by IEEE 754 double precision, computing
  :math:`\\pi` to a certain number of decimal places, and sorting an array of
  :math:`N` elements are all examples of problems.

**Application**
  Software capable of solving a *problem* with measurable correctness and
  performance. Math libraries, Python scripts, C functions, and entire software
  packages are all examples of applications.

**Platform**
  A collection of software **and** hardware on which an *application* may run a
  *problem*. A specific processor coupled with an operating system, compiler,
  runtime, drivers, library dependencies, etc is an example of a precise
  platform definition.

These definitions are flexible, allowing the same performance data to be used
for multiple case studies with different interpretations of these terms.

Rather than store raw performance data in columns corresponding to these
definitions, the P3 Analysis Library provides functionality to *project* raw
performance data onto specific meanings of "problem", "application" and
"platform".

Using Projection to Rename Columns
----------------------------------

The simplest example of projection is a straightforward renaming of columns.

Let's assume that we've collected some performance data from a few different
implementations of a function, running a number of problem sizes on multiple
machines.

.. important::
    Although we are looking at "function" performance here, the concepts
    generalize to entire software packages.

Our raw performance data might look like this:

.. list-table::
    :widths: 20 20 20 20
    :header-rows: 1

    * - size
      - implementation
      - machine
      - fom

    * - 128x128x128
      - Library 1
      - Cluster 1
      - 0.5

    * - 256x256x256
      - Library 1
      - Cluster 1
      - 2.0

    * - 128x128x128
      - Library 2
      - Cluster 1
      - 0.7

    * - 256x256x256
      - Library 2
      - Cluster 1
      - 2.1

    * - 128x128x128
      - Library 1
      - Cluster 2
      - 0.25

    * - 256x256x256
      - Library 1
      - Cluster 2
      - 1.0

    * - 128x128x128
      - Library 2
      - Cluster 2
      - 0.125

    * - 256x256x256
      - Library 2
      - Cluster 2
      - 0.5

The most obvious projection of this data onto P3 definitions is as follows:

- Each input size maps to a different problem, because each input
  represents a different task to be solved, with its own expected answer to
  validate against.

- Each implementation maps to a different application, because each
  library's implementation of the function produces a solution for a given
  input with measurable performance and correctness.

- Each machine maps to a different platform, because each cluster name
  describes the combination of hardware **and** software used to run the
  experiments.

.. important::
    In reality, a single value is unlikely to provide enough information to
    fully and unambiguously describe a function's behavior, its implementation,
    or the state of a machine when its performance was recorded. But we'll come
    back to that later.

"""

# %%
# After loading our data into a :py:class:`pandas.DataFrame`
# (``df``), we can use the
# :py:func:`p3.data.projection` function to perform this
# projection, renaming the columns as described above.

# sphinx_gallery_start_ignore
# sphinx_gallery_thumbnail_path = "_static/projection_thumbnail.png"
import matplotlib.pyplot as plt
import pandas as pd

import p3

rename_data = {
    "size": ["128x128x128", "256x256x256"] * 4,
    "implementation": (["Library 1"] * 2 + ["Library 2"] * 2) * 2,
    "machine": ["Cluster 1"] * 4 + ["Cluster 2"] * 4,
    "fom": [0.5, 2.0, 0.7, 2.1, 0.25, 1.0, 0.125, 0.5],
}

df = pd.DataFrame(rename_data)
# sphinx_gallery_end_ignore

proj = p3.data.projection(
    df,
    problem=["size"],
    application=["implementation"],
    platform=["machine"],
)
print(proj)

# %%
# Following projection, our performance data is now ready to be passed to
# functions in the :py:mod:`p3.metrics` module.

# %%
# Using Projection to Combine Columns
# -----------------------------------
#
# As we alluded to earlier, it's unlikely that a single column of the raw data
# fully captures the definition of a "problem", "application" or "platform".
#
# Let's make our raw data slightly more complicated, by introducing the notion
# that the function of interest is available in both single precision (FP32)
# and double precision (FP64).
#
# .. list-table::
#     :widths: 20 20 20 20 20
#     :header-rows: 1
#
#     * - size
#       - precision
#       - implementation
#       - machine
#       - fom
#
#     * - 128x128x128
#       - FP32
#       - Library 1
#       - Cluster 1
#       - 0.5
#
#     * - 256x256x256
#       - FP32
#       - Library 1
#       - Cluster 1
#       - 2.0
#
#     * - 128x128x128
#       - FP32
#       - Library 2
#       - Cluster 1
#       - 0.7
#
#     * - 256x256x256
#       - FP32
#       - Library 2
#       - Cluster 1
#       - 2.1
#
#     * - 128x128x128
#       - FP32
#       - Library 1
#       - Cluster 2
#       - 0.25
#
#     * - 256x256x256
#       - FP32
#       - Library 1
#       - Cluster 2
#       - 1.0
#
#     * - 128x128x128
#       - FP32
#       - Library 2
#       - Cluster 2
#       - 0.125
#
#     * - 256x256x256
#       - FP32
#       - Library 2
#       - Cluster 2
#       - 0.5
#
#     * - 128x128x128
#       - FP64
#       - Library 1
#       - Cluster 1
#       - 1.0
#
#     * - 256x256x256
#       - FP64
#       - Library 1
#       - Cluster 1
#       - 4.0
#
#     * - 128x128x128
#       - FP64
#       - Library 2
#       - Cluster 1
#       - 1.4
#
#     * - 256x256x256
#       - FP64
#       - Library 2
#       - Cluster 1
#       - 4.2
#
#     * - 128x128x128
#       - FP64
#       - Library 1
#       - Cluster 2
#       - 0.5
#
#     * - 256x256x256
#       - FP64
#       - Library 1
#       - Cluster 2
#       - 2.0
#
#     * - 128x128x128
#       - FP64
#       - Library 2
#       - Cluster 2
#       - 0.25
#
#     * - 256x256x256
#       - FP64
#       - Library 2
#       - Cluster 2
#       - 1.0
#
# How does this impact our projection? The implementation and machine columns
# are still enough to describe the application and platform (respectively),
# but what about the problem? The answer is, of course: "It depends".
#
# Luckily, this dataset is simple enough that we can enumerate our options:
#
# 1. Each unique (size, precision) tuple maps to a different problem,
#    representing that the problem definition requires the task to be solved to
#    a specific precision (and that the precision has a material impact on the
#    verification of results).
#
# 2. Each size maps to a different problem as before, representing that the
#    problem definition does **not** require the task to be solved to any
#    specific precision, and that implementations are free to select whichever
#    precision delivers the best performance.
#
# Neither of these options is more correct than the other. Rather, they
# represent different studies.
#
# Both projections can be performed with the :py:func:`p3.data.projection`
# function, by passing different arguments.
#
# For the first projection, we now need to specify the names of two columns
# ("size" and "precision") to define the problem:

# sphinx_gallery_start_ignore
df["precision"] = "FP32"
combine_data = {
    "size": ["128x128x128", "256x256x256"] * 4,
    "precision": ["FP64"] * 8,
    "implementation": (["Library 1"] * 2 + ["Library 2"] * 2) * 2,
    "machine": ["Cluster 1"] * 4 + ["Cluster 2"] * 4,
    "fom": [1.0, 4.0, 1.4, 4.2, 0.5, 2.0, 0.25, 1.0],
}
df = pd.concat([df, pd.DataFrame(combine_data)], ignore_index=True)
# sphinx_gallery_end_ignore

proj1 = p3.data.projection(
    df,
    problem=["size", "precision"],
    application=["implementation"],
    platform=["machine"],
)
print(proj1)

# %%
# The original "size" and "precision" columns have been removed, and their
# values have been concatenated to form the new "problem" column.
#
# For the second projection, we just need to specify "size", exactly as we did
# before:

proj2 = p3.data.projection(
    df,
    problem=["size"],
    application=["implementation"],
    platform=["machine"],
)
print(proj2)

# %%
# This time, the original "size" column has been removed, but the "precision"
# column remains.
#
# Clearly, the values provided to the projection function change the structure
# of the resulting :py:class:`pandas.DataFrame`. But why does that matter?
# Well, let's take a look at what happens if we compute the maximum "fom" for
# each (problem, application, platform) tuple in our projected datasets:

max1 = proj1.groupby(["problem", "application", "platform"])["fom"].max()
print(max1)

# %%

max2 = proj2.groupby(["problem", "application", "platform"])["fom"].max()
print(max2)

# %%
#
# Similar :py:func:`pandas.DataFrame.groupby` calls form the backbone of many
# functions provided by the P3 Analysis Library, since metrics like
# "application efficiency" and "performance portability" ultimately depend on
# an understanding of which variable combinations deliver the best performance.
#
# .. important::
#     The selected projection can have significant impact on the results of
#     subsequent analysis, and it is critical to ensure that the projection
#     is correct before digging too deep into (or presenting!) any results.
#
# Next Steps
# ----------
#
# After raw performance data has been projected onto definitions
# of "problem", "application", and "platform", it can be passed to
# any of the P3 Analysis Library functions that expect a
# :py:class:`pandas.DataFrame`.
#
# The examples below show how to use projected data to compute
# and visualize derived metrics like "application efficiency",
# "performance portability", and "code divergence".
#
# .. minigallery::
#     :add-heading: Examples
#
#     ../../examples/metrics/application_efficiency.py
#     ../../examples/cascade/plot_simple_cascade.py
#     ../../examples/navchart/plot_simple_navchart.py
