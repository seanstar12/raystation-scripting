### Scale Objectives & Clinical Goals

# This script scales all optimization objectives, constraints, and clinical goals for the current beam set by a user-defined factor

from connect import *
case = get_current("Case")
plan = get_current("Plan")
beam_set = get_current("BeamSet")
structure_set = plan.GetTotalDoseStructureSet()
patient = get_current("Patient")

import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
from System.Windows.Forms import Application, Form, Label, ComboBox, Button, TextBox
from System.Drawing import Point, Size

class FactorForm(Form):
   def __init__(self, plan):
      self.Size = Size(420, 230)
      self.Text = 'Scale Objectives and Clinical Goals'
      label = Label()
      label.Text = 'Enter a factor to scale the dose'
      label.Location = Point(105, 20)
      label.AutoSize = True
      self.Controls.Add(label)
      self.textbox = TextBox()
      self.textbox.Location = Point(140, 45)
      self.textbox.AutoSize = True
      self.Controls.Add(self.textbox)

      label2 = Label()
      label2.Text = 'Apply factor to:'
      label2.Location = Point(105, 75)
      label2.AutoSize = True
      self.Controls.Add(label2)
      options = ['Objectives', 'Clinical Goals', 'Both']
      self.combobox = ComboBox()
      self.combobox.DataSource = options
      self.combobox.Location = Point(140, 100)
      self.combobox.AutoSize = True
      self.Controls.Add(self.combobox)

      button = Button()
      button.Text = 'OK'
      button.AutoSize = True
      button.Location = Point(150, 145)
      button.Click += self.ok_button_clicked
      self.Controls.Add(button)

   def ok_button_clicked(self, sender, event):
      self.factor = self.textbox.Text
      self.option = self.combobox.SelectedValue
      self.Close()
form = FactorForm(plan)
Application.Run(form)
factor = form.factor
factor = float(factor)
option = form.option
po = plan.PlanOptimizations[beam_set.Number-1]
planobjectives = po.Objective.ConstituentFunctions

if option == 'Objectives' or option =='Both':
   for i in planobjectives:
      if hasattr(i.DoseFunctionParameters, "LowDoseDistance"):
         i.DoseFunctionParameters.HighDoseLevel = round(i.DoseFunctionParameters.HighDoseLevel * factor , 1)
         i.DoseFunctionParameters.LowDoseLevel = round(i.DoseFunctionParameters.LowDoseLevel * factor , 1)
      else:
         i.DoseFunctionParameters.DoseLevel = round(i.DoseFunctionParameters.DoseLevel *factor, 1)
   if hasattr(po.Constraints, "_0"):
      for i in po.Constraints:
         if hasattr(i.DoseFunctionParameters, "LowDoseDistance"):
            i.DoseFunctionParameters.HighDoseLevel = round(i.DoseFunctionParameters.HighDoseLevel * factor , 1)
            i.DoseFunctionParameters.LowDoseLevel = round(i.DoseFunctionParameters.LowDoseLevel * factor , 1)
         else:
            i.DoseFunctionParameters.DoseLevel = round(i.DoseFunctionParameters.DoseLevel *factor, 1)

if option == 'Clinical Goals' or option == 'Both':
   for i in plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions:
      type = i.PlanningGoal.Type
      if type == "DoseAtVolume" or type == "AverageDose" or type == "DoseAtAbsoluteVolume" :
         i.PlanningGoal.AcceptanceLevel = round(i.PlanningGoal.AcceptanceLevel * factor, 0)
      elif type == "ConformityIndex" or type == "VolumeAtDose" or type == "AbsoluteVolumeAtDose" :
         i.PlanningGoal.ParameterValue = round(i.PlanningGoal.ParameterValue * factor, 0)

