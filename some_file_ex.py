import bpy
from bpy.props import StringProperty
from bpy.props import CollectionProperty
import sys

class OBJECT_OT_custompath(bpy.types.Operator):
    #bl_label = "Select epic.gs data file"
    bl_label = ""
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
        #print("FILEPATH %s"%self.properties.filepath)#display the file name and current path        
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
        obj = context.object
        layout = self.layout
        row = layout.row()
        row.label(text="Open and process an epic.gs.data file:")
        row = layout.row(align=True)
        row.prop( context.scene, "epic_gs_filename", text="")
        p = row.operator( OBJECT_OT_custompath.bl_idname, icon = "FILESEL")
        p.filepath = context.scene.epic_gs_filename 

        # cell type object templates
        row = layout.row()
        row.label(text="Object templates for cell types:")

        row = layout.row()
        split = row.split()

        col = split.column()
        col.label(text="C cell:")
        col.prop_search(obj, "C_cell_template", context.scene, "objects", text="")
        #col.prop_search(obj, "C_cell_template", context, "scene", text="")

        col = split.column()
        col.label(text="D cell:")
        col.prop_search(obj, "D_cell_template", context.scene, "objects", text="")

        row = layout.row()
        split = row.split()

        col = split.column()
        col.label(text="E cell:")
        col.prop_search(obj, "E_cell_template", context.scene, "objects", text="")

        col = split.column()
        col.label(text="P cell:")
        col.prop_search(obj, "P_cell_template", context.scene, "objects", text="")
        


def process_epic_gs_button(self, context):
    self.layout.operator('file.select_all_toggle',        
        OBJECT_OT_custompath.bl_idname,
        icon = "FILESEL"
    )

# registration
def register():
    bpy.types.Scene.epic_gs_filename = bpy.props.StringProperty(
        name = "Epic filename",
        default = "",
        description = "Epic gs name"
    )
bpy.types.Scene.C_cell_template = bpy.props.StringProperty(
        name = "C Cell Object template",
        default = "",
        description = "This object will be cloned to produce all of the C cells in the data file"
    )
    bpy.types.Object.D_cell_template = bpy.props.StringProperty(
        name = "D Cell Object template",
        description = "This object will be cloned to produce all of the D cells in the data file"
    )
    bpy.types.Object.E_cell_template = bpy.props.StringProperty(
        name = "E Cell Object template",
        description = "This object will be cloned to produce all of the E cells in the data file"
    )
    bpy.types.Object.P_cell_template = bpy.props.StringProperty(
        name = "P Cell Object template",
        description = "This object will be cloned to produce all of the P cells in the data file"
    )


    bpy.utils.register_class(OBJECT_OT_custompath)
    bpy.utils.register_class(file_processing_panel)
    bpy.types.INFO_MT_mesh_add.append(process_epic_gs_button)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_custompath)
    bpy.utils.unregister_class(file_processing_panel)
    bpy.types.INFO_MT_mesh_add.remove(process_epic_gs_button)

if __name__ == "__main__":
    register()
