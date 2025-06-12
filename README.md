# Drop Geometry onto Surface or Mesh in Rhino3D (Custom Direction)

This Rhino3D script allows you to drop geometry onto a surface, polysurface, extrusion, or mesh along a **custom user-defined direction**. This is especially useful when working with sloped, vertical, or non-horizontal targets in architectural or computational design workflows.

## What Does the Script Do?

The **Drop Geometry onto Target** tool allows you to:

* Select multiple objects to be dropped.
* Choose a single target object (surface, polysurface, extrusion, or mesh).
* Define the **drop direction** by either:

  * Typing in an XYZ vector manually.
  * Picking two points to define the direction interactively in the viewport.
* For each object:

  * Detect the bounding box corner most forward in the drop direction.
  * Cast a ray from that point along the vector.
  * If intersection is detected, move the object to align precisely with the surface.

## Why Use It?

Rhino’s built-in tools do not offer efficient workflows for projecting geometry onto arbitrarily sloped or curved targets in a directional way. This tool is ideal when:

* Dropping geometry onto inclined topography or curved façades.
* Aligning modular parts along a specific axis.
* Automating vertical or directional placement for design iteration or preparation for fabrication.

This script reduces the need for temporary construction geometry or manual alignment.

## How to Use the Script

### Load the Script in Rhino

**Method 1**:

1. Type `_RunPythonScript` in the command line.
2. Browse to the location where you saved the script and select it.

### Method 2 Creating a Button or Alias for Easy Access (Optional)

#### Creating a Toolbar Button

1. **Right-click** on an empty area of the toolbar and select **New Button**.
2. In the **Button Editor**:

   * **Left Button Command**:

     ```plaintext
     ! _-RunPythonScript "FullPathToYourScript\drop_geometry_custom_direction.py"
     ```

     Replace `FullPathToYourScript` with the actual file path where you saved the script.
   * **Tooltip and Help**: Add a description such as: `Drop objects onto a surface along a user-defined direction`.
   * **Set an Icon (Optional)**: You can assign an icon to the button for easier identification.

#### Creating an Alias

1. Go to **Tools > Options** and select the **Aliases** tab.

2. **Create a New Alias**:

   * **Alias**: Choose a short command name, e.g., `dropdir`.
   * **Command Macro**:

     ```plaintext
     _-RunPythonScript "FullPathToYourScript\drop_geometry_custom_direction.py"
     ```

3. **Use the Alias**: Type the alias (e.g., `dropdir`) into the command line and press **Enter** to run the script.

### Using the Command

1. **Select** the objects you want to drop.
2. **Select** the target geometry (one of: surface, polysurface, extrusion, or mesh).
3. **Specify the drop direction**:

   * Type an XYZ vector (e.g., `0, 0, -1`), or
   * Pick two points to define a custom direction.
4. For each object:

   * The script will calculate the forward-most point in the drop direction.
   * Cast a ray to intersect the target geometry.
   * If an intersection is found, move the object accordingly.
   * If no intersection is found, it will be skipped with a warning.

The viewport will refresh and a summary message will indicate how many objects were successfully dropped.

## Technical Notes

* Supports only **one target object** per run.
* Works with:

  * Meshes
  * Surfaces and polysurfaces (BREPs)
  * Extrusions (converted to BREPs internally)
* The drop direction is automatically unitised.
* If the entered vector is zero or invalid, a default direction of (0, 0, -1) will be used.
* Ray intersection tolerance uses the document’s `ModelAbsoluteTolerance`.
* Only rigid translation is applied — geometry is not rotated or deformed.
