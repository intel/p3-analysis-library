#!/usr/bin/env python3
# Copyright (c) 2024 Intel Corporation
# SPDX-License-Identifier: 0BSD
"""
Working with Application Efficiency
===================================

Understanding relative performance.

One goal of P3 analysis is to understand how well a given application is able
to adapt to and make effective use of the capabilities of different
platforms. Comparisons of *raw* performance (e.g., time to solution) across
platforms can't help us, because raw performance doesn't reflect how fast an
application **should** run.

To address this, the P3 Analysis Library works with normalized *performance
efficiency* data. With normalized data, an application's performance can be
represented as a number in the range :math:`[0, 1]`, where :math:`1` means
an application is achieving the best possible performance.

There are multiple ways we can normalize the data to measure relative
efficiency, and for this tutorial we will consider *application efficiency*.

Application Efficiency
----------------------

The simplest form of performance efficiency we can work with is *application
efficiency*, defined below:

**Application Efficiency**
  The performance of an *application*, measured relative to the best known
  performance previously demonstrated for solving the same *problem* on the
  same *platform*.

Working with application efficiency is simple because it does not rely on
performance models or theoretical hardware limits. Although it can't tell us
whether an application is performing as well as theoretically possible, it
shows how an application compares to the state-of-the-art, which is often good
enough.

Calculating Application Efficiency
----------------------------------

Let's begin with a very simple example, with a single application, using the
data below:

.. list-table::
    :widths: 20 20 20 20 20
    :header-rows: 1

    * - problem
      - application
      - platform
      - fom
      - date

    * - Test
      - MyApp
      - A
      - 25.0
      - 2023
    * - Test
      - MyApp
      - B
      - 12.5
      - 2023
    * - Test
      - MyApp
      - C
      - 25.0
      - 2023
    * - Test
      - MyApp
      - D
      - NaN
      - 2023
    * - Test
      - MyApp
      - E
      - 5.0
      - 2023

.. tip::
    A NaN or 0.0 performance result is interpreted by the P3 Analysis Library
    to mean that an application run was in some way invalid. We can use this
    to explicitly represent cases where applications did not compile on
    specific platforms, did not run to completion, or ran but produced
    numerical results that failed some sort of verification.

"""

# %%
# After loading this data into a pandas DataFrame (`df`), we can use the
# :py:func:`p3.metrics.application_efficiency` function to calculate a table of
# application efficiencies.

#sphinx_gallery_start_ignore
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import p3

myapp_data = {
    "problem": ["Test"] * 5,
    "application": ["MyApp"] * 5,
    "platform": ["A", "B", "C", "D", "E"],
    "fom": [25.0, 12.5, 25.0, np.nan, 5.0],
    "date": [2023] * 5,
}

df = pd.DataFrame(myapp_data)
#sphinx_gallery_end_ignore

effs = p3.metrics.application_efficiency(df)
print(effs)

# %%
# These initial results may be a little surprising, because they're all
# either 1.0 or 0.0. What happened? Since our dataset contains only one result
# for MyApp on each platform, each non-zero result is the "best known" result
# for that platform! The only exception is Platform D, which is assigned an
# efficiency of 0.0 to reflect that it did not run.
#
# .. tip::
#     Calculating meaningful application efficiency results requires a minimum
#     of two results per platform.
#
# Digging Deeper: Adding More Data
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Let's see what happens if we add some more data, from a different application
# running on the same platforms:
#
# .. list-table::
#     :widths: 20 20 20 20 20
#     :header-rows: 1
#
#     * - problem
#       - application
#       - platform
#       - fom
#       - date
#
#     * - Test
#       - YourApp
#       - A
#       - 25.0
#       - 2023
#     * - Test
#       - YourApp
#       - B
#       - 10.0
#       - 2023
#     * - Test
#       - YourApp
#       - C
#       - 12.5
#       - 2023
#     * - Test
#       - YourApp
#       - D
#       - 6.0
#       - 2023
#     * - Test
#       - YourApp
#       - E
#       - 1.0
#       - 2023

# %%
# After updating our DataFrame, we can re-run the same function as before to
# recompute the application efficiencies.

#sphinx_gallery_start_ignore
yourapp_data = {
    "problem": ["Test"] * 5,
    "application": ["YourApp"] * 5,
    "platform": ["A", "B", "C", "D", "E"],
    "fom": [25.0, 10.0, 12.5, 6.0, 1.0],
    "date": [2023] * 5,
}

df = pd.concat([df, pd.DataFrame(yourapp_data)], ignore_index=True)
#sphinx_gallery_end_ignore

effs = p3.metrics.application_efficiency(df)
print(effs)

# %%
# YourApp is now the fastest (best known) application on every platform,
# and so it assigned an application efficiency of 1.0 everywhere. The
# application efficiency values for MyApp are all between 0.0 and 1.0,
# reflecting how close it gets to the state-of-the-art performance on each
# platform.
#
# .. important::
#     Adding new data changed the application efficiencies for MyApp *and*
#     YourApp. Application efficiency values can become stale over time,
#     and accurate P3 analysis requires us to track "best known" results
#     carefully.
#
# Plotting Application Efficiency
# -------------------------------
#
# The P3 Analysis Library does not contain any dedicated functionality for
# plotting application efficiency values. However, it is straightforward to use
# :py:mod:`matplotlib` and/or the plotting functionality of :py:mod:`pandas` to
# produce useful visualizations.
#
# For example, plotting a bar chart of application efficiences for one
# application can help us to summarize that application's performance more
# effectively than a table:

filtered = effs[effs["application"]=="MyApp"]
filtered.plot(kind="bar", x="platform", y="app eff", xlabel="Platform", ylabel="Application Efficiency", legend=False)
plt.savefig("application_efficiency_bars_2023.png")

# %%
# We can now clearly see that MyApp can adapt to and make very effective use of
# Platforms A and B, is within 2x of state-of-the-art performance on Platform
# C, but performs poorly on Platforms D and E. The key takeaway from this
# analysis is that a developer wishing to improve the "performance portability"
# of MyApp should focus on improving support for Platforms D and E.
#
# Working with Historical Data
# ----------------------------
#
# The performance of an application can change over time, as developers add new
# features and optimize for new platforms, or due to changes in the software
# stack (e.g., new compiler or driver versions).
#
# Let's see how this could affect the application efficiency of MyApp, by adding
# some new data points collected at a later point in time:
#
# .. list-table::
#     :widths: 20 20 20 20 20
#     :header-rows: 1
#
#     * - problem
#       - application
#       - platform
#       - fom
#       - date
#
#     * - Test
#       - MyApp
#       - A
#       - 30.0
#       - 2024
#     * - Test
#       - MyApp
#       - B
#       - 15.0
#       - 2024
#     * - Test
#       - MyApp
#       - C
#       - 25.0
#       - 2024
#     * - Test
#       - MyApp
#       - D
#       - 3.0
#       - 2024
#     * - Test
#       - MyApp
#       - E
#       - 2.5
#       - 2024

# %%
# We can compute application efficiency as before:

#sphinx_gallery_start_ignore
new_myapp_data = {
    "problem": ["Test"] * 5,
    "application": ["MyApp"] * 5,
    "platform": ["A", "B", "C", "D", "E"],
    "fom": [30.0, 15.0, 25.0, 3.0, 2.5],
    "date": [2024] * 5,
}

df = pd.concat([df, pd.DataFrame(new_myapp_data)], ignore_index=True)
#sphinx_gallery_end_ignore

effs = p3.metrics.application_efficiency(df)
print(effs)

# %%
# These latest results suggest that the developers of MyApp acted upon
# earlier results and improved support for Platforms D and E. But in doing so,
# a small performance regression was introduced in Platforms A and B.
#
# .. note::
#     Such trade-offs are very common, especially when developers wish to
#     maintain a single source code that targets multiple platforms.
#
# Computing the correct application efficiency values for MyApp and YourApp
# requires that our dataset contains all of our historical performance results.
# Since what we're really interested in understanding is the *latest*
# application efficiency, we should take care to filter our data appropriately
# before producing any plots.

filtered = effs[(effs["application"]=="MyApp") & (effs["date"]==2024)]
filtered.plot(kind="bar", x="platform", y="app eff", xlabel="Platform", ylabel="Application Efficiency", legend=False)
plt.savefig("application_efficiency_bars_2024.png")
