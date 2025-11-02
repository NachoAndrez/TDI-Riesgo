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
        
    def _get_profile_series(self, column):
        """
        Devuelve la serie de viento (como floats) para el nodo indicado.
        """
        valores = reader.get_column(self.archivo, self.hoja_eo, f"_{column}")
        return [float(v) for v in valores]

    def get_perfil_eolico(self, column, keys=None):  # Verificar
        serie = self._get_profile_series(column)

        if not serie:
            raise ValueError(f"No se encontró perfil eólico para el nodo '{column}'.")

        if keys is None:
            return serie

        try:
            tiempo = int(keys)
        except (TypeError, ValueError):
            raise ValueError(f"Índice de tiempo inválido '{keys}' para el perfil eólico del nodo '{column}'.")

        tiempos = reader.get_column(self.archivo, self.hoja_eo, 'time')
        mapa_tiempos = {int(t): idx for idx, t in enumerate(tiempos)}

        if tiempo not in mapa_tiempos:
            raise ValueError(f"El tiempo {keys} no existe en el perfil eólico del nodo '{column}'.")

        idx = mapa_tiempos[tiempo]

        if idx >= len(serie):
            raise ValueError(
                f"El tiempo {keys} está fuera del rango del perfil eólico del nodo '{column}'."
            )

        return serie[idx]

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