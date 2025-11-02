import in_out.reader as reader

class Time:
    def __init__(self):
        self.archivo = 'data/datos.xlsx'
        self.hoja = 'dem'

    def get(self, column, keys= None):
        if keys:
            i = reader.get_column(self.archivo, self.hoja, 'periods').index(keys)
            return reader.get_column(self.archivo, self.hoja, column)[i]
        else:
            return reader.get_column(self.archivo, self.hoja, column)

    def get_time_periods(self, keys= None):
        times = []
        for t in self.get('periods', keys):
            times.append(int(t))
        return times

    def get_timestep(self, keys= None):
        return 1
