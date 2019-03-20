import sys
import bpy

def CreateLineageTracker( tips ):
    tree_nodes = Lineage.build_tree_from_tips( tips )
    root = Lineage.get_root( tree_nodes )
    return new LineageTracker(tree_nodes, root['name'])

class LineageTracker():
    # persistant object wrapper around the static methods
    def __init__(self, tree_nodes, current=None):
        self.tree_nodes = tree_nodes
        self.current = current

    def set(self, node_str):
        if node_str in self.tree_nodes:
            self.current = node_str
        else:
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
            pointer = self.clone_pointer
            pointer.set(name)
            pointers.append(pointer)

        return pointers

    def clone_pointer(self):
        return new LineageTracker(self.tree_nodes, self.current)
        
# static
class Lineage:
    def build_tree_from_tips( tips ):
        nodes = {}
        
        for tip in tips:
            
            this_cell = { 'name': tip, 'parent': None, 'children': [] }
            Lineage.recursively_link_parents(this_cell, nodes)

        return nodes

    def recursively_link_parents(child_node, nodes):

            print("child_node", child_node['name'], file=sys.stderr)

            parent_cell_name = Lineage.get_parent_name( child_node['name'] )

            # stop at the top
            if parent_cell_name is None: return
                
            # create parent, unless sibling has already done so
            if parent_cell_name not in nodes:
                nodes[parent_cell_name] = { 'name': parent_cell_name, 'parent': None, 'children': [] }

            child_node['parent'] = nodes[parent_cell_name]
            if child_node not in child_node['parent']['children']:
                child_node['parent']['children'].append( child_node )

            # do grandparent
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
        self.cellname = self.cellname
        self.obj = obj
        self.mball = mball
        self.mball_el = mball_el
    def copy(self):
        return new Cell_Datum(self.cellname, self.obj, self.mball, self.mball_el)

    # static utils
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
        current_frame = scene.frame_current

        el = mball.elements.new()
        el.co = el_template.co.copy()
        el.keyframe_insert("co")
        el.hide = False
        el.keyframe_insert("hide")
        scene.frame_current = 1
        el.hide = True
        el.keyframe_insert("hide")
        scene.frame_current = current_frame

        return el

class Cell:
    def spawn(cellname, scene):
        # nucleus
        mball = bpy.data.metaballs.new(cellname + "_nuc")
        obj = bpy.data.objects.new(cellname + "_nuc")
        scene.objects.link(obj)
        mball.resolution = 0.16
        mball.render_resolution = 0.1
        el = mball.elements.new()
        el.radius = 2
        nuc_data = new Cell_Datum(cellname, obj, mball, el)
        # membrane
        mball = bpy.data.metaballs.new(cellname + "_mem")
        obj = bpy.data.objects.new(cellname + "_mem")
        scene.objects.link(obj)
        mball.resolution = 0.16
        mball.render_resolution = 0.1
        el = mball.elements.new()
        el.radius = 4
        mem_data = new Cell_Datum(cellname, obj, mball, el)
        
        # make a Cell
        return new Cell(cellname, scene, nuc_data, mem_data)
        
    def __init__(self, cellname, scene, nucleus_datum, membrane_datum)
        self.cellname = self.cellname
        self.scene = scene 
        self.nucleus = nucleus_datum
        self.membrane = membrane_datum
        
        self.nucleus_mball = nucleus_mball
        self.membrane_mball = membrane_mball
        self.nucleus_el = nucleus_el
        self.membrane_el = membrane_el
        self.nucleus_obj = nucleus_obj
        self.membrane_obj = membrane_obj

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
            leftCell = new Cell(cell_left_name, self.scene, nucleus_left, membrane_left)

        if len(child_names) > 1:
            nucleus_right = self.nucleus.copy()
            membrane_right = self.membrane.copy()
            cell_right_name = child_names[1] 

            # debut new mesh elements for "right"
            nucleus_right.mball_el = Cell_Datum.debut_el_copy_at_current_frame( nucleus_left.mball_el, nucleus_left.mball, self.scene )
            membrane_right.mball_el = Cell_Datum.debut_el_copy_at_current_frame( membrane_left.mball_el, membrane_left.mball, self.scene )

            # make new objects for "right"
            nucleus_right.obj = Cell_Datum.debut_obj_copy_at_current_frame(cell_right_name + "_nuc", nucleus_right.obj, nucleus_right.mball, scene)
            membrane_right.obj = Cell_Datum.debut_obj_copy_at_current_frame(cell_right_name + "_mem", membrane_right.obj, membrane_right.mball, scene)
            rightCell = new Cell(cell_right_name, self.scene, nucleus_right, membrane_right)

        return leftCell, rightCell

    def end_cytokinesis(self):
        # Copy all data and create new metaballs and objects specific to this cell only
        # this will prevent the current cell from re-merging into its sibling, and will allow
        # its material and texture properties to be set individually
        return

if __name__ == '__main__':
    P0 = CreateLineageTracker(['Ea', 'D'])
    P0_cell = Cell.spawn(P0, bpy.context.scene)
