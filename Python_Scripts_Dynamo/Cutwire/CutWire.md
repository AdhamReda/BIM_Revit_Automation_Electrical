1. **Find Intersections:** Checks all input lines against each other to locate exact intersection coordinates.
2. **Filter Out T-Junctions:** Skips intersection points that occur exactly at the start or end of either line, protecting standard corners from being split.
3. **Parametric Gap Calculation:** Computes precise parametric offsets (`delta_param`) for both straight lines (linear distance) and arcs (radians based on radius) to ensure uniform gap widths in millimeters.
4. **Reconstruct & Place Components:** Splits the original intersecting line into segmented boundaries, places the `cutwire` detail component at the gap boundaries, rotates the component to match the line's local tangent vector, and deletes the original full-length line.
