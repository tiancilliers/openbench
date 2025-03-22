import numpy as np
import json
import os

def rank_relative(benchmarks):
    for bench in benchmarks:
        print(bench)
        print()
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
    benchmark_ks, k_n, k_d = [], 0, 0
    for i in range(len(benchmarks)):
        bench_k_n, bench_k_d = 0, 0
        for j in range(len(models)):
            if benchmark_matr[j][i] is not None:
                bench_k_n += benchmark_matr[j][i]*v[-1,j]
                bench_k_d += benchmark_matr[j][i]**2
        benchmark_ks.append(bench_k_n/bench_k_d)
        if benchmarks[i].get("scale_factor") is not None:
            k_n += bench_k_n/bench_k_d*benchmarks[i]["scale_factor"]
            k_d += bench_k_n**2/bench_k_d**2
    overall_k = k_n/k_d
    solve_res = v[-1,:]*overall_k*100
    return ({model:res for model,res in zip(models, solve_res)}, [benchmark_k*overall_k for benchmark_k in benchmark_ks])

def read_all_benches(filter):
    with open('data_list.json', 'r') as f:
        data_list = json.load(f)
    sources = []
    for file in data_list[filter["class"]]:
        with open(file["path"], 'r') as f:
            sources.append(json.load(f))
        for bench, sf in zip(sources[-1]["benchmarks"], file["scale_factors"]):
            bench["scale_factor"] = sf
    benchmarks = [bench for source in sources if source.get("class") == filter["class"] for bench in source["benchmarks"]]
    benchmarks = [bench for bench in benchmarks if all(bench.get(key) == value for key,value in filter["subfilters"].items())]
    return benchmarks

def update_data_list():
    with open('data_list.json', 'r') as f:
        old_data_list = json.load(f)
    new_data_list = {}
    for file in os.listdir("data"):
        if file.endswith(".json"):
            with open(f"data/{file}", 'r') as f:
                data = json.load(f)
            if new_data_list.get(data["class"], None) is None:
                new_data_list[data["class"]] = []
            new_data_list[data["class"]] += [{"path":f"data/{file}", "scale_factors":[]}]
    for class_name in new_data_list.keys():
        file_scale_factors = {file["path"]:file["scale_factors"] for file in old_data_list.get(class_name, [])}
        benches = []
        n_benches = []
        for file in new_data_list[class_name]:
            with open(file["path"], 'r') as f:
                data = json.load(f)
            sf = file_scale_factors.get(file["path"], [])
            n_benches.append(len(data["benchmarks"]))
            for i in range(len(data["benchmarks"])):
                benches.append(data["benchmarks"][i])
                if i < len(sf):
                    benches[-1]["scale_factor"] = sf[i]
        scores, bench_ks = rank_relative(benches)
        cumn = 0
        for i, n in enumerate(n_benches):
            new_data_list[class_name][i]["scale_factors"] = bench_ks[cumn:cumn+n]
            cumn += n
    with open('data_list.json', 'w') as f:
        json.dump(new_data_list, f, indent=4)

#update_data_list()

benchmarks = read_all_benches({"class":"graphics","subfilters":{}})
scores, bench_ks = rank_relative(benchmarks)
for model, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
    print(f"{model:<30} {score:6.0f}")
