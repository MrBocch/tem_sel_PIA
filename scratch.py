"""

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

                    candidate_trip[i], candidate_trip[j] = (candidate_trip[j],candidate_trip[i],)
                    
                    # fully re-evaluate solution
                    candidate.total_latency = evaluate(inst,candidate,)

                    # improvement found
                    if (candidate.total_latency < best_solution.total_latency):

                        if debug:
                            old = best_solution.total_latency
                            new = candidate.total_latency

                            print(f"swap (client {trip[i]}) <-> (client {trip[j]}) | delta: {new - old}")

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
"""

