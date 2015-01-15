#a Imports

#c Classes
class c_overlap_2d( object ):
    """
    This class manages overlapping objects each with a 2D bounding box
    The class is given a set of objects, each with its bounding box
    A caller can then interrograte the class to find a list of all the objects in the class' set which overlap a given bounding box

    This can be used, for example, with the class containing the walls and floors of a platform game, and the class being
    interrogated to find the wall/floor elements that a player bounding box overlaps with, to determine movement capabilities of the player.

    The objects in the class' set are called 'elements'.

    The basic overlap class splits the 2D space into 'buckets'. Each bucket is a bucket_size * bucket_size region.
    Each bucket contains a list of the elements whose bounding box overlaps with that bucket.
    An element may be in the list of more than one bucket.

    Buckets are from (nx*bucket_size, ny*bucket_size) inclusive to ((n+1)x*bucket_size, (n+1)y*bucket_size) exclusive
    """
    #f __init__
    def __init__( self, bucket_size=32 ):
        self.bucket_size = bucket_size
        self.buckets = {}
        pass
    #f bucket_index
    def bucket_index( self, coord, inclusive=True ):
        """
        Determine the bucket index (X or Y - buckets are square regions) for a coordinate

        if inclusive is False, then round down - effectively 'find bucket index for just less than coord'
        """
        if inclusive:
            return (coord/self.bucket_size)
        return (coord+self.bucket_size-1)/self.bucket_size
    # bucket_bbox
    def bucket_bbox( self, bbox ):
        """
        Given a bounding box that is (inclusive,inclusive,exclusive,exclusive) in world coordinates,
        find the bucket index bounding box that is (inclusive,inclusive,inclusive,inclusive) that covers it
        """
        bucket_bbox = (self.bucket_index( bbox[0], True ),
                       self.bucket_index( bbox[1], True ),
                       self.bucket_index( bbox[2], False ),
                       self.bucket_index( bbox[3], False ) )
        return bucket_bbox
    # add_element
    def add_element( self, bbox, element ):
        """
        Given a bounding box that is (inclusive,inclusive,exclusive,exclusive) coordinates, add the element to all the buckets it overlaps with

        The process is to determine bucket_bbox - the buckets that the element needs to be part of, and then
        add to the bucket lists for each of those buckets
        """
        bucket_bbox = self.bucket_bbox( bbox )
        for x in range( bucket_bbox[2]-bucket_bbox[0]+1 ):
            for y in range( bucket_bbox[3]-bucket_bbox[1]+1 ):
                if (x,y) not in self.buckets: self.buckets[(x,y)]=[]
                self.buckets[(x,y)].append( (bbox,element) )
                pass
            pass
        pass
    #f remove_element
    def remove_element( self, bbox, element ):
        """
        Given a bounding box that is (inclusive,inclusive,exclusive,exclusive) coordinates, remove the element to all the buckets it overlaps with

        The process is to determine bucket_bbox - the buckets that the element needs to be part of, and then
        remove the element from the bucket lists for each of those buckets if it is in them
        """
        bucket_bbox = self.bucket_bbox( bbox )
        for x in range( bucket_bbox[2]-bucket_bbox[0]+1 ):
            for y in range( bucket_bbox[3]-bucket_bbox[1]+1 ):
                if (x,y) in self.buckets:
                    bucket = self.buckets[(x,y)]
                    i = 0
                    while i<len(bucket):
                        if bucket[i][1] == element:
                            bucket.pop(i)
                            break
                        i += 1
                        pass
                    pass
                pass
            pass
        pass
    #f check_bbox_overlap
    def check_bbox_overlap( self, bbox0, bbox1 ):
        """
        Given real-world coordinates, with bounding boxes as (inclusive,inclusive,exclusive,exclusive),
        determine if the bounding boxes overlap

        The bounding boxes do not overlap if one is to the left of the other, or if one is to above the other
        However, if none of these hold, then there must be some overlap
        """
        # Not overlapping if either box is to the right or below the other box
        if bbox0[0] >= bbox1[2]: return False
        if bbox0[1] >= bbox1[3]: return False
        if bbox1[0] >= bbox0[2]: return False
        if bbox1[1] >= bbox0[3]: return False
        return True
    #f find_overlap
    def find_overlap( self, bbox ):
        """
        Find the list of elements that overlap a bounding box in real-world coordinates (inclusive,inclusive,exclusive,exclusive)

        To do this, find the buckets that the bounding box covers.
        Then for each bucket, check every element in the bucket to see if it overlaps the test bbox
        If it does, add the element to the result list - if it is not already in the list
        """
        results = []
        bucket_bbox = self.bucket_bbox( bbox )
        for x in range( bucket_bbox[2]-bucket_bbox[0]+1 ):
            for y in range( bucket_bbox[3]-bucket_bbox[1]+1 ):
                if (x,y) in self.buckets:
                    for (tgt_bbox, tgt_element) in self.buckets[(x,y)]:
                        if self.check_bbox_overlap( bbox, tgt_bbox ):
                            if tgt_element not in results:
                                results.append(tgt_element)
                                pass
                            pass
                        pass
                    pass
                pass
            pass
        return results

