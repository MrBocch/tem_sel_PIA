from Item import Item
from Heuristics import MaxP, MinW, MaxPW, Def

import os
def get_intances():
    instances = []
    for filename in os.listdir("instances/"):
        file_path = os.path.join("instances/", filename)
        with open(file_path, "r") as f:
            instance = []
            for line in f:
                l = (line.strip()).split(",")[1:]
                if l[0] == "Benefit":
                    continue
                else:
                    #Benefit, Weight
                    #Item(weight, profit)
                    item = Item(int(l[1]), int(l[0]))
                    instance.append(item)

            instances.append(instance)

    return instances

print(get_intances())
