import random

# Definición de una instancia del problema de la mochila
def generate_knapsack_instance(num_items, capacity):
    items = [(random.randint(1, 100), random.randint(1, 50)) for _ in range(num_items)]  # (profit, weight)
    return items, capacity

# Generar instancias basadas en el documento
def generate_document_instances():
    instances_alpha1 = [generate_knapsack_instance(50, 50) for _ in range(400)]  # α1 (entrenamiento)
    instances_alpha2 = [generate_knapsack_instance(50, 50) for _ in range(400)]  # α2 (pruebas)
    instances_beta1 = [generate_knapsack_instance(20, random.randint(30, 100)) for _ in range(600)]  # β1 (difíciles, 20 ítems)
    instances_beta2 = [generate_knapsack_instance(50, random.randint(50, 150)) for _ in range(600)]  # β2 (difíciles, 50 ítems)
    return instances_alpha1, instances_alpha2, instances_beta1, instances_beta2

# Heurísticas básicas
def heuristic_default(items):
    return items  # Orden original

def heuristic_max_profit(items):
    return sorted(items, key=lambda x: x[0], reverse=True)

def heuristic_max_profit_weight(items):
    return sorted(items, key=lambda x: x[0] / x[1], reverse=True)

def heuristic_min_weight(items):
    return sorted(items, key=lambda x: x[1])

# Aplicación de heurística a una instancia
def apply_heuristic(items, capacity, heuristic):
    sorted_items = heuristic(items)
    total_profit, total_weight = 0, 0
    knapsack = []

    for profit, weight in sorted_items:
        if total_weight + weight <= capacity:
            knapsack.append((profit, weight))
            total_profit += profit
            total_weight += weight

    return total_profit, knapsack

# Cargar instancias
i_alpha1, i_alpha2, i_beta1, i_beta2 = generate_document_instances()

# Evaluación con algoritmo genético balanceado y entrenamiento
def genetic_algorithm_train(instances, pop_size=10, generations=50, mutation_rate=0.1):
    heuristics = [heuristic_default, heuristic_max_profit, heuristic_max_profit_weight, heuristic_min_weight]

    # Generar población inicial con distribución balanceada
    population = []
    for _ in range(pop_size):
        sequence = [heuristics[i % len(heuristics)] for i in range(50)]  # Secuencia de heurísticas balanceada
        population.append(sequence)

    def fitness(heuristic_seq, instances):
        total_profit = 0
        for items, capacity in instances:
            profit, _ = apply_heuristic(items, capacity, lambda x: [heuristic_seq[i % len(heuristic_seq)](x)[i] for i in range(len(x))])
            total_profit += profit
        return total_profit / len(instances)

    for _ in range(generations):
        # Evaluación de aptitud en todas las instancias
        scores = [(fitness(ind, instances), ind) for ind in population]
        scores.sort(reverse=True, key=lambda x: x[0])
        population = [ind for _, ind in scores[:pop_size//2]]

        # Cruza
        offspring = []
        for _ in range(pop_size//2):
            p1, p2 = random.sample(population, 2)
            crossover_point = random.randint(1, len(p1) - 1)
            child = p1[:crossover_point] + p2[crossover_point:]
            offspring.append(child)

        # Mutación balanceada
        for child in offspring:
            if random.random() < mutation_rate:
                idx = random.randint(0, len(child) - 1)
                child[idx] = random.choice(heuristics)

        population.extend(offspring)

    best_solution = max(population, key=lambda ind: fitness(ind, instances))
    best_profit = fitness(best_solution, instances)
    return best_profit, best_solution

# Ejecutar entrenamiento en instancias específicas
def train_and_evaluate():
    best_profit, best_solution = genetic_algorithm_train(i_alpha1)  # Entrenamos con α1
    print(f"\nTraining Completed. Best Profit: {best_profit}")
    print(f"Best Heuristic Sequence: {[h.__name__ for h in best_solution]}")
    print("\nSample Instances Used:")
    for i, (items, capacity) in enumerate(i_alpha1[:5]):  # Imprimir 5 instancias de muestra
        print(f"Instance {i+1}: Capacity={capacity}, Items={items}")

# Ejecutar entrenamiento y evaluación
train_and_evaluate()
