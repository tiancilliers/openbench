import numpy as np
import json

def rank_relative(benchmarks, unity):
    models = list(set(model for bench in benchmarks for model in bench['models']))
    benchmark_sum_sq = [sum(result**2 for result in bench['results']) for bench in benchmarks]
    benchmark_dicts = [{model:result for model,result in zip(bench['models'],bench['results'])} for bench in benchmarks]
    benchmark_matr = [[bench.get(model, None) for bench in benchmark_dicts] for model in models]
    solve_matr = [[0 for _ in range(len(models))] for _ in range(len(models))]
    for i in range(len(models)):
        for j in range(len(models)):
            if i == j:
                solve_matr[i][j] = sum((benchmark_matr[i][k]**2/benchmark_sum_sq[k]-1)**2 for k in range(len(benchmarks)) if benchmark_matr[i][k] is not None)
            else:
                solve_matr[i][j] = sum((benchmark_matr[i][k]**2/benchmark_sum_sq[k]-1)*benchmark_matr[i][k]*benchmark_matr[j][k]/benchmark_sum_sq[k] for k in range(len(benchmarks)) if benchmark_matr[i][k] is not None and benchmark_matr[j][k] is not None)
    u, e, v = np.linalg.svd(np.array(solve_matr))
    solve_res = v[-1,:]/v[-1,models.index(unity)]
    return {model:res for model,res in zip(models, solve_res)}

def read_all_benches(filter):
    with open('data_list.json', 'r') as f:
        data_list = json.load(f)
    sources = []
    for filename in data_list[filter["class"]]:
        with open(filename, 'r') as f:
            sources.append(json.load(f))
    benchmarks = [bench for source in sources if source.get("class") == filter["class"] for bench in source["benchmarks"]]
    benchmarks = [bench for bench in benchmarks if all(bench.get(key) == value for key,value in filter["subfilters"].items())]
    return benchmarks

benchmarks = read_all_benches({"class":"graphics","subfilters":{"type":"gaming-average"}})
ranking = rank_relative(benchmarks, "RTX 5070")
print(sorted(ranking.items(), key=lambda x: x[1], reverse=True))