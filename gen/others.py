import in_out.reader as reader

class Others:
    def __init__(self):
        self.archivo = 'data/datos.xlsx'
        self.hoja = 'others'

    def get(self, column, keys= None):
        if keys:
            i = reader.get_column(self.archivo, self.hoja, 'name').index(keys)
            return reader.get_column(self.archivo, self.hoja, column)[i]
        else:
            return reader.get_column(self.archivo, self.hoja, column)
        
    def get_frequency_nom(self):
        return float(self.get('f_nom')[0])
    
    def get_slack_node(self):
        return float(self.get('slack_node')[0])
    
    def get_frequency_min(self):
        return float(self.get('f_min')[0])
    
    def get_K_load(self):
        return float(self.get('K_load')[0])
    
    def get_factor_conversion(self):
        return float(self.get('factor_conversion')[0])