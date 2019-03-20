import sys
# blender modules
#import bpy
#import mathutils

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

class Cell:
    def __init__(self, cellname, scene, initial_position, insert_keyframes=False):
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
        self.membrane_left = self.membrane_mball.elements.new()
        self.membrane_right = self.membrane_mball.elements.new()
        # sizing?

        # positioning
        self.position_left(initial_position)
        self.position_right(initial_position)
        if insert_keyframes:
            self.key_left_co()
            self.key_right_co()
    
    # Position nuclei and membranes together
    def position_and_key_left(self, vec):
        self.position_left(vec)
        self.key_left_co()
    def position_and_key_right(self, vec):
        self.position_right(vec)
        self.key_right_co()
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
