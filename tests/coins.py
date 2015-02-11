#!/usr/bin/env python
"""
Problem: how many ways to have 'N' pennies given coins of value 'a,b,c,d'

Assume to start with that the smallest coin is 1 and N is an integer, and a<b<c<d

Consider a solution consisting of (N,0,0...) i.e. N of the smallest coin.
Take the 'next smallest coin' for a solution - b.
There is another solution if N>b of (N-b,1,0...). And possibly that with 'next smallest coin' of b.
There is another potential solution of (N-c,0,1...) i.e. 'next smallest coin of c'.
These solutions cannot overlap

Now, if the smallest coin is larger than 1, then we can add a '1' coin to start with, but filter out any results that use the '1' coin.
Indeed, we can actually always have a 'bogus plastic coin' (as it were) of value 1 that we prepend to the real coins list, and then remove any results that include the plastic coin.
The real coins can start at '1' too without any problem.

A next step is to have a purse of coins.
This can be a dictionary of 'coin value' : 'number of coins'

Then the set of possible coins to use is a plastic 1 coin, and the keys of the purse (sorted smallest to large).
The function for calculating solutions must keep track of the coins used from the purse, and can only continue if purse[coin to swap in]>coins_used[coin to swap in].

"""
def find_solution( total, coin_set, purse, coins_used, current_solution, next_smallest_coin_index, results, filter_fn = lambda x:True ):
    """
    Given a 'current_solution' add (through a filter) solutions that use at least one 'next_smallest_coin_index' or larger to replace the plastic 1 coins

    If 'next_smallest_coin_index' is outside the set of coins, then there are no more solutions
    Given that the coin set is sorted lowest-to-highest, if the new coin value exceeds the number of plastic ones, then there are no more solutions

    Now, if there are coins of 'next_coin_value' left in the purse, then there is possible a (filterable) solution using one more coin of 'next_coin_value'.
    So, copy the current solution and list of coins used, and update by adding a 'next_coin_value' to the coins used and removing that number of plastic 1s.
    Add the solution to the results (if filtered okay - this filter can ignore any solution with number of plastic 1s > 0) and then recurse to find any more solutions from this new solution

    Finally, recurse with 'next_coin_value'+1; this can only add in higher value coins and therefore cannot overlap with the previous recursion.
    """
    if next_smallest_coin_index >= len(coin_set): return results

    next_coin_value = coin_set[next_smallest_coin_index]
    if next_coin_value>current_solution[0]: return results

    if purse[next_coin_value]<coins_used[next_smallest_coin_index]:
        new_solution = current_solution[:]
        new_coins_used = coins_used[:]
        new_solution[0] -= next_coin_value
        new_solution[next_smallest_coin_index] += 1
        new_coins_used[next_smallest_coin_index] += 1
        if filter_fn(new_solution):
            results.append( new_solution )
            pass
        results = find_solution( total, coin_set, purse, new_coins_used, new_solution, next_smallest_coin_index, results, filter_fn )
        pass

    return find_solution( total, coin_set, purse, coins_used, current_solution, next_smallest_coin_index+1, results, filter_fn )

def find_coin_sets( total, purse ):
    coin_set = purse.keys()
    coin_set.sort()
    coin_set.insert(0,1)
    initial_solution = [total]+[0]*(len(coin_set)-1)
    return find_solution( total, coin_set, purse, [0]*len(coin_set), initial_solution, 1, [], lambda x:(x[0]==0) )

total = 200
purse = {1:10, 2:10, 5:10, 10:20, 20:5, 50:5, 100:5, 200:1}
purse = {1:10,  2:5, 5:3,  10:5,  20:5, 50:3, 100:5, 200:1}
r = find_coin_sets( total, purse )
for i in range(len(r)):
    print i, r[i]
    pass

