#!/usr/bin/env python
import math
"""
Consider

x^2 + y^2 = z^2

where x,y,z are integers>0 and there is no common factor to all three.
Note that this latter means that x is coprime to y; y is coprime to z; x is coprime to z. Otherwise if 'f' were a factor of two of x,y,z then modulo f all three (x^2, y^2, z^2) would have to be zero, hence all three would have factor 'f'.

If x and y were both even, then z would have to be even, and 2 would be a common factor; hence x and y are not both even

Note now that the square of an odd number is 1 modulo 4

If x and y were both odd, then z^2 would have to be even (say (2n)^2 = 4(n^2)) - and it would be 0 mod 4. But x^2 and y^2 were both 1 mod 4, so x^2+y^2 mod 4 != z^2 mod 4.
Hence x and y cannot both be odd.

So, we can now take x to be even, and y to be odd (and z odd).

Take x=2k.

x^2 + y^2 = z^2
=>
4k^2 + y^2 = z^2
y^2 = (z+2k)(z-2k)

Now we can clearly rewrite z+2k to be m.a^2, and z-2k as m.b^2, so that (z+2k)(z-2k) = (m.a.b)^2, where a,b,m are integers, and a,b are coprime (i.e. m = hcf of (z+2k) and (z-2k))
Also, note that a>b (for our cases where x, y, z > 0)

So,
z + 2k = m.a^2
z - 2k = m.b^2
y      = (m.a.b)^2

adding gives
2z    = m(a^2 + b^2)
4k    = m(a^2 - b^2)

Since z and x have no common factors, z and k have no common factors, hence m=1.

z = (a^2+b^2)/2
k = (a^2-b^2)/4

Since z is odd, and z+2k = a^2, a must be odd. Similarly b must be odd.
Rewrite them as a=2c+1 and b=2d+1:
z = (4c^2 + 4c + 1 + 4d^2 + 4d + 1)/2
  = 2c^2 + 2c + 2d^2 +2d +1
  = 2(c+d+1)(c+d) - 4cd +1
k = (a+b)(a-b)/4
  = (2c+2d+2)(2c-2d)/4
  = (c+d+1)(c-d)
x = 2(c+d+1)(c-d)
y = (2c+1)(2d+1)
  = 2(c+d+1) + 4cd - 1

Again, rewriting p=c+d+1, q=c-d (which means 4cd=(p-1)^2-q^2); and noting that c=(a-1)/2, d=(b-1)/2, p=c+d+1=(a+b)/2, q=(a-b)/2, p+q=a, p-q=b
z = 2p(p-1) - (p-1).(p-1) + q^2 + 1
  = p^2 + q^2
x = 2pq
y = p^2 - q^2

Note again that since a>b, c>d and p>q.
Also, since a must be coprime to b, p+q has to be coprime to p-q
It is worth pointing out that not all c,d are not primitive triples. For example, (c,d) in (1+3n,1), (2+5n,2), (3+7n,3), ... are not primitive.

Note also that this holds for every p>q, and every Pythagorean Triple must satisfy this arrangement.

So we can iterate through p,q as integers where p>q>0, where p+q is coprime to p-q, and we will generate all the Pythagorean Triples.

Now, we can consider Plato family triples where z-x=1.
This corresponds to:
p^2+q^2-2pq = (p-q)^2 = 1, and hence where p=q+1
So, if we iterate through q=1,2,3 ... and have p=q+1 we iterate through all the Plato family triples.
We find then that
y = 2q+1
x = 2q(q+1)
z = 2q^2+2q+1 = 2q(q+1)+1 = x+1
These triples are then 3,4,5; 5,12,13; 7,24,25; 9,40,41; 11,60,61, etc

We can also consider Pythagoras family triples where z-y=2
This corresponds to:
p^q+q^2-p^q+q^2 = 2q^2 = 2 => q=1
y = p^2-1
x = 2p
z = p^2+1
The triples are then 3,4,5; 15,8,17; 35,12,37; 63,16,65, etc.
Note that there are nonprimitive Pythagoras family triples not included here, where a Plato triple is doubled (e.g. 6,8,10; 10,24,26, etc)

Now we can consider half of the Fermat family of triples where y-x=1 (the other half is x-y=1):
y-x = p^2 - q^2 - 2pq = 1
Solving for q gives:
1.q^2 + 2p.q - (p^2-1) = 0
q = sqrt(p^2+p^2+1)-2p = sqrt( 2p^2+1 ) - p
This has solutions for p=2,q=1; p=12,q=5; p=70,q=29; p=408,q=169; p=2378,q=985, ...
These correspond to (3, 4, 5), (119, 120, 169), (4059, 4060, 5741), (137903, 137904, 195025), (4684659, 4684660, 6625109), ...

Now we can consider the other half of the Fermat family of triples where x-y=1:
x-y = 2pq - p^2 - q^2 = 1
Solving for q gives:
1.q^2 + 2p.q - (p^2+1) = 0
q = sqrt(p^2+p^2-1)-2p = sqrt( 2p^2-1 ) - p

2378 985.0 (4684659, 4684660, 6625109)
1 0.0 (1, 0, 1)
5 2.0 (21, 20, 29)
29 12.0 (697, 696, 985)
169 70.0 (23661, 23660, 33461)
985 408.0 (803761, 803760, 1136689)

This has solutions for p=5,q=2; p=29,q=12; p=169, q=70; p=985, q=408; p=5741, q=2378, ...
These correspond to (21, 20, 29), (697, 696, 985), (23661, 23660, 33461), (803761, 803760, 1136689), (27304197, 27304196, 38613965), ...

Note that 119 = 6*20-3+2; 696 = 6*119-20+2; 4059=6*696-119+2

This means that if we have (a0,b0,c0), (a1,b1,c1), (a2,b2,c2), ... for all the Fermat family numbers (starting at 3,4,5)

Then for even n>=2 we have (an) = 6*bn-1 - an-2 + 2;

If we actually term 'an' to be the smallest of an/bn above, and an = A.x^n + B.y^n + C, then
an+2 - 6an+1 + an - 2 = A.x^n(x^2-6x+1) + B.y^n(y^2-6y+1) -4C -2 = 0
For this to hold whatever n, we have x=3+2rt2 and y=3-2rt2 and C=-0.5
an = A.(3+2rt2)^n + B.(3-2rt2)^n - 0.5
a0 = A + B - 0.5 = 3 => B = 7/2 - A
a1 = A.(3+2rt2) + B.(3-2rt2) - 0.5 = 20
=> 3A + 2A.rt2 + 21/2 - 7rt2 + -3A + 2Art2 = 41/2
=> 8A.rt2 + 21 - 14rt2 = 41
=> 8A.rt2 = 20+14rt2
=> A = 7/4 + 5rt2/4
=> B = 7/4 - 5rt2/4
-> smallest of Fermat family number for 'n' is an=(7/4+5rt2/4).(3+2rt2)^n + (7/4-5rt2/4).(3-2rt2)^n - 1/2


Now to investigate a UAD approach to Pythagoras - starting at c=1/d=0, arrange in a tree with each node having Up/Along/Down (to the right)

z = 2(c+d+1)(c+d) - 4cd +1
x = 2(c+d+1)(c-d)
y = 2(c+d+1) + 4cd - 1

Hall uses (for a,b,h as x,y,z):
Up    ->  a-2b+2h,  2a-b+2h,  2a-2b+3h
Along ->  a+2b+2h,  2a+b+2h,  2a+2b+3h
Down  -> -a+2b+2h, -2a+b+2h, -2a+2b+3h

In our case where we have (c,d), we use:
Up    (c,d) -> (c+(2d+1),d)
Along (c,d) -> (d+(2c+1),c)
Down  (c,d) -> (2c-d,    c)

We start at node (1,0) (since c>d>=0).
The tree that is created here is a tree of all pairs of odd numbers that are coprime.

Down y -> -2c-2d-2-4cd+1 + 4c^2-4d^2+4c-4d + 4(c+d+1)(c+d)-8cd+2
        = -2c-2d-2-4cd+1 + 4c^2-4d^2+4c-4d + 4c^2+4d^2+8cd+4c+4d-8cd+2
        =    -2d  -4cd+1 + 8c^2     +6c
        = 8c^2 +6c -4cd-2d + 1
        = y(2c-d, c)
      x = -4(c+d+1)-8cd+2 + 2(c+d+1)(c-d)  + 4(c+d+1)(c+d)-8cd+2
        = -4c-4d-4-8cd+2  +2c^2-2d^2+2c-2d + 4c^2+4d^2+8cd+4c+4d-8cd+2
        =  2c-2d          +6c^2+2d^2                            -8cd
        = 2(3c-d+1)(c-d)
        = x(2c-d, c)
      z = -4(c+d+1)-8cd+2 + 4(c+d+1)(c-d)   + 6(c+d+1)(c+d)-12cd+3
        = -4c-4d-4 -8cd+2 + 4c^2-4d^2+4c-4d + 6c^2+6d^2+12cd+6c+6d-12cd+3
        =                 +10c^2+2d^2       +               +6c-2d-8cd +1
        = 10c^2      +6c      +2d^2 -2d       -8cd +1
        = 18c^2 -6cd +6c -6cd +2d^2 -2d -8c^2 +4cd +1
        = 2(9c^2-3cd+3c-3cd+d^2-d)      -8c^2 +4cd +1
        = 2(3c-d+1)(3c-d) -4c(2c-d) +1
        = z( 2c-d, c)
Hence "Down" is (c,d) -> (2c-d,c). Starting at 1,0 -> 2,1 -> 3,2 -> 4,3 -> 5,4 etc
Up   x ->  4(c+d+1)+8cd-2 - 2(c+d+1)(c-d)   + 4(c+d+1)(c+d)-8cd+2
        =  4c+4d+4 +8cd-2  -2c^2+2d^2-2c+2d + 4c^2+4d^2+8cd+4c+4d-8cd+2
        =       +4         +2c^2+6d^2+6c+10d            +8cd
        =  2c^2+6d^2+6c+10d+8cd+4
        = 2(c^2+3d^2+3c+5d+4cd+2)
        = 2((c+2d+1)^2 - d^2 + c+2d+1 -d)
        = x(c+2d+1,d)
Hence "Up" is (c,d) -> (c+2d+1,d). Starting at 1,0 -> 2,0 -> 3,0 -> 4,0 -> 5,0
Along x -> 4(c+d+1)+8cd-2 + 2(c+d+1)(c-d)   + 4(c+d+1)(c+d)-8cd+2
         =  4c+4d+4 +8cd-2  +2c^2-2d^2+2c-2d + 4c^2+4d^2+8cd+4c+4d-8cd+2
         =       +4 +8cd    +6c^2+2d^2+10c+6d
         = 2 ( 3c^2 + d^2 + 5c + 3d + 4cd + 2 )
         = x(2c+d+1,c)


The tree is very similar to an HCF tree. Look at it in reverse
UAD inverse of Down  is (x,y)<-(c,d): d=x,c=2x-y   => x=d, y=2d-c
UAD inverse of Along is (x,y)<-(c,d): d=x,c=2x+y+1 => x=d, y=c-(2d+1)
UAD inverse of Up    is (x,y)<-(c,d): d=y,c=x+2y+1 => x=c-(2d+1), y=d

def hcf( a, b ):
    if (a<b): (a,b)=(b,a)
    while b>0:
        (a,b) = (b,a%b)
        pass
    return a
We have a=2c+1, b=2d+1, and c>d so a>b so ignore the swap.
So consider the internal of the while loop.
First, if b<a<2b then 2d+1<2c+1<4d+2 => d<c<=2d then we want to go to (x,y) corresponding to (b,(2b-a))
In this case 2b-a=4d+2-2c-1 = 2(2d-c)+1, i.e. go to (d,2d-c) (reverse of Down)
Now, if 2b<=a<3b then 4d+2<=2c+1<6d+3 => 2d<c<3d+1 then we want to go to (x,y) corresponding to (b,(a-2b))
In this case a-2b=2c+1-4d-2 = 2(c-2d-1)+1, i.e. go to (d,c-(2d+1)) (reverse of Along)
Now, if 3b<=a then 6d+3<=2c+1 => 3d+1<=c then we want to go to (x,y) corresponding to (a-2b,b)
In this case a-2b=2c+1-4d-2 = 2(c-2d-1)+1, i.e. go to (c-(2d+1),d) (reverse of Up)
[Note that the first step is not QUITE HCF; we would go to a-b in HCF, except that is EVEN and so cannot be covered; however,
the tree is not about finding the HCF - it is a tree which one could reach any point in HCF function path]

Rewriting the inverse rules:
 d<c<=2d => (c,d) -> (d,2d-c)     (reverse down)
2d<c<=3d => (c,d) -> (d,c-(2d+1)) (reverse along)
3d<c     => (c,d) -> (c-(2d+1),d) (reverse up)

If we start at any point (c,d) corresponding to two spaces that are coprime, then HCF ends up at a%b==0, and that ends up at tree node (c,d)=(n,n).
Otherwise HCF will terminate at (a,b)=(n,1); the tree runs this down to node (c,d)=(1,0)

So if we backtrack from any (c,d) and we reach (n,n) then 2c+1 and 2d+ have a common factor of 2n+1; if not we will reach (1,0) and 2c+1 and 2d+1 are coprime.

This means that we can run through the tree to generate all the primitive Pythagorean triples.

Note that the 'along' arrow for (c,d) starting at (1,0) yields (1,0), (3,1), (8,3), (20,8), ...
The recurrence relation here is xn+2 = 2xn+1 + xn + 1.
If xn = A.d^n + B, we get A.d^n( d^2 - 2d -1 ) + B-2B-B + 1 = 0
If B=-0.5 and d=1+-sqrt(2) then we have solutions for A1 and A2 (d1=1-sqrt(2), d2+sqrt(2)):
xn = A1.d1^n + A2.d2^n - 0.5
But x0=1, and x1=3
Hence A1+A2=3/2; A1.d1+A2.d2=7/2.
Solving yields A1=(3/4 - 1/sqrt(2)), A2=(3/4 + 1/sqrt(2))



Consider the area of triangles (half base times height, i.e. xy/2):
x = 2(c+d+1)(c-d)
y = (2c+1)(2d+1)
A = xy/2 = (c^2-d^2+c-d)(4cd+2c+2d+1)
         = 4c^3d+2c^3+2c^2d+c^2 - 4cd^3-2cd^2-2d^3-d^2 +4c^2d+2c^2+2cd+c -4cd^2-2cd-2d^2-d
         = 4c^3d+2c^3           - 4cd^3      -2d^3     +6c^2d+3c^2    +c -6cd^2    -3d^2-d
         = cd(4c^2-4d^2 -6d -6c) + 2(c^3-d^3) + 3(c^2-d^2) + (c-d)
      [  = (c+d+1)(c-d)(2c+1)(2d+1) ]

If c-d=0 mod 3 then A=0 mod 3
If c-d=1 mod 3 then either 2d+1 or 2c+1=2d+3 or c+d+1=2d+2 is 0 mod 3, so A=0 mod 3
If c-d=2 mod 3 then either 2d+1 or 2c+1=2d+5 or c+d+1=2d+3 is 0 mod 3, so A=0 mod 3
So A=0 mod 3.

If c-d=0 mod 2 then A=0 mod 2
If c-d=1 mod 2 then c+d+1=2d+2=0 mod 2, so A=0 mod 2
So A=0 mod 2.

Combining means that the area of every Pythagorean triangle is a multiple of 6.
Looking at (x+y)^2-z^2 = 4xy, which is (x+y-z)(x+y+z):
z = 2(c+d+1)(c+d) - 4cd +1 = 2c^2 + 2d^2 + 2c + 2d + 1
x = 2(c+d+1)(c-d)          = 2c^2 - 2d^2 + 2c - 2d
y = 2(c+d+1) + 4cd - 1     =             + 2c + 2d + 1 + 4cd
x+y-z = -4d^2 +2c -2d + 4cd    = 2(      c+2cd-d-2d^2) = 2(c-d)(2d+1)   (new definition of T)
x+y+z =  4c^2 +6c +2d +2 + 4cd = 2(2c^2+3c+2cd+d     ) = 2(c+d+1)(2c+1) (new definition of S)
Consider now U=(2c+1)(c-d), V=(c+d+1)(2d+1);
 U+V = 2c^2-2cd+c-d + 2cd+c+2d^2+d+2d+1
     = 2c^2    +2c  +      +2d^2  +2d+1
     = z
     = S-T

Note that if c=d+1 then A=1*(2d+1)*(2d+2)*(2d+3); so the product of three consecutive integers is the area of a Pythogarean Triangle.

Can A be a square? We need only consider primitive triangles, since area of a triangle A scaled up by N linearly is A*N^2.
Given c>d, and we know that 2c+1 and 2d+1 are coprime, for A to be a square we would need (c-d)(c+d+1) to be a square times (2c+1)(2d+1).
Now we know that A is a multiple of 6, so it is even.
If c-d is even then c-d must be a multiple of 4 for A to be a square; i.e. c=d+4B. The area is then 4B(4B+2d+1)(8B+2d+1)(2d+1).
We can rewrite this as 4Bb(b-4B)(b+4B).
The common factors of b and b-4B cannot be 2 (since b is odd) and therefore would have to be factors of B i.e. b=f.h, B=g.h
Then b-4B = fh-4gh = h(f-4g); then we have 4fgh^4(f-4g)(f+4g) = (2h^2)^2.fg.(f-16g^2). If f and g are coprime then (f-16g^2) has to be a multiple of f and g, which it clearly is not
So if c-d is even then A cannot be a square

If c-d is odd then one of c or d is even and the other is odd; c+d+1 is a multiple of 4 (e.g. 4B); c=4B-d-1.
Then A = (4B-b)(4B-1)(8B-b)b= (1-4B)(8B-b)(4B-b)(0-b). As before, A cannot be a square.

So independent of c-d is odd or even, A cannot be a square.

Consider f and g, for any f,g>0. Then consider fg(g-f)(g+f) - this is the area of a Pythogarean Triangle. (The c=d+1, or c-d=1, above is a special case.)
In this case, f=c-d, and g=c+d+1.

Note also that if c=3d, then A=2d(6d+1)(4d+1)(2d+1)
Note also that if c=2d, then A= d(3d+1)(4d+1)(2d+1)

If (2c+1)(2d+1) = 1+(c-d)(c+d+1) (i.e. y=1+x/2)?
    4cd+2c+2d+1 = c^2-d^2+c-d+1
d^2 + d(4c+3) + c(1-c) = 0
d = (-4c-3)/2 +- sqrt(16c^2+9+24c+4c^2-4c)/2
  = (-3-4c)/2 +- sqrt(20c^2+20c+9)/2
  = (-3/2-2c) +  sqrt(5c^2+5c+9/4)
(since d>0). As d is an integer, sqrt(5c^2+5c+9/4) must be k+1/2 for some integer k
-> k^2 + k + 1/4 = 5c^2+5c+9/4
-> k^2 + k = 5c^2 + 5c +2
-> c(c+1) = (k^2+k-2)/5
( and d=k-2c-1 )

Note that for every 2m+1 we have (2m+1)^2=4(m^2+m)+1 = 4(m(m+1))+1
So m(m+1) = ((2m+1)^2-1)/4
So c(c+1) = ((2c+1)^2-1)/4 = (k^2+k-2)/5
=> (2c+1)^2 = (4k(k+1)-8+5)/5
            = (4k(k+1)+1-4)/5
            = ((2k+1)^2-4)/5
So we need odd integer solutions to K^2 = 4+5C^2, and K=2k+1, C=2c+1
Solutions occur for:
c=0, C=1, K=3, k=1 (but c<1 so not a solution for us)
c=1, C=3, K=7, k=3, d=0
c=10, C=21, K=47, k=23, d=2
c=27, C=55, K=123, k=61, d=6
c=188, C=377, K=843, k=421, d=44

 why?   c    d              A    c-d c+d+1 2c+1 2d+1         (x,y,z)               (c-d)(2c+1) (c+d+1)(2d+1)
 2 :    1    0 :            6 :    1    2    3    1 :                  (3, 4, 5) :      3      2
 3 :    1    0 :            6 :    1    2    3    1 :                  (3, 4, 5) :      3      2
 1 :    2    0 :           30 :    2    3    5    1 :                (5, 12, 13) :     10      3
 4 :    3    1 :          210 :    2    5    7    3 :               (21, 20, 29) :     14     15
 1 :    6    1 :         1560 :    5    8   13    3 :               (39, 80, 89) :     65     24
 3 :    8    3 :         7140 :    5   12   17    7 :            (119, 120, 169) :     85     84
 2 :   10    2 :        10920 :    8   13   21    5 :            (105, 208, 233) :    168     65
 4 :   20    8 :       242556 :   12   29   41   17 :            (697, 696, 985) :    492    493
 2 :   27    6 :       510510 :   21   34   55   13 :          (715, 1428, 1597) :   1155    442
 1 :   44   10 :      3495030 :   34   55   89   21 :         (1869, 3740, 4181) :   3026   1155
 3 :   49   20 :      8239770 :   29   70   99   41 :         (4059, 4060, 5741) :   2871   2870
 1 :  116   27 :    164237040 :   89  144  233   55 :      (12815, 25632, 28657) :  20737   7920
 4 :  119   49 :    279909630 :   70  169  239   99 :      (23661, 23660, 33461) :  16730  16731
 2 :  188   44 :   1125770256 :  144  233  377   89 :      (33553, 67104, 75025) :  54288  20737
 3 :  288  119 :   9508687656 :  169  408  577  239 :   (137903, 137904, 195025) :  97513  97512
 2 :  493  116 :  52886430870 :  377  610  987  233 :   (229971, 459940, 514229) : 372099 142130
 4 :  696  288 : 323015470680 :  408  985 1393  577 :  (803761, 803760, 1136689) : 568344 568345
 1 :  798  188 : 362487682830 :  610  987 1597  377 : (602069, 1204140, 1346269) : 974170 372099
 3 : 1681  696 : 10973017315470 :  985 2378 3363 1393 : (4684659, 4684660, 6625109) : 3312555 3312554
 1 : 2090  493 : 17029219589256 : 1597 2584 4181  987 : (4126647, 8253296, 9227465) : 6677057 2550408
 2 : 3382  798 : 116720030923320 : 2584 4181 6765 1597 : (10803705, 21607408, 24157817) : 17480760 6677057
 4 : 4059 1681 : 372759573255306 : 2378 5741 8119 3363 : (27304197, 27304196, 38613965) : 19306982 19306983
why=1 for ((c-d)*(c+d+1) - (2*c+1)*(2*d+1)) = 1
why=2 for ((c-d)*(c+d+1) - (2*c+1)*(2*d+1)) = -1
why=3 for ((c-d)*(2*c+1) - (c+d+1)*(2*d+1)) = 1
why=4 for ((c-d)*(2*c+1) - (c+d+1)*(2*d+1)) = -1

Note that for reason 4 we are following along the 'along' axis of the UAD tree
Here c = (3/4-1/sqrt(2)).(1-sqrt(2))^n     + (3/4+1/sqrt(2)).(1+sqrt(2))^n     - 1/2
and  d = (3/4-1/sqrt(2)).(1-sqrt(2))^(n-1) + (3/4+1/sqrt(2)).(1+sqrt(2))^(n-1) - 1/2
or A1,d1,A2,d2=3/4-1/sqrt(2), 1-sqrt(2), 3/4+1/sqrt(2), 1+sqrt(2)
Note that d2+d1=2; d2-d1=2sqrt(2); d2d1=-1, d2+1=sqrt(2).d2; d1+1=-sqrt(2).d1; A1.A2=1/16
     c = A1.d1^n     + A2.d2^n     - 1/2
     d = A1.d1^(n-1) + A2.d2^(n-1) - 1/2
Hence c-d = A1(d1-1).d1^(n-1) + A2(d2-1).d2^(n-1)
          = sqrt(2)( A2d2^(n-1) - A1d1^(n-1) )
     2c+1 = 2(A1.d1^n + A2.d2^n)

(c-d).(2c+1)  = sqrt(2)( A2d2^(n-1) - A1d1^(n-1) ) . 2(A1.d1^n + A2.d2^n)
              = 2sqrt(2)( A2^2.d2^(2n-1) - A1^2.d1^(2n-1) - A1A2.d1^(n-1).d2^n + A1A2.d1^n.d2^(n-1)
              = 2sqrt(2)( A2^2.d2^(2n-1) - A1^2.d1^(2n-1) - A1A2.d1^(n-1).d2^(n-1).(d2-d1) )
              = 2sqrt(2)( A2^2.d2^(2n-1) - A1^2.d1^(2n-1) - 2A1A2.sqrt(2).(d1d2)^(n-1) )
              = 2sqrt(2)( A2^2.d2^(2n-1) - A1^2.d1^(2n-1) - 2A1A2.sqrt(2).(-1)^(n-1) )
              = 2sqrt(2)( A2^2.d2^(2n-1) - A1^2.d1^(2n-1)) - 8A1A2.(-1)^(n-1) )
              = 2sqrt(2)( A2^2.d2^(2n-1) - A1^2.d1^(2n-1)) -(-1)^(n-1)/2 )

     c+d+1 = A2(d2+1).d2^(n-1) + A1(d1+1).d1^(n-1)
           = sqrt(2)(A2.d2^(n) - A1.d1^(n))
      2d+1 = 2(A1.d1^(n-1) + A2.d2^(n-1))

(c+d+1)(2d+1) = sqrt(2)(A2.d2^(n) - A1.d1^(n)) . 2(A1.d1^(n-1) + A2.d2^(n-1))
              = 2sqrt(2)( A2^2.d2^(2n-1) - A1^2.d1^(2n-1) + A1A2.d1^(n-1).d2^n + A1A2.d1^n.d2^(n-1)
              = 2sqrt(2)( A2^2.d2^(2n-1) - A1^2.d1^(2n-1) + A1A2.d1^(n-1).d2^(n-1).(d2-d1) )
              = 2sqrt(2)( A2^2.d2^(2n-1) - A1^2.d1^(2n-1) + 2A1A2.sqrt(2).(d1d2)^(n-1) )
              = 2sqrt(2)( A2^2.d2^(2n-1) - A1^2.d1^(2n-1) + 2A1A2.sqrt(2).(-1)^(n-1) )
              = 2sqrt(2)( A2^2.d2^(2n-1) - A1^2.d1^(2n-1)) + 8A1A2.(-1)^(n-1) )
              = 2sqrt(2)( A2^2.d2^(2n-1) - A1^2.d1^(2n-1)) + (-1)^(n-1)/2 )

Hence
(c+d+1)(2d+1) - (c-d).(2c+1) = (-1)^(n-1)/2 + (-1)^(n-1)/2
                             = -1^(n-1)
Hence there are two factors of A that differ by one for these c,d; further which is larger alternates as one goes across the UAD tree.
Since the UAD tree continues forever, there must be an infinite number of areas A that can be factored into two successive integers.

Now look at the other two entries:
 why?   c    d              A    c-d c+d+1 2c+1 2d+1         (x,y,z)               (c-d)(2c+1) (c+d+1)(2d+1)
 2 :    1    0 :            6 :    1    2    3    1 :                  (3, 4, 5) :      3      2
 1 :    6    1 :         1560 :    5    8   13    3 :               (39, 80, 89) :     65     24
 2 :   27    6 :       510510 :   21   34   55   13 :          (715, 1428, 1597) :   1155    442
 1 :  116   27 :    164237040 :   89  144  233   55 :      (12815, 25632, 28657) :  20737   7920
 2 :  493  116 :  52886430870 :  377  610  987  233 :   (229971, 459940, 514229) : 372099 142130
 1 : 2090  493 : 17029219589256 : 1597 2584 4181  987 : (4126647, 8253296, 9227465) : 6677057 2550408

 1 :    2    0 :           30 :    2    3    5    1 :                (5, 12, 13) :     10      3
 2 :   10    2 :        10920 :    8   13   21    5 :            (105, 208, 233) :    168     65
 1 :   44   10 :      3495030 :   34   55   89   21 :         (1869, 3740, 4181) :   3026   1155
 2 :  188   44 :   1125770256 :  144  233  377   89 :      (33553, 67104, 75025) :  54288  20737
 1 :  798  188 : 362487682830 :  610  987 1597  377 : (602069, 1204140, 1346269) : 974170 372099
 2 : 3382  798 : 116720030923320 : 2584 4181 6765 1597 : (10803705, 21607408, 24157817) : 17480760 6677057

These form two trees, starting at 1/0 and 2/0.
The first has recurrence relation: xn+2 = 4xn+1 + xn + 2 and values of 1 and 6 for n=0,1
This can be resolved to xn = A1.d1^n + A2.d2^n - 1/2, where A1+A2=3/2, A1-A2=7/10.sqrt(5), A1.A2=-1/20, d1+d2=4, d1-d2=2sqrt(5), d1d2=-1
A1=3/4+7/20sqrt(5), A2=3/4-7/20sqrt(5), d1=2+sqrt(5), d2=2-sqrt(5), d1^2=9+2sqrt(5)=sqrt(5).d1+4

The second has recurrence relation: xn+2 = 4xn+1 + xn + 2 and values of 2 and 10 for n=0,1 (i.e. same as first but different initial values)
This can be resolved to xn = A1.d1^n + A2.d2^n - 1/2, where A1+A2=5/2, A1-A2=11/10.sqrt(5), , A1.A2=-1/20, d1+d2=4, d1-d2=2sqrt(5), d1d2=-1
A1=5/4+11/20sqrt(5), A2=5/4-11/20sqrt(5), d1=2+sqrt(5), d2=2-sqrt(5)

Note that c(n+2) = 4c(n+1)+c(n)+2, and that d(n)=c(n+1); hence c(n) = 4d(n)+c(n-2)+2
     c = A1.d1^n     + A2.d2^n     - 1/2
     d = A1.d1^(n-1) + A2.d2^(n-1) - 1/2

In both these cases we have (c-d)(c+d+1) - (2c+1)(2d+1) = +-1
Hence c-d = A1(d1-1).d1^(n-1) + A2(d2-1).d2^(n-1)
          = (A1.d1^n + A2.d2^n) - (A1.d1^(n-1) + A2.d2^(n-1))
    c+d+1 = A2(d2+1).d2^(n-1) + A1(d1+1).d1^(n-1)
          = (A1.d1^n + A2.d2^n) + (A1.d1^(n-1) + A2.d2^(n-1))
     2d+1 = 2(A1.d1^(n-1) + A2.d2^(n-1))
     2c+1 = 2(A1.d1^n + A2.d2^n)

(c-d).(c+d+1)  = ( (A1.d1^n + A2.d2^n) - (A1.d1^(n-1) + A2.d2^(n-1)) ) . (A1.d1^n + A2.d2^n) + (A1.d1^(n-1) + A2.d2^(n-1))
               = (A1^2.d1^n + A2^2.d2^n)^2 - (A1^2.d1^(n-1) + A2^2.d2^(n-1))^2
               = (A1^2.d1^2n + A2^2.d2^2n + 2A1A2.d1^n.d2^n) - (A1^2.d1^(2n-2) + A2^2.d2^(2n-2) + 2A1A2.d1^(n-1).d2^(n-1))
               = (A1^2.d1^2n + A2^2.d2^2n + 2A1A2.(d1d2)^n)  - (A1^2.d1^(2n-2) + A2^2.d2^(2n-2) + 2A1A2.d1d2^(n-1))
               = (A1^2.d1^2n + A2^2.d2^2n) - (A1^2.d1^(2n-2) + A2^2.d2^(2n-2)) +  2A1A2.(-1)^n - 2A1A2.(-1)^(n-1))
               = (A1^2.d1^2n + A2^2.d2^2n) - (A1^2.d1^(2n-2) + A2^2.d2^(2n-2)) +  4A1A2.(-1)^n
               = (A1^2.d1^2n - A1^2.d1^(2n-2)) + (A2^2.d2^2n - A2^2.d2^(2n-2)) +  4A1A2.(-1)^n

(2c+1)(2d+1)  = 2(A1.d1^n + A2.d2^n) . 2(A1.d1^(n-1) + A2.d2^(n-1))
              = 4(A1^2.d1^(2n-1) + A2^2.d2^(2n-1) + A1A2.d1^n.d2^(n-1)   + A1A2.d1^(n-1).d2^n)
              = 4(A1^2.d1^(2n-1) + A2^2.d2^(2n-1) + A1A2.d1.(d1d2)^(n-1) + A1A2.d2.(d1d2)^(n-1))
              = 4(A1^2.d1^(2n-1) + A2^2.d2^(2n-1) + A1A2.d1.(-1)^(n-1)   + A1A2.d2.(-1)^(n-1))
              = 4(A1^2.d1^(2n-1) + A2^2.d2^(2n-1) + A1A2.(-1)^(n-1)(d1+d2))
              = 4(A1^2.d1^(2n-1) + A2^2.d2^(2n-1) + A1A2.(-1)^(n-1)(4))
              = 4A1^2.d1^(2n-1) + 4A2^2.d2^(2n-1) + 16A1A2.(-1)^(n-1))
Note that A1^2.d1^2n - 4A1^2.d1^(2n-1) - A1^2.d1^(2n-2) = A1^2.d1^(n-2).(d1^2-4d1-1)
 But (d1^2-4d1-1) = 0 (as that is the recurrence relation)
Hence A1^2.d1^2n - 4A1^2.d1^(2n-1) - A1^2.d1^(2n-2) = 0
Hence (c-d).(c+d+1) - (2c+1).(2d+1) = 4A1A2.(-1)^n - 16A1A2.(-1)^(n-1)
                                    = 4A1A2.(-1)^n + 16A1A2.(-1)^n
                                    = 20A1A2.(-1)^n
Since A1A2=-1/20
(c-d).(c+d+1) - (2c+1).(2d+1) = (-1)^(n+1)

Hence again there are two factors of A that differ by one for these c,d; further which is larger alternates as one goes across the UAD tree.
Since the UAD tree continues forever, there must be an infinite number of areas A that can be factored into two successive integers.


We can create another tree of 'no common factors with none being multiple of 3 either' (UAD tree is no common factors with none being multiple of 2 either).

We have to cover:
2/1
4/1
5/1, 5/2, 5/4
7/1, 7/2, 7/4, 7/5
8/1, 8/5, 8/7
10/1, 10/5, 10/7
11/1, 11/2, 11/4, 11/7, 11/8, 11/10
...

A has 3n+1/3m+2 -> 2c/d :3(2n)+2/3m+2
B has 3n+1/3m+1 -> c+d/d:3(n+m)+2/3m+1 and 6n+2/3+1 allowed
C has 3n+2/3m+1
D has 3n+2/3m+2 -> 

Starting at 2/1 -> 4/1 or 5/1 or 7/2?
4/1 -> 7/4 or 8/1 or 5/4


"""

def ns( ap, cp) : return (2*(ap-cp)*(ap+cp+1), (2*ap+1)*(2*cp+1), 2*(ap**2+ap+cp**2+cp+1)-1 )

def triples(p,q):
    p=int(p+0.0001)
    q=int(q+0.0001)
    return (p**2-q**2, 2*p*q, p**2+q**2)

def fermat_triples_1():
    import math
    for p in range(5000):
        q=math.sqrt(2*p**2+1)-p
        if (q-int(q))**2<0.0000000001: print p,q,triples(p,q)
        pass
    pass


def fermat_triples_2():
    import math
    for p in range(50000):
        if p==0:continue
        q=math.sqrt(2*p**2-1)-p
        if (q-int(q))**2<0.0000000001: print p,q,triples(p,q)
        pass
    pass

fermat_triples_1()

fermat_triples_2()

def hcf( a, b ):
    if a<b: (a,b)=(b,a)
    while b>0:
        (a,b) = (b,a%b)
        pass
    return a

def triples_cd(c,d):
    return (2*(c+d+1)+4*c*d-1,
            2*(c+d+1)*(c-d),
            2*(c+d+1)*(c+d) - 4*c*d +1)

def is_primitive( xyz ):
    if hcf(xyz[0],xyz[1])>1: return False
    return True


def get_uad_map( uad, m ):
    uad_map = []
    for i in range(m): uad_map.append([0]*m)
    for c in range(m):
        for d in range(m):
            uad_map[c][d] = (uad[0](c,d,m), uad[1](c,d,m), uad[2](c,d,m))
            pass
        pass
    return uad_map

uad_map_fns = ( lambda c,d,m:((c+2*d+1) % m,d  % m),
                lambda c,d,m:((2*c+d+1) % m,c  % m),                
                lambda c,d,m:((2*c-d)   % m,c  % m) )
mod3_uad_map = get_uad_map( uad_map_fns, 3 )
for l in mod3_uad_map: print l

mod5_uad_map = get_uad_map( uad_map_fns, 5 )
for l in mod5_uad_map: print l


def area_factors( c,d, f, reason="" ):
    xyz = triples_cd(c,d)
    if f(xyz):
        print "%2s : %4d %4d : %12d : %4d %4d %4d %4d : %26s : %6d %6d"%(reason,c,d,xyz[0]*xyz[1]/2,c-d,c+d+1,2*c+1,2*d+1,str(xyz),(c-d)*(2*c+1),(c+d+1)*(2*d+1))
        pass
    pass

def is_square(x):
    return (int(math.sqrt(x))**2==x)

n2_p_n = []
for i in range(40): n2_p_n.append(i*(i+1))
for c in range(10000):
    diff = 1
    if c<1: continue
    for d in range(c):
        #area_factors(c,d, lambda xyz:(is_primitive(xyz) and (is_square(1+xyz[0]*xyz[1]*2))))
        area_factors(c,d, lambda xyz:( ((c-d)*(c+d+1)==diff+(2*c+1)*(2*d+1)) and is_primitive(xyz) and (is_square(1+xyz[0]*xyz[1]*2))), "1")
        area_factors(c,d, lambda xyz:( ((c-d)*(c+d+1)+diff==(2*c+1)*(2*d+1)) and is_primitive(xyz) and (is_square(1+xyz[0]*xyz[1]*2))), "2")
        area_factors(c,d, lambda xyz:( ((c-d)*(2*c+1)==diff+(c+d+1)*(2*d+1)) and is_primitive(xyz) and (is_square(1+xyz[0]*xyz[1]*2))), "3")
        area_factors(c,d, lambda xyz:( ((c-d)*(2*c+1)+diff==(c+d+1)*(2*d+1)) and is_primitive(xyz) and (is_square(1+xyz[0]*xyz[1]*2))), "4")
        area_factors(c,d, lambda xyz:( ((c-d)*(2*d+1)==diff+(c+d+1)*(2*c+1)) and is_primitive(xyz) and (is_square(1+xyz[0]*xyz[1]*2))), "5")
        area_factors(c,d, lambda xyz:( ((c-d)*(2*d+1)+diff==(c+d+1)*(2*c+1)) and is_primitive(xyz) and (is_square(1+xyz[0]*xyz[1]*2))), "6")
        pass
    pass

for c in range(300):
    C=2*c+1
    if int(math.sqrt(4+5*C**2))**2 == 4+5*C**2:
        print c,C,4+5*C**2, math.sqrt(4+5*C**2)
