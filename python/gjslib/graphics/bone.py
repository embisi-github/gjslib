#!/usr/bin/env python
#a Imports
import sys, os
import math

sys.path.insert(0, os.path.abspath('../python'))
import gjslib.math.bezier as bezier

#a Documentation
r"""
A bone has a 'base' set of properties - what it is expected to be
A bone then has a 'perturbation' set of properties - 
This allows for a 'target' set of properties (base with perturbation applied)
And a 'current' set of properties (animated from last 'current' toward 'target')

Derived bones can attach to 'base' or 'current' properties - generally not 'target'
"""
#a Local bezier stuff
#c c_bezier
class c_bezier( object ):
    b_coeffs_of_tn = { 1:((1,),) }
    db_coeffs_of_tn = {}
    #f calculate_b_coeffs_of_tn
    @classmethod
    def calculate_b_coeffs_of_tn( cls, order=1 ):
        if order in cls.b_coeffs_of_tn: return
        cls.calculate_b_coeffs_of_tn( order-1 )
        f_nm1 = cls.b_coeffs_of_tn[order-1]
        r = []
        for i in range(order):
            r.append([0]*(order))
            pass
        for c in range(order-1):
            for tn in range(order-1):
                r[c+1][tn+1] += f_nm1[c][tn]
                r[c]  [tn+1] -= f_nm1[c][tn]
                r[c]  [tn]   += f_nm1[c][tn]
                pass
            pass
        for i in range(order):
            r[i] = tuple(r[i])
            pass
        cls.b_coeffs_of_tn[order] = tuple(r)
        pass
    #f update_db_coeffs_of_tn
    @classmethod
    def update_db_coeffs_of_tn( cls ):
        for (n, f_n) in cls.b_coeffs_of_tn.iteritems():
            r = []
            for p in f_n:
                dp = []
                for i in range(len(p)-1):
                    dp.append((i+1)*p[i+1])
                    pass
                dp.append(0)
                r.append( tuple(dp) )
                pass
            cls.db_coeffs_of_tn[n] = tuple(r)
            pass
        pass
    #f __init__
    def __init__( self, pts, pt_coords=None, pt_class=None ):
        self.pts = pts
        self.order = len(pts)
        if type(pts[0])==tuple:
            self.dimension = len(pts[0])
            self.pt_coords = lambda p:p
            self.pt_class = tuple
            pass
        else:
            if pt_coords is not None:
                self.pt_coords = pt_coords
                pass
            else:
                self.pt_coords = lambda p:p.get_coords()
                pass
            #print pts
            self.dimension = len(self.pt_coords(pts[0]))
            if pt_class is not None:
                self.pt_class = pt_class
                pass
            else:
                self.pt_class =  pts[0].__class__
                pass
            pass
        if self.order not in self.db_coeffs_of_tn:
            self.__class__.calculate_b_coeffs_of_tn( order=self.order )
            self.__class__.update_db_coeffs_of_tn()
            pass
        pass
    #f coord
    def coord( self, t, gradient=False ):
        factor = 1.0
        coeffs_of_tn = self.b_coeffs_of_tn[self.order]
        if gradient:
            coeffs_of_tn = self.db_coeffs_of_tn[self.order]
            factor = 1.0
            pass
        tn = [1]*self.order
        for i in range(self.order-1):
            tn[i+1] = tn[i]*t
            pass
        r = [0] * self.dimension
        for i in range(self.order):
            scale = 0
            for j in range(self.order):
                scale += coeffs_of_tn[i][j]*tn[j]
                pass
            cs = self.pt_coords(self.pts[i])
            scale *= factor
            for j in range(self.dimension):
                r[j] += cs[j]*scale
                pass
            pass
        return self.pt_class(r)
    pass
#x = c_bezier( pts=((1,),
#                   (3,),
#                   (4,),
#                   (5,),
#                   (7,)) )
#for t in (0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0):
#    print x.coord(t,gradient=True)
#die

#a Bone expression classes
#c c_bone_op
class c_bone_op( object ):
    op_string="<none>"
    derefs_var = False
    defines_var = False
    def __repr__( self ):
        return "op'%s'"%(self.op_string)
    pass

#c c_bone_op_mult
class c_bone_op_mult( c_bone_op ):
    op_string = "*"
    pass

#c c_bone_op_add
class c_bone_op_add( c_bone_op ):
    op_string = "+"
    pass

#c c_bone_op_sub
class c_bone_op_sub( c_bone_op ):
    op_string = "-"
    pass

#c c_bone_op_rot
class c_bone_op_rot( c_bone_op ):
    op_string = "rot"
    pass

#c c_bone_op_div
class c_bone_op_div( c_bone_op ):
    op_string = "/"
    pass

#c c_bone_op_pop
class c_bone_op_pop( c_bone_op ):
    op_string = "pop"
    pass

#c c_bone_op_get
class c_bone_op_get( c_bone_op ):
    op_string = "get"
    derefs_var = True
    pass

#c c_bone_op_set
class c_bone_op_set( c_bone_op ):
    op_string = "set"
    defines_var = True
    pass

#c c_bone_op_direction
class c_bone_op_direction( c_bone_op ):
    op_string = "direction"
    pass

#c c_bone_op_point
class c_bone_op_point( c_bone_op ):
    op_string = "point"
    pass

#c c_bone_op_dup
class c_bone_op_dup( c_bone_op ):
    op_string = "dup"
    pass

#c c_bone_op_neg
class c_bone_op_neg( c_bone_op ):
    op_string = "neg"
    pass

#c c_bone_op_swap
class c_bone_op_swap( c_bone_op ):
    op_string = "swap"
    pass

#c c_bone_expr_element
class c_bone_expr_element( object ):
    #f find_dependencies
    def find_dependencies( self, expression, stack, scope, dependencies, defines ):
        pass
    pass

#c c_bone_expr_op
class c_bone_expr_op( c_bone_expr_element ):
    #f __init__
    def __init__( self, op ):
        """
        op is a subclass of c_bone_op
        """
        self.op = op
        #print self, op
        pass
    #f evaluate
    def evaluate( self, expression, stack, scope ):
        e = None
        n_ops = 0
        k = (self.op, )
        if k not in expression.expression_ops and len(stack)>0:
            k = (self.op, type(stack[-1]) )
            pass
        if k not in expression.expression_ops and len(stack)>1:
            k = (self.op, type(stack[-1]), type(stack[-2]) )
            pass
        if k not in expression.expression_ops:
            return expression.set_error("Could not find op %s to do"%(str(k)))
        e_op = expression.expression_ops[k]
        n_ops = len(k)-1
        r = None
        if e_op is True:
            r = True
        elif n_ops==0:
            r = expression.expression_ops[e_op[0]]()
            pass
        elif n_ops==1:
            r = e_op[0](stack[-1-e_op[1]])
            pass
        else: # if n_ops==2:
            r = e_op[0](stack[-1-e_op[1]],stack[-1-e_op[2]])
            pass
        if r is True:
            stack.pop()
            pass
        elif r is not None:
            for i in range(n_ops): stack.pop()
            if type(r)==tuple:
                for ri in r:
                    stack.append(ri)
                    pass
                pass
            else:
                stack.append(r)
                pass
            pass
        else:
            return expression.set_error("Expression failed")
        return True
    pass

    #f find_dependencies
    def find_dependencies( self, expression, stack, scope, dependencies, defines ):
        if self.op.defines_var:
            node = stack.pop()
            if node not in defines: defines.append(node)
            pass
        elif self.op.derefs_var:
            node = stack.pop()
            if node not in dependencies: dependencies.append(node)
            pass
        pass
#c c_bone_expr_push
class c_bone_expr_push( c_bone_expr_element ):
    #f __init__
    def __init__( self, v ):
        self.v = v
        pass
    #f evaluate
    def evaluate( self, expression, stack, scope ):
        stack.append( self.v.copy() )
        return True
    pass
#c c_bone_expr_push_bone_var
class c_bone_expr_push_bone_var( c_bone_expr_element ):
    #f __init__
    def __init__( self, id ):
        self.id = id
        pass
    #f evaluate
    def evaluate( self, expression, stack, scope ):
        node = scope.find_node_or_fail(self.id)
        stack.append( node )
        return True
    #f find_dependencies
    def find_dependencies( self, expression, stack, scope, dependencies, defines ):
        node = scope.find_node_or_fail(self.id)
        stack.append( node )
        pass
    pass

#c c_bone_expr
class c_bone_expr( object ):
    """
    An expression is an initial stack contents and a list of expression elements
    To evaluate the expression the initial stack contents is copied, then the expression elements are evaluated one by one
    """
    expression_ops = {}
    script_op2s = {"mult":c_bone_expr_op(c_bone_op_mult),
                   "add":c_bone_expr_op(c_bone_op_add),
                   "rot":c_bone_expr_op(c_bone_op_rot),
                   "div":c_bone_expr_op(c_bone_op_div),
                   "dir":c_bone_expr_op(c_bone_op_direction),
                   "pt":c_bone_expr_op(c_bone_op_point),
                   }
    script_op1s = {"neg":c_bone_expr_op( c_bone_op_neg ),
                   }
    script_op1s.update(script_op2s)
    script_op0s = {"dup":c_bone_expr_op( c_bone_op_dup ),
                   "pop":c_bone_expr_op( c_bone_op_pop )
                   }
    script_op0s.update(script_op1s)
    #f reset_opts
    @classmethod
    def reset_ops( cls ):
        cls.expression_ops = {}
        pass
    #f add_op
    @classmethod
    def add_op( cls, stack_tuple, op ):
        cls.expression_ops[ stack_tuple ] = op
        pass
    #f __init__
    def __init__( self ):
        self.elements = []
        self.error = None
        pass
    #f add_element
    def add_element( self, e ):
        self.elements.append( e )
        pass
    #f add_script
    def add_script( self, script ):
        if type(script)==float:
            self.add_element( c_bone_expr_push( c_bone_type_scalar().set(script) ) )
            pass
        elif type(script)==int:
            self.add_element( c_bone_expr_push( c_bone_type_scalar().set(0.0+script) ) )
            pass
        elif type(script)==list:
            for t in script:
                self.add_script( t )
                pass
            pass
        elif (type(script)==tuple) and (len(script)==3):
            if script[0]=="set":
                self.add_script( script[2] )
                self.add_element( c_bone_expr_push_bone_var( script[1] ) )
                self.add_element( c_bone_expr_op( c_bone_op_set ) )
                pass
            elif script[0] in self.script_op2s:
                self.add_script( script[1] )
                self.add_script( script[2] )
                self.add_element( self.script_op2s[script[0]] )
                pass
            else:
                raise Exception("Cannot interpret script %s"%(str(script)))
            pass
        elif (type(script)==tuple) and (len(script)==2):
            if script[0]=="set":
                self.add_element( c_bone_expr_push_bone_var( script[1] ) )
                self.add_element( c_bone_expr_op( c_bone_op_set ) )
                pass
            elif script[0]=="get":
                self.add_element( c_bone_expr_push_bone_var( script[1] ) )
                self.add_element( c_bone_expr_op( c_bone_op_get ) )
                pass
            elif script[0] in self.script_op1s:
                self.add_script( script[1] )
                self.add_element( self.script_op1s[script[0]] )
                pass
            else:
                raise Exception("Cannot interpret script %s"%(str(script)))
            pass
        elif (type(script)==str):
            if script in self.script_op0s:
                self.add_element( self.script_op0s[script] )
                pass
            else:
                raise Exception("Cannot interpret script %s"%(str(script)))
            pass
        pass
    #f clear_error
    def clear_error( self ):
        self.error = None
        pass
    #f get_error
    def get_error( self ):
        return self.error
    #f set_error
    def set_error( self, error_msg ):
        self.error = error_msg
        return False
    #f errored
    def errored( self ):
        return self.error is not None
    #f evaluate
    def evaluate( self, scope ):
        stack = []
        self.clear_error()
        for e in self.elements:
            if not e.evaluate( self, stack, scope ): break
            pass
        if self.errored():
            return (False, self.get_error())
        return (True, stack )
    #f find_dependencies
    def find_dependencies( self, scope ):
        stack = []
        dependencies = []
        defines = []
        for e in self.elements:
            e.find_dependencies( self, stack, scope, dependencies, defines )
            pass
        return (dependencies, defines)

#a Bone type classes
#c c_bone_type
class c_bone_type( object ):
    type_list = {}
    @classmethod
    def add_type( cls ):
        cls.type_list[cls.type_name] = cls
        pass
    @classmethod
    def find_type( cls, name ):
        if name not in cls.type_list:
            return None
        return cls.type_list[name]
    @classmethod
    def e_type_not_found( cls, name ):
        return Exception("Bone type %s not found"%name)
    #f __init__
    def __init__( self, id=None ):
        self.id = None
        self.value = None
        self.implicit_dependents = []
        pass
    #f add_implicit_dependent
    def add_implicit_dependent( self, other ):
        self.implicit_dependents.append(other)
        return self
    #f get_implicit_dependents
    def get_implicit_dependents( self ):
        return self.implicit_dependents
    #f set
    def set( self, value, var=None ):
        self.value = value
        return self
    #f get
    def get( self ):
        return self.value
    #f copy
    def copy( self ):
        return self.__class__().set( self.value )
    #f dup
    def dup( self ):
        return (self, self.copy())
    #f __repr__
    def __repr__( self ):
        return "bt:%s"%(str(self.value))
    #f visualization
    def visualization( self ):
        return ("text",str(self))
    pass

#c c_bone_type_vector
class c_bone_type_vector( c_bone_type ):
    type_name = "vector"
    #f get_coords
    def get_coords( self ):
        return self.value.get_coords()
    #f set
    def set( self, value, var=None ):
        import copy
        self.value = copy.copy(value)
        return self
    #f add
    def add( self, v ):
        self.value = self.value.add( other=v.get() )
        return self
    #f mult_by_scalar
    def mult_by_scalar( self, v ):
        self.value = self.value.scale( factor=v.get() )
        return self
    #f rot_by_scalar
    def rot_by_scalar( self, v ):
        angle = math.radians(v.get())
        c = math.cos(angle)
        s = math.sin(angle)
        self.value = self.value.mult_by_matrix( ( (c,s),(-s,c) ) )
        return self
    #f neg
    def neg( self ):
        self.value = self.value.scale( factor=-1.0 )
        return self
    #f visualization
    def visualization( self ):
        return ("vector",self.value)
    pass

#c c_bone_type_bezier
class c_bone_type_bezier( c_bone_type ):
    type_name = "bezier"
    #f set
    def set( self, vectors, var=None ):
        self.vectors = vectors
        self.var = var
        for v in vectors:
            v.instance().add_implicit_dependent( var )
            pass
        self.bezier = c_bezier( pts=vectors, pt_coords=lambda p:p.instance().get_coords(), pt_class=vectors[0].instance().value.__class__ )
        #print "BEZIER",c_bone_type_vector().set(self.bezier.coord(0.0))
        pass
    #f copy
    def copy( self ):
        return self
    #f coord
    def coord( self, v ):
        return c_bone_type_vector().set(self.bezier.coord( t=v.get(), gradient=False ) )
    #f direction
    def direction( self, v ):
        return c_bone_type_vector().set(self.bezier.coord( t=v.get(), gradient=True ) )
    #f __repr__
    def __repr__( self ):
        return "btbez:%s"%(str(self.bezier))
    #f visualization
    def visualization( self ):
        vis = []
        for v in self.vectors:
            vis.append(v.instance())
        return ("bezier",self.bezier,vis,self.var)

#c c_bone_type_scalar
class c_bone_type_scalar( c_bone_type ):
    type_name = "scalar"
    #f add
    def add( self, v ):
        self.value += v.value
        return self
    #f mult
    def mult( self, v ):
        self.value *= v.value
        return self
    #f div
    def div( self, v ):
        self.value /= v.v
        return self
    #f neg
    def neg( self ):
        self.value = -self.value
        return self
    #f visualization
    def visualization( self ):
        return ("float",self.value)

#f Assemble known classes
c_bone_type_vector.add_type()
c_bone_type_bezier.add_type()
c_bone_type_scalar.add_type()
#print c_bone_type.type_list

#a Bone classes
#c c_bone_base
class c_bone_base( object ):
    """
    This class is the base class for bones, bone variables, and bone groups. It permits a hierarchical naming system and search.
    """
    #v Required properties
    bone_variables = None
    has_instance = False
    #f __init__
    def __init__( self, name, parent=None, **kwargs ):
        self.name = name
        self.bone_variables = {}
        self.children = []
        self.parent = parent
        if parent is not None: parent.add_child(self)
        self.expressions = {}
        pass
    #f set_parent
    def set_parent( self, parent ):
        self.parent = parent
        return self
    #f add_expression
    def add_expression( self, id, scope, script=None ):
        self.expressions[id] = {"scope":scope, "expr":c_bone_expr(), "defines":[], "dependencies":[]}
        if script is not None:
            self.expressions[id]["expr"].add_script( script )
            pass
        return self.expressions[id]["expr"]
    #f evaluate_expressions
    def evaluate_expressions( self, ids=None ):
        if ids is None: ids=self.expressions.keys()
        for id in ids:
            print "Evaluating", id, self.expressions[id]
            print self.expressions[id]["expr"].evaluate( scope=self.expressions[id]["scope"] )
            pass
        pass
    #f create_dependencies
    def create_dependencies( self, ids=None, include_children=True ):
        if ids is None: ids=self.expressions.keys()
        for id in ids:
            print "Finding dependencies", id, self.expressions[id]
            (dependencies,defines) = self.expressions[id]["expr"].find_dependencies( scope=self.expressions[id]["scope"] )
            self.expressions[id]["dependencies"] = dependencies
            self.expressions[id]["defines"] = defines
            pass
        if include_children:
            for c in self.children:
                c.create_dependencies( ids=None, include_children=True )
                pass
            pass
        pass
    #f collate_dependencies
    def collate_dependencies( self, result=None ):
        if result is None: result = []
        for id in self.expressions.keys():
            result.append( (self, id, self.expressions[id]["dependencies"], self.expressions[id]["defines"]) )
            pass
        for c in self.children:
            c.collate_dependencies(result)
            pass
        return result
    #f add_child
    def add_child( self, node ):
        self.children.append(node)
        node.set_parent(self)
        return node
    #f find_node
    def find_node( self, hierarchical_name, result=None ):
        if result is None: result=[]
        if type(hierarchical_name)==str: hierarchical_name=hierarchical_name.split('.')
        if len(hierarchical_name)<1: return None
        if hierarchical_name[0] != self.name: return None
        result.append(self)
        if len(hierarchical_name)==1: return (self, result)
        for c in self.children:
            r = c.find_node(hierarchical_name[1:], result)
            if r is not None:
                return r
            pass
        for i in range(len(hierarchical_name)-1): result.append(None)
        return (self, result)
    #f find_node
    def find_node( self, hierarchical_name, result=None ):
        if result is None: result=[]
        if type(hierarchical_name)==str: hierarchical_name=hierarchical_name.split('.')
        return self.find_node_in_children( hierarchical_name, result)
    #f find_node_in_children
    def find_node_in_children( self, hierarchical_name, result ):
        for c in self.children:
            if hierarchical_name[0] == c.name:
                result.append(c)
                if len(hierarchical_name)==1: return (c, result)
                return c.find_node_in_children( hierarchical_name[1:], result)
            pass
        for i in range(len(hierarchical_name)): result.append(None)
        return (self, result)
    #f e_failed_to_find_node
    def e_failed_to_find_node( self, hierarchical_name ):
        return Exception("Failed to find node %s"%str(hierarchical_name))
    #f find_node_or_fail
    def find_node_or_fail( self, hierarchical_name ):
        t = self.find_node( hierarchical_name )
        if (t is None) or (t[1][-1]!=t[0]):
            raise self.e_failed_to_find_node(hierarchical_name)
        return t[0]
    #f set_node
    def set_node( self, hierarchical_name, value ):
        node = self.find_node_or_fail( hierarchical_name )
        return node.set(value)
    #f iterate
    def iterate( self, callback, include_children=True ):
        callback(self)
        if not include_children: return
        for c in self.children:
            c.iterate(callback, include_children=include_children)
            pass
        pass
    #f __repr__
    def __repr__( self ):
        if self.parent is not None:
            return "%s.%s.%s"%(self.__class__.__name__,self.parent.name,self.name)
        return "%s.%s"%(self.__class__.__name__,self.name)

#c c_bone_var
class c_bone_var( c_bone_base ):
    """
    A bone variable is a named calculateable value.

    It may be defined by a stack of operations which permit operations on other bone variables.
    """
    has_instance = True
    #f __init__
    def __init__( self, name, var_type=None, **kwargs ):
        c_bone_base.__init__( self, name, **kwargs )
        if var_type is not None:
            if type(var_type)==str:
                var_type_name = var_type
                var_type = c_bone_type.find_type( var_type_name )
                if var_type is None:
                    raise c_bone_type.e_type_not_found(var_type_name)
                pass
            pass
        self.var_instance = var_type( id=name )
        self.var_type = var_type
        pass
    #f instance
    def instance( self ):
        return self.var_instance
    #f set_to_instance_value
    def set_to_instance_value( self, inst ):
        return self.var_instance.set(inst.get())
    #f set
    def set( self, value ):
        return self.var_instance.set(value, var=self)
    #f get
    def get( self ):
        return self.var_instance.get()
    #f copy
    def copy( self ):
        return self.var_instance.copy()
    pass

#c c_bone_group
class c_bone_group( c_bone_base ):
    """
    A bone group is a named object containing a set of bones or bone groups. It may have some bone variable properties of its own.

    A bone group does not have any lines or areas; bones must have them.
    """
    is_bone = False

#c c_bone
class c_bone( c_bone_base ):
    """
    A bone is a linear object with two ends; at every point along the bone it also has a gradient.
    It is implemented as a Bezier curve with constrained points.
    Bones have 'bone variable' properties that are used to define the points.
    Bones have 'name' properties that are unique to their 'bone group'

    Bones may have an associated set of 'skin' curves and areas, which are bezier curve lists.
    Each Bezier control point is derived from a position along the bone (0<=t<=1), and a 2?5?x2 rotation/shear matrix
    The matrix is applied to BLAH and scaled by the length of the bone (distance between t=0 and t=1)
    """
    #f __init__
    def __init__( self, name, **kwargs ):
        c_bone_base.__init__( self, name, **kwargs )
    #f get_coords
    def get_coords( self, t ):
        pass

#a Add expression ops stuff
c_bone_expr.reset_ops()
c_bone_expr.add_op( (c_bone_op_rot, c_bone_type_vector, c_bone_type_scalar), ( c_bone_type_vector.rot_by_scalar, 0, 1 ) )
c_bone_expr.add_op( (c_bone_op_rot, c_bone_type_scalar, c_bone_type_vector), ( c_bone_type_vector.rot_by_scalar, 1, 0 ) )
c_bone_expr.add_op( (c_bone_op_mult, c_bone_type_vector, c_bone_type_scalar), ( c_bone_type_vector.mult_by_scalar, 0, 1 ) )
c_bone_expr.add_op( (c_bone_op_mult, c_bone_type_scalar, c_bone_type_vector), ( c_bone_type_vector.mult_by_scalar, 1, 0 ) )
c_bone_expr.add_op( (c_bone_op_add,  c_bone_type_vector, c_bone_type_vector), ( c_bone_type_vector.add, 0, 1 ) )
c_bone_expr.add_op( (c_bone_op_add,  c_bone_type_scalar, c_bone_type_scalar), ( c_bone_type_scalar.add, 0, 1 ) )
c_bone_expr.add_op( (c_bone_op_mult, c_bone_type_scalar, c_bone_type_scalar), ( c_bone_type_scalar.mult, 0, 1 ) )
c_bone_expr.add_op( (c_bone_op_div,  c_bone_type_scalar, c_bone_type_scalar), ( c_bone_type_scalar.div, 0, 1 ) )
c_bone_expr.add_op( (c_bone_op_pop,), True )
c_bone_expr.add_op( (c_bone_op_dup, c_bone_type_scalar), (c_bone_type_scalar.dup, 0) )
c_bone_expr.add_op( (c_bone_op_dup, c_bone_type_vector), (c_bone_type_vector.dup, 0) )
c_bone_expr.add_op( (c_bone_op_neg, c_bone_type_scalar), (c_bone_type_scalar.neg, 0) )
c_bone_expr.add_op( (c_bone_op_neg, c_bone_type_vector), (c_bone_type_vector.neg, 0) )
c_bone_expr.add_op( (c_bone_op_get, c_bone_var ), (c_bone_var.copy, 0 ) )
c_bone_expr.add_op( (c_bone_op_set, c_bone_type_scalar, c_bone_var ), (c_bone_var.set_to_instance_value, 1, 0 ) )
c_bone_expr.add_op( (c_bone_op_set, c_bone_var, c_bone_type_scalar ), (c_bone_var.set_to_instance_value, 0, 1 ) )
c_bone_expr.add_op( (c_bone_op_set, c_bone_type_vector, c_bone_var ), (c_bone_var.set_to_instance_value, 1, 0 ) )
c_bone_expr.add_op( (c_bone_op_set, c_bone_var, c_bone_type_vector ), (c_bone_var.set_to_instance_value, 0, 1 ) )
c_bone_expr.add_op( (c_bone_op_direction, c_bone_type_bezier, c_bone_type_scalar ), (c_bone_type_bezier.direction, 0, 1 ) )
c_bone_expr.add_op( (c_bone_op_direction, c_bone_type_scalar, c_bone_type_bezier ), (c_bone_type_bezier.direction, 1, 0 ) )
c_bone_expr.add_op( (c_bone_op_point, c_bone_type_bezier, c_bone_type_scalar ), (c_bone_type_bezier.coord, 0, 1 ) )
c_bone_expr.add_op( (c_bone_op_point, c_bone_type_scalar, c_bone_type_bezier ), (c_bone_type_bezier.coord, 1, 0 ) )

#a Functions
#f add_bezier_bone
def add_bezier_bone( parent, bone_name, script, num_pts=3 ):
    bone     = c_bone( bone_name, parent=parent )
    bez_pts = []
    for i in range(num_pts):
        bez_pts.append( bone.add_child( c_bone_var("base_%d"%i, "vector") ) )
        pass
    bone_bez = bone.add_child( c_bone_var("base_bezier", "bezier") )
    bone.add_expression( id="script", scope=parent, script=script )
    bone.evaluate_expressions( ("script",) )
    bone_bez.set( bez_pts )
    return bone

#f script_bez_vec
def script_bez_vec( bezier_name, t=0.0, rotation=0.0, scale=0.0 ):
    return [("add",
             ("pt", t, ("get",bezier_name)),
             ("rot", rotation, ("mult", scale, ("dir", t, ("get",bezier_name)))))]

#f add_extend_bone
def add_extend_bone( parent, bone_name, bone_to_extend, scale=1.0, rotation=0.0, src=0.0 ):
    return add_bezier_bone( parent, bone_name,
                            num_pts=3,
                            script=[("rot", rotation, ("mult", scale, ("dir", src, ("get","%s.base_bezier"%bone_to_extend)))),
                                    ("pt",   src, ("get","%s.base_bezier"%bone_to_extend)),
                                    ("dup"),
                                    ("set", "%s.base_0"%bone_name), ("pop"),
                                    ("add"), ("set", "%s.base_2"%bone_name), ("pop"),
                                    ("set", "%s.base_1"%bone_name, ("mult", 0.5, ("add", ("get", "%s.base_0"%bone_name), ("get", "%s.base_2"%bone_name)))),
                                    ] )

#f bezier4_script
def bezier4_script( bone_name, pts ):
    script = []
    for i in range(len(pts)):
        pt = pts[i]
        if len(pts[i])==2:
            script.append( ("pt", pt[1], ("get", "%s.base_bezier"%pt[0])) )
            pass
        else:
            script.extend( script_bez_vec( "%s.base_bezier"%pt[0], t=pt[1], scale=pt[2], rotation=pt[3] ) )
            pass
        script.extend( [ ("set", "%s.base_%d"%(bone_name,i)), "pop" ] )
        pass
    return script

#a Test stuff
def main():
    pass

#a Toplevel
if __name__ == '__main__':
    main()
