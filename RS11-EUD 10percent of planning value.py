### Scale EUDs

# This script scales all EUD objectives to be 10% less than the planning dose of the structure

from connect import *
case = get_current("Case")
plan = get_current("Plan")
beam_set = get_current("BeamSet")
structure_set = plan.GetTotalDoseStructureSet()
patient = get_current("Patient")

# Message Box creation
import ctypes

def Mbox(title, text, style):
   return ctypes.windll.user32.MessageBoxW(0, text, title, style)

# Shortcuts
po = plan.PlanOptimizations[beam_set.Number-1]
clinigoals = po.TreatmentCourseSource.EvaluationSetup.EvaluationFunctions
planobjectives = po.Objective.ConstituentFunctions

# changes EUD Objectives to be 10% less than Average Dose....if function values are up to date
for i in planobjectives:
   roiname = i.ForRegionOfInterest.Name
   dosefunction = i.DoseFunctionParameters
   functvalue = i.FunctionValue
   if hasattr(dosefunction, 'FunctionType') and dosefunction.FunctionType == "MaxEud":
      if hasattr(functvalue,'PlanningValue'):
         planningvalue = functvalue.PlanningValue
         dosefunction.DoseLevel = round(planningvalue * .9 , 2)
      else:
         Mbox("Cannot complete request", "Compute " + roiname + " Function Value First", 0)