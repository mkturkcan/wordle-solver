import json
import numpy as np
from joblib import Parallel, delayed

with open('words.json') as f:
    words = json.loads(f.read())
    
all_words = list(set(words['solutions']+words['herrings']))

def calculate_guess(x,y):
    res = [i for i in '?????']
    for i in range(5):
        if x[i] == y[i]:
            res[i] = 'G'
    for i in range(5):
        if x[i] in y and res[i] != 'G':
            res[i] = 'Y'
    return res

remaining = {}
for j in all_words:
    remaining[j] = 0
    
counter_checkpoint = 0
soln_counter = counter_checkpoint

def process(i):
    for j in all_words:
        remaining[j] = 0
    i_ind = i
    i = words['solutions'][i]
    for j in all_words:
        Gkeys = {}
        Ykeys = {}
        res = calculate_guess(j,i)
        for k in range(5):
            if res[k] == 'G':
                if j[k] in Gkeys:
                    Gkeys[j[k]] += 1
                else:
                    Gkeys[j[k]] = 1
        for k in range(5):
            if res[k] == 'Y':
                if j[k] in Ykeys:
                    Ykeys[j[k]] += 1
                else:
                    Ykeys[j[k]] = 1
        
        possible_solutions = all_words
        for k in range(5):
            if res[k] == 'G':
                possible_solutions = [s for s in possible_solutions if s[k] == j[k]]
            elif res[k] == 'Y':
                possible_solutions = [s for s in possible_solutions if j[k] in s and j[k] != s[k]]
                if Ykeys[j[k]]>1:
                    threshold = Ykeys[j[k]]
                    if j[k] in Gkeys:
                        threshold += Gkeys[j[k]]
                    possible_solutions = [s for s in possible_solutions if s.count(j[k])>=threshold]
            else:
                if j[k] not in Gkeys and j[k] not in Ykeys:
                    possible_solutions = [s for s in possible_solutions if j[k] not in s]
                else:
                    if j[k] in Gkeys and j[k] in Ykeys: # only n of these exist
                        possible_solutions = [s for s in possible_solutions if s.count(j[k])==Gkeys[j[k]]+Ykeys[j[k]]]
                    elif j[k] in Gkeys: # only n of these exist
                        possible_solutions = [s for s in possible_solutions if s.count(j[k])==Gkeys[j[k]]]
                    elif j[k] in Ykeys: # only n of these exist
                        possible_solutions = [s for s in possible_solutions if s.count(j[k])==Ykeys[j[k]]]
        remaining[j] += len(possible_solutions)
    return remaining
    
results = Parallel(n_jobs=16)(delayed(process)(i) for i in range(len(words['solutions'])))


final_results = {}
for j in all_words:
    final_results[j] = 0
for result in results:
    for j in result.keys():
        final_results[j] += result[j]
        


remaining_keys = list(final_results.keys())
remaining_vals = list(final_results.values())

vals_sorter = np.argsort(remaining_vals)
print('Printing Best Words (In Order)')
for a in range(100):
    print(a+1, remaining_keys[vals_sorter[a]], remaining_vals[vals_sorter[a]])