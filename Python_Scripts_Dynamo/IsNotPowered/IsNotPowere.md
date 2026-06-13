Description

This Dynamo Python script identifies electrical fixtures that are not connected to any electrical circuit within the currently active Revit view. It collects all electrical fixtures visible in the view, checks whether each fixture belongs to an electrical system through its MEP model, and returns a list of fixtures with no assigned circuit.

Purpose

The script is intended for electrical model QA/QC and BIM automation workflows, helping engineers quickly locate unpowered or uncircuited devices before project issuance, coordination reviews, or model handover. By automatically detecting missing circuit connections, it reduces manual checking effort and improves model accuracy.
