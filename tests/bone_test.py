#!/usr/bin/arch -32 /System/Library/Frameworks/Python.framework/Versions/2.7/bin/python
#a Imports
import pygame
import sys, os

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
    pass

#c c_bone_op_set
class c_bone_op_set( c_bone_op ):
    op_string = "set"
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
        pass
    #f set
    def set( self, value ):
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
    pass

#c c_bone_type_vector
class c_bone_type_vector( c_bone_type ):
    type_name = "vector"
    #f get_coords
    def get_coords( self ):
        return self.value.get_coords()
    #f set
    def set( self, value ):
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
    #f neg
    def neg( self ):
        self.value = self.value.scale( factor=-1.0 )
        return self

#c c_bone_type_bezier
class c_bone_type_bezier( c_bone_type ):
    type_name = "bezier"
    #f set
    def set( self, vectors ):
        self.vectors = vectors
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
    #f __init__
    def __init__( self, name, parent=None, **kwargs ):
        self.name = name
        self.bone_variables = {}
        self.children = []
        self.parent = parent
        if parent is not None: parent.add_child(self)
        self.expressions = {}
        pass
    #f add_expression
    def add_expression( self, id, scope, script=None ):
        self.expressions[id] = (scope, c_bone_expr())
        if script is not None:
            self.expressions[id][1].add_script( script )
            pass
        return self.expressions[id][1]
    #f evaluate_expressions
    def evaluate_expressions( self, ids=None ):
        if ids is None: ids=self.expressions.keys()
        for id in ids:
            print "Evaluating", id, self.expressions[id]
            print self.expressions[id][1].evaluate( scope=self.expressions[id][0] )
            pass
        pass
    #f add_child
    def add_child( self, node ):
        self.children.append(node)
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
    #f __repr__
    def __repr__( self ):
        return "%s.%s"%(self.__class__.__name__,self.name)

#c c_bone_var
class c_bone_var( c_bone_base ):
    """
    A bone variable is a named calculateable value.

    It may be defined by a stack of operations which permit operations on other bone variables.
    """
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
        return self.var_instance.set(value)
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
c_bone_expr.add_op( (c_bone_op_mult, c_bone_type_vector, c_bone_type_scalar), ( c_bone_type_vector.mult_by_scalar, 0, 1 ) )
c_bone_expr.add_op( (c_bone_op_mult, c_bone_type_scalar, c_bone_type_vector), ( c_bone_type_vector.mult_by_scalar, 1, 0 ) )
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

#a Test stuff

ship = c_bone_group("ship")
ship.add_child( c_bone_var("anchor_point", "vector") )
ship.add_child( c_bone_var("direction", "vector") )
ship.add_child( c_bone_var("size", "scalar") )

from gjslib.math.bezier import c_point
null_point = c_point((0.0,0.0))
ship.set_node( "anchor_point", c_point((1.0,1.0)) )
ship.set_node( "direction", c_point((0.0,1.0)) )
ship.set_node( "size", 3.0 )

bone_1 = c_bone( "bone1", parent=ship )
base_a = bone_1.add_child( c_bone_var("base_a", "vector") )
base_b = bone_1.add_child( c_bone_var("base_b", "vector") )
base_mid = bone_1.add_child( c_bone_var("base_mid", "vector") )
bone_1_b = bone_1.add_child( c_bone_var("base_bezier", "bezier") )

bone_1.add_expression( id="base_ab", scope=ship, script= [("mult",
                                                           ("get","size"),
                                                           ("mult", 0.5, ("get","direction"))),
                                                          ("dup"),
                                                          ("set", "bone1.base_a", ("add", ("get","anchor_point"))), ("pop"),
                                                          ("neg"),
                                                          ("set", "bone1.base_b", ("add", ("get","anchor_point"))), ("pop"),
                                                          ]
                       )

bone_1.add_expression( id="base_mid", scope=bone_1, script=[ ("set", "base_mid", ("mult", 0.5, ("add", ("get", "base_a"), ("get", "base_b")))) ] )
bone_1.evaluate_expressions( ("base_ab", "base_mid") )
bone_1_b.set( (base_a,base_mid,base_b) )
bone_1.add_expression( id="bezier_notes", scope=bone_1, script=[ ("dir", ("get", "base_bezier"), 0.0),
                                                                 ("dir", ("get", "base_bezier"), 0.5),                                                                 
                                                                 ("dir", ("get", "base_bezier"), 1.0),                                                                 
                                                                 ("pt",  ("get", "base_bezier"), 0.0),                                                                 
                                                                 ("pt",  ("get", "base_bezier"), 0.5),                                                                 
                                                                 ("pt",  ("get", "base_bezier"), 1.0),
                                                                 ])

print bone_1.evaluate_expressions( ("bezier_notes",) )

# bone_1 has 'base_a' = 'anchor point' + 'size'/2*'direction'
# 'perturb_shake' = rotate(shake_angle) * size/2 * direction - size/2 * direction
# 'perturb_a' = +'pertrub_shake'
# 'perturb_b' = -'pertrub_shake'
subbone_1_1 = c_bone( "sub1", parent=bone_1 )
subbone_1_2 = c_bone( "sub2", parent=bone_1 )
