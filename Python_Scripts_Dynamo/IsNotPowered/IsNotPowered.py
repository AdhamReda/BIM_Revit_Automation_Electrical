import clr
import math
clr.AddReference('RevitServices')
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *


from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
doc = DocumentManager.Instance.CurrentDBDocument
view=doc.ActiveView.Id
fixtures=FilteredElementCollector(doc,view).OfCategory(BuiltInCategory.OST_ElectricalFixtures).WhereElementIsNotElementType().ToElements()
def check_is_powered(ele):
    if ele and hasattr(ele, "MEPModel"):
        ele_mep = ele.MEPModel
        if ele_mep is not None:
            if hasattr(ele_mep, "GetElectricalSystems"):
                systems = ele_mep.GetElectricalSystems()
                if systems is not None and systems.Count > 0:
                    return True
            elif hasattr(ele_mep, "ElectricalSystems"):
                systems = ele_mep.ElectricalSystems
                if systems is not None and systems.Size > 0:
                    return True
    return False
results = []

for fixture in fixtures:
    if not check_is_powered(fixture):
        results.append(fixture)

OUT = results
