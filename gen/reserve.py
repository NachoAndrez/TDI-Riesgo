import in_out.reader as reader

class RerserveRequirementLoad:
    def __init__(self):
        self.archivo = 'data/datos.xlsx'
        self.hoja = 'reserva'

    def get(self, column, keys= None):
        if keys:
            i = reader.get_column(self.archivo, self.hoja, 'periods').index(keys)
            return reader.get_column(self.archivo, self.hoja, column)[i]
        else:
            return reader.get_column(self.archivo, self.hoja, column)


    def requirement_per_node(self, node, time):
        return float(self.get(f'_{node}', str(time)))
    