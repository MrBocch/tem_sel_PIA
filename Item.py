class Item:
    def __init__(self, weight, profit):
      self.weight = weight
      self.profit = profit

    def __str__(self):
        return f"Beneficio: {self.profit} - Peso: {self.weight}"

    def __repr__(self):
        return f"P: {self.profit}, W: {self.weight}\n"

    def to_binary(self):
        # convertir item into binario
        # tamano minimo de que? todos deben de ser de mismo tamano
        # como max peso y max profit por objeto es _x_, 2**x
        bin_size = '04b'
        weight_bits = format(self.weight, bin_size)
        profit_bits = format(self.profit, bin_size)
        return f"{weight_bits}{profit_bits}"
