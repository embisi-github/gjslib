#a Imports
import math

#f vector_sq
def vector_sq( v ):
    return v[0]*v[0] + v[1]*v[1]

#f vector_dot_product
def vector_dot_product( v0, v1 ):
    return v0[0]*v1[0] + v0[1]*v1[1]

#f find_collision_time_circle_circle
def find_collision_time_circle_circle( p0, v0, r0, p1, v1, r1 ):
    """
    Find the time (0<t<=1) at which p0+v0 and p1+v1 reach distance r0+r1 apart

    Distance = | (p1+t.v1 - (p0+t.v0)) | = r0+r1

    (r0+r1)^2 = (p1-p0 + t*(v1-v0)) . (p1-p0 + t*(v1-v0))

    p10 = p1-p0
    v10 = v1-v0
    r10sq = (r0+r1)^2

    r10sq = (p10 + t*v10) . (p10 + t*v10) = p10^2 + t^2*v10^2 + 2*t*p10.v10

    v10^2*t^2 + 2*p10.v10*t + p10^2-r10sq = 0

    t = (-2v10.p10 +- sqrt( 4*(p10.v10)^2 - 4*v10^2*(p10^2-r10sq) ) ) / (2v10^2)

    t = (-v10.p10 +- sqrt( (p10.v10)^2 - (v10^2*(p10^2-r10sq)) ) ) / v10^2

    if ((p10.v10)^2 - (v10^2*(p10^2-r10sq)) < 0 then no collision _EVER_

    So, if 0<t<=1 and
    t = (-v10.p10 +- sqrt( (p10.v10)^2 - (v10^2*(p10^2-r10sq)) ) ) / v10^2

    [ discriminant =  (p10.v10)^2 - (v10^2*(p10^2-r10sq)) ]

    v10^2.t = sqrt( (p10.v10)^2 - (v10^2*(p10^2-r10sq)) ) - v10.p10 is from 0 to v10^2

    Example: p10 is (3,0), v10 is (-1,0), and r0=r1=1
    2^2 = ((3,0) + t*(-1,0)) . ((3,0) + t*(-1,0)) = 9 + t^2 - 6t
    Hence
    t^2 - 6t + 5 = 0
    => t = 1 or 5

    p10.v10 = -3 ; p10^2 = 9 ; r10sq = 4 ; v10^2 = 1
    discriminant = 9 - 1*(9-4) = 4
    """
    p10 = ( p1[0]-p0[0], p1[1]-p0[1] )
    v10 = ( v1[0]-v0[0], v1[1]-v0[1] )
    v10sq = vector_sq( v10 )
    if v10sq<1e-20: return None

    p10sq = vector_sq( p10 )
    r10sq = (r0+r1)*(r0+r1)
    #print p10sq, v10sq, r10sq
    p10_dot_v10 = vector_dot_product( p10, v10 )
    #print p10_dot_v10
    discriminant = p10_dot_v10*p10_dot_v10 - v10sq*(p10sq-r10sq)
    #print p10, v10
    #print "Discriminant", discriminant
    if discriminant<0: return None

    v10sq_times_t = -math.sqrt(discriminant) - p10_dot_v10
    #print "v10sq_times_t b", v10sq_times_t
    if (v10sq_times_t>0) and (v10sq_times_t<=v10sq): return v10sq_times_t/v10sq
    v10sq_times_t = math.sqrt(discriminant) - p10_dot_v10
    #print "v10sq_times_t a", v10sq_times_t
    if (v10sq_times_t>0) and (v10sq_times_t<=v10sq): return v10sq_times_t/v10sq

    return None

#c c_transform_matrix
class c_transform_matrix( object ):
    def __init__( self, a,b,c,d ):
        self.values = (a,b,c,d)
        pass
    def determinant( self ):
        return self.values[0]*self.values[3] - self.values[1]*self.values[2]
    def apply( self, x, y ):
        return ( self.values[0]*x+self.values[1]*y,
                 self.values[2]*x+self.values[3]*y )
    def scale( self, s ):
        self.values = ( self.values[0]*s,
                        self.values[1]*s,
                        self.values[2]*s,
                        self.values[3]*s,
                        )
        pass
    def __repr__( self ):
        return str(self.values)

#f find_collision_time_rectangle_corners_line
def find_collision_time_rectangle_corners_line( p, v, x, y, ls, ld ):
    """
    Find the smallest time (0<t<=1) at which corners p+v.t + -1/1.x + -1/1y hit line -1/1.ls + k.ld

    Collide at p + dx.x + dy.y + t.v = dl.ls + k.ld

    Or k.ld - t.v = p + dx.x + dy.y - dl.ls

    where dx = -1/1, dy=-1/1, dl=-1/1, -1<=k<=1, 0<t<=1

    We can solve this with:
    k.ld - t.v = | ldx  -vx | | k | = | px | + ...
                 | ldy  -vy | | t | = | py |


     (-ldx*vy + ldy*vx)| k | = |  -vy  vx || px | + ...
                       | t | = | -ldy ldx || py |


    need determinant = (ldy*vx - ldx*vy)
    and transform = 1/determinant * [ vy -vx | -ldy ldx ]
    and  p_t = transform * p, x_t = transform*x, y_t = transform*y, ls_t = transform*ls
    then determinant*t = p_tx + dx.x_tx + dy.y_tx - dl.ls_tx
    and  determinant*k = p_ty + dx.x_ty + dy.y_ty - dl.ls_ty

    If corners are (2,0)+-(0.5,0)+-(0,0.5) + (-2,0).t and line is (0.5,0)+k.(0,0.5)
    expect dx=-1,dy=1,t=0.5 we have (0.5,0.5) and k=1.

    determinant = (0.5*-2) - (0*0) = -1
    transform = [0 2 | 0.5 0]
    """
    print "Testing corners of %s+t.%s +-%s +-%s against line %s + k.%s"%(str(p),str(v),str(x),str(y),str(ls),str(ld))
    transform = c_transform_matrix( -v[1], v[0], -ld[1], ld[0] )
    determinant = transform.determinant()
    if (determinant>-1E-9) and (determinant<1E-9): return None
    transform.scale(1/determinant)

    p_t = transform.apply( p[0], p[1] )
    x_t = transform.apply( x[0], x[1] )
    y_t = transform.apply( y[0], y[1] )
    ls_t = transform.apply( ls[0], ls[1] )

    min_t = 2
    for (dx, dy, dl) in ( (-1,-1,-1), (-1,-1,1),
                                (-1,1,-1), (-1,1,-1),
                                (1,-1,-1), (1,-1,-1),
                                (1,1,-1), (1,1,-1), ):
        t = (p_t[1] + dx*x_t[1] + dy*y_t[1] - dl*ls_t[1] )
        if False:
            k = (p_t[0] + dx*x_t[0] + dy*y_t[0] + dl*ls_t[0] )
            print dx,dy,dl,t,k, (p[0]+dx*x[0]+dy*y[0]+v[0]*t, p[1]+dx*x[1]+dy*y[1]+v[1]*t), (dl*ls[0]+ld[0]*k,dl*ls[1]+ld[1]*k)
            pass
        if (t>0) and (t<=1) and (t<min_t):
            k = (p_t[0] + dx*x_t[0] + dy*y_t[0] - dl*ls_t[0] )
            if (-1<=k) and (k<=1):
                # corner 0 if dx,dy=1,1; 1 if dx,dy=-1,1; 2 if dx,dy=-1,-1, 3 if dx,dy=1,-1
                # corner n = (1-dy)+(1-dx*dy)/2
                # line 0 if dl is 1, 1 if dl is -1
                min_t = t
                pass
            pass
        pass
    if min_t>1: return None
    #print "T:",min_t
    return min_t

#f find_collision_time_rectangle_rectangle
def find_collision_time_rectangle_rectangle( p0, v0, x0, p1, v1, x1 ):
    """
    A rectangle is p0 + -1/1.x0 + -1/1.y0, where y0 = rot(90)*x0
    if x0 = (x0x, x0y) then y0 = (-x0y, x0x)

    Find the smallest time (0<t<=1) at which corners of rect0 hit lines of rect1 or vice versa

    Need to try 4 setups: 
    corners of p0+v0+ -1/1.x0 + -1/1.y0 hit lines p1+v1 + -1/1.x1 + k.y1
    corners of p0+v0+ -1/1.x0 + -1/1.y0 hit lines p1+v1 + -1/1.y1 + k.x1
    corners of p1+v1+ -1/1.x1 + -1/1.y1 hit lines p0+v0 + -1/1.x0 + k.y0
    corners of p1+v1+ -1/1.x1 + -1/1.y1 hit lines p0+v0 + -1/1.y0 + k.x0
    """
    y0 = (-x0[1], x0[0])
    y1 = (-x1[1], x1[0])
    p10 = ( p1[0]-p0[0], p1[1]-p0[1] )
    v10 = ( v1[0]-v0[0], v1[1]-v0[1] )

    min_t = 2
    t = find_collision_time_rectangle_corners_line( p10, v10, x1, y1, x0, y0 )
    if (t is not None) and (t<min_t): min_t = t
    find_collision_time_rectangle_corners_line( p10, v10, x1, y1, y0, x0 )
    if (t is not None) and (t<min_t): min_t = t
    find_collision_time_rectangle_corners_line( p10, v10, x0, y0, x1, y1 )
    if (t is not None) and (t<min_t): min_t = t
    find_collision_time_rectangle_corners_line( p10, v10, x0, y0, y1, x1 )
    if (t is not None) and (t<min_t): min_t = t

    if (min_t>1): return None
    return min_t

#f find_velocities_after_bounce
def find_velocities_after_bounce( cor, p0, v0, m0, p1, v1, m1 ):
    """
    For two colliding masses at p0/p1 with velocities v0/v1 and masses m0/m1,
    calculate the resulting velocities after the collision given a coefficient
    of restition of cor

    First find the line of collision - which is along p1-p0
    Generate unit vector p10u (and hence perpendicular p10n)
    Then resolve the velocities into components along the line of collision and perpendicular
    (cv0 = v0.p10u, pv0 = v0.p10n)
    We note then that v0 = cv0*p10 + pv0*p10n and same for v1/cv1/pv1.

    Then note that closing velocity = cv1-cv0 (which it should be clear is <0 as it reduces p1-p0)
    The post-collision closing velocity = -cor.(cv1-cv0) = ncv1-ncv0
    Also, m0.cv0+m1.cv1 = m0.ncv0 + m1.ncv1, by conservation of momentum

    Note finally that the post-collision velocity is
      nv0 = ncv0*p10u + pv0*p10n
    And hence nv0 = v0 + (ncv0-cv0) * p10u
    We can rewrite ncv0-cv0 as dcv0

    So, rewriting the momentum equation we get
      m0.ncv0 + m1.ncv1 = m0.cv0 + m1.cv1
      m0.(ncv0-cv0) + m1.(ncv1-cv1) = 0
      m1.dcv1 + m0.dcv0 = 0

    And rewriting the cor equation we get
      ncv1 - ncv0 = cor.cv0 - cor.cv1
      (ncv1-cv1) - (ncv0-cv0) = (cor+1).cv0 - (cor+1).cv1
      dcv0 - dcv1 = (cor+1).cv1 - (cor+1).cv0

    Putting into an alternate form
    | 1   -1 | (dcv0, dcv1) = ( (1+cor)(cv1 - cv0), 0 )
    | m0  m1 |            

    Solving by inverting the matrix (1 -1, m0 m1)
    (dcv0, dcv1) = 1/(m1+m0) |  m1   1 | ( (1+cor)(cv1-cv0), 0 )
                             | -m0   1 | 

    A last note is that (cv1-cv0) = (v1-v0).p10u

    Now plug in ncv0 and ncv1 to get the new velocities
      nv0 = v0 + dcv0 * p10u
      nv1 = v1 + dcv1 * p10u
    """
    p10 = ((p1[0]-p0[0]), (p1[1]-p0[1]))
    len_p10 = math.sqrt(p10[0]*p10[0] + p10[1]*p10[1])
    if len_p10<1E-9:
        raise Exception("Collision of two objects which are at the same spot has no meaning")

    p10u = (p10[0]/len_p10, p10[1]/len_p10)

    #print "p10u",str(p10u)

    v10 = ((v1[0]-v0[0]), (v1[1]-v0[1]))
    cv10 = v10[0]*p10u[0] + v10[1]*p10u[1]

    #print "cv10u",cv10

    transform = c_transform_matrix( m1, 1, -m0, 1 )
    transform.scale(1.0/(m1+m0))

    #print transform

    dcv = transform.apply( (1+cor)*cv10, 0 )

    #print "dcv",str(dcv)

    dv0 = ( dcv[0]*p10u[0], dcv[0]*p10u[1] )
    dv1 = ( dcv[1]*p10u[0], dcv[1]*p10u[1] )
    return ( dv0, dv1 )
