# Copyright (c) 2019-2023 Intel Corporation
# SPDX-License-Identifier: MIT

import collections
import itertools as it

from p3._utils import _require_columns
from p3.data._validation import _validate_coverage_json


def _extract_platforms(setmap):
    """
    Extract a list of unique platforms from a set map
    """
    unique_platforms = set(it.chain.from_iterable(setmap.keys()))
    return list(unique_platforms)


def _distance(setmap, p1, p2):
    """
    Compute distance between two platforms
    """
    total = 0
    for pset, count in setmap.items():
        if (p1 in pset) or (p2 in pset):
            total += count
    d = 0
    for pset, count in setmap.items():
        if (p1 in pset) ^ (p2 in pset):
            d += count / float(total)
    return d


def _average_distance(setmap):
    """
    Compute average pair-wise distance between all platforms
    """
    platforms = _extract_platforms(setmap)

    d = 0
    npairs = 0
    for p1, p2 in it.combinations(platforms, 2):
        d += _distance(setmap, p1, p2)
        npairs += 1

    if npairs == 0:
        return 0
    return d / float(npairs)


def _coverage_to_divergence(maps):
    """
    Fold a list of coverage maps into a divergence score.
    """
    linemap = collections.defaultdict(set)
    for p, coverage in enumerate(maps):
        for entry in coverage:
            unique_fn = (entry["file"], entry["id"])
            for region in entry["lines"]:
                # If a region is a single integer, it represents one line.
                if isinstance(region, int):
                    line = region
                    linemap[(unique_fn, line)].add(p)

                # If a region is a list, it represents a [start, end] pair.
                if isinstance(region, list):
                    for line in range(region[0], region[1]):
                        linemap[(unique_fn, line)].add(p)

    setmap = collections.defaultdict(int)
    for key, platforms in linemap.items():
        setmap[frozenset(platforms)] += 1

    return _average_distance(setmap)


def _coverage_string_to_json(string):
    """
    Convert a coverage string into a JSON object
    """
    return _validate_coverage_json(string)


def divergence(df, cov=None):
    r"""
    Calculate code divergence.

    Code divergence is calculated as proposed by Harrell and Kitson
    in "`Effective Performance Portability`_", using the Jaccard distance
    to measure the distance between two source codes.

    For a given set of platforms, :math:`H`, the code divergence :math:`CD` of
    an application :math:`a` solving problem :math:`p` is an average of
    pairwise distances:

    .. math::
        CD(a, p, H) = \binom{|H|}{2}^{-1}
                      \sum_{\{i, j\} \in H \times H} {d_{i, j}(a, p)}

    where :math:`d_{i, j}(a, p)` represents the distance between the source
    code required by platforms :math:`i` and :math:`j` for application
    :math:`a` to solve problem :math:`p`.

    The distance is calculated as:

    .. math::
        d_{i, j}(a, p) = 1 - \frac{|c_i(a, p) \cap c_j(a, p)|}
                                  {|c_i(a, p) \cup c_j(a, p)|}

    where :math:`c_i` and :math:`c_j` are the lines of code required to compile
    application :math:`a` and solve problem :math:`p` using platforms :math:`i`
    and :math:`j`. A distance of 0 means that all code is shared between the
    two platforms, whereas a distance of 1 means that no code is shared.

    .. _Effective Performance Portability:
        https://doi.org/10.1109/P3HPC.2018.00006

    Parameters
    ----------
    df: DataFrame
        A pandas DataFrame storing performance data. The following columns are
        required: "problem", "platform", "application".

        If `cov` is None, a "coverage" column is required. Values of the
        "coverage" column must be coverage traces adhering to the P3 Analysis
        Library coverage schema. Otherwise, a "coverage_key" column is
        required.

    cov: DataFrame, optional
        A pandas DataFrame storing coverage data. The following columns are
        required: "coverage_key", "coverage".

        Values of the "coverage" column must be coverage traces adhering to the
        P3 Analysis Library coverage schema.

    Returns
    -------
    DataFrame
        A new pandas DataFrame storing the code divergence values calculated
        from the configuration and coverage data provided.

    Raises
    ------
    ValueError
        If any of the required columns are missing.
        If any coverage string fails to validate against the P3 coverage
        schema.

    TypeError
        If any value in the "coverage" column is not a JSON string.

    """
    _require_columns(df, ["problem", "platform", "application"])
    if cov is None:
        # The original df must already contain coverage information
        _require_columns(df, ["coverage"])
        p3df = df.copy()
    else:
        # Expand original df by substituting the sha for its coverage string
        _require_columns(df, ["coverage_key"])
        _require_columns(cov, ["coverage_key", "coverage"])
        p3df = df.join(cov.set_index("coverage_key"), on="coverage_key")

    p3df["coverage"] = p3df["coverage"].apply(_coverage_string_to_json)

    key = ["problem", "application"]
    groups = p3df[key + ["coverage"]].groupby(key)
    cd = groups.agg(_coverage_to_divergence)
    cd.reset_index(inplace=True)
    cd.rename(columns={"coverage": "divergence"}, inplace=True)

    return cd
