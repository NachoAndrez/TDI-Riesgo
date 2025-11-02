# --- Importar módulo de lectura ---
import in_out.reader as reader
import pandas as pd
import os

# --- Importar módulo de series de tiempo ---
import time_series

# --- Importar módulos Generación y Demanda ---
import gen.Grid as grid
import gen.load as load
import gen.others as others
import gen.pv_gen as pv_gen
import gen.reserve as reserve
import gen.thermal_gen as thermal_gen
import gen.w_gen as w_gen

#--- Importar módulos de optimización ---
from opt_model.manager import OptModel
from opt_model.functions import OptVars, OptSets, OptConstraints, OptObjective, OutputManager
import pyomo.environ as pyo


# --- Crear instancias de los componentes ---
Demanda  = load.ActiveLoad()
PV       = pv_gen.PhotovoltaicGen()
red    = grid.Grid_grid()
tiempo     = time_series.Time()
thermal  = thermal_gen.ThermalGen()
otros  = others.Others()
reserva  = reserve.RerserveRequirementLoad()
Wind    = w_gen.WindGen()

crear_outputmanager = OutputManager(Demanda, PV, red, tiempo, thermal, otros, reserva, Wind)

# --- Directorio para guardar resultados ---
path = "logs/"
os.makedirs(path, exist_ok=True)

def print_to_csv(df, file_name):
    df.to_csv(os.path.join(path, file_name), index=True)

# --- Proceso principal ---
try:
    # Crear y resolver el modelo
    opt = OptModel(Demanda, PV, red, tiempo, thermal, otros, reserva, Wind)
    model = opt.build_model()
    opt.solve_model(0.5/100, solvername='gurobi', log_folder=path, model=model)


    print_to_csv(crear_outputmanager.get_var(model.P_th,      ['THgen', 'interval']), "P_th.csv")
    print_to_csv(crear_outputmanager.get_var(model.P_ls,      ['nodes', 'interval']), "P_ls.csv")
    print_to_csv(crear_outputmanager.get_var(model.P_w,       ['Wgen', 'interval']), "P_w.csv")
    print_to_csv(crear_outputmanager.get_var(model.P_pv,      ['PVgen', 'interval']), "P_pv.csv")
    print_to_csv(crear_outputmanager.get_var(model.f,         ['lines', 'interval']), "flow.csv")


    reader.eliminar_parquet()

except Exception as e:
    print("Error:", e)
    reader.eliminar_parquet()