import in_out.reader as reader
import math
class Grid_grid:
    def __init__(self):
        self.archivo = 'data/datos.xlsx'
        self.hoja = 'red'
        self.hoja_nodos = 'nodos'

    def get(self, column, keys= None):
        if keys:
            i = reader.get_column(self.archivo, self.hoja, 'id').index(keys)
            return reader.get_column(self.archivo, self.hoja, column)[i]
        else:
            reader.get_column(self.archivo, self.hoja, column)
            return reader.get_column(self.archivo, self.hoja, column)
        
    def getN(self, column, keys= None):
        if keys:
            i = reader.get_column(self.archivo, self.hoja_nodos, 'id').index(keys)
            return reader.get_column(self.archivo, self.hoja_nodos, column)[i]
        else:
            reader.get_column(self.archivo, self.hoja_nodos, column)
            return reader.get_column(self.archivo, self.hoja_nodos, column)

    def get_nodes(self, keys= None):
        return self.getN('nodes', keys)
    
    def get_conect_in(self, keys= None):
        return self.get('conect_in', keys)
    
    def get_conect_out(self, keys= None):
        return self.get('conect_out', keys)
    
    def get_max_flow(self, keys= None):
        return float(self.get('max_flow', keys))
    
    def get_line_ids(self, keys= None):
        return self.get('id', keys)
    
    def get_lines_in_by_bus(self, keys_list= None):
        lines_in = {}
        for i in keys_list:
            node = self.get_conect_out(i) 
            if node not in lines_in:
                lines_in[node] = []
            lines_in[node].append(i)
        return lines_in

    def get_lines_out_by_bus(self, keys_list= None):
        lines_in = {}
        for i in keys_list:
            node = self.get_conect_in(i) 
            if node not in lines_in:
                lines_in[node] = []
            lines_in[node].append(i)
        return lines_in


    def get_line_origin_nodes(self, keys_list=None):
        lines_in = {}

        for i in keys_list:
            try:
                node = self.get_conect_in(i)  # Esta función debe retornar el nodo origen de la línea i
                lines_in[i] = node
            except Exception as e:
                print(f"Error al obtener nodo de origen para la línea '{i}': {e}")
        return lines_in
    
    def get_line_dest_nodes(self, keys_list=None):
        lines_out = {}

        for i in keys_list:
            try:
                node = self.get_conect_out(i)  # Esta función debe retornar el nodo origen de la línea i
                lines_out[i] = node
            except Exception as e:
                print(f"Error al obtener nodo de origen para la línea '{i}': {e}")
        return lines_out
    
    def get_reactance(self, keys= None):
        return float(self.get('reactance', keys))
    