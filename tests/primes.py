#!/usr/bin/env python

def calculate_x_n_mod_p( x, p, x_n_mod_p=None, n=1 ):
    """
    Calculate x^n mod p, returning result. Requires x<p.

    A cache of results is kept in x_n_mod_p (dictionary of n => x^n mod p)
    If n=0 then x^n mod p =1
    If n in x_n_mod_p.keys() then =x_n_mod_p[n]
    Else split n into (a,b) = (n/2),(n-n/2) (where n/2 is integer division)
    Then x^n = x^(a+b) = x^a . x^b (all mod p)
    Get x_a and x_b (recursively) mod p
    Multiply x_a by x_b, and find r = remainder after division by p
    Set x_n_mod_p[n] = r
    Return r
    """
    if x_n_mod_p is None: x_n_mod_p={}
    if n==0: return 1
    if n==1: return x
    if n in x_n_mod_p: return x_n_mod_p[n]
    a = n/2
    b = n-n/2
    x_a = calculate_x_n_mod_p( x,p,x_n_mod_p, a )
    x_b = calculate_x_n_mod_p( x,p,x_n_mod_p, b )
    r = (x_a * x_b) % p
    x_n_mod_p[n] = r
    return r

def test_is_not_prime( p, xes=(2,3,5), verbose=False ):
    for x in xes:
        if (x>=p): continue
        x_n_mod_p = {}
        x_p_mod_p = calculate_x_n_mod_p( x,p,x_n_mod_p, p )
        if verbose: print "%d^%d = %d (mod %d)"%(x,p,x_p_mod_p,p)
        if x_p_mod_p!=x: return True
        pass
    if verbose:
        print p,"may be prime - tried",xes
        pass
    return False

#print test_is_not_prime( 11 )
#print test_is_not_prime( 39 )
#print test_is_not_prime( 65537 )
#print test_is_not_prime( 1238561239631, xes=(2,3,5,7,11,13,17,19) )
print test_is_not_prime( 561, xes=range(3,559,2), verbose=True )
print calculate_x_n_mod_p( 2,561,n=(561-1)/2 )

#xes = (2,3) # Works for 100 primes
xes = (2,3,5,7,11,13,17,19,23,29,31,37,41,43,47)
max_p = 542  # 100th prime is 541
xes = (2,3)
max_p = 580 
#max_p = 7920 # 1000th prime is 7919
primes = []
for i in range(max_p):
    if i<2: continue
    if not test_is_not_prime( i, xes ):
        primes.append(i)
        pass
    pass
num_primes = len(primes)
for j in range((num_primes+9)/10):
    l = ""
    for i in range(10):
        if i+j*10 >= num_primes: continue
        l += "%5d "%primes[i+j*10]
        pass
    print l
print len(primes)
print primes

