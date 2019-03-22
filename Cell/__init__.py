bl_info = {
    "name" : "Cell division metaball modeller",
    "author" : "David C. King",
    "version" : (2, 79, 0),
    "location" : "View3D > Tools > Create",
    "description" : "Model cell divisions as nuclear and membrane metaballs",
    "tracker_url" : "https://github.com/meekrob/c-blenderi/issues",
    "warning" : "",
    "wiki_url" : "https://github.com/meekrob/c-blenderi/wiki",
    "category" : "3D View"
}
import sys
import bpy

def CreateLineageTracker( tips ):
    tree_nodes = Lineage.build_tree_from_tips( tips )
    root = Lineage.get_root( tree_nodes )
    return LineageTracker(tree_nodes, root['name'], root)

class LineageTracker:
    # persistant object wrapper around the static methods
    def __init__(self, tree_nodes, current=None, tree=None):
        self.tree_nodes = tree_nodes
        self.current = current
        self.root = tree

    def set(self, node_str):
        print( self.tree_nodes.keys(), file=sys.stderr)
        node_names = [node_name for node_name in self.tree_nodes.keys()]
        if node_str in node_names:
            self.current = node_str
        else:
            print("KeyError with %s" % node_str, file=sys.stderr)
            raise "KeyError"

    def __str__(self):
        return self.current

    def get_parent(self):
        return Lineage.get_parent(self.current, self.tree_nodes)

    def get_child_names(self):
        return Lineage.get_child_names(self.current, self.tree_nodes)        

    def get_children(self):
        names = Lineage.get_child_names(self.current, self.tree_nodes)
        pointers = []
        for name in names:
            pointer = self.clone_pointer()
            pointer.set(name)
            pointers.append(pointer)

        return pointers

    def clone_pointer(self):
        return LineageTracker(self.tree_nodes, self.current)
        
# static
class Lineage:
    def build_tree_from_tips( tips ):
        nodes = {}
        
        for tip in tips:
            
            this_cell = { 'name': tip, 'parent': None, 'children': [] }
            nodes[tip] = this_cell
            Lineage.recursively_link_parents(this_cell, nodes)

        return nodes

    def recursively_link_parents(child_node, nodes):
            node_dict = ",".join(nodes.keys())
            print("\n= ENTER ================= ========================", file=sys.stderr) 
            print("Lineage.recursively_link_parents( <%s>, {%s})" % (child_node['name'], node_dict), file=sys.stderr)


            parent_cell_name = Lineage.get_parent_name( child_node['name'] )
            print("child_node %s parent? %s" % (child_node['name'], parent_cell_name), file=sys.stderr)

            # stop at the top
            if parent_cell_name is None: 
                print("============= RETURN ===============>", file=sys.stderr)
                return
                
            # create parent, unless sibling has already done so
            if parent_cell_name not in nodes:
                print("CREATE NODE:", parent_cell_name, file=sys.stderr)
                nodes[parent_cell_name] = { 'name': parent_cell_name, 'parent': None, 'children': [] }
            else:
                names = [child['name'] for child in nodes[parent_cell_name]['children']]
                print("PARENT EXISTS:", parent_cell_name, str(names), file=sys.stderr)

            node_dict = ",".join(nodes.keys())
            print("node_dict:", '{' + node_dict + '}', file=sys.stderr)

            child_node['parent'] = nodes[parent_cell_name]
            try:
                names = [child['name'] for child in child_node['parent']['children']]
                if child_node['name'] not in names:
                #if child_node not in child_node['parent']['children']:
                    #names = [child['name'] for child in child_node['parent']['children']]
                    child_node['parent']['children'].append( child_node )
                    new_names = [child['name'] for child in child_node['parent']['children']]
                    print(child_node['name'], "not in %s['children']:" % parent_cell_name, str(names), "=>", str(new_names), file=sys.stderr)
            except RecursionError as re:
                names = [child['name'] for child in child_node['parent']['children']]
                print("Maximum recursion exceeded on child_node (name:%s) in" % child_node['name'], str(names), file=sys.stderr)
                Lineage.print_tree(child_node)
                raise re

            # do grandparent
            node_dict = ",".join(nodes.keys())
            print("Lineage.recursively_link_parents(child_node['parent'], nodes)", file=sys.stderr)
            print("Lineage.recursively_link_parents( <%s>, {%s})" % (child_node['parent']['name'], node_dict), file=sys.stderr)
            print("============= Recurse ===============>", file=sys.stderr)
            Lineage.recursively_link_parents(child_node['parent'], nodes)

    def print_tree(root, depth=0):
        tab = "    "
        print(tab * depth, end="")

        print("name %s [%x]: (children=%d)" % (root['name'], id(root), len(root['children'])))
        for i,child in enumerate(root['children']):
            print(tab * depth, i, end="")
            Lineage.print_tree(child, depth+1)
    

    def get_root(tree_nodes):
        node = next(iter(tree_nodes.values()))
        while node['parent'] is not None:
            node = node['parent']

        return node

    def get_parent(cellname, tree_nodes):
        if cellname in tree_nodes:
            return tree_nodes[cellname]['parent']

        return None

    def get_children(cellname, tree_nodes):
        if cellname in tree_nodes:
            return tree_nodes[cellname]['children']

        return None

    def get_child_names(cellname, tree_nodes):
        children = Lineage.get_children(cellname, tree_nodes)
        if children:
            names = [child['name'] for child in children]
            names.sort()
            return names

        return []

    def get_parent_name(celltype):
        if celltype == 'P0': return None
        # top level 
        if celltype == 'P1' or celltype == 'AB':  return 'P0'

        if celltype == 'E' or celltype == 'MS':   return 'EMS'

        if celltype == 'EMS' or celltype == 'P2': return 'P1'

        if celltype == 'C' or celltype == 'P3':  return 'P2'

        if celltype == 'D' or celltype == 'P4':  return 'P3'

        if celltype == 'Z3' or celltype == 'Z2': return 'P4'

        if celltype == 'Z1': return 'MSpppaap'

        # celltypes whose parents 
        # ARE one letter shorter
        return celltype[:-1]


class Cell_Datum:
    def __init__(self, cellname, obj, mball, mball_el):
        self.cellname = cellname
        self.obj = obj
        self.mball = mball
        self.mball_el = mball_el
    def copy(self):
        return Cell_Datum(self.cellname, self.obj, self.mball, self.mball_el)

    # static utils
    def debut_mball_copy_at_current_frame(new_name, mball, scene):
        current_frame = scene.frame_current
        new_mball = bpy.data.metaballs.new()

    def debut_obj_copy_at_current_frame(new_name, obj_template, mball, scene):
        current_frame = scene.frame_current
        obj = bpy.data.objects.new(new_name, mball)
        # objects are kept at origin, don't set location
        obj.hide = False
        obj.keyframe_insert("hide")
        scene.frame_current = 1
        obj.hide = True
        obj.keyframe_insert("hide")
        scene.frame_current = current_frame
        return obj

    def debut_el_copy_at_current_frame(el_template, mball, scene):
        # this is a new element of mball, cloning properties of el_template
        current_frame = scene.frame_current
        el = Cell.clone_el_inside_metaball(el_template)
        el.keyframe_insert("co")
        # reduction factor to keep the volumes the same
        el.radius = el_template.radius * 5/6
        el_template.radius = el.radius
        el_template.keyframe_insert("radius")
        el.keyframe_insert("radius")
        # debut in timeline
        Cell.hide_at_frame(el, scene, 1)
        Cell.show_at_frame(el, scene, current_frame)
        return el

class Cell:
    def show_at_frame(obj, scene, frame):
        Cell.hide_at_frame(obj, scene, frame, False)

    def hide_at_frame(obj, scene, frame, hide=True):
        save_frame = scene.frame_current
        scene.frame_current = frame
        obj.hide = hide
        obj.keyframe_insert("hide")
        scene.frame_current = save_frame

    def clone_el_inside_metaball(metaball_element):
        mball = metaball_element.id_data
        new_el = mball.elements.new()
        new_el.co = metaball_element.co.copy()
        new_el.radius = metaball_element.radius
        # ... what else?
        return new_el

    def clone_mobj(new_name, template_el): 
        # old mball is the id_data of the template element
        old_mobj_mball = template_el.id_data

        # create a new metaball object
        new_mobj = bpy.data.objects.new(new_name, bpy.data.metaballs.new(new_name))
        new_mobj_mball = new_mobj.data # new mball is the data of the new_mobj

        # copy metaball properties
        new_mobj_mball.resolution = old_mobj_mball.resolution
        new_mobj_mball.render_resolution = old_mobj_mball.render_resolution
        new_mobj_mball.threshold = old_mobj_mball.threshold

        # clone metaball elements
        new_el = new_mobj_mball.elements.new()
        new_el.co = template_el.co.copy()
        new_el.radius = template_el.radius
        # new object with name "new_name", data is a metaball, clones of all objects
        return new_mobj
            
    def spawn(cellname, scene):
        # nucleus
        mball = bpy.data.metaballs.new(str(cellname) + "_nuc")
        obj = bpy.data.objects.new(str(cellname) + "_nuc", mball)
        scene.objects.link(obj)
        mball.resolution = 0.16
        mball.render_resolution = 0.1
        el = mball.elements.new()
        el.radius = 2
        nuc_data = Cell_Datum(cellname, obj, mball, el)
        # membrane
        mball = bpy.data.metaballs.new(str(cellname) + "_mem")
        obj = bpy.data.objects.new(str(cellname) + "_mem", mball)
        scene.objects.link(obj)
        mball.resolution = 0.16
        mball.render_resolution = 0.1
        el = mball.elements.new()
        el.radius = 4
        mem_data = Cell_Datum(cellname, obj, mball, el)
        
        # make a Cell
        return Cell(cellname, scene, nuc_data, mem_data)
        
    def __init__(self, cellname, scene, nucleus_datum, membrane_datum):
        self.cellname = cellname
        self.scene = scene 
        self.set_nucleus_datum(nucleus_datum)
        self.set_membrane_datum(membrane_datum)
        
    def set_nucleus_datum(self, nucleus_datum):
        self.nucleus = nucleus_datum
        self.nucleus_mball = nucleus_datum.mball
        self.nucleus_el = nucleus_datum.mball_el
        self.nucleus_obj = nucleus_datum.obj

    def set_membrane_datum(self, membrane_datum):
        self.membrane = membrane_datum
        self.membrane_mball = membrane_datum.mball
        self.membrane_el = membrane_datum.mball_el
        self.membrane_obj = membrane_datum.obj

    def __str__(self):
        return str(self.cellname)

    def move_to(self, vec, insert_keyframes=True):
        self.membrane_el.co = vec
        self.nucleus_el.co = vec
        if insert_keyframes:
            self.membrane_el.keyframe_insert("co")
            self.nucleus_el.keyframe_insert("co")

    def start_mitosis(self):
        leftCell = None
        rightCell = None
        # Duplicate geometry, and return new Cell objects that encapsulate the children of the current cell.
        # They will still share the same base metaballs so they can separate in a smooth manner. Object naming 
        # will change stay the same for parent to represent child1, and parent.child2 will be added, with its visibility hidden until the current frame
        child_names = self.cellname.get_children()

        if len(child_names) > 0:
            nucleus_left = self.nucleus
            membrane_left = self.membrane
            cell_left_name = child_names[0]
            leftCell = Cell(cell_left_name, self.scene, nucleus_left, membrane_left)

        if len(child_names) > 1:
            nucleus_right = self.nucleus.copy() # "shallow" copy
            membrane_right = self.membrane.copy() # "shallow" copy
            cell_right_name = child_names[1] 

            ## Add keyframes to the current_frame - 1
            current_frame = self.scene.frame_current
            previous_frame = current_frame - 1
            self.scene.frame_current = previous_frame
            ### key exact position before duplication to prevent a "studder"
            nucleus_left.mball_el.keyframe_insert("co")
            membrane_left.mball_el.keyframe_insert("co")
            ### account for apparent "blow-up" of metaballs when doubled
            nucleus_left.mball_el.keyframe_insert("radius")
            membrane_left.mball_el.keyframe_insert("radius")

            ## Restore current position
            self.scene.frame_current = current_frame

            # debut new mesh elements for "right", includes reducing the radius of the new elements to account for the change in volume
            nucleus_right.mball_el = Cell_Datum.debut_el_copy_at_current_frame( nucleus_left.mball_el, nucleus_left.mball, self.scene )
            membrane_right.mball_el = Cell_Datum.debut_el_copy_at_current_frame( membrane_left.mball_el, membrane_left.mball, self.scene )

            # make new Cell for right-hand element (only the metaball element is different)
            rightCell = Cell(cell_right_name, self.scene, nucleus_right, membrane_right)

        return leftCell, rightCell

    def end_cytokinesis(self):
        # Copy all data and create new metaballs and objects specific to this cell only
        # this will prevent the current cell from re-merging into its sibling, and will allow
        # its material and texture properties to be set individually
        current_frame = self.scene.frame_current
        scene = self.scene

        ### nucleus
        new_nucleus = Cell.clone_mobj(str(self.cellname) + "_nuc", self.nucleus_el)
        scene.objects.link(new_nucleus)
        new_nucleus_el = new_nucleus.data.elements[0]
        new_nucleus_el.keyframe_insert("co")
        ## replace in timeline
        # hide previous
        #Cell.hide_at_frame(self.nucleus_el, scene, current_frame) 
        # debut new
        #Cell.hide_at_frame(new_nucleus_el, scene, 1)
        #Cell.show_at_frame(new_nucleus_el, scene, current_frame)
        
        ### membrane
        new_membrane = Cell.clone_mobj(str(self.cellname) + "_mem", self.membrane_el)
        scene.objects.link(new_membrane)
        new_membrane_el = new_membrane.data.elements[0]
        new_membrane_el.keyframe_insert("co")
        ## replace in timeline
        # hide previous
        #Cell.hide_at_frame(self.membrane_el, scene, current_frame) 
        # debut new
        #Cell.hide_at_frame(new_membrane_el, scene, 1)
        #Cell.show_at_frame(new_membrane_el, scene, current_frame)

        # replace Cell_Datum instances
        self.set_nucleus_datum(Cell_Datum(self.cellname, new_nucleus, new_nucleus.data, new_nucleus.data.elements[0]))
        self.set_membrane_datum(Cell_Datum(self.cellname, new_membrane, new_membrane.data, new_membrane.data.elements[0]))

from mathutils import Vector

if __name__ == '__main__':
    P0 = CreateLineageTracker(['AB', 'P1'])
    Lineage.print_tree(P0.root)
    P0_cell = Cell.spawn(P0, bpy.context.scene)
    P0_cell.move_to( Vector((0,0,1)) )

    bpy.context.scene.frame_current = 24
    AB_cell, P1_cell = P0_cell.start_mitosis()

    bpy.context.scene.frame_current = 128
    if AB_cell:
        AB_cell.move_to( Vector((5,1,2)) )
    if P1_cell:
        P1_cell.move_to( Vector((-5,0,2)) )

    bpy.context.scene.frame_current = 129
    AB_cell.end_cytokinesis()
    bpy.context.scene.frame_current = 140
    AB_cell.move_to( Vector((5,1,5)) )
    
    bpy.context.scene.frame_current = 1