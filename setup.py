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
red      = grid.Grid_grid()
tiempo   = time_series.Time()
thermal  = thermal_gen.ThermalGen()
otros    = others.Others()
reserva  = reserve.RerserveRequirementLoad()
Wind     = w_gen.WindGen()

# ⚠️ Orden correcto según OptRules.__init__(PV, red, tiempo, thermal, otros, Demanda, reserva, Wind)
crear_outputmanager = OutputManager(PV, red, tiempo, thermal, otros, Demanda, reserva, Wind)

# --- Directorio para guardar resultados ---
path = "logs/"
os.makedirs(path, exist_ok=True)

def print_to_csv(df, file_name):
    df.to_csv(os.path.join(path, file_name), index=True)

def fix_binaries_and_resolve_lp(model, solver="gurobi"):
    """
    Fija binarios relevantes (x_th) y resuelve el despacho como LP para obtener duales.
    Evita fijar u_th/d_th si no participan en restricciones (pueden quedar sin valor).
    """
    # Sufijo de duales
    if not hasattr(model, "dual"):
        model.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)

    # Fijar SOLO x_th (robusto si algún valor viene None)
    if hasattr(model, "x_th"):
        for idx in model.x_th:
            val = pyo.value(model.x_th[idx], exception=False)
            val = 0 if (val is None) else int(round(val))
            model.x_th[idx].fix(val)

    # Resolver LP (ya sin discreción efectiva)
    pyo.SolverFactory(solver).solve(model, tee=False)
    return model

# --- Proceso principal ---
try:
    # Crear y resolver el modelo (UC MILP)
    opt = OptModel(Demanda, PV, red, tiempo, thermal, otros, reserva, Wind)
    model = opt.build_model()
    opt.solve_model(0.5/100, solvername='gurobi', log_folder=path, model=model)

    # Re-optimizar como LP para obtener duales (LMPs)
    model = fix_binaries_and_resolve_lp(model, solver="gurobi")

    # Guardar variables principales
    print_to_csv(crear_outputmanager.get_var(model.P_th, ['THgen', 'interval']), "P_th.csv")
    print_to_csv(crear_outputmanager.get_var(model.P_ls, ['nodes', 'interval']), "P_ls.csv")
    print_to_csv(crear_outputmanager.get_var(model.P_w,  ['Wgen', 'interval']), "P_w.csv")
    print_to_csv(crear_outputmanager.get_var(model.P_pv, ['PVgen', 'interval']), "P_pv.csv")
    print_to_csv(crear_outputmanager.get_var(model.f,    ['lines', 'interval']), "flow.csv")

    # 🚀 Guardar LMPs ($/MWh). Requiere que OutputManager tenga get_LMPs(...)
    lmp_df = crear_outputmanager.get_LMPs(model, divide_by_dt=True)  # divide por dt para $/MWh
    print_to_csv(lmp_df, "LMPs.csv")

    # Limpieza opcional
    reader.eliminar_parquet()

except Exception as e:
    print("Error:", e)
    reader.eliminar_parquet()
