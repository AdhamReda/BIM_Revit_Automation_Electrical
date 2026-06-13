import clr

# Revit API
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Electrical import *

# Dynamo Services
clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

doc = DocumentManager.Instance.CurrentDBDocument

# Inputs
fixtures = IN[0]
newPanel = UnwrapElement(IN[1])

# Ensure list
if not isinstance(fixtures, list):
    fixtures = [fixtures]

fixtures = [UnwrapElement(f) for f in fixtures]

modifiedCircuits = []

TransactionManager.Instance.EnsureInTransaction(doc)

for fixture in fixtures:
    mep = fixture.MEPModel
    if not mep:
        continue

    systems = mep.GetElectricalSystems()
    if not systems:
        continue

    for system in systems:
        # Only change POWER circuits
        if system.SystemType == ElectricalSystemType.PowerCircuit:
            try:
                system.SelectPanel(newPanel)
                modifiedCircuits.append(system.Id)
            except:
                pass

TransactionManager.Instance.TransactionTaskDone()

OUT = modifiedCircuits
