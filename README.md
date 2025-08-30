# Blender-ball-joint-generator
# Ball Joint Generator (Blender Add-on)

Blender add-on to generate ball and socket joints.  
Designed for action figure prototyping and 3D printing.

---

## Installation
1. Open **Edit > Preferences > Add-ons**  
2. Click **Install...** and select `ball_joint_generator.py` or `.zip`  
3. Enable **Ball Joint Generator**  

---

## Usage
1. Open 3D View  
2. Press **N** to show sidebar  
3. Select **Ball Joint** tab  
4. Click **Add Ball Joint**  
5. Ball and socket mesh will be created  

---

## Parameters
- **Ball Radius**: radius of ball mesh  
- **Socket Thickness**: wall thickness of socket mesh  
- **Clearance (Gap)**: space between ball and socket  
- **Segments**: sphere subdivision level  
- **Sync**: synchronize socket with ball parameters  

---

## Recommended Values
- **Clearance**: 0.2 – 0.5 mm for 3D print fit  
- **Segments**: 16–32 for low poly, 64+ for smooth surface  
- **Socket Thickness**: 2 mm or more for structural stability  

---

## Notes
- UV Sphere based geometry  
- Distortion may appear near poles  
- Tested with Blender 3.x  
- No rigging or animation support  

---

## License
MIT License
