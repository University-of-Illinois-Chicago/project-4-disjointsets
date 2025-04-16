#
# Union Find (Disjoint Sets) Data Structure Implementation
# 
class UnionFind:
    #
    # Default constructor
    #
    def __init__(self, n: int) -> None:
        self.parent = list(range(n)) 
        self.rank = [1] * n 
    
    #
    # Returns the root of the set containing element 'x'.
    #
    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])

        return self.parent[x]
    
    #
    # Merges the sets containing 'x' and 'y'.
    #
    def union(self, x: int, y: int) -> None:
        x = self.find(x)
        y = self.find(y)

        if x == y:
            return

        if self.rank[x] < self.rank[y]:
            self.parent[x] = y
            self.rank[y] += self.rank[x]
        else:
            self.parent[y] = x
            self.rank[x] += self.rank[y]

    #
    # Representation method
    #
    def __repr__(self) -> str:
        return "\n".join([self.parent, self.rank])
    
    #
    # String method
    #
    def __str__(self) -> str:
        return f"UnionFind(\n\tparent={self.parent}\n\trank  ={self.rank}\n)"
    

# Test the Union Find (Disjoint Sets) data structure if run as a script
if __name__ == "__main__":
    ds = UnionFind(10)

    # {0, 3, 6}
    ds.union(0, 3)
    ds.union(0, 6)

    # {1, 4, 7}
    ds.union(1, 4)
    ds.union(1, 7)

    # {2, 5, 8}
    ds.union(2, 5)
    ds.union(2, 8)

    # {0, 3, 6}, {1, 4, 7}, {2, 5, 8}, {9}
    print(ds)

    # Test union and find
    assert ds.find(0) == ds.find(3), "Test 1.1 failed: 0 and 3 should be connected"
    assert ds.find(0) == ds.find(6), "Test 1.2 failed: 0 and 6 should be connected"
    assert ds.find(3) == ds.find(0), "Test 1.3 failed: 3 and 0 should be connected"
    assert ds.find(3) == ds.find(6), "Test 1.4 failed: 3 and 6 should be connected"
    assert ds.find(6) == ds.find(0), "Test 1.5 failed: 6 and 0 should be connected"
    assert ds.find(6) == ds.find(3), "Test 1.6 failed: 6 and 3 should be connected"

    # Additional union and find tests
    assert ds.find(1) == ds.find(4), "Test 2.1 failed: 1 and 4 should be connected"
    assert ds.find(4) == ds.find(7), "Test 2.2 failed: 4 and 7 should be connected"
    assert ds.find(2) == ds.find(5), "Test 2.3 failed: 2 and 5 should be connected"
    assert ds.find(5) == ds.find(8), "Test 2.4 failed: 5 and 8 should be connected"

    # Test nodes from different sets
    assert ds.find(0) != ds.find(1), "Test 3.1 failed: 0 and 1 should not be connected"
    assert ds.find(0) != ds.find(2), "Test 3.2 failed: 0 and 2 should not be connected"
    assert ds.find(9) != ds.find(1), "Test 3.3 failed: 9 and 1 should not be connected"

    # Test a single isolated element
    assert ds.find(9) == 9, "Test 4 failed: 9 should be its own set"

    print("All tests passed.")