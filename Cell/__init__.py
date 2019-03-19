# blender modules
import bpy
import mathutils

class Cell:
    def __init__(self, cellname, scene):
        # initialize base objects
        self.nucleus_mball = bpy.data.metaballs.new(cellname + "_nuc_mball")
        self.membrane_mball = bpy.data.metaballs.new(cellname + "_mem_mball")
        self.nucleus_obj = bpy.data.objects.new(cellname + "_nuc_obj")
        self.membrane_obj = bpy.data.objects.new(cellname + "_mem_obj")
        # link objects to scene
        scene.objects.link(self.nucleus_obj)
        scene.objects.link(self.membrane_obj)
        # create metaball elements
        self.nucleus_left = self.nucleus_mball.elements.new()
        self.nucleus_right = self.nucleus_mball.elements.new()
        # sizing?
        self.membrane_left = self.membrane_mball.elements.new()
        self.membrane_right = self.membrane_mball.elements.new()
        # sizing?
    
    # Position nuclei and membranes together
    # assign
    def position_left(self, vec):
        self.membrane_left.co = vec
        self.nucleus_left.co = vec
    def position_right(self, vec):
        self.membrane_right.co = vec
        self.nucleus_right.co = vec
    # key
    def key_left_co(self):
        self.membrane_left.keyframe_insert("co")
        self.nucleus_left.keyframe_insert("co")
    def key_right_co(self):
        self.membrane_right.keyframe_insert("co")
        self.nucleus_right.keyframe_insert("co")

    # Visibility
    #  hide: assign+key 
    def key_left_hide(self, hide=True):
        self.membrane_left.hide = hide
        self.membrane_left.keyframe_insert("hide")
        self.nucleus_left.hide = hide
        self.nucleus_left.keyframe_insert("hide")
    def key_right_hide(self, hide=True):
        self.membrane_right.hide = hide
        self.membrane_right.keyframe_insert("hide")
        self.nucleus_right.hide = hide
        self.nucleus_right.keyframe_insert("hide")
    #  show: assign+key 
    def key_left_show(self):
        self.key_left_hide(False)
    def key_right_show(self):
        self.key_right_hide(False)
