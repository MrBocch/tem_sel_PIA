import random
from itertools import combinations
from Item import Item
from Heuristics import Def, MaxP, MinW, MaxPW

# capacity of knapsack
W = 50

# number of items
n = 50

# maximum weight per item
w = 15

# maximum profit per item
p = 15

# tournament size
TS = 2

# mutation rate
MR = 0.01

def generate_chromosome(W, n, w, p):
    chromosomes = []
    for i in range(n):
        # empezar de 0 o 1?
        weight = random.randint(1, w)
        profit = random.randint(1, p)
        item = Item(weight, profit)
        chromosomes.append(item)

    return chromosomes

def chromosome_to_string(items):
    return (''.join([(s.to_binary()) for s in items]))

def generate_instances(instances):
    global W, n, w, p
    intcs = []
    for i in range(instances):
        intcs.append(generate_chromosome(W,n,w,p))

    return intcs

def instance_profit(items):
    return sum([i.profit for i in items])

def generate_csv(file, items):
    with open(file, "w") as f:
        f.write('Item,Benefit,Weight\n')
        for idx, item in enumerate(items):
            f.write(f"{idx},{item.profit},{item.weight}\n")

def tournament_winner(items):
    global W
    p1_scores = [Def(items[0], W), MaxP(items[0], W), MinW(items[0], W), MaxPW(items[0], W)]
    p1_scores = [instance_profit(l) for l in p1_scores]
    p2_scores = [Def(items[1], W), MaxP(items[1], W), MinW(items[1], W), MaxPW(items[1], W)]
    p2_scores = [instance_profit(l) for l in p2_scores]
    # menor es mejor
    if fitness(p1_scores) >= fitness(p2_scores):
        return items[1]
    else:
        return items[0]

def fitness(scores):
    return sum(abs(x - y) for x, y in combinations(scores, 2))
    # data y codigo yo deben de ir juntos
    # queremos que instancias que todos tengan puntuaje mas cercanas
    # ff = (abs(scores[0] - scores[1]) + abs(scores[0] - scores[2]) + abs(scores[0] - scores[3]) +
          # abs(scores[1] - scores[2]) + abs(scores[1] - scores[3]) +
          # abs(scores[2] - scores[3])
          # )
    # return ff


def crossover(s1, s2):
    length = min(len(s1), len(s2))
    mid = length // 2
    margin = max(1, length // 4)
    point = random.randint(mid - margin, mid + margin)

    child1 = s1[:point] + s2[point:]
    child2 = s2[:point] + s1[point:]
    return child1, child2

def mutate(c):
    global MR
    mutated = [
        '1' if bit == '0' and random.random() < MR else
        '0' if bit == '1' and random.random() < MR else bit
        for bit in c
    ]
    return "".join(mutated)

def string_to_instance(s):
    # bin_size = '04b' (p+w) = (4+4)
    bin_size = 8
    s_split = [s[i:i+bin_size] for i in range(0, len(s), bin_size)]
                         #weight          #profit
    instance = [Item(int(s_s[:4], 2), int(s_s[4:], 2)) for s_s in s_split]
    return instance

def next_generation(items, c1, c2):
    global W
    population = []
    for i in items:
        profits = [Def(i, W), MaxP(i, W), MinW(i, W), MaxPW(i, W)]
        score = [instance_profit(l) for l in profits]
        population.append(fitness(score))

    # eliminamos dos con peor fitness
    items = pop_two_highest(items, population)
    items.append(c1)
    items.append(c2)
    return items

def two_highest_indices(lst):
    high1, high2 = (0, 1) if lst[0] > lst[1] else (1, 0)

    for i in range(2, len(lst)):
        if lst[i] > lst[high1]:
            high2, high1 = high1, i
        elif lst[i] > lst[high2]:
            high2 = i

    return [high1, high2]

def pop_two_highest(lst, pop):
    indices = two_highest_indices(pop)
    indices.sort(reverse=True)  # Sort in descending order to pop safely
    lst.pop(indices[0])  # Pop the first highest
    lst.pop(indices[1])  # Pop the second highest
    return lst

def training(population):
    # salimos de loop despues de cuantas iteraciones
    global TS
    iteracion = 0
    while True:
        print(f"iteracion {iteracion}")
    # selection, tournament
        print("tournament")
        # partir lista en dos
        t1 = random.sample(population[:len(population)//2], TS)
        t2 = random.sample(population[len(population)//2:], TS)
        padre1 = tournament_winner(t1)
        padre2 = tournament_winner(t2)
    # crossover
        print("crossover")
        schrome_p1 = chromosome_to_string(padre1)
        schrome_p2 = chromosome_to_string(padre2)

        c1, c2 = crossover(schrome_p1, schrome_p2)
    # mutate
        print("mutating")
        c1 = mutate(c1)
        c2 = mutate(c2)
    # new generation
        print("next generation")
        c1 = string_to_instance(c1)
        c2 = string_to_instance(c2)
        population = next_generation(population, c1, c2)
        iteracion += 1
        print(len(population))

population = generate_instances(10)
training(population)
