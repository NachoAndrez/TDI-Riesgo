import in_out.reader as reader

class WindGen:
    def __init__(self):
        self.archivo = 'data/datos.xlsx'
        self.hoja = 'gen_w'
        self.hoja_eo = 'perfil_eolico'

    def get(self, column, keys= None):
        if keys:
            i = reader.get_column(self.archivo, self.hoja, 'name').index(keys)
            return reader.get_column(self.archivo, self.hoja, column)[i]
        else:
            return reader.get_column(self.archivo, self.hoja, column)
        
    def get_perfil_eolico(self, column, keys= None):  # Verificar
        if keys:
            return float(reader.get_column(self.archivo, self.hoja_eo, f"_{column}")[keys-1])
        else:
            return reader.get_column(self.archivo, self.hoja_eo, f"_{column}")

    def get_names(self, keys= None):
        return self.get('name', keys)    

    def get_nodes(self, keys= None):
        return self.get('nodo', keys)

    def get_pmax(self, keys= None):
        return float(self.get('P_max', keys))
    
    def get_pmin(self, keys= None):
        return float(self.get('P_min', keys))
    
    def get_fp(self, keys= None):
        return float(self.get('fp', keys))
    
    def get_cvar(self, keys= None):
        return float(self.get('c_var', keys))
    
    def get_name_per_node(self, node):
        names = []
        for name in self.get_names():
            if self.get('nodo', name) == node:
                names.append(name)
        return names