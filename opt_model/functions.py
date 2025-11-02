# functions_pyomo.py
#from typing import Any, Dict, Iterable, List, Tuple, Optional
import pyomo.environ as pyo
import time
import pandas as pd

class OptRules(object):
    """
    Clase base para definir conjuntos, variables, restricciones y función objetivo.
    """
    def __init__(self, PV, red, tiempo, thermal, otros, Demanda, reserva, Wind):
        self.pv = PV
        self.grid = red
        self.time = tiempo
        self.thermal = thermal
        self.reserva = reserva
        self.Wind = Wind
        self.others = otros
        self.load = Demanda
        self.others = otros

# =========================
#      CONJUNTOS
# =========================
class OptSets(OptRules):
    def build_sets(self, model: pyo.ConcreteModel):
        """
        Define los conjuntos y mapas de red en el modelo Pyomo.
        """
        # --- Sets base ---
        T_list = list(self.time.get_time_periods())
        B_list = list(self.grid.get_nodes())
        L_list = list(self.grid.get_line_ids())
        G_list = list(self.thermal.get_names())
        PV_list = list(self.pv.get_names())
        W_list = list(self.Wind.get_names())


        model.T = pyo.Set(initialize=T_list, ordered=True)
        model.B = pyo.Set(initialize=B_list, ordered=False)
        model.L = pyo.Set(initialize=L_list, ordered=False)
        model.G = pyo.Set(initialize=G_list, ordered=False)
        model.PVgen = pyo.Set(initialize=PV_list, ordered=False)
        model.Wgen = pyo.Set(initialize=W_list, ordered=False)


        # Mapas de línea -> nodos (parámetros)
        i_map = self.grid.get_line_origin_nodes(L_list)  # dict {l: bus_i}
        j_map = self.grid.get_line_dest_nodes(L_list)    # dict {l: bus_j}
        model.i = pyo.Param(model.L, initialize=i_map, within=pyo.Any, mutable=False)
        model.j = pyo.Param(model.L, initialize=j_map, within=pyo.Any, mutable=False)

        # Conjuntos de líneas que entran/salen de cada bus (diccionarios auxiliares)
        model._Lin = self.grid.get_lines_in_by_bus(L_list)   # dict {b: list(l)}
        model._Lout = self.grid.get_lines_out_by_bus(L_list) # dict {b: list(l)}


# =========================
#      VARIABLES
# =========================
class OptVars(OptRules):
    def build_all_variables(self, model: pyo.ConcreteModel):
        # Generación diésel por bus [MW]
        model.P_th = pyo.Var(model.G, model.T, within=pyo.NonNegativeReals)
        model.x_th = pyo.Var(model.G, model.T, within=pyo.Binary)
        model.u_th = pyo.Var(model.G, model.T, within=pyo.Binary)
        model.d_th = pyo.Var(model.G, model.T, within=pyo.Binary)

        # Generación PV [MW]
        model.P_pv = pyo.Var(model.PVgen, model.T, within=pyo.NonNegativeReals)

        # Generación eólica [MW]
        model.P_w = pyo.Var(model.Wgen, model.T, within=pyo.NonNegativeReals)

        # Ángulo de fase DC [rad]
        model.theta = pyo.Var(model.B, model.T, within=pyo.Reals)

        # Flujo por línea [MW]
        model.f = pyo.Var(model.L, model.T, within=pyo.Reals)

        # Load shedding [MW]
        model.P_ls = pyo.Var(model.B, model.T, within=pyo.NonNegativeReals)




# =========================
#    RESTRICCIONES
# =========================
class OptConstraints(OptRules):
    def build_all_constraints(self, model: pyo.ConcreteModel):
        # Paso de tiempo (horas)
        dt = self.time.get_timestep()

        # ----------- 1) Límites de generación convencional por nodo -----------
        
        def max_limits_gen(m, g, t):
                return m.P_th[g, t] <= self.thermal.get_max_power(g) * m.x_th[g, t]

        
        def min_limits_gen(m, g, t):
            return m.P_th[g, t] >= self.thermal.get_min_power(g) * m.x_th[g, t]
        
        # ----------- 2) Límites de generación PV por nodo -----------
        def pv_generation_limit_rule(m, pv, t):

            nodo = self.pv.get_nodes(pv)
            p_max_pv = self.pv.get_pmax(pv) * self.pv.get_perfil_solar(nodo,t)  # MW
            return m.P_pv[pv, t] <= p_max_pv
        
        # ----------- 3) Límites de generación eólica por nodo -----------
        def w_generation_limit_rule(m, w, t):
            nodo = self.Wind.get_nodes(w)
            p_max_w = self.Wind.get_pmax(w) * self.Wind.get_perfil_eolico(nodo,t)  # MW
            return m.P_w[w, t] <= p_max_w
 

        # ----------- 4) Balance nodal de potencia activa (SIN red) -----------
        def nodal_balance_rule(m, b, t):

            f_in = sum(m.f[l, t] for l in model._Lin.get(b, []))
            f_out = sum(m.f[l, t] for l in model._Lout.get(b, []))
            lhs = (
                      sum(m.P_th[g, t] for g in self.thermal.get_name_per_node(b)) 
                    + sum(m.P_pv[pv, t] for pv in self.pv.get_name_per_node(b))  
                    + sum(m.P_w[w, t] for w in self.Wind.get_name_per_node(b)) 
                    + f_in + m.P_ls[b, t]
                    )
            rhs = (self.load.consume_per_node(b, t) + f_out)
            return lhs == rhs

        # ----------- 5) Flujo DC por línea -----------
        x_map = {l: self.grid.get_reactance(l) for l in model.L}
        model.x = pyo.Param(model.L, initialize=x_map, within=pyo.PositiveReals, mutable=False)

        def dc_flow_rule(m, l, t):
            return m.f[l, t] == (1.0 / m.x[l]) * (m.theta[m.i[l], t] - m.theta[m.j[l], t])

        # ----------- 6) Límite térmico por línea -----------
        fmax_map = {l: self.grid.get_max_flow(l) for l in model.L}
        model.Fmax = pyo.Param(model.L, initialize=fmax_map, within=pyo.NonNegativeReals, mutable=False)

        def flow_limit_rule(m, l, t):
            return pyo.inequality(-m.Fmax[l], m.f[l, t], m.Fmax[l])

        # ----------- 7) Referencia de ángulo (slack) -----------
        first_bus = next(iter(model.B.data())) if len(model.B) > 0 else None

        def slack_ref_rule(m, t):
            if first_bus is None:
                return pyo.Constraint.Skip
            return m.theta[first_bus, t] == 0.0

        # Añadir todas las restricciones al modelo
        model.Max_gen         = pyo.Constraint(model.G, model.T, rule=max_limits_gen)
        #model.Min_gen         = pyo.Constraint(model.G, model.T, rule=min_limits_gen)
        model.PV_gen_limit    = pyo.Constraint(model.PVgen, model.T, rule=pv_generation_limit_rule)
        model.W_gen_limit     = pyo.Constraint(model.Wgen, model.T, rule=w_generation_limit_rule)
        model.NodalBalance    = pyo.Constraint(model.B, model.T, rule=nodal_balance_rule)
        model.DCFlow          = pyo.Constraint(model.L, model.T, rule=dc_flow_rule)
        model.FlowLimit       = pyo.Constraint(model.L, model.T, rule=flow_limit_rule)
        model.SlackRef        = pyo.Constraint(model.T, rule=slack_ref_rule)

        print('All constraints have been successfully created.')


# =========================
#       OBJETIVO
# =========================
class OptObjective(OptRules):
    def build_objective(self, model: pyo.ConcreteModel):
        """
        Minimiza costo.
        """
        dt = self.time.get_timestep()
        Load_sheeding_cost = 1000.0  # Costo por MW de load shedding

        expr = sum(
            self.thermal.get_variable_cost(g) * model.P_th[g, t] * dt
            for g in model.G
            for t in model.T
        )

        
        expr += sum(
            Load_sheeding_cost * model.P_ls[b, t] * dt
            for b in model.B
            for t in model.T
        )
        return expr
# ==========================
class OutputManager(OptRules):
    def get_var(self, variable, index_names):
        var_values = pd.DataFrame.from_dict(
            variable.extract_values(),
            orient='index',
            columns=[str(variable)]
        )
        var_values.index = pd.MultiIndex.from_tuples(var_values.index)
        var_values.index.names = index_names
        return var_values

    def get_dual_prices(self, constraint, index_names, model, divide_by_dt=True, colname="dual"):
        if not hasattr(model, "dual"):
            raise ValueError("Falta model.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT).")
        dt = getattr(self.time, "get_timestep", lambda: 1.0)()
        data = {}
        for idx in constraint:
            con_comp = constraint[idx]
            if (con_comp is None) or (not con_comp.active):
                continue
            mu = model.dual.get(con_comp, None)
            if mu is None:
                continue
            val = mu / dt if (divide_by_dt and dt != 0) else mu
            data[idx] = val
        df = pd.DataFrame.from_dict(data, orient='index', columns=[colname])
        if not df.empty:
            if isinstance(next(iter(data.keys())), tuple):
                df.index = pd.MultiIndex.from_tuples(df.index)
                if len(index_names) == df.index.nlevels:
                    df.index.names = index_names
                else:
                    df.index.names = (index_names + [None]*df.index.nlevels)[:df.index.nlevels]
            else:
                df.index.name = index_names[0] if index_names else None
            df.sort_index(inplace=True)
        return df

    def get_LMPs(self, model, divide_by_dt=True):
        return self.get_dual_prices(
            constraint=model.NodalBalance,
            index_names=["bus", "t"],
            model=model,
            divide_by_dt=divide_by_dt,
            colname="LMP"
        )