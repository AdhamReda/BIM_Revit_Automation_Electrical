import clr
import math

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

doc = DocumentManager.Instance.CurrentDBDocument

# 1. Inputs
input_lines = IN[0] if isinstance(IN[0], list) else [IN[0]]
detail_lines = [UnwrapElement(x) for x in input_lines if x is not None]

gap_mm = float(IN[1])
gap_ft = gap_mm / 304.8
half_gap = gap_ft / 2

tol = 0.005

# 2. Find Family Symbol
all_symbols = FilteredElementCollector(doc).OfClass(FamilySymbol).OfCategory(BuiltInCategory.OST_DetailComponents)
symbol = None

for s in all_symbols:
    if s.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString() == "cutwire":
        #if s.Family.Name == "Cutwire Detail Item Family Name": here put your detail Item family name
            symbol = s
            break

if not symbol:
    OUT = "Family Type 'cutwire' not found."
else:
    # 3. Analyze all intersections
    line_map = {line.Id: [] for line in detail_lines}
    
    for i in range(len(detail_lines)):
        for j in range(i + 1, len(detail_lines)):
            la = detail_lines[i]
            lb = detail_lines[j]
            
            res_data = la.GeometryCurve.Intersect(lb.GeometryCurve, None)
            
            if isinstance(res_data, tuple):
                comp_result, inter_array = res_data[0], res_data[1]
            else:
                comp_result, inter_array = res_data, None
            
            if comp_result == SetComparisonResult.Overlap and inter_array:
                pt = inter_array.get_Item(0).XYZPoint
                
                # EndPoint Skip Logic (Checking both lines to avoid T-Junction cuts)
                la_p0 = la.GeometryCurve.GetEndPoint(0)
                la_p1 = la.GeometryCurve.GetEndPoint(1)
                lb_p0 = lb.GeometryCurve.GetEndPoint(0)
                lb_p1 = lb.GeometryCurve.GetEndPoint(1)
                
                if (pt.DistanceTo(la_p0) > tol and pt.DistanceTo(la_p1) > tol and
                    pt.DistanceTo(lb_p0) > tol and pt.DistanceTo(lb_p1) > tol):
                    
                    line_map[la.Id].append(pt)

    # 4. Execute modifications
    TransactionManager.Instance.EnsureInTransaction(doc)
    if not symbol.IsActive: symbol.Activate()

    for line in detail_lines:
        pts = line_map[line.Id]
        if not pts: continue
        
        g_curve = line.GeometryCurve
        l_style = line.LineStyle
        
        # Sort points parametrically along the curve (works for Arcs and Lines)
        pts.sort(key=lambda p: g_curve.Project(p).Parameter)
        
        current_param = g_curve.GetEndParameter(0)
        end_param = g_curve.GetEndParameter(1)
        
        # Determine the parametric gap size
        if isinstance(g_curve, Arc):
            # Arc parameter is radians. Arc Length = Radius * Angle
            delta_param = half_gap / g_curve.Radius
        else:
            # Line parameter is length
            delta_param = half_gap
            
        for inter_pt in pts:
            # Get the exact parameter of the intersection on the curve
            inter_param = g_curve.Project(inter_pt).Parameter
            
            param_before = inter_param - delta_param
            param_after = inter_param + delta_param
            
            # Create segment before the gap
            # Tolerance check to prevent Revit from failing on microscopic segments
            if param_before > current_param + 0.001: 
                seg_curve = g_curve.Clone()
                seg_curve.MakeBound(current_param, param_before)
                seg = doc.Create.NewDetailCurve(doc.ActiveView, seg_curve)
                seg.LineStyle = l_style
            
            # Place symbols at the gap boundaries
            for p_val in [param_before, param_after]:
                # Evaluate the exact 3D point and the Tangent vector at this parameter
                pt_on_curve = g_curve.Evaluate(p_val, False)
                transform = g_curve.ComputeDerivatives(p_val, False)
                tangent = transform.BasisX.Normalize()
                
                # Calculate angle based on the curve's tangent at this specific spot
                angle = math.atan2(tangent.Y, tangent.X)
                
                inst = doc.Create.NewFamilyInstance(pt_on_curve, symbol, doc.ActiveView)
                axis = Line.CreateBound(pt_on_curve, pt_on_curve.Add(XYZ.BasisZ))
                ElementTransformUtils.RotateElement(doc, inst.Id, axis, angle)
            
            # Move the cursor to the end of this gap
            current_param = param_after
            
        # Create final segment from last gap to the end of the original line
        if end_param > current_param + 0.001:
            seg_curve = g_curve.Clone()
            seg_curve.MakeBound(current_param, end_param)
            final_seg = doc.Create.NewDetailCurve(doc.ActiveView, seg_curve)
            final_seg.LineStyle = l_style
            
        # Delete the original "solid" line
        doc.Delete(line.Id)

    TransactionManager.Instance.TransactionTaskDone()
    OUT = "Success: Processed both Straight Lines and Arcs."
