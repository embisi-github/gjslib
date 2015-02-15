#a Imports
import gjslib.graphics.bone as bones
from gjslib.math.bezier import c_point

#a Test stuff
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

    bone_1 = bones.add_bezier_bone( ship, "bone1", num_pts=3, script = [ ("mult", ("get","size"), ("mult", 0.5, ("get","direction"))),
                                                                   ("dup"),
                                                                   ("set", "bone1.base_0", ("add", ("get","anchor_point"))), ("pop"),
                                                                   ("neg"),
                                                                   ("set", "bone1.base_2", ("add", ("get","anchor_point"))), ("pop"),
                                                                   ("set", "bone1.base_1", ("mult", 0.5, ("add", ("get", "bone1.base_0"), ("get", "bone1.base_2")))),
                                                                   ] )
    bone2 = bones.add_extend_bone( ship, "bone2", "bone1", scale=-0.95, rotation= 0.0, src=0.0 )
    bone3 = bones.add_extend_bone( ship, "bone3", "bone2", scale=0.5,  rotation= 0.0, src=1.0 )
    bone4 = bones.add_extend_bone( ship, "bone4", "bone1", scale=0.5,  rotation= 0.0, src=1.0 )
    bone5 = bones.add_extend_bone( ship, "bone5", "bone2", scale= 0.45, rotation= bone_angles["mid_t"], src=1.0 )
    bone6 = bones.add_extend_bone( ship, "bone6", "bone2", scale= 0.45, rotation=-bone_angles["mid_t"], src=1.0 )
    bone7 = bones.add_extend_bone( ship, "bone7", "bone1", scale=-0.8, rotation= bone_angles["mid_m"], src=0.0 )
    bone8 = bones.add_extend_bone( ship, "bone8", "bone1", scale=-0.8, rotation=-bone_angles["mid_m"], src=0.0 )
    bone9 = bones.add_extend_bone( ship, "bone9", "bone1", scale= 0.7, rotation=-bone_angles["mid_b"], src=1.0 )
    bone10 =bones.add_extend_bone( ship, "bone10","bone1", scale= 0.7, rotation= bone_angles["mid_b"], src=1.0 )
    bone11= bones.add_extend_bone( ship, "bone11","bone4", scale= 0.5, rotation=-bone_angles["base"], src=1.0 )
    bone12= bones.add_extend_bone( ship, "bone12","bone4", scale= 0.5, rotation= bone_angles["base"], src=1.0 )
    bone13= bones.add_bezier_bone( ship, "bone13", num_pts=4, script= bones.bezier4_script( "bone13", ( ("bone9",1.0),
                                                                                             ("bone9",1.0,0.5,180-skin_angles["mid_b"]),
                                                                                             ("bone11",1.0,0.5,   -skin_angles["bottom"]),
                                                                                             ("bone11",1.0) ) ) )
    bone14= bones.add_extend_bone( ship, "bone14","bone13", scale=-0.6, rotation=bone_angles["fin_t"], src=0.2 )
    bone15= bones.add_extend_bone( ship, "bone15","bone14", scale=-0.8, rotation=bone_angles["fin_b"]-180.0, src=1.0 )
    bone16= bones.add_bezier_bone( ship, "bone16", num_pts=4, script= bones.bezier4_script( "bone16", ( ("bone10",1.0),
                                                                                             ("bone10",1.0,0.5,  -180+skin_angles["mid_b"]),
                                                                                             ("bone12",1.0,0.5, skin_angles["bottom"]),
                                                                                             ("bone12",1.0) ) ) )
    bone17= bones.add_extend_bone( ship, "bone17","bone16", scale=-0.6, rotation=-bone_angles["fin_t"], src=0.2 )
    bone18= bones.add_extend_bone( ship, "bone18","bone17", scale=-0.8, rotation=180.0-bone_angles["fin_b"], src=1.0 )

    skin1 = bones.add_bezier_bone( ship, "skin1", num_pts=4, script= bones.bezier4_script( "skin1", ( ("bone12",1.0),
                                                                                           ("bone12",1.0,0.4, 180+skin_angles["jet"]),
                                                                                           ("bone11",1.0,0.4, 180-skin_angles["jet"]),
                                                                                           ("bone11",1.0) ) ) )
    skin2 = bones.add_bezier_bone( ship, "skin2", num_pts=4, script= bones.bezier4_script( "skin2", ( ("bone9",1.0),
                                                                                           ("bone9",1.0,0.5, 180-skin_angles["mid_b"]),
                                                                                           ("bone11",1.0,0.5, -skin_angles["bottom"]),
                                                                                           ("bone11",1.0) ) ) )
    skin3 = bones.add_bezier_bone( ship, "skin3", num_pts=4, script= bones.bezier4_script( "skin3", ( ("bone10",1.0),
                                                                                           ("bone10",1.0,0.5, -180+skin_angles["mid_b"]),
                                                                                           ("bone12",1.0,0.5, skin_angles["bottom"]),
                                                                                           ("bone12",1.0) ) ) )
    skin4 = bones.add_bezier_bone( ship, "skin4", num_pts=4, script= bones.bezier4_script( "skin4", ( ("bone9",1.0),
                                                                                           ("bone9",1.0,-0.5, 180-skin_angles["mid_b"]),
                                                                                           ("bone7",1.0,0.5, skin_angles["mid_m"]),
                                                                                           ("bone7",1.0) ) ) )
    skin5 = bones.add_bezier_bone( ship, "skin5", num_pts=4, script= bones.bezier4_script( "skin5", ( ("bone10",1.0),
                                                                                           ("bone10",1.0,0.5, skin_angles["mid_b"]),
                                                                                           ("bone8",1.0,-0.5, 180-skin_angles["mid_m"]),
                                                                                           ("bone8",1.0) ) ) )
    skin6 = bones.add_bezier_bone( ship, "skin6", num_pts=4, script= bones.bezier4_script( "skin6", ( ("bone7",1.0),
                                                                                           ("bone7",1.0,-0.5, skin_angles["mid_m"]),
                                                                                           ("bone5",1.0,0.5, 180-skin_angles["mid_t"]),
                                                                                           ("bone5",1.0) ) ) )
    skin7 = bones.add_bezier_bone( ship, "skin7", num_pts=4, script= bones.bezier4_script( "skin7", ( ("bone8",1.0),
                                                                                           ("bone8",1.0, 0.5, 180-skin_angles["mid_m"]),
                                                                                           ("bone6",1.0,-0.5, skin_angles["mid_t"]),
                                                                                           ("bone6",1.0) ) ) )
    skin8 = bones.add_bezier_bone( ship, "skin8", num_pts=4, script= bones.bezier4_script( "skin8", ( ("bone5",1.0),
                                                                                           ("bone5",1.0,-0.5, 180-skin_angles["mid_t"]),
                                                                                           ("bone3",1.0,0.3, 90+skin_angles["top"]),
                                                                                           ("bone3",1.0) ) ) )
    skin9 = bones.add_bezier_bone( ship, "skin9", num_pts=4, script= bones.bezier4_script( "skin9", ( ("bone6",1.0),
                                                                                           ("bone6",1.0,0.5, skin_angles["mid_t"]),
                                                                                           ("bone3",1.0,0.3, 270-skin_angles["top"]),
                                                                                           ("bone3",1.0) ) ) )

    leg1skin1 = bones.add_bezier_bone( ship, "leg1skin1", num_pts=4, script= bones.bezier4_script( "leg1skin1", ( ("skin2",0.75),
                                                                                                      ("bone14",0.50,0.4, 90.0),
                                                                                                      ("bone15",0.30,0.4, 90.0),
                                                                                                      ("bone15",1.0) ) ) )
    leg1skin2 = bones.add_bezier_bone( ship, "leg1skin2", num_pts=4, script= bones.bezier4_script( "leg1skin2", ( ("skin4",0.45),
                                                                                                      ("bone14",0.50,-0.4, 90.0),
                                                                                                      ("bone15",0.30,-0.4, 90.0),
                                                                                                      ("bone15",1.0) ) ) )
    leg2skin1 = bones.add_bezier_bone( ship, "leg2skin1", num_pts=4, script= bones.bezier4_script( "leg2skin1", ( ("skin3",0.75),
                                                                                                      ("bone17",0.50,-0.4, 90.0),
                                                                                                      ("bone18",0.30,-0.4, 90.0),
                                                                                                      ("bone18",1.0) ) ) )
    leg2skin2 = bones.add_bezier_bone( ship, "leg2skin2", num_pts=4, script= bones.bezier4_script( "leg2skin2", ( ("skin5",0.45),
                                                                                                      ("bone17",0.50,0.4, 90.0),
                                                                                                      ("bone18",0.30,0.4, 90.0),
                                                                                                      ("bone18",1.0) ) ) )

    decring1 = bones.add_bezier_bone( ship, "decring1", num_pts=4, script= bones.bezier4_script( "decring1", ( ("skin6",0.8),
                                                                                                      ("bone2",0.9),
                                                                                                      ("bone2",0.9),
                                                                                                      ("skin7",0.8) ) ) )

    decring2 = bones.add_bezier_bone( ship, "decring2", num_pts=4, script= bones.bezier4_script( "decring2", ( ("skin6",0.0),
                                                                                                      ("bone2",0.05),
                                                                                                      ("bone2",0.05),
                                                                                                      ("skin7",0.0) ) ) )

    decwind0 = bones.add_bezier_bone( ship, "decwind0", num_pts=4, script= bones.bezier4_script( "decwind0", ( ("decring2",0.2,0.08,90.0),
                                                                                                   ("decring2",0.3,0.08,90.0),
                                                                                                   ("decring2",0.5,0.1,90.0),
                                                                                                   ("decring2",0.6,0.1,90.0) ) ) )

    decwind1 = bones.add_bezier_bone( ship, "decwind1", num_pts=4, script= bones.bezier4_script( "decwind1", ( ("decwind0",0.0),
                                                                                                   ("decwind0",0.0,1.17,90.0),
                                                                                                   ("decwind0",0.0,1.17,90.0),
                                                                                                   ("decwind0",0.5,1.0,90.0) ) ) )

    decwind2 = bones.add_bezier_bone( ship, "decwind2", num_pts=4, script= bones.bezier4_script( "decwind2", ( ("decwind0",1.0),
                                                                                                   ("decwind0",1.0,1.5,90.0),
                                                                                                   ("decwind0",1.0,1.5,90.0),
                                                                                                   ("decwind0",0.5,1.0,90.0) ) ) )

    decring3 = bones.add_bezier_bone( ship, "decring3", num_pts=4, script= bones.bezier4_script( "decring3", ( ("skin4",0.3),
                                                                                                      ("bone1",0.9),
                                                                                                      ("bone1",0.9),
                                                                                                      ("skin5",0.3) ) ) )

    decdoor0 = bones.add_bezier_bone( ship, "decdoor0", num_pts=4, script= bones.bezier4_script( "decdoor0", ( ("decring3",0.65),
                                                                                                   ("decring3",0.6,0.4,90),
                                                                                                   ("decring3",0.95,0.4,90),
                                                                                                   ("decring3",0.9) ) ) )

    return ship

