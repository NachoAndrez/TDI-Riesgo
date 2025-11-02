import in_out.reader as reader

class ThermalGen:
    def __init__(self):
        self.archivo = 'data/datos.xlsx'
        self.hoja = 'gen_th'

    def get(self, column, keys= None):
        if keys:
            i = reader.get_column(self.archivo, self.hoja, 'name').index(keys)
            return reader.get_column(self.archivo, self.hoja, column)[i]
        else:
            return reader.get_column(self.archivo, self.hoja, column)

    def get_names(self, keys= None):
        return self.get('name', keys)
    
    def get_max_power(self, keys= None):
        return float(self.get('P_max', keys))
    
    def get_min_power(self, keys= None):
        return float(self.get('P_min', keys))
    
    def get_nodes(self, keys= None):
        nodes = list(self.get('nodo', keys))
        node_list = [x  for x in nodes if x!= '0' ]

        return node_list
    
    def get_reserve_max(self, keys= None):
        return float(self.get('reserva_max', keys))
    
    def get_startup_cost(self, keys= None):
        return float(self.get('c_on', keys))
    
    def get_shutdown_cost(self, keys= None):
        return float(self.get('c_off', keys))
    
    def get_variable_cost(self, keys= None):
        return float(self.get('c_var', keys))
    
    def get_giro_cost(self, keys= None):
        return float(self.get('c_giro', keys))
    
    def get_min_on_time(self, keys= None):
        return float(self.get('t_on', keys))
    
    def get_min_off_time(self, keys= None):
        return float(self.get('t_off', keys))
    
    def get_ramp_up(self, keys= None):
        return float(self.get('r_up', keys))
    
    def get_ramp_down(self, keys= None):
        return float(self.get('r_down', keys))
    
    def get_droop(self, keys= None):
        return float(self.get('Droop', keys))
    
    def get_K_tourbine(self, keys= None):
        return float(self.get('K_m', keys))
    
    def get_inertia_constant(self, keys= None):
        return float(self.get('J', keys))
    
    def get_primary_response_constant(self, keys= None):
        return float(self.get('coef_resp_primaria', keys))
    
    def get_name_per_node(self, node):
        names = []
        for name in self.get_names():
            if self.get('nodo', name) == node:
                names.append(name)
        return names