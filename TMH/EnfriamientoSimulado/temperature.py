class Temperature:
    temperature: float
    cooling_rate: float

    def __init__(self, initial_temperature, cooling_rate):
        self.temperature = initial_temperature
        self.cooling_rate = cooling_rate

    def linear(self):
        self.temperature -= self.cooling_rate
        return self.temperature

    def proportional(self):
        self.temperature = self.cooling_rate * self.temperature
        return self.temperature

    def relative(self):
        # T = T0 / (1 + cT)
        # 0<cT<1 valor pequeño
        self.temperature = self.temperature / (1 + self.cooling_rate * self.temperature)
        return self.temperature

    def staged(self, i, stages):
        if i % stages == 0:
            return self.linear()

    def reduce(self, type, *args, **kwargs):
        if type == 1:
            return self.linear()
        elif type == 2:
            return self.proportional()
        elif type == 3:
            return self.relative()
        elif type == 4:
            return self.staged(*args, **kwargs)
        else:
            raise Exception("Invalid temperature reduction type")
