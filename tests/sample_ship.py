#a Imports
import gjslib.graphics.bone as bones
from gjslib.math.bezier import c_point

#a Test stuff
def build_ship():
    skin_angles = { "jet":10.0, "bottom":70.0, "mid_b":65.0, "mid_m":85.0, "mid_t":115.0, "top":20.0 }
    bone_angles = { "base":60.0, "mid_b":80.0, "mid_m":80.0, "mid_t":80.0, "fin_t":80.0, "fin_b":40.0 }
    for b in bone_angles:
        import random
        bone_angles[b] += random.random()*5*0
    for s in skin_angles:
        import random
        skin_angles[b] += random.random()*5*0
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
    bone13= bones.add_bezier_bone( ship, "bone13", num_pts=4, script= bones.bezier4_script( ( ("bone9",1.0),
                                                                                             ("bone9",1.0,0.5,180-skin_angles["mid_b"]),
                                                                                             ("bone11",1.0,0.5,   -skin_angles["bottom"]),
                                                                                             ("bone11",1.0) ) ) )
    bone14= bones.add_extend_bone( ship, "bone14","bone13", scale=-0.6, rotation=bone_angles["fin_t"], src=0.2 )
    bone15= bones.add_extend_bone( ship, "bone15","bone14", scale=-0.8, rotation=bone_angles["fin_b"]-180.0, src=1.0 )
    bone16= bones.add_bezier_bone( ship, "bone16", num_pts=4, script= bones.bezier4_script( ( ("bone10",1.0),
                                                                                             ("bone10",1.0,0.5,  -180+skin_angles["mid_b"]),
                                                                                             ("bone12",1.0,0.5, skin_angles["bottom"]),
                                                                                             ("bone12",1.0) ) ) )
    bone17= bones.add_extend_bone( ship, "bone17","bone16", scale=-0.6, rotation=-bone_angles["fin_t"], src=0.2 )
    bone18= bones.add_extend_bone( ship, "bone18","bone17", scale=-0.8, rotation=180.0-bone_angles["fin_b"], src=1.0 )

    ship_plane = ship.add_child(bones.c_bone_plane("ship_plane"))
    ship_skin = ship_plane.add_child(bones.c_bone_drawable("ship_skin",fill=(255,150,120), stroke=(0,0,0) ))
    skin1 = bones.add_bezier_bone( ship_skin, "skin1", num_pts=4, scope=ship, script= bones.bezier4_script( ( ("bone12",1.0),
                                                                                           ("bone12",1.0,0.4, 180+skin_angles["jet"]),
                                                                                           ("bone11",1.0,0.4, 180-skin_angles["jet"]),
                                                                                           ("bone11",1.0) ) ) )
    skin2 = bones.add_bezier_bone( ship_skin, "skin2", num_pts=4, scope=ship, script= bones.bezier4_script( ( ("bone9",1.0),
                                                                                           ("bone9",1.0,0.5, 180-skin_angles["mid_b"]),
                                                                                           ("bone11",1.0,0.5, -skin_angles["bottom"]),
                                                                                           ("bone11",1.0) ) ) )
    skin3 = bones.add_bezier_bone( ship_skin, "skin3", num_pts=4, scope=ship, script= bones.bezier4_script( ( ("bone10",1.0),
                                                                                           ("bone10",1.0,0.5, -180+skin_angles["mid_b"]),
                                                                                           ("bone12",1.0,0.5, skin_angles["bottom"]),
                                                                                           ("bone12",1.0) ) ) )
    skin4 = bones.add_bezier_bone( ship_skin, "skin4", num_pts=4, scope=ship, script= bones.bezier4_script( ( ("bone9",1.0),
                                                                                           ("bone9",1.0,-0.5, 180-skin_angles["mid_b"]),
                                                                                           ("bone7",1.0,0.5, skin_angles["mid_m"]),
                                                                                           ("bone7",1.0) ) ) )
    skin5 = bones.add_bezier_bone( ship_skin, "skin5", num_pts=4, scope=ship, script= bones.bezier4_script( ( ("bone10",1.0),
                                                                                           ("bone10",1.0,0.5, skin_angles["mid_b"]),
                                                                                           ("bone8",1.0,-0.5, 180-skin_angles["mid_m"]),
                                                                                           ("bone8",1.0) ) ) )
    skin6 = bones.add_bezier_bone( ship_skin, "skin6", num_pts=4, scope=ship, script= bones.bezier4_script( ( ("bone7",1.0),
                                                                                           ("bone7",1.0,-0.5, skin_angles["mid_m"]),
                                                                                           ("bone5",1.0,0.5, 180-skin_angles["mid_t"]),
                                                                                           ("bone5",1.0) ) ) )
    skin7 = bones.add_bezier_bone( ship_skin, "skin7", num_pts=4, scope=ship, script= bones.bezier4_script( ( ("bone8",1.0),
                                                                                           ("bone8",1.0, 0.5, 180-skin_angles["mid_m"]),
                                                                                           ("bone6",1.0,-0.5, skin_angles["mid_t"]),
                                                                                           ("bone6",1.0) ) ) )
    skin8 = bones.add_bezier_bone( ship_skin, "skin8", num_pts=4, scope=ship, script= bones.bezier4_script( ( ("bone5",1.0),
                                                                                           ("bone5",1.0,-0.5, 180-skin_angles["mid_t"]),
                                                                                           ("bone3",1.0,0.3, 90+skin_angles["top"]),
                                                                                           ("bone3",1.0) ) ) )
    skin9 = bones.add_bezier_bone( ship_skin, "skin9", num_pts=4, scope=ship, script= bones.bezier4_script( ( ("bone6",1.0),
                                                                                           ("bone6",1.0,0.5, skin_angles["mid_t"]),
                                                                                           ("bone3",1.0,0.3, 270-skin_angles["top"]),
                                                                                           ("bone3",1.0) ) ) )
    ship_skin.add_child(bones.c_bone_ref("sk1", skin1, opts={"start":0.0,"end":1.0}))
    ship_skin.add_child(bones.c_bone_ref("sk2", skin2, opts={"start":1.0,"end":0.0}))
    ship_skin.add_child(bones.c_bone_ref("sk4", skin4, opts={"start":0.0,"end":1.0}))
    ship_skin.add_child(bones.c_bone_ref("sk6", skin6, opts={"start":0.0,"end":1.0}))
    ship_skin.add_child(bones.c_bone_ref("sk8", skin8, opts={"start":0.0,"end":1.0}))
    ship_skin.add_child(bones.c_bone_ref("sk9", skin9, opts={"start":1.0,"end":0.0}))
    ship_skin.add_child(bones.c_bone_ref("sk7", skin7, opts={"start":1.0,"end":0.0}))
    ship_skin.add_child(bones.c_bone_ref("sk5", skin5, opts={"start":1.0,"end":0.0}))
    ship_skin.add_child(bones.c_bone_ref("sk3", skin3, opts={"start":0.0,"end":1.0}))

    leg1_plane = ship.add_child(bones.c_bone_plane("leg1_plane",depth=10))
    leg1_skin = leg1_plane.add_child(bones.c_bone_drawable("leg1_skin",fill=(255,200,200), stroke=(0,0,0) ))
    leg1skin1 = bones.add_bezier_bone( leg1_skin, "leg1skin1", num_pts=4, scope=(ship_skin,ship), script= bones.bezier4_script( ( ("skin2",0.75),
                                                                                                      ("bone14",0.50,0.4, 90.0),
                                                                                                      ("bone15",0.30,0.4, 90.0),
                                                                                                      ("bone15",1.0) ) ) )
    leg1skin2 = bones.add_bezier_bone( leg1_skin, "leg1skin2", num_pts=4, scope=(ship_skin,ship), script= bones.bezier4_script( ( ("skin4",0.45),
                                                                                                      ("bone14",0.50,-0.4, 90.0),
                                                                                                      ("bone15",0.30,-0.4, 90.0),
                                                                                                      ("bone15",1.0) ) ) )
    leg1_skin.add_child(bones.c_bone_ref("ls1", leg1skin1, opts={"start":1.0,"end":0.0}))
    leg1_skin.add_child(bones.c_bone_ref("ls2", leg1skin2, opts={"start":0.0,"end":1.0}))

    leg2_plane = ship.add_child(bones.c_bone_plane("leg2_plane", depth=10))
    leg2_skin = leg2_plane.add_child(bones.c_bone_drawable("leg2_skin",fill=(255,200,200), stroke=(0,0,0) ))
    leg2skin1 = bones.add_bezier_bone( leg2_skin, "leg2skin1", num_pts=4, scope=(ship_skin,ship), script= bones.bezier4_script( ( ("skin3",0.75),
                                                                                                      ("bone17",0.50,-0.4, 90.0),
                                                                                                      ("bone18",0.30,-0.4, 90.0),
                                                                                                      ("bone18",1.0) ) ) )
    leg2skin2 = bones.add_bezier_bone( leg2_skin, "leg2skin2", num_pts=4, scope=(ship_skin,ship), script= bones.bezier4_script( ( ("skin5",0.45),
                                                                                                      ("bone17",0.50,0.4, 90.0),
                                                                                                      ("bone18",0.30,0.4, 90.0),
                                                                                                      ("bone18",1.0) ) ) )

    leg2_skin.add_child(bones.c_bone_ref("ls1", leg2skin1, opts={"start":1.0,"end":0.0}))
    leg2_skin.add_child(bones.c_bone_ref("ls2", leg2skin2, opts={"start":0.0,"end":1.0}))

    decring1 = bones.add_bezier_bone( ship_skin, "decring1", num_pts=4, scope=(ship_skin,ship), script= bones.bezier4_script( ( ("skin6",0.8),
                                                                                                      ("bone2",0.9),
                                                                                                      ("bone2",0.9),
                                                                                                      ("skin7",0.8) ) ) )

    decring2 = bones.add_bezier_bone( ship_skin, "decring2", num_pts=4, scope=(ship_skin,ship), script= bones.bezier4_script( ( ("skin6",0.0),
                                                                                                      ("bone2",0.05),
                                                                                                      ("bone2",0.05),
                                                                                                      ("skin7",0.0) ) ) )

    decwind0 = bones.add_bezier_bone( ship_skin, "decwind0", num_pts=4, scope=(ship_skin,ship), script= bones.bezier4_script( ( ("decring2",0.2,0.08,90.0),
                                                                                                   ("decring2",0.3,0.08,90.0),
                                                                                                   ("decring2",0.5,0.1,90.0),
                                                                                                   ("decring2",0.6,0.1,90.0) ) ) )

    decwind1 = bones.add_bezier_bone( ship_skin, "decwind1", num_pts=4, scope=(ship_skin,ship), script= bones.bezier4_script( ( ("decwind0",0.0),
                                                                                                   ("decwind0",0.0,1.17,90.0),
                                                                                                   ("decwind0",0.0,1.17,90.0),
                                                                                                   ("decwind0",0.5,1.0,90.0) ) ) )

    decwind2 = bones.add_bezier_bone( ship_skin, "decwind2", num_pts=4, scope=(ship_skin,ship), script= bones.bezier4_script( ( ("decwind0",1.0),
                                                                                                   ("decwind0",1.0,1.5,90.0),
                                                                                                   ("decwind0",1.0,1.5,90.0),
                                                                                                   ("decwind0",0.5,1.0,90.0) ) ) )

    decring3 = bones.add_bezier_bone( ship_skin, "decring3", num_pts=4, scope=(ship_skin,ship), script= bones.bezier4_script( ( ("skin4",0.3),
                                                                                                      ("bone1",0.9),
                                                                                                      ("bone1",0.9),
                                                                                                      ("skin5",0.3) ) ) )

    decdoor0 = bones.add_bezier_bone( ship_skin, "decdoor0", num_pts=4, scope=(ship_skin,ship), script= bones.bezier4_script( ( ("decring3",0.65),
                                                                                                   ("decring3",0.6,0.4,90),
                                                                                                   ("decring3",0.95,0.4,90),
                                                                                                   ("decring3",0.9) ) ) )

    decorations = ship.add_child(bones.c_bone_plane("decorations", depth=-10))
    decring1_d   = decorations.add_child(bones.c_bone_drawable("dec_ring1", stroke=(0,0,0) ))
    decring1_d.add_child(bones.c_bone_ref("r1", decring1, opts={"start":0.0,"end":1.0}))
    decring2_d   = decorations.add_child(bones.c_bone_drawable("dec_ring2", stroke=(0,0,0) ))
    decring2_d.add_child(bones.c_bone_ref("r2", decring2, opts={"start":0.0,"end":1.0}))
    decring3_d   = decorations.add_child(bones.c_bone_drawable("dec_ring3", stroke=(0,0,0) ))
    decring3_d.add_child(bones.c_bone_ref("r3", decring3, opts={"start":0.0,"end":1.0}))
    decwin_d   = decorations.add_child(bones.c_bone_drawable("dec_win", fill=(255,255,200),stroke=(0,0,0) ))
    decwin_d.add_child(bones.c_bone_ref("w0", decwind0, opts={"start":1.0,"end":0.0}))
    decwin_d.add_child(bones.c_bone_ref("w1", decwind1, opts={"start":0.0,"end":1.0}))
    decwin_d.add_child(bones.c_bone_ref("w2", decwind2, opts={"start":1.0,"end":0.0}))
    decdoor_d   = decorations.add_child(bones.c_bone_drawable("dec_door", stroke=(0,0,0) ))
    decdoor_d.add_child(bones.c_bone_ref("d0", decdoor0, opts={"start":1.0,"end":0.0}))

    return ship

