P3 Analysis
===========

The goal of P3 analysis is to understand the interaction of application
performance, application portability and developer productivity. Using
quantitative metrics, developers can set objective goals and measure their
progress towards those goals.

Terminology
###########

The terminology used by the P3 Analysis Library was first introduced in
"`Implications of a Metric for Performance Portability`_".

.. _Implications of a Metric for Performance Portability:
   https://doi.org/10.1016/j.future.2017.08.007

**Problem**
  A task with a pass/fail metric for which quantitative performance may be
  measured.

**Application**
  Software capable of solving a *problem* with measurable correctness and
  performance.

**Platform**
  A collection of software and hardware on which an *application* may run a
  *problem*.

**Application Efficiency**
  The performance of an *application*, measured relative to the best known
  performance previously demonstrated for solving the same *problem* on the
  same *platform*.

**Architectural Efficiency**
  The performance of an *application*, measured relative to the theoretical
  peak performance of the *platform* (e.g. peak memory bandwidth).

Some of these definitions are flexible, allowing the same performance data
to be used for multiple case studies with different interpretations of these
terms. The library is designed with this flexibility in mind (see
:py:func:`p3.data.projection`); concrete definitions are not required when
collecting data.
