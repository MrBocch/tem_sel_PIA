
# Default heuristic, packs the items in the same order that they
# are contained in the instance
def Def(items, capacity):
    sack = []
    sack_total_weight = 0
    banned = [] # index of items wich go over capacity
    i = 0
    while len(banned) != len(items):
        if i == len(items):
            i = 0

        if i in banned:
            i += 1
            continue

        item = items[i]
        if sack_total_weight + item.weight <= capacity:
            sack.append(item)
            sack_total_weight += item.weight
        else:
            banned.append(i)

        i += 1

    return sack

# Max profit heuristic, spam sack with item with most profit
def MaxP(items, capacity):
    sorted_items = sorted(items, key=lambda item: (-item.profit, item.weight))
    sack = []
    sack_total_weight = 0
    for item in sorted_items:
        while sack_total_weight + item.weight <= capacity:
            sack_total_weight += item.weight
            sack.append(item)

    return sack

# Min weight heuristic, spam sack with item with least weight ratio
def MinW(items, capacity):
    sorted_items = sorted(items, key=lambda item: (item.weight, -item.profit))
    sack = []
    sack_total_weight = 0
    for item in sorted_items:
        while sack_total_weight + item.weight <= capacity:
            sack_total_weight += item.weight
            sack.append(item)
        # podemos salir de lopp porque sabemos que no existe otro
        # item con un peso menos que el primero
        break

    return sack

def MaxPW(items, capacity):
    sorted_items = sorted(items, key=lambda item: item.profit/item.weight, reverse=True)
    sack = []
    sack_total_weight = 0
    for item in sorted_items:
        while sack_total_weight + item.weight <= capacity:
            sack_total_weight += item.weight
            sack.append(item)

    return sack
