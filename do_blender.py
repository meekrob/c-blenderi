# This stub runs a python script relative to the currently open
# blend file, useful when editing scripts externally.

import bpy
import sys # for  stderr
import math # for log2
import time # for time.time()

sys.path.append('/Users/david/epic_gs_data')
import trace_lineage

start_time = time.time()

#e_end_pnts = [ 
#"Ealaa", "Ealap", "Ealpa", "Ealpp", "Earaa", "Earap", "Earpa", "Earpp",
#"Eplaa", "Eplap", "Eplpa", "Eplpp", "Epraa", "Eprap", "Eprpa", "Eprpp" ]

end_pnts = trace_lineage.ALL_END_PNTS


n_stages = int( math.log2( len( end_pnts ) ) )

parents = {}
# since get_parent has to go backwards, reverse the sequence from 0-n_stages
stages_low_high = list(range(n_stages))[::-1]
for stage in stages_low_high:
    parents[ stage ] = {}
    for end_pnt in end_pnts:
        parents[ stage ][ trace_lineage.get_parent( end_pnt ) ] = ''

def scale_value(inval):
    MINV = 20000
    MAXV = 90000
    margin = MAXV - MINV
    percent_max = (inval - MINV) / margin
    return percent_max

NTICKS = 4
#def do_thing(metaball, end_cell, filename):
def do_thing(metaball, end_cell, min_time, max_time, big_data):
    last_cell = ''
    #ticker = 0
    #for timepnt, row, found_cell in trace_lineage.parse_gs_epic_file([end_cell], filename):
    timer = time.time()
    for timepnt, row, found_cell in trace_lineage.search_gs_epic_file([end_cell], min_time, max_time, big_data):
        #if ticker:
            #if ticker - 1 == 0:
                #print("at",  str(timepnt) + ",", NTICKS, "post cell division", file=sys.stderr)
            #ticker -= 1
        if found_cell != last_cell:
            print("at cell division", str(timepnt) + ",", last_cell, "==>", found_cell, "in %.4f seconds" % (time.time() - timer), file=sys.stderr)
            ticker = NTICKS
            timer = time.time()
        last_cell = found_cell
        if not row:
            continue
        frame = timepnt *12
        bpy.context.scene.frame_current = frame
        bpy.context.object.location = (row['x']/100,row['y']/100,row['z']/10)
        size = row['size']/200
        bpy.context.object.scale = (size,size,size)
        #bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_LocScale')
        #bpy.ops.anim.keyframe_insert(type='BUILTIN_KSI_LocScale')
        bpy.context.object.keyframe_insert('scale')
        bpy.context.object.keyframe_insert('location')
        # do something with the material
        curMat = bpy.context.object.active_material
        #if 'ecdf' in row:
        if False:
            curMat.node_tree.nodes['ColorRamp'].inputs[0].default_value = row['ecdf']
        else:
            curMat.node_tree.nodes['ColorRamp'].inputs[0].default_value = scale_value(row['value'])
        curMat.node_tree.nodes['ColorRamp'].inputs[0].keyframe_insert("default_value", frame = frame )


bpy.context.scene.render.engine = 'CYCLES'

###############
## profiling ##
###############
import cProfile, pstats, io
#from pstats import SortKey
pr = cProfile.Profile()
pr.enable()

#big_data = trace_lineage.get_big_data('mml-1_5_CD20070804.csv')
infilename = 'pha4_b2_CD20060629.csv'
#infilename = 'pha4_b2_CD20060629_w_q.csv'
#do_thing(obj, celltype, 'elt7_c2a_CD20070310.csv')
#infilename = 'mml-1_5_CD20070804.csv'
#infilename = 'elt7_c2a_CD20070310.csv'
min_time, max_time, big_data = trace_lineage.load_gs_epic_file(infilename)

#base_mat = bpy.data.materials.get('epic_color_ramp')
base_mat = bpy.data.materials.get('ab_emission')
#ab_mat = bpy.data.materials.get('outer_cells')
ab_mat = bpy.data.materials.get('ab_emission')

current_cell_type_char = ''
profilers = {}
active_profiler = None

for celltype in end_pnts:
    cell_start_time = time.time()
    cell_type_char = celltype[0]

    # run a different profiler for each cell type
    if current_cell_type_char != cell_type_char:
        if active_profiler:
            active_profiler.disable()
        current_cell_type_char = cell_type_char
        active_profiler = cProfile.Profile()
        active_profiler.enable()
        profilers[current_cell_type_char] = active_profiler 

    print("Doing", celltype, file=sys.stderr)
    print("==============", file=sys.stderr)
    #bpy.ops.object.metaball_add(type='BALL', radius=1)
    if celltype.startswith('C'):
        bpy.ops.mesh.primitive_cone_add(
            radius1=1, radius2=0, depth=2, view_align=False, enter_editmode=False, location=(0, 0, 0), 
            layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.scene.layers[0] = True

    elif celltype.startswith('D'):
        bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=3, view_align=False, enter_editmode=False, location=(0, 0, 0), 
        layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.scene.layers[1] = True

    elif celltype.startswith('E'):
        #bpy.ops.mesh.primitive_torus_add(location=(0, 0, 0), view_align=False, rotation=(0, 1.5708, 0), 
        #layers=(False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False), 
        #mode='MAJOR_MINOR', major_radius=0.5, minor_radius=0.25, abso_major_rad=0.75, abso_minor_rad=0.25)
        bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2,
        size=1, 
        view_align=False, 
        enter_editmode=False, 
        location=(0,0,0), 
        layers=(False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.scene.layers[2] = True

    elif celltype.startswith('MS'):
        bpy.ops.mesh.primitive_cube_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), 
        layers=(False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.scene.layers[3] = True

    elif celltype.startswith('Z'):
        #bpy.ops.mesh.primitive_monkey_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), 
        #layers=(False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.ops.mesh.primitive_round_cube_add(layers=(False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False), rotation=(0, 0, 0), location=(0,0,0), view_align=False)
        bpy.context.scene.layers[4] = True

### subdivide AB cells into different layers
    elif celltype.startswith('ABpl'):
        bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2,
        size=1, 
        view_align=False, 
        enter_editmode=False, 
        location=(0,0,0), 
        layers=(False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.scene.layers[5] = True
    elif celltype.startswith('ABpr'):
        bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2,
        size=1, 
        view_align=False, 
        enter_editmode=False, 
        location=(0,0,0), 
        layers=(False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.scene.layers[6] = True
    elif celltype.startswith('ABal'):
        bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2,
        size=1, 
        view_align=False, 
        enter_editmode=False, 
        location=(0,0,0), 
        layers=(False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.scene.layers[7] = True
    else:
        bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2,
        size=1, 
        view_align=False, 
        enter_editmode=False, 
        location=(0,0,0), 
        layers=(False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.scene.layers[8] = True


    # create the material
    if not celltype.startswith('MS') and not celltype.startswith('AB'):
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subsurf"].levels = 2

    if celltype.startswith('AB'):
        new_mat = ab_mat.copy()
    else:
        new_mat = base_mat.copy()

    new_mat.name = celltype

    obj = bpy.context.object
    obj.data.materials.append(new_mat)
    obj.name = celltype
    scn = bpy.context.scene
    scn.frame_start = 1
    scn.frame_end = 212*12
    do_thing(obj, celltype, min_time, max_time, big_data)
    cell_end_time = time.time()
    print("Finished cell in %.4f seconds" % (cell_end_time - cell_start_time), file=sys.stderr)

## final cell type profiler
if active_profiler:
    active_profiler.disable()

end_time = time.time()
print("Done thing in %d seconds" % int(end_time - start_time), file=sys.stderr)
###################
## end profiling ##
###################
pr.disable()
s = io.StringIO()
#sortby = SortKey.CUMULATIVE
sortby = 'cumtime'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue(), file=sys.stderr)

for cell_symbol,pr in profilers.items():
    print("PROFILER FOR", cell_symbol, file=sys.stderr)
    s = io.StringIO()
    sortby = 'cumtime'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue(), file=sys.stderr)
