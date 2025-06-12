import rhinoscriptsyntax as rs
import Rhino

def get_drop_direction():
    option = rs.GetString(
        "Define drop direction (enter 'vector' to type XYZ or 'points' to pick two points)",
        "points",
        ["vector", "points"]
    )

    if option == "vector":
        vx = rs.GetReal("X component", 0)
        vy = rs.GetReal("Y component", 0)
        vz = rs.GetReal("Z component", -1)
        direction = Rhino.Geometry.Vector3d(vx, vy, vz)
    else:
        start_pt = rs.GetPoint("Pick first point (start of direction)")
        if not start_pt:
            rs.MessageBox("No point selected. Using default downward vector.")
            return Rhino.Geometry.Vector3d(0, 0, -1)

        end_pt = rs.GetPoint("Pick second point (end of direction)")
        if not end_pt:
            rs.MessageBox("No point selected. Using default downward vector.")
            return Rhino.Geometry.Vector3d(0, 0, -1)

        direction = end_pt - start_pt

    if direction.IsZero:
        rs.MessageBox("Direction cannot be zero. Using default downward vector.")
        direction = Rhino.Geometry.Vector3d(0, 0, -1)

    direction.Unitize()
    return direction

def drop_geometry_onto_target():
    obj_ids = rs.GetObjects("Select objects to drop onto surface/mesh", preselect=True, select=True)
    if not obj_ids:
        print("No objects selected.")
        return

    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt("Select one surface, polysurface, extrusion, or mesh as the target")
    go.SubObjectSelect = False
    go.GroupSelect = False
    go.Get()
    if go.CommandResult() != Rhino.Commands.Result.Success:
        print("No valid target selected.")
        return
    target_objref = go.Object(0)
    if not target_objref:
        print("No valid target object reference.")
        return
    target_obj = target_objref.Object()
    if not target_obj:
        print("No valid target object reference.")
        return

    target_geometry = target_obj.Geometry
    is_mesh = isinstance(target_geometry, Rhino.Geometry.Mesh)
    is_brep = isinstance(target_geometry, Rhino.Geometry.Brep)
    is_extrusion = isinstance(target_geometry, Rhino.Geometry.Extrusion)

    brep_for_intersection = None

    if is_mesh:
        geometry_for_intersection = target_geometry
    elif is_brep:
        geometry_for_intersection = target_geometry
    elif is_extrusion:
        brep_for_intersection = target_geometry.ToBrep()
        if brep_for_intersection is None:
            print("Extrusion could not be converted to Brep.")
            return
        geometry_for_intersection = brep_for_intersection
        is_brep = True
    else:
        print("Target must be a surface, polysurface, extrusion, or mesh.")
        return

    drop_dir = get_drop_direction()
    doc = Rhino.RhinoDoc.ActiveDoc
    moved_count = 0

    for obj_id in obj_ids:
        geom = rs.coercegeometry(obj_id)
        if not geom:
            continue

        bbox = geom.GetBoundingBox(True)
        min_proj_pt = None
        min_proj_val = float("inf")
        for corner in bbox.GetCorners():
            proj_val = Rhino.Geometry.Vector3d(corner.X, corner.Y, corner.Z).Dot(drop_dir)
            if proj_val < min_proj_val:
                min_proj_val = proj_val
                min_proj_pt = corner

        if not min_proj_pt:
            print("Could not find front point for object {}".format(obj_id))
            continue

        ray = Rhino.Geometry.Ray3d(min_proj_pt, drop_dir)
        intersection_point = None

        if is_mesh:
            mesh = geometry_for_intersection
            dist = Rhino.Geometry.Intersect.Intersection.MeshRay(mesh, ray)
            if dist >= 0:
                intersection_point = ray.PointAt(dist)
        else:
            end_pt = min_proj_pt + drop_dir * 999999
            line = Rhino.Geometry.Line(min_proj_pt, end_pt)
            line_curve = Rhino.Geometry.LineCurve(line)
            tolerance = doc.ModelAbsoluteTolerance
            brep = geometry_for_intersection

            res = Rhino.Geometry.Intersect.Intersection.CurveBrep(line_curve, brep, tolerance)
            intersection_points = []
            if isinstance(res, tuple) and len(res) > 0:
                rc = res[0]
                if rc:
                    for item in res[1:]:
                        if not item:
                            continue
                        for sub in item:
                            if isinstance(sub, Rhino.Geometry.Point3d):
                                intersection_points.append(sub)
                            elif hasattr(sub, 'PointA'):
                                intersection_points.append(sub.PointA)

            if intersection_points:
                valid_pts = []
                for pt in intersection_points:
                    vec = pt - min_proj_pt
                    if vec * drop_dir > 0:
                        valid_pts.append(pt)
                if valid_pts:
                    intersection_point = min(valid_pts, key=lambda p: (p - min_proj_pt).Length)

        if intersection_point:
            move_vec = intersection_point - min_proj_pt
            rs.MoveObject(obj_id, move_vec)
            moved_count += 1
        else:
            print("No intersection found along direction for object {}. Skipping.".format(obj_id))

    doc.Views.Redraw()
    print("Dropped {} object(s) onto the target.".format(moved_count))

def main():
    drop_geometry_onto_target()

if __name__ == "__main__":
    main()