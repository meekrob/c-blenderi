bl_info = {
    "name" : "EPIC GS data Processor",
    "author" : "David C. King",
    "version" : (2, 79, 0),
    "location" : "View3D > Tools > Create",
    "description" : "Process EPIC.GS data files into full animations: 1 object per cell",
    "tracker_url" : "https://github.com/meekrob/c-blenderi/issues",
    "warning" : "",
    "wiki_url" : "https://github.com/meekrob/c-blenderi/wiki",
    "category" : "3D View"
}

import bpy
from bpy.props import StringProperty
from bpy.props import CollectionProperty
import sys

from epic_gs_data_addon import trace_lineage

class OBJECT_OT_epic(bpy.types.Operator):
    """Epic processing button"""
    bl_label = "Process file"
    bl_idname = "object.epic"
    bl_options = {'REGISTER'}

    run_this_shit = False

    def execute(self, context):
        if context.scene.render.engine != 'CYCLES':
            context.scene.render.engine = 'CYCLES'

        print("Running this shit: FILEPATH %s" % context.scene.epic_gs_filename)
        if context.scene.epic_gs_filename == '':
            self.report({'ERROR_INVALID_INPUT'}, "Need to specify a file")
            return {'CANCELLED'}

        self.report({'INFO'}, "Processing file: %s" % context.scene.epic_gs_filename)
        infilename = context.scene.epic_gs_filename

        # set up the scene
        if context.scene.default_cell_template != "":
            cell_template = bpy.data.objects.get( context.scene.default_cell_template )
        else:
            # add an object
            pass

        # process data
        min_time, max_time, big_data = trace_lineage.load_gs_epic_file(infilename)
        return {'FINISHED'}

        

class OBJECT_OT_custompath(bpy.types.Operator):
    #bl_label = "Select epic.gs data file"
    bl_label = "Process EPIC.GS file"
    bl_idname = "object.custom_path"
    __doc__ = ""

    bl_options = {'REGISTER'}

    filename_ext = "*.csv"
    filter_glob = StringProperty(
        name = "Filename",
        description = "File to Process",
        default=filename_ext, options={'HIDDEN'}
    )    

    filepath = StringProperty(
        name="File Path", 
        description="Filepath used for importing txt files", 
        maxlen= 1024, 
        default= "")

    def execute(self, context):
        print("FILEPATH %s"%self.properties.filepath)#display the file name and current path        
        context.scene.epic_gs_filename = self.properties.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class file_processing_panel(bpy.types.Panel):
    """File processing panel"""
    bl_label = "Epic.gs.data processer"
    bl_idname = "OBJECT_PT_file_process"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Create"
    bl_context = "objectmode"

    def draw(self, context):
        print("draw: dir(context)", dir(context), file=sys.stderr)
        #obj = bpy.context.scene.objects.get("embryo_parent")
        scene = bpy.context.scene

        layout = self.layout
        row = layout.row()
        row.label(text="Open and process an epic.gs.data file:")
        row = layout.row(align=True)
        row.prop( context.scene, "epic_gs_filename", text="")
        p = row.operator( OBJECT_OT_custompath.bl_idname, text="", icon = "FILESEL")
        p.filepath = context.scene.epic_gs_filename 

        row = layout.row()
        row.label(text="Setup:")

        # empty parent for everything
        row = layout.row()
        row.label(text="Embryo parent")
        row.prop_search(bpy.context.scene, "embryo_parent", bpy.context.scene, "objects", text="")

        # cell type object templates
        row = layout.row()
        row.label(text="Object template for cell types:")

        row = layout.row()
        row.prop_search(bpy.context.scene, "default_cell_template", bpy.context.scene, "objects", text="")
        scene = context.scene

        #row = layout.row()
        #row.label(text="Material template for cell types 1:")

        #row = layout.row()
        #row.prop_search(bpy.context.scene, "default_cell_material", bpy.data.materials, "materials", text="")

        #row = layout.row()
        #row.label(text="Material template for cell types 2:")

        #row = layout.row()
        #row.prop_search(bpy.types, "default_cell_material", bpy.types, "materials", text="")
        row = layout.row()
        row.prop(bpy.data, "default_cell_material")

        row = layout.row()
        split = row.split()

        col = split.column()
        col.label(text="C cell:")
        col.prop_search(bpy.context.scene, "C_cell_template", bpy.context.scene, "objects", text="")

        col = split.column()
        col.label(text="D cell:")
        col.prop_search(bpy.context.scene, "D_cell_template", bpy.context.scene, "objects", text="")

        row = layout.row()
        split = row.split()

        col = split.column()
        col.label(text="E cell:")
        col.prop(bpy.context.scene, "E_cell_template", text="")

        col = split.column()
        col.label(text="P cell:")
        col.prop_search(bpy.context.scene, "P_cell_template", bpy.context.scene, "objects", text="")

        row = layout.row()
        row.label(text="Operations:")
        row = layout.row()
        p = row.operator(OBJECT_OT_epic.bl_idname)
        


def process_epic_gs_button(self, context):
    self.layout.operator('file.select_all_toggle',        
        OBJECT_OT_custompath.bl_idname,
        icon = "FILESEL"
    )

def layers_tuple(selected=0):
    layer_list = [False] * 20
    layer_list[0] = True
    return tuple(layer_list)


# registration
def register():
    print("-register-", file=sys.stderr)

    """
    # While trying to activate as an add-on
    # AttributeError: '_RestrictContext' object has no attribute 'scene'
    if bpy.context.scene.objects.find("embryo_parent") < 0:
        bpy.ops.object.empty_add(
            type='PLAIN_AXES', 
            view_align=False, 
            location=(0, 0, 0), 
            layers=layers_tuple()
        )
        bpy.context.object.name = "embryo_parent"
    """

    bpy.types.Scene.epic_gs_filename = bpy.props.StringProperty(
        name = "Epic filename",
        default = "",
        description = "Epic gs name"
    )
    main_blender_object = bpy.types.Scene
    #blender_object = bpy.types.Object
    main_blender_object.embryo_parent = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name = "Embryo object parent",
        description = "All added objects are parented to this object",
        poll = empty_check_function
    )

    main_blender_object.default_cell_template = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name = "Default object to use for all cells",
        description = "This object will be cloned to produce any cells",
        poll = mesh_check_function
    )

    main_blender_object.C_cell_template = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name = "C Cell Object template",
        description = "This object will be cloned to produce all of the C cells in the data file",
        poll = mesh_check_function

    )
    main_blender_object.D_cell_template = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name = "D Cell Object template",
        description = "This object will be cloned to produce all of the D cells in the data file",
        poll = mesh_check_function

    )
    main_blender_object.E_cell_template = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name = "E Cell Object template",
        description = "This object will be cloned to produce all of the E cells in the data file",
        poll = mesh_check_function
    )
    main_blender_object.P_cell_template = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name = "P Cell Object template",
        description = "This object will be cloned to produce all of the P cells in the data file",
        poll = mesh_check_function

    )
    bpy.types.Material.default_cell_material = bpy.props.PointerProperty(
        type=bpy.types.Material,
        name = "Default cell material",
        description = "This material will be assigned to all cells",
        poll = material_check_function
    )

    bpy.utils.register_module(__name__)
    #bpy.utils.register_class(OBJECT_OT_epic)
    #bpy.utils.register_class(OBJECT_OT_custompath)
    #bpy.utils.register_class(file_processing_panel)
    bpy.types.INFO_MT_mesh_add.append(process_epic_gs_button)

def mesh_check_function(self, obj):
    return obj.type == 'MESH'

def empty_check_function(self, obj):
    return obj.type == 'EMPTY'

def material_check_function(self, obj):
    return obj.type == 'MATERIAL'

def unregister():
    bpy.utils.unregister_module(__name__)
    #bpy.utils.unregister_class(OBJECT_OT_epic)
    #bpy.utils.unregister_class(OBJECT_OT_custompath)
    #bpy.utils.unregister_class(file_processing_panel)
    bpy.types.INFO_MT_mesh_add.remove(process_epic_gs_button)
    del bpy.types.Scene.epic_gs_filename
    del bpy.types.Scene.embryo_parent
    del bpy.types.Scene.default_cell_template
    del bpy.types.Scene.C_cell_template
    del bpy.types.Scene.D_cell_template
    del bpy.types.Scene.E_cell_template
    del bpy.types.Scene.P_cell_template

if __name__ == "__main__":
    register()

