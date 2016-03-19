import math

def vector_prod3(a,b):
    r = [ a[1]*b[2] - a[2]*b[1],
          a[2]*b[0] - a[0]*b[2],
          a[0]*b[1] - a[1]*b[0] ]
    return r

def vector_length(v):
    return math.sqrt(dot_product(v,v))

def vector_separation(a,b):
    d = vector_add(a,b,scale=-1.0)
    return math.sqrt(dot_product(d,d))

def vector_normalize(v, epsilon=1E-8):
    d = math.sqrt(dot_product(v,v))
    if d<epsilon: d=1
    return vector_scale(v,1.0/d)

def vector_min(a, b):
    r = []
    for i in range(len(a)):
        if a[i] is None:
            r.append(b[i])
            pass
        else:
            r.append(min(a[i],b[i]))
        pass
    return r

def vector_max(a, b):
    r = []
    for i in range(len(a)):
        if a[i] is None:
            r.append(b[i])
            pass
        else:
            r.append(max(a[i],b[i]))
        pass
    return r

def vector_scale(a,scale=1.0):
    d = []
    for i in range(len(a)):
        d.append(a[i]*scale)
        pass
    return d

def vector_add(a,b,scale=1.0):
    d = []
    for i in range(len(a)):
        d.append(a[i]+b[i]*scale)
        pass
    return d

def cos_angle_between(a,b, epsilon=1E-16):
    l = vector_length(a) * vector_length(b)
    if l<epsilon: return 1.0
    return dot_product(a,b)/l

def dot_product(a,b):
    r = 0
    for i in range(len(a)):
        r += a[i]*b[i]
        pass
    return r

def point_on_plane(p0,p1,p2,k01,k02):
    # mp = p0 + k01.(p1-p0) + k02.(p2-p0)
    mp = vector.add(p0, p1, scale=k01 )
    mp = vector.add(mp, p2, scale=k02 )
    mp = vector.add(mp, p0, scale=(-k01-k02) )
    return mp

#a Closest meeting of two lines
def closest_meeting_of_two_lines(p0, d0, p1, d1, too_close=0.0001):
    """
    Points on the lines are p0+s.d0 and p1+t.d1
    The closest points are c0 and c1, with sc and tc the closest coefficients

    Consider a 3D space with the axes d0, d1 and d0 x d1
    Every point in space can be represented as (a,b,c) = a.d0 + b.d1 + c.(d0 x d1)
    for some a,b,c for the point

    Points on p0+s.d0 are expressed in this space as s'.d0 + P0b.d1 + P0c.(d0 x d1)
    Points on p1+t.d1 are expressed in this space as P1a.d0 + t'.d1 + P1c.(d0 x d1)

    A vector between these two points is then:
    (s'-P1a).d0 + (P0b-t').d1 + (P0c-P1c).(d0 x d1)

    This has minimum length when s'-P1a is zero and P0b-t' is zero (since d0 x d1 is perpendicular to d0 and d1)

    Now, p0 is at P0a.d0 + P0b.d1 + P0c.(d0 x d1), and s=s'-P0a (and t=t'-P1b)
    p0.d0 = P0a.(d0.d0) + P0b.(d1.d0)
    p0.d1 = P0a.(d0.d1) + P0b.(d1.d1)
    i.e. [d0.d0 d1.d0] [P0a]  = [p0.d0]
         [d0.d1 d1.d1] [P0b]    [p0.d1]
    and
         [d0.d0 d1.d0] [P1a]  = [p1.d0]
         [d0.d1 d1.d1] [P1b]    [p1.d1]
    =>  P0a = 1/(d0.d0 . d1.d1 - d1.d0 . d0.d1) ( d1.d1 . p0.d0 - d1.d0 . p0.d1)
    and P0b = 1/(d0.d0 . d1.d1 - d1.d0 . d0.d1) (-d1.d0 . p0.d0 + d0.d0 . p0.d1)
    and P1a = 1/(d0.d0 . d1.d1 - d1.d0 . d0.d1) ( d1.d1 . p1.d0 - d1.d0 . p1.d1)
    and P1b = 1/(d0.d0 . d1.d1 - d1.d0 . d0.d1) (-d1.d0 . p1.d0 + d0.d0 . p1.d1)

    Now s=s'-P0a = P1a-P0a, t=t'-P1b = P0b-P1b
    s = 1/(d0.d0 . d1.d1 - d1.d0 . d0.d1) . (d1.d1 . d0.(p1-p0) - d1.d0 . d1.(p1-p0) )
    t = 1/(d0.d0 . d1.d1 - d1.d0 . d0.d1) . (d0.d0 . d1.(p1-p0) - d1.d0 . d0.(p1-p0) )
    
    If we set D = (d0.d0 . d1.d1 - d1.d0 . d0.d1) (determinant of our solution matrix)
    we can see when the solution is degenerate

    D = |d0|^2 . |d1|^2 - (|d0||d1|cos(d0d1) )^2
    D = sin^2(d0d1) . (|d0||d1|)^2
    If d0 and d1 are approximately unit vectors, D is then sin^2(angle) between
    i.e. D<epsilon implies the lines are too close to parallel

    We can also see how 'close' the lines are by |c1-c0|, or (c1-c0).(c1-c0)
    Indeed, we can have a measure of 'goodness' using (c1-c0).(c1-c0) / D

    """
    p1p0 = vector_add(p1,p0,scale=-1.0)
    d0d0 = dot_product(d0,d0)
    d1d1 = dot_product(d1,d1)
    d0d1 = dot_product(d0,d1)

    d0p10 = dot_product(d0,p1p0)
    d1p10 = dot_product(d1,p1p0)

    D = d0d0*d1d1 - d0d1*d0d1

    if D<too_close:
        zero = vector_add(p0,p0,scale=-1.0)
        return ( zero, zero, 0.0, 1.0/too_close )

    s = (d1d1*d0p10 - d0d1*d1p10) / D
    t = (d0d1*d0p10 - d0d0*d1p10) / D

    c0 = vector_add(p0,d0,scale=s)
    c1 = vector_add(p1,d1,scale=t)

    dc = vector_add(c1,c0,scale=-1.0)
    dc2 = dot_product(dc,dc)

    goodness = dc2/D
    if goodness>1.0/too_close: goodness=1.0/too_close
    return (c0, c1, dc2, goodness)

