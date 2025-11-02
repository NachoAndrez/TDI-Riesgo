import time
import pandas as pd
import pyomo.environ as pyo
import os
import sys
# Importa bloques individuales desde functions.py
from opt_model.functions import OptSets, OptVars, OptConstraints, OptObjective, OutputManager

class OptModel:
    def __init__(self, Demanda, PV, red, tiempo, thermal, otros, reserva, Wind):
        self.pv = PV
        self.grid = red
        self.time = tiempo
        self.thermal = thermal
        self.reserva = reserva
        self.Wind = Wind
        self.others = otros
        self.load = Demanda
        self.constraint_rules = OptConstraints(self.pv, self.grid, self.time, self.thermal, self.others, self.load, self.reserva, self.Wind)
        self.objective_rules =    OptObjective(self.pv, self.grid, self.time, self.thermal, self.others, self.load, self.reserva, self.Wind)
        self.bound_rules =             OptVars(self.pv, self.grid, self.time, self.thermal, self.others, self.load, self.reserva, self.Wind)
        self.set_builder =             OptSets(self.pv, self.grid, self.time, self.thermal, self.others, self.load, self.reserva, self.Wind)
        self.output_manager =    OutputManager(self.pv, self.grid, self.time, self.thermal, self.others, self.load, self.reserva, self.Wind)
        #self.model = self.build_model()



    def build_model(self):

        model = pyo.ConcreteModel()
        #Completar
        self.set_builder.build_sets(model)
        self.bound_rules.build_all_variables(model)
        self.constraint_rules.build_all_constraints(model)
        self.objective_rules = OptObjective(self.pv, self.grid, self.time, self.thermal, self.others, self.load, self.reserva, self.Wind)
        model.op_cost=pyo.Expression(rule=self.objective_rules.build_objective(model))
        model.obj = pyo.Objective(rule=model.op_cost)

        # write model #
        filename = 'model.lp'
        model.write(filename, io_options={'symbolic_solver_labels': True})
        return model


    def solve_model(self, gap, solvername, log_folder=".", model=None):

        log_file = f"{log_folder}/log.txt"
        if os.path.exists(log_file):
            os.remove(log_file)

        if solvername == 'glpk':
            solverpath_folder = 'C:\\glpk\\w64'
            sys.path.append(solverpath_folder)
            opt = pyo.SolverFactory('glpk',tee=True)
            opt.options['mipgap'] = gap
            opt.options['log']="log.out"
            opt.options['cuts']=""
            opt.options['fpump']=""

        elif solvername == 'gurobi':

            opt = pyo.SolverFactory('gurobi', solver_io="python")
            #opt.options['outlev'] = 1
            opt.options['Threads'] = 4
            opt.options['LogToConsole'] = 1
            opt.options['OutputFlag'] = 1
            opt.options['MIPGap'] =gap
            opt.options['LogFile'] = log_file

        print("Solving opt model")
        time_start = time.time()
        result=opt.solve(model)
        self.time_total = time.time() - time_start
        self.solution_status=result.solver.termination_condition
        self.opt_cost_result=-1

        if (self.solution_status=='optimal'):
            self.opt_cost_result = pyo.value(model.op_cost)
            print("Solution time [sec]:", self.time_total)
            print("Operation Cost:", self.opt_cost_result)
        return 0