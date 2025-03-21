# OpenBench
OpenBench is an open-source PC component benchmark repository and processing software.

## How it works
OpenBench takes as input a set of benchmarks, each giving some performance metric of some subset of models. Since this performance metric may be different, it is only assumed to be directly correlated to the real performance through some constant factor. OpenBench's algorithm then produces a relative ranking of models present in one or more benchmarks, as well as a set of these constant factors, such that the ranking minimizes the mean squared error (MSE) between the performance numbers multiplied by the constant factors and the output ranking. **This basically allows the relative scoring of all models in each benchmark to contribute to the overall ranking in a mathematically optimal manner**. 

OpenBench then scales the relative ranking of all models in a way that minimizes the change of existing models when new benchmarks are added. While slightly arbitrary, this allows the use of the BenchScore as a performance number that should not change as new, higher-performing, models are added. The vision for this is that retailers can use this database to provide accurate and stable performance estimates to their customers.

### TLDR
* The ratio between scores of different models is as accurate as possible
* The absolute scores change as little as possible when new benchmarks are added

## How to use
Access the OpenBench rankings [here](https://tiancilliers.github.io/openbench).

For more advanced use, use the `openbench.py` program. This contains the same algorithm, and a usage guide will be added in the future.

## How to contribute
Add benchmark results to the `data/` directory, following the existing formatting, and submit a pull request.

> [!IMPORTANT]  
> Do not modify the `data_list.json` file manually. This file contains the parameters needed for the correct BenchScore scaling, and needs to be updated via the correct algorithm to avoid scores fluctuating.
