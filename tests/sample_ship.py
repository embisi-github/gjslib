#a Imports
import bone_test as bones
from gjslib.math.bezier import c_point

#a Functions
def add_bezier_bone( parent, bone_name, script, num_pts=3 ):
    bone     = bones.c_bone( bone_name, parent=parent )
    bez_pts = []
    for i in range(num_pts):
        bez_pts.append( bone.add_child( bones.c_bone_var("base_%d"%i, "vector") ) )
        pass
    bone_bez = bone.add_child( bones.c_bone_var("base_bezier", "bezier") )
    bone.add_expression( id="script", scope=parent, script=script )
    bone.evaluate_expressions( ("script",) )
    bone_bez.set( bez_pts )
    return bone

def script_bez_vec( bezier_name, t=0.0, rotation=0.0, scale=0.0 ):
    return [("add",
             ("pt", t, ("get",bezier_name)),
             ("rot", rotation, ("mult", scale, ("dir", t, ("get",bezier_name)))))]

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

#a Test stuff
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

def build_ship():
    skin_angles = { "jet":10.0, "bottom":70.0, "mid_b":65.0, "mid_m":85.0, "mid_t":115.0, "top":20.0 }
    bone_angles = { "base":60.0, "mid_b":80.0, "mid_m":80.0, "mid_t":80.0, "fin_t":80.0, "fin_b":40.0 }
    for b in bone_angles:
        import random
        bone_angles[b] += random.random()*5
    for s in skin_angles:
        import random
        skin_angles[b] += random.random()*5
    ship = bones.c_bone_group("ship")
    ship.add_child( bones.c_bone_var("anchor_point", "vector") )
    ship.add_child( bones.c_bone_var("direction", "vector") )
    ship.add_child( bones.c_bone_var("size", "scalar") )

    null_point = c_point((0.0,0.0))
    ship.set_node( "anchor_point", c_point((0.0,0.0)) )
    ship.set_node( "direction", c_point((0.0,1.0)) )
    ship.set_node( "size", 5.0 )

    bone_1 = add_bezier_bone( ship, "bone1", num_pts=3, script = [ ("mult", ("get","size"), ("mult", 0.5, ("get","direction"))),
                                                                   ("dup"),
                                                                   ("set", "bone1.base_0", ("add", ("get","anchor_point"))), ("pop"),
                                                                   ("neg"),
                                                                   ("set", "bone1.base_2", ("add", ("get","anchor_point"))), ("pop"),
                                                                   ("set", "bone1.base_1", ("mult", 0.5, ("add", ("get", "bone1.base_0"), ("get", "bone1.base_2")))),
                                                                   ] )
    bone2 = add_extend_bone( ship, "bone2", "bone1", scale=-0.95, rotation= 0.0, src=0.0 )
    bone3 = add_extend_bone( ship, "bone3", "bone2", scale=0.5,  rotation= 0.0, src=1.0 )
    bone4 = add_extend_bone( ship, "bone4", "bone1", scale=0.5,  rotation= 0.0, src=1.0 )
    bone5 = add_extend_bone( ship, "bone5", "bone2", scale= 0.45, rotation= bone_angles["mid_t"], src=1.0 )
    bone6 = add_extend_bone( ship, "bone6", "bone2", scale= 0.45, rotation=-bone_angles["mid_t"], src=1.0 )
    bone7 = add_extend_bone( ship, "bone7", "bone1", scale=-0.8, rotation= bone_angles["mid_m"], src=0.0 )
    bone8 = add_extend_bone( ship, "bone8", "bone1", scale=-0.8, rotation=-bone_angles["mid_m"], src=0.0 )
    bone9 = add_extend_bone( ship, "bone9", "bone1", scale= 0.7, rotation=-bone_angles["mid_b"], src=1.0 )
    bone10 =add_extend_bone( ship, "bone10","bone1", scale= 0.7, rotation= bone_angles["mid_b"], src=1.0 )
    bone11= add_extend_bone( ship, "bone11","bone4", scale= 0.5, rotation=-bone_angles["base"], src=1.0 )
    bone12= add_extend_bone( ship, "bone12","bone4", scale= 0.5, rotation= bone_angles["base"], src=1.0 )
    bone13= add_bezier_bone( ship, "bone13", num_pts=4, script= bezier4_script( "bone13", ( ("bone9",1.0),
                                                                                             ("bone9",1.0,0.5,180-skin_angles["mid_b"]),
                                                                                             ("bone11",1.0,0.5,   -skin_angles["bottom"]),
                                                                                             ("bone11",1.0) ) ) )
    bone14= add_extend_bone( ship, "bone14","bone13", scale=-0.6, rotation=bone_angles["fin_t"], src=0.2 )
    bone15= add_extend_bone( ship, "bone15","bone14", scale=-0.8, rotation=bone_angles["fin_b"]-180.0, src=1.0 )
    bone16= add_bezier_bone( ship, "bone16", num_pts=4, script= bezier4_script( "bone16", ( ("bone10",1.0),
                                                                                             ("bone10",1.0,0.5,  -180+skin_angles["mid_b"]),
                                                                                             ("bone12",1.0,0.5, skin_angles["bottom"]),
                                                                                             ("bone12",1.0) ) ) )
    bone17= add_extend_bone( ship, "bone17","bone16", scale=-0.6, rotation=-bone_angles["fin_t"], src=0.2 )
    bone18= add_extend_bone( ship, "bone18","bone17", scale=-0.8, rotation=180.0-bone_angles["fin_b"], src=1.0 )

    skin1 = add_bezier_bone( ship, "skin1", num_pts=4, script= bezier4_script( "skin1", ( ("bone12",1.0),
                                                                                           ("bone12",1.0,0.4, 180+skin_angles["jet"]),
                                                                                           ("bone11",1.0,0.4, 180-skin_angles["jet"]),
                                                                                           ("bone11",1.0) ) ) )
    skin2 = add_bezier_bone( ship, "skin2", num_pts=4, script= bezier4_script( "skin2", ( ("bone9",1.0),
                                                                                           ("bone9",1.0,0.5, 180-skin_angles["mid_b"]),
                                                                                           ("bone11",1.0,0.5, -skin_angles["bottom"]),
                                                                                           ("bone11",1.0) ) ) )
    skin3 = add_bezier_bone( ship, "skin3", num_pts=4, script= bezier4_script( "skin3", ( ("bone10",1.0),
                                                                                           ("bone10",1.0,0.5, -180+skin_angles["mid_b"]),
                                                                                           ("bone12",1.0,0.5, skin_angles["bottom"]),
                                                                                           ("bone12",1.0) ) ) )
    skin4 = add_bezier_bone( ship, "skin4", num_pts=4, script= bezier4_script( "skin4", ( ("bone9",1.0),
                                                                                           ("bone9",1.0,-0.5, 180-skin_angles["mid_b"]),
                                                                                           ("bone7",1.0,0.5, skin_angles["mid_m"]),
                                                                                           ("bone7",1.0) ) ) )
    skin5 = add_bezier_bone( ship, "skin5", num_pts=4, script= bezier4_script( "skin5", ( ("bone10",1.0),
                                                                                           ("bone10",1.0,0.5, skin_angles["mid_b"]),
                                                                                           ("bone8",1.0,-0.5, 180-skin_angles["mid_m"]),
                                                                                           ("bone8",1.0) ) ) )
    skin6 = add_bezier_bone( ship, "skin6", num_pts=4, script= bezier4_script( "skin6", ( ("bone7",1.0),
                                                                                           ("bone7",1.0,-0.5, skin_angles["mid_m"]),
                                                                                           ("bone5",1.0,0.5, 180-skin_angles["mid_t"]),
                                                                                           ("bone5",1.0) ) ) )
    skin7 = add_bezier_bone( ship, "skin7", num_pts=4, script= bezier4_script( "skin7", ( ("bone8",1.0),
                                                                                           ("bone8",1.0, 0.5, 180-skin_angles["mid_m"]),
                                                                                           ("bone6",1.0,-0.5, skin_angles["mid_t"]),
                                                                                           ("bone6",1.0) ) ) )
    skin8 = add_bezier_bone( ship, "skin8", num_pts=4, script= bezier4_script( "skin8", ( ("bone5",1.0),
                                                                                           ("bone5",1.0,-0.5, 180-skin_angles["mid_t"]),
                                                                                           ("bone3",1.0,0.3, 90+skin_angles["top"]),
                                                                                           ("bone3",1.0) ) ) )
    skin9 = add_bezier_bone( ship, "skin9", num_pts=4, script= bezier4_script( "skin9", ( ("bone6",1.0),
                                                                                           ("bone6",1.0,0.5, skin_angles["mid_t"]),
                                                                                           ("bone3",1.0,0.3, 270-skin_angles["top"]),
                                                                                           ("bone3",1.0) ) ) )

    leg1skin1 = add_bezier_bone( ship, "leg1skin1", num_pts=4, script= bezier4_script( "leg1skin1", ( ("skin2",0.75),
                                                                                                      ("bone14",0.50,0.4, 90.0),
                                                                                                      ("bone15",0.30,0.4, 90.0),
                                                                                                      ("bone15",1.0) ) ) )
    leg1skin2 = add_bezier_bone( ship, "leg1skin2", num_pts=4, script= bezier4_script( "leg1skin2", ( ("skin4",0.45),
                                                                                                      ("bone14",0.50,-0.4, 90.0),
                                                                                                      ("bone15",0.30,-0.4, 90.0),
                                                                                                      ("bone15",1.0) ) ) )
    leg2skin1 = add_bezier_bone( ship, "leg2skin1", num_pts=4, script= bezier4_script( "leg2skin1", ( ("skin3",0.75),
                                                                                                      ("bone17",0.50,-0.4, 90.0),
                                                                                                      ("bone18",0.30,-0.4, 90.0),
                                                                                                      ("bone18",1.0) ) ) )
    leg2skin2 = add_bezier_bone( ship, "leg2skin2", num_pts=4, script= bezier4_script( "leg2skin2", ( ("skin5",0.45),
                                                                                                      ("bone17",0.50,0.4, 90.0),
                                                                                                      ("bone18",0.30,0.4, 90.0),
                                                                                                      ("bone18",1.0) ) ) )

    decring1 = add_bezier_bone( ship, "decring1", num_pts=4, script= bezier4_script( "decring1", ( ("skin6",0.8),
                                                                                                      ("bone2",0.9),
                                                                                                      ("bone2",0.9),
                                                                                                      ("skin7",0.8) ) ) )

    decring2 = add_bezier_bone( ship, "decring2", num_pts=4, script= bezier4_script( "decring2", ( ("skin6",0.0),
                                                                                                      ("bone2",0.05),
                                                                                                      ("bone2",0.05),
                                                                                                      ("skin7",0.0) ) ) )

    decwind0 = add_bezier_bone( ship, "decwind0", num_pts=4, script= bezier4_script( "decwind0", ( ("decring2",0.2,0.08,90.0),
                                                                                                   ("decring2",0.3,0.08,90.0),
                                                                                                   ("decring2",0.5,0.1,90.0),
                                                                                                   ("decring2",0.6,0.1,90.0) ) ) )

    decwind1 = add_bezier_bone( ship, "decwind1", num_pts=4, script= bezier4_script( "decwind1", ( ("decwind0",0.0),
                                                                                                   ("decwind0",0.0,1.17,90.0),
                                                                                                   ("decwind0",0.0,1.17,90.0),
                                                                                                   ("decwind0",0.5,1.0,90.0) ) ) )

    decwind2 = add_bezier_bone( ship, "decwind2", num_pts=4, script= bezier4_script( "decwind2", ( ("decwind0",1.0),
                                                                                                   ("decwind0",1.0,1.5,90.0),
                                                                                                   ("decwind0",1.0,1.5,90.0),
                                                                                                   ("decwind0",0.5,1.0,90.0) ) ) )

    decring3 = add_bezier_bone( ship, "decring3", num_pts=4, script= bezier4_script( "decring3", ( ("skin4",0.3),
                                                                                                      ("bone1",0.9),
                                                                                                      ("bone1",0.9),
                                                                                                      ("skin5",0.3) ) ) )

    decdoor0 = add_bezier_bone( ship, "decdoor0", num_pts=4, script= bezier4_script( "decdoor0", ( ("decring3",0.65),
                                                                                                   ("decring3",0.6,0.4,90),
                                                                                                   ("decring3",0.95,0.4,90),
                                                                                                   ("decring3",0.9) ) ) )

    return ship

