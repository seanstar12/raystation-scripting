### Copy objectives to new beamset
### jch 12/10/20
# This script will copy objectives from one beamset to another

from connect import *
case = get_current("Case")
plan = get_current("Plan")


beam_set = get_current("BeamSet")
structure_set = plan.GetTotalDoseStructureSet()
patient = get_current("Patient")

bscurrent = beam_set.DicomPlanLabel
planoptions = []
bsoptions = []
planbsoptions = []
for i in case.TreatmentPlans:
   planname = i.Name
   for i in case.TreatmentPlans[planname].PlanOptimizations:
      poname = i
      if hasattr(i.Objective, "ConstituentFunctions"):
         for i in poname.OptimizedBeamSets:
            bsname = i.DicomPlanLabel
            planbsname = "Plan: " + planname + "   BS: " + bsname
            planbsoptions.append(planbsname)
            planoptions.append(planname)
            bsoptions.append(bsname)

import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
from System.Windows.Forms import Application, Form, Label, ComboBox, Button, TextBox
from System.Drawing import Point, Size
class FactorForm(Form):
   def __init__(self, plan):
      self.Size = Size(500, 150)
      self.Text = 'Copy Objectives'
      label = Label()
      label.Text = 'Copy Objectives from Plan:'
      label.Location = Point(50, 25)
      label.AutoSize = True
      self.Controls.Add(label)
      self.combobox = ComboBox()
      self.combobox.DataSource = planbsoptions
      self.combobox.Location = Point(200, 25)
      self.combobox.AutoSize = True
      self.combobox.DropDownWidth = 225
      self.Controls.Add(self.combobox)
      
      button = Button()
      button.Text = 'OK'
      button.AutoSize = True
      button.Location = Point(200, 60)
      button.Click += self.ok_button_clicked
      self.Controls.Add(button)
   def ok_button_clicked(self, sender, event):
      self.option = self.combobox.SelectedValue
      self.Close()
form = FactorForm(plan)
Application.Run(form)
option = form.option

selectionindex = planbsoptions.index(option)
copyplanname = case.TreatmentPlans[planoptions[selectionindex]].Name
bsnumber = case.TreatmentPlans[copyplanname].BeamSets[bsoptions[selectionindex]].Number
bscurrentnumber = beam_set.Number
count = -1

### Does not handle RBE Dose
### Do I want to add co-optimization
### Do I want to add Target EUD and Uniformity Constraint
if hasattr(case.TreatmentPlans[copyplanname].PlanOptimizations[bsnumber-1].Objective, "ConstituentFunctions"):
   for i in case.TreatmentPlans[copyplanname].PlanOptimizations[bsnumber-1].Objective.ConstituentFunctions:
      optiroi = i.ForRegionOfInterest.Name
      if hasattr(i.DoseFunctionParameters, "FunctionType"):
         optitype = i.DoseFunctionParameters.FunctionType
      elif hasattr(i.DoseFunctionParameters, "LowDoseDistance"):
         optitype = "DoseFallOff"
      optiweight = i.DoseFunctionParameters.Weight
      optiallbeams = i.UseBeamSpecificForAllBeams
      optibeam = None
      optirobust = i.UseRobustness
      optibeamset = None
      opticonstraint = False
      if hasattr(i.OfDoseDistribution, "ForBeam"):
         optibeam = i.OfDoseDistribution.ForBeam.Name
      if optiallbeams or hasattr(i.OfDoseDistribution, "ForBeam"):
         optibeamset = bscurrent
      if hasattr(i.Constraint, "UpperBound"):
         opticonstraint = True
      count += 1
      print(optiroi)
      print(count)
      if optitype == "DoseFallOff":
         optihidl = i.DoseFunctionParameters.HighDoseLevel
         optilodl = i.DoseFunctionParameters.LowDoseLevel
         optidist = i.DoseFunctionParameters.LowDoseDistance
         optiadapt = i.DoseFunctionParameters.AdaptToTargetDoseLevels
         with CompositeAction('Add Optimization Function'):
            retval_0 = plan.PlanOptimizations[bscurrentnumber-1].AddOptimizationFunction(FunctionType=optitype, RoiName=optiroi, IsConstraint=opticonstraint, RestrictAllBeamsIndividually=optiallbeams,
                                                                         RestrictToBeam=optibeam, IsRobust=optirobust, RestrictToBeamSet=optibeamset, UseRbeDose=False)
            plan.PlanOptimizations[bscurrentnumber-1].Objective.ConstituentFunctions[count].DoseFunctionParameters.HighDoseLevel = optihidl
            plan.PlanOptimizations[bscurrentnumber-1].Objective.ConstituentFunctions[count].DoseFunctionParameters.LowDoseLevel = optilodl
            plan.PlanOptimizations[bscurrentnumber-1].Objective.ConstituentFunctions[count].DoseFunctionParameters.LowDoseDistance = optidist
            plan.PlanOptimizations[bscurrentnumber-1].Objective.ConstituentFunctions[count].DoseFunctionParameters.Weight = optiweight
      elif optitype in ["MinDose", "MaxDose", "MinDvh", "MaxDvh", "UniformDose"]:
         optidl = i.DoseFunctionParameters.DoseLevel
         optipervol = i.DoseFunctionParameters.PercentVolume
         with CompositeAction('Add Optimization Function'):
            retval_1 = plan.PlanOptimizations[bscurrentnumber-1].AddOptimizationFunction(FunctionType=optitype, RoiName=optiroi, IsConstraint=opticonstraint, RestrictAllBeamsIndividually=optiallbeams,
                                                                         RestrictToBeam=optibeam, IsRobust=optirobust, RestrictToBeamSet=optibeamset, UseRbeDose=False)
            plan.PlanOptimizations[bscurrentnumber-1].Objective.ConstituentFunctions[count].DoseFunctionParameters.DoseLevel = optidl
            plan.PlanOptimizations[bscurrentnumber-1].Objective.ConstituentFunctions[count].DoseFunctionParameters.PercentVolume = optipervol
            plan.PlanOptimizations[bscurrentnumber-1].Objective.ConstituentFunctions[count].DoseFunctionParameters.Weight = optiweight
      elif optitype == "MinEud" or optitype == "MaxEud":
         optidl = i.DoseFunctionParameters.DoseLevel
         optialpha = i.DoseFunctionParameters.EudParameterA
         with CompositeAction('Add Optimization Function'):
            retval_3 = plan.PlanOptimizations[bscurrentnumber-1].AddOptimizationFunction(FunctionType=optitype, RoiName=optiroi, IsConstraint=opticonstraint, RestrictAllBeamsIndividually=optiallbeams,
                                                                         RestrictToBeam=optibeam, IsRobust=optirobust, RestrictToBeamSet=optibeamset, UseRbeDose=False)
            plan.PlanOptimizations[bscurrentnumber-1].Objective.ConstituentFunctions[count].DoseFunctionParameters.DoseLevel = optidl
            plan.PlanOptimizations[bscurrentnumber-1].Objective.ConstituentFunctions[count].DoseFunctionParameters.EudParameterA = optialpha
            plan.PlanOptimizations[bscurrentnumber-1].Objective.ConstituentFunctions[count].DoseFunctionParameters.Weight = optiweight
      else:
         print("Cannot use " + optitype + " for " + optiroi)
else:
   print("No Optimization Objectives for " + option)

count = -1

if hasattr(case.TreatmentPlans[copyplanname].PlanOptimizations[bsnumber-1].Constraints, "_0"):
   for i in case.TreatmentPlans[copyplanname].PlanOptimizations[bsnumber-1].Constraints:
      optiroi = i.ForRegionOfInterest.Name
      if hasattr(i.DoseFunctionParameters, "FunctionType"):
         optitype = i.DoseFunctionParameters.FunctionType
      elif hasattr(i.DoseFunctionParameters, "LowDoseDistance"):
         optitype = "DoseFallOff"
      optiweight = i.DoseFunctionParameters.Weight
      optiallbeams = i.UseBeamSpecificForAllBeams
      optibeam = None
      optirobust = i.UseRobustness
      optibeamset = None
      opticonstraint = False
      if hasattr(i.OfDoseDistribution, "ForBeam"):
         optibeam = i.OfDoseDistribution.ForBeam.Name
      if optiallbeams or hasattr(i.OfDoseDistribution, "ForBeam"):
         optibeamset = bscurrent
      if hasattr(i.Constraint, "UpperBound"):
         opticonstraint = True
      count += 1
      print(optiroi)
      print(count)
      if optitype == "DoseFallOff":
         optihidl = i.DoseFunctionParameters.HighDoseLevel
         optilodl = i.DoseFunctionParameters.LowDoseLevel
         optidist = i.DoseFunctionParameters.LowDoseDistance
         optiadapt = i.DoseFunctionParameters.AdaptToTargetDoseLevels
         with CompositeAction('Add Optimization Function'):
            retval_0 = plan.PlanOptimizations[bscurrentnumber-1].AddOptimizationFunction(FunctionType=optitype, RoiName=optiroi, IsConstraint=opticonstraint, RestrictAllBeamsIndividually=optiallbeams,
                                                                         RestrictToBeam=optibeam, IsRobust=optirobust, RestrictToBeamSet=optibeamset, UseRbeDose=False)
            plan.PlanOptimizations[bscurrentnumber-1].Constraints[count].DoseFunctionParameters.HighDoseLevel = optihidl
            plan.PlanOptimizations[bscurrentnumber-1].Constraints[count].DoseFunctionParameters.LowDoseLevel = optilodl
            plan.PlanOptimizations[bscurrentnumber-1].Constraints[count].DoseFunctionParameters.LowDoseDistance = optidist
            plan.PlanOptimizations[bscurrentnumber-1].Constraints[count].DoseFunctionParameters.Weight = optiweight
      elif optitype in ["MinDose", "MaxDose", "MinDvh", "MaxDvh", "UniformDose"]:
         optidl = i.DoseFunctionParameters.DoseLevel
         optipervol = i.DoseFunctionParameters.PercentVolume
         with CompositeAction('Add Optimization Function'):
            retval_1 = plan.PlanOptimizations[bscurrentnumber-1].AddOptimizationFunction(FunctionType=optitype, RoiName=optiroi, IsConstraint=opticonstraint, RestrictAllBeamsIndividually=optiallbeams,
                                                                         RestrictToBeam=optibeam, IsRobust=optirobust, RestrictToBeamSet=optibeamset, UseRbeDose=False)
            plan.PlanOptimizations[bscurrentnumber-1].Constraints[count].DoseFunctionParameters.DoseLevel = optidl
            plan.PlanOptimizations[bscurrentnumber-1].Constraints[count].DoseFunctionParameters.PercentVolume = optipervol
            plan.PlanOptimizations[bscurrentnumber-1].Constraints[count].DoseFunctionParameters.Weight = optiweight
      elif optitype == "MinEud" or optitype == "MaxEud":
         optidl = i.DoseFunctionParameters.DoseLevel
         optialpha = i.DoseFunctionParameters.EudParameterA
         with CompositeAction('Add Optimization Function'):
            retval_3 = plan.PlanOptimizations[bscurrentnumber-1].AddOptimizationFunction(FunctionType=optitype, RoiName=optiroi, IsConstraint=opticonstraint, RestrictAllBeamsIndividually=optiallbeams,
                                                                         RestrictToBeam=optibeam, IsRobust=optirobust, RestrictToBeamSet=optibeamset, UseRbeDose=False)
            plan.PlanOptimizations[bscurrentnumber-1].Constraints[count].DoseFunctionParameters.DoseLevel = optidl
            plan.PlanOptimizations[bscurrentnumber-1].Constraints[count].DoseFunctionParameters.EudParameterA = optialpha
            plan.PlanOptimizations[bscurrentnumber-1].Constraints[count].DoseFunctionParameters.Weight = optiweight
      else:
         print("Cannot use " + optitype + " for " + optiroi)
else:
   print("No Optimization Constraints for " + option)