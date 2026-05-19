import os
import random
from dataclasses import dataclass
from typing import Self
from typing import override

# =========================================
# modelar texto de instancia como un objeto
# =========================================
@dataclass
class Instance:
    nb_clients: int
    nb_trips: int
    vehicle_capacity: int
    client_demands: list[int]
    service_times: list[int]
    travel_times: list[list[int]]

    # ================================================
    # codigo que corre cuando imprimimos una instancia
    # ================================================
    @override
    def __str__(self) -> str:
        lines: list[str] = []

        lines.append("VRP Instance")
        lines.append(f"Clients: {self.nb_clients}")
        lines.append(f"Trips: {self.nb_trips}")
        lines.append(f"Capacity: {self.vehicle_capacity}")

        lines.append("\nDemands:")
        lines.append(" ".join(map(str, self.client_demands)))

        lines.append("\nService Times:")
        lines.append(" ".join(map(str, self.service_times)))
        

        lines.append("\nTravel Time Matrix:")
        header = "  | " + " ".join(f"{i:4}" for i in range(self.nb_clients + 1))
        lines.append(header)
        lines.append("-" * len(header))

        for idx, row in enumerate(self.travel_times):
            label = "D" if idx == 0 else str(idx)
            formatted = f"{label:2}| " + " ".join(f"{x:4}" for x in row)
            lines.append(formatted)

        # for row in self.travel_times:
        #     formatted = " ".join(f"{x:4}" for x in row)
        #     lines.append(formatted)

        return "\n".join(lines)

    # ===========================
    # codigo para parsear archivo
    # ===========================
    @classmethod
    def from_string(cls, text: str) -> Self:
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        nb_clients = 0
        nb_trips = 0
        vehicle_capacity = 0

        client_demands: list[int] = []
        service_times: list[int] = []
        travel_times: list[list[int]] = []

        i = 0

        while i < len(lines):
            line = lines[i]

            if line.startswith("nbClients:"):
                nb_clients = int(line.split(":")[1])

            elif line.startswith("nbTrips:"):
                nb_trips = int(line.split(":")[1])

            elif line.startswith("VehCapacity:"):
                vehicle_capacity = int(line.split(":")[1])

            elif line.startswith("ClientDemands:"):
                i += 1
                client_demands = list(map(int, lines[i].split()))

            elif line.startswith("ServiceTimes:"):
                i += 1
                service_times = list(map(int, lines[i].split()))

            elif line.startswith("TravelTimes:"):
                for _ in range(nb_clients + 1):
                    i += 1
                    row = list(map(int, lines[i].split()))
                    travel_times.append(row)

            i += 1

        return cls(
            nb_clients=nb_clients,
            nb_trips=nb_trips,
            vehicle_capacity=vehicle_capacity,
            client_demands=client_demands,
            service_times=service_times,
            travel_times=travel_times,
        )

# =============================
# como representamos soluciones
# =============================
@dataclass
class Solution:
    trips: list[list[int]]
    total_latency: int

# ========================================================
# codigo para extraer el texto de una instancia de archivo
# ========================================================
def get_instances_paths(folder : str) -> list[str] :
    return [f"{folder}/{f}" for f in os.listdir(folder) if f[0] == "M"]
    # return ["./instancias/MT-DMP10s0-01.txt"
    #       ,"./instancias/MT-DMP15s0-03.txt"
    #       ,"./instancias/MT-DMP15s0-04.txt"
    #       ,"./instancias/MT-DMP10s0-05.txt"]

# toma path the instancia, y regresa objeto de instancia
def open_instances(f : str) -> Instance :
    contents : str = ""
    with open(f, "r", encoding="utf-8") as instance:
        contents = instance.read()

    instance = Instance.from_string(contents)
    return instance

# ===============
# helper function
# ===============
def feasible_customers_exist(
    inst: Instance,
    unvisited_clients: set[int],
    remaining_capacity: int,
) -> bool:
    for customer in unvisited_clients:
        demand = inst.client_demands[customer - 1]

        if demand <= remaining_capacity:
            return True

    return False

# ==============================
# creador de RCL basado en valor
# ==============================
def build_rcl(
    candidates: list[tuple[int, int]],
    alpha: float,
) -> list[int]:
    min_cost = min(cost for _, cost in candidates)
    max_cost = max(cost for _, cost in candidates)

    threshold = (min_cost + alpha * (max_cost - min_cost))

    return [customer for customer, cost in candidates if cost <= threshold]

# ===================
# codigo de algoritmo
# ===================
def grasp(inst: Instance, alpha : float, debug=True) -> Solution:
    trips: list[list[int]] = []
    remaining_capacity : int = inst.vehicle_capacity
    unvisited_clients: set[int] = set(range(1, inst.nb_clients + 1))

    # constructive phase
    # Deposit is node (0)
    while len(unvisited_clients) != 0:
        current_trip: list[int] = []
        remaining_capacity = inst.vehicle_capacity
        current_node = 0

        while feasible_customers_exist(inst, unvisited_clients, remaining_capacity):
            # consiguir candidatos que almenos pueden ser satisfasidos
            # lista de candidatos (candidato, costo)
            candidates: list[tuple[int, int]] = []
            for customer in unvisited_clients:
                demand = inst.client_demands[customer - 1]

                if demand <= remaining_capacity:
                    travel_time = inst.travel_times[current_node][customer]

                    candidates.append((customer, travel_time))
            # crear RCL filtrando con ...
            rcl : list[int] = build_rcl(candidates, alpha)
            chosen : int = random.choice(rcl)

            # agregar cliente al viaje
            current_trip.append(chosen)

            # remover de no visitados
            unvisited_clients.remove(chosen)

            # actualizar capacidad
            remaining_capacity -= (inst.client_demands[chosen - 1])

            # mover vehiculo
            current_node = chosen

        trips.append(current_trip)

    solution = Solution(trips=trips,total_latency=0,)

    solution.total_latency = evaluate(inst,solution,)

    if debug:
        print("solution after constructive phase")
        print(solution)
    # =====================
    # local search phase
    # movements are, within
    # trips, swap nodes
    # =====================
    solution = local_search(inst, solution, debug)

    if debug:
        print("solution after local search")
        print(solution)

    return solution


from copy import deepcopy
# =================================
# local search function
# movements are swapping two clients
# within the same trip
# =================================
def local_search(
    inst: Instance,
    solution: Solution,
    debug: bool = False,
) -> Solution:

    best_solution = deepcopy(solution)

    improved = True

    while improved:
        improved = False

        # explore neighborhood
        for t_idx, trip in enumerate(best_solution.trips):

            for i in range(len(trip)):
                for j in range(i + 1, len(trip)):

                    # create candidate solution
                    candidate = deepcopy(best_solution)

                    # apply swap
                    candidate_trip = candidate.trips[t_idx]

                    candidate_trip[i], candidate_trip[j] = (
                        candidate_trip[j],
                        candidate_trip[i],
                    )

                    # fully re-evaluate solution
                    candidate.total_latency = evaluate(
                        inst,
                        candidate,
                    )

                    # improvement found
                    if (
                        candidate.total_latency
                        < best_solution.total_latency
                    ):

                        if debug:
                            old = best_solution.total_latency
                            new = candidate.total_latency

                            print(
                                f"swap "
                                f"(client {trip[i]}) "
                                f"<-> "
                                f"(client {trip[j]}) "
                                f"| delta: {new - old}"
                            )

                        best_solution = candidate
                        improved = True

        solution = best_solution

    return best_solution

def trip_latency(inst: Instance, trip: list[int]) -> int:
    # Latency contribution of a single trip starting from depot
    latency = 0
    current_time = 0
    current_node = 0

    for customer in trip:
        current_time += inst.travel_times[current_node][customer]
        latency += current_time
        current_time += inst.service_times[customer - 1]
        current_node = customer

    return latency


# =================================
# Funcion para evaluar una solucion
# el evaluador va simular la ruta
# (tambien) agrega latencia de
# una ruta termina para regresar
# al depo
# =================================
def evaluate(inst: Instance,solution: Solution,) -> int:
    total_latency = 0
    current_time = 0

    for trip in solution.trips:
        current_node = 0  # depot

        for customer in trip:
            # travel to customer
            travel_time = inst.travel_times[current_node][customer]
            current_time += travel_time
            # customer waited until now
            total_latency += current_time
            # service time
            service_time = inst.service_times[customer - 1]
            current_time += service_time
            # vehicle moves to customer
            current_node = customer

        # return to depot after trip
        return_time = inst.travel_times[current_node][0]
        current_time += return_time

    return total_latency

def main():
    instances : list[str] = get_instances_paths("instancias")
    for i in instances:
        print("\n================================================")
        print("================================================")
        i = open_instances(i)
        print(i, end="\n\n")
        # print(i.travel_times)
        grasp(i, 0.3)
        print("================================================")
        print("================================================")



main()
