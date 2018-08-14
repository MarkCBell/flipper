
''' A module for representing basic ways of changing triangulations.

Provides three classes: Isometry, EdgeFlip and LinearTransformation.

Perhaps in the future we will add a Spiral move so that curves can be
shortened in polynomial time. '''

import flipper

class Move(object):
    ''' This represents an abstract move between triangulations and provides the framework for subclassing. '''
    def __init__(self, source_triangulation, target_triangulation):
        assert isinstance(source_triangulation, flipper.kernel.Triangulation)
        assert isinstance(target_triangulation, flipper.kernel.Triangulation)
        
        self.source_triangulation = source_triangulation
        self.target_triangulation = target_triangulation
        self.zeta = self.source_triangulation.zeta
    
    def __repr__(self):
        return str(self)
    
    def __call__(self, other):
        if isinstance(other, flipper.kernel.Lamination):
            if other.triangulation != self.source_triangulation:
                raise TypeError('Cannot apply Isometry to a lamination not on the source triangulation.')
            
            return self.target_triangulation.lamination(
                self.apply_geometric(other.geometric),
                self.apply_algebraic(other.algebraic),
                remove_peripheral=False)
        else:
            return NotImplemented
    
    def apply_geometric(self, vector):  # pylint: disable=unused-argument, no-self-use
        ''' Return the list of geometric intersection numbers corresponding to the image of the given lamination under self. '''
        
        return NotImplemented
    
    def apply_algebraic(self, vector):  # pylint: disable=unused-argument, no-self-use
        ''' Return the list of algebraic intersection numbers corresponding to the image of the given lamination under self. '''
        
        return NotImplemented
    
    def encode(self):
        ''' Return the Encoding induced by this isometry. '''
        
        return flipper.kernel.Encoding([self])

class Isometry(Move):
    ''' This represents an isometry from one Triangulation to another.
    
    Triangulations can create the isometries between themselves and this
    is the standard way users are expected to create these. '''
    def __init__(self, source_triangulation, target_triangulation, label_map):
        ''' This represents an isometry from source_triangulation to target_triangulation.
        
        It is given by a map taking each edge label of source_triangulation to a label of target_triangulation. '''
        
        assert isinstance(label_map, dict)
        
        super(Isometry, self).__init__(source_triangulation, target_triangulation)
        self.label_map = dict(label_map)
        
        self.flip_length = 0  # The number of flips needed to realise this move.
        
        # If we are missing any labels then use a depth first search to find the missing ones.
        # Hmmm, should always we do this just to check consistency?
        for i in self.source_triangulation.labels:
            if i not in self.label_map:
                raise flipper.AssumptionError('This label_map not defined on edge %d.' % i)
        
        self.index_map = dict((i, flipper.kernel.norm(self.label_map[i])) for i in self.source_triangulation.indices)
        # Store the inverses too while we're at it.
        self.inverse_label_map = dict((self.label_map[i], i) for i in self.source_triangulation.labels)
        self.inverse_index_map = dict((i, flipper.kernel.norm(self.inverse_label_map[i])) for i in self.source_triangulation.indices)
        self.inverse_signs = dict((i, +1 if self.inverse_index_map[i] == self.inverse_label_map[i] else -1) for i in self.source_triangulation.indices)
    
    def __str__(self):
        return 'Isometry ' + str([self.target_triangulation.edge_lookup[self.label_map[i]] for i in self.source_triangulation.indices])
    def __reduce__(self):
        return (self.__class__, (self.source_triangulation, self.target_triangulation, self.label_map))
    def __len__(self):
        return 1  # The number of pieces of this move.
    def package(self):
        ''' Return a small amount of data such that self.source_triangulation.encode([data]) == self.encode(). '''
        
        if not all(self.label_map[i] == i for i in self.source_triangulation.indices):  # If self is not the identity isometry.
            return {i: self.label_map[i] for i in self.source_triangulation.labels}
        else:
            return None
    
    def apply_geometric(self, vector):
        return [vector[self.inverse_index_map[i]] for i in range(self.zeta)]
    
    def apply_algebraic(self, vector):
        return [vector[self.inverse_index_map[i]] * self.inverse_signs[i] for i in range(self.zeta)]
    
    def inverse(self):
        ''' Return the inverse of this isometry. '''
        
        # inverse_corner_map = dict((self(corner), corner) for corner in self.corner_map)
        return Isometry(self.target_triangulation, self.source_triangulation, self.inverse_label_map)
    
    def applied_geometric(self, lamination, action):
        ''' Return the action and condition matrices describing the PL map
        applied to the geometric coordinates of the given lamination after
        post-multiplying by the action matrix. '''
        
        assert isinstance(lamination, flipper.kernel.Lamination)
        assert isinstance(action, flipper.kernel.Matrix)
        
        return flipper.kernel.Matrix([action[self.inverse_index_map[i]] for i in range(self.zeta)]), flipper.kernel.zero_matrix(0)
    
    def pl_action(self, index, action):
        ''' Return the action and condition matrices describing the PL map
        applied to the geometric coordinates by the cell of the specified index
        after post-multiplying by the action matrix. '''
        
        assert isinstance(index, flipper.IntegerType)
        assert isinstance(action, flipper.kernel.Matrix)
        
        return (flipper.kernel.Matrix([action[self.inverse_index_map[i]] for i in range(self.zeta)]), flipper.kernel.zero_matrix(0))
    
    def extend_bundle(self, triangulation3, tetra_count, upper_triangulation, lower_triangulation, upper_map, lower_map):  # pylint: disable=unused-argument, too-many-arguments
        ''' Modify triangulation3 to extend the embedding of upper_triangulation via upper_map under this move. '''
        
        maps_to_triangle = lambda X: isinstance(X[0], flipper.kernel.Triangle)
        
        # These are the new maps onto the upper and lower boundary that we will build.
        new_upper_map = dict()
        new_lower_map = dict()  # We are allowed to leave blanks in new_lower_map.
        
        for triangle in upper_triangulation:
            new_triangle = self.target_triangulation.triangle_lookup[self.label_map[triangle.labels[0]]]
            new_corner = self.target_triangulation.corner_lookup[self.label_map[triangle.corners[0].label]]
            perm = flipper.kernel.permutation.cyclic_permutation(new_corner.side - 0, 3)
            old_target, old_perm = upper_map[triangle]
            
            if maps_to_triangle(upper_map[triangle]):
                new_upper_map[new_triangle] = (old_target, old_perm * perm.inverse())
                # Don't forget to update the lower_map too.
                new_lower_map[old_target] = (new_triangle, perm * old_perm.inverse())
            else:
                new_upper_map[new_triangle] = (old_target, old_perm * perm.inverse().embed(4))
        
        # Remember to rebuild the rest of lower_map, which hasn't changed.
        for triangle in lower_triangulation:
            if triangle not in new_lower_map:
                new_lower_map[triangle] = lower_map[triangle]
        
        return tetra_count, self.target_triangulation, new_upper_map, new_lower_map

class EdgeFlip(Move):
    ''' Represents the change to a lamination caused by flipping an edge. '''
    def __init__(self, source_triangulation, target_triangulation, edge_label):
        super(EdgeFlip, self).__init__(source_triangulation, target_triangulation)
        assert isinstance(edge_label, flipper.IntegerType)
        
        self.flip_length = 1  # The number of flips needed to realise this move.
        self.edge_label = edge_label
        self.edge_index = flipper.kernel.norm(self.edge_label)
        self.zeta = self.source_triangulation.zeta
        assert self.source_triangulation.is_flippable(self.edge_index)
        
        self.square = self.source_triangulation.square_about_edge(self.edge_label)
    
    def __str__(self):
        return 'Flip %s%d' % ('' if self.edge_index == self.edge_label else '~', self.edge_index)
    def __reduce__(self):
        return (self.__class__, (self.source_triangulation, self.target_triangulation, self.edge_label))
    def __len__(self):
        return 2  # The number of pieces of this move.
    def package(self):
        ''' Return a small amount of data such that self.source_triangulation.encode([data]) == self.encode(). '''
        
        return self.edge_label
    
    def apply_geometric(self, vector):
        a, b, c, d = self.square
        m = max(vector[a.index] + vector[c.index], vector[b.index] + vector[d.index]) - vector[self.edge_index]
        return [vector[i] if i != self.edge_index else m for i in range(self.zeta)]
    
    def apply_algebraic(self, vector):
        a, b, c, d = self.square
        m = b.sign() * vector[b.index] + c.sign() * vector[c.index]
        return [vector[i] if i != self.edge_index else m for i in range(self.zeta)]
    
    def inverse(self):
        ''' Return the inverse of this map. '''
        
        return EdgeFlip(self.target_triangulation, self.source_triangulation, ~self.edge_label)
    
    def applied_geometric(self, lamination, action):
        ''' Return the action and condition matrices describing the PL map
        applied to the geometric coordinates of the given lamination after
        post-multiplying by the action matrix. '''
        
        assert isinstance(lamination, flipper.kernel.Lamination)
        assert isinstance(action, flipper.kernel.Matrix)
        
        a, b, c, d, e = [edge.index for edge in self.square] + [self.edge_index]
        
        rows = [list(row) for row in action]
        if lamination(a) + lamination(c) >= lamination(b) + lamination(d):
            rows[e] = [rows[a][i] + rows[c][i] - rows[e][i] for i in range(self.zeta)]
            Cs = flipper.kernel.Matrix([[action[a][i] + action[c][i] - action[b][i] - action[d][i] for i in range(self.zeta)]])
        else:
            rows[e] = [rows[b][i] + rows[d][i] - rows[e][i] for i in range(self.zeta)]
            Cs = flipper.kernel.Matrix([[action[b][i] + action[d][i] - action[a][i] - action[c][i] for i in range(self.zeta)]])
        return flipper.kernel.Matrix(rows), Cs
    
    def pl_action(self, index, action):
        ''' Return the action and condition matrices describing the PL map
        applied to the geometric coordinates by the cell of the specified index
        after post-multiplying by the action matrix. '''
        
        assert isinstance(index, flipper.IntegerType)
        assert isinstance(action, flipper.kernel.Matrix)
        
        a, b, c, d, e = [edge.index for edge in self.square] + [self.edge_index]
        
        rows = [list(row) for row in action]
        if index == 0:
            rows[e] = [rows[a][i] + rows[c][i] - rows[e][i] for i in range(self.zeta)]
            Cs = flipper.kernel.Matrix([[action[a][i] + action[c][i] - action[b][i] - action[d][i] for i in range(self.zeta)]])
        elif index == 1:
            rows[e] = [rows[b][i] + rows[d][i] - rows[e][i] for i in range(self.zeta)]
            Cs = flipper.kernel.Matrix([[action[b][i] + action[d][i] - action[a][i] - action[c][i] for i in range(self.zeta)]])
        else:
            raise IndexError('Index out of range.')
        return flipper.kernel.Matrix(rows), Cs
    
    def extend_bundle(self, triangulation3, tetra_count, upper_triangulation, lower_triangulation, upper_map, lower_map):  # pylint: disable=too-many-arguments
        
        ''' Modify triangulation3 to extend the embedding of upper_triangulation via upper_map under this move. '''
        
        assert upper_triangulation == self.source_triangulation
        
        # We use these two functions to quickly tell what a triangle maps to.
        maps_to_triangle = lambda X: isinstance(X[0], flipper.kernel.Triangle)
        maps_to_tetrahedron = lambda X: not maps_to_triangle(X)
        
        # These are the new maps onto the upper and lower boundary that we will build.
        new_upper_map = dict()
        new_lower_map = dict()
        # We are allowed to leave blanks in new_lower_map.
        # These will be filled in at the end using lower_map.
        new_upper_triangulation = self.target_triangulation
        VEERING_LEFT, VEERING_RIGHT = flipper.kernel.triangulation3.VEERING_LEFT, flipper.kernel.triangulation3.VEERING_RIGHT
        
        # Get the next tetrahedra to add.
        tetrahedron = triangulation3.tetrahedra[tetra_count]
        
        # Setup the next tetrahedron.
        tetrahedron.edge_labels[(0, 1)] = VEERING_RIGHT
        tetrahedron.edge_labels[(1, 2)] = VEERING_LEFT
        tetrahedron.edge_labels[(2, 3)] = VEERING_RIGHT
        tetrahedron.edge_labels[(0, 3)] = VEERING_LEFT
        
        edge_label = self.edge_label  # The edge to flip.
        
        # We'll glue it into the core_triangulation so that it's 1--3 edge lies over edge_label.
        # WARNINNG: This is reliant on knowing how flipper.kernel.Triangulation.flip_edge() relabels things!
        cornerA = upper_triangulation.corner_of_edge(edge_label)
        cornerB = upper_triangulation.corner_of_edge(~edge_label)
        
        # We'll need to swap sides on an inverse edge so our convertions below work.
        if edge_label != self.edge_index: cornerA, cornerB = cornerB, cornerA
        
        (A, side_A), (B, side_B) = (cornerA.triangle, cornerA.side), (cornerB.triangle, cornerB.side)
        if maps_to_tetrahedron(upper_map[A]):
            tetra, perm = upper_map[A]
            tetrahedron.glue(2, tetra, flipper.kernel.permutation.permutation_from_pair(0, perm(side_A), 2, perm(3)))
        else:
            tri, perm = upper_map[A]
            new_lower_map[tri] = (tetrahedron, flipper.kernel.permutation.permutation_from_pair(perm(side_A), 0, 3, 2))
        
        if maps_to_tetrahedron(upper_map[B]):
            tetra, perm = upper_map[B]
            # The permutation needs to: 2 |--> perm(3), 0 |--> perm(side_A), and be odd.
            tetrahedron.glue(0, tetra, flipper.kernel.permutation.permutation_from_pair(2, perm(side_B), 0, perm(3)))
        else:
            tri, perm = upper_map[B]
            new_lower_map[tri] = (tetrahedron, flipper.kernel.permutation.permutation_from_pair(perm(side_B), 2, 3, 0))
        
        # Rebuild the upper_map.
        new_cornerA = new_upper_triangulation.corner_of_edge(edge_label)
        new_cornerB = new_upper_triangulation.corner_of_edge(~edge_label)
        new_A, new_B = new_cornerA.triangle, new_cornerB.triangle
        # Most of the triangles have stayed the same.
        # This relies on knowing how the upper_triangulation.flip_edge() function works.
        old_fixed_triangles = [triangle for triangle in upper_triangulation if triangle not in (A, B)]
        new_fixed_triangles = [triangle for triangle in new_upper_triangulation if triangle not in (new_A, new_B)]
        for old_triangle, new_triangle in zip(old_fixed_triangles, new_fixed_triangles):
            new_upper_map[new_triangle] = upper_map[old_triangle]
            if maps_to_triangle(upper_map[old_triangle]):  # Don't forget to update the lower_map too.
                target_triangle, perm = upper_map[old_triangle]
                new_lower_map[target_triangle] = (new_triangle, perm.inverse())
        
        # This relies on knowing how the upper_triangulation.flip_edge() function works.
        perm_A = flipper.kernel.permutation.cyclic_permutation(new_upper_triangulation.corner_of_edge(edge_label).side, 3)
        perm_B = flipper.kernel.permutation.cyclic_permutation(new_upper_triangulation.corner_of_edge(~edge_label).side, 3)
        new_upper_map[new_A] = (tetrahedron, flipper.kernel.Permutation((3, 0, 2, 1)) * perm_A.embed(4).inverse())
        new_upper_map[new_B] = (tetrahedron, flipper.kernel.Permutation((1, 2, 0, 3)) * perm_B.embed(4).inverse())
        
        # Remember to rebuild the rest of lower_map, which hasn't changed.
        for triangle in lower_triangulation:
            if triangle not in new_lower_map:
                new_lower_map[triangle] = lower_map[triangle]
        
        return tetra_count+1, self.target_triangulation, new_upper_map, new_lower_map

class LinearTransformation(Move):
    ''' Represents the change to a lamination caused by a linear map. '''
    def __init__(self, source_triangulation, target_triangulation, geometric, algebraic):
        super(LinearTransformation, self).__init__(source_triangulation, target_triangulation)
        assert isinstance(geometric, flipper.kernel.Matrix)
        assert isinstance(algebraic, flipper.kernel.Matrix)
        
        self.flip_length = 0  # The number of flips needed to realise this move.
        self.geometric = geometric
        self.algebraic = algebraic
    
    def __str__(self):
        return str(self.geometric) + str(self.algebraic)
    def __len__(self):
        return 1  # The number of pieces of this move.
    def package(self):
        ''' Return a small amount of data such that self.source_triangulation.encode([data]) == self.encode(). '''
        
        return self
    
    def apply_geometric(self, vector):
        return self.geometric(vector)
    def apply_algebraic(self, vector):
        return self.algebraic(vector)
    
    def inverse(self):  # pylint: disable=no-self-use
        ''' Return the inverse of this map.
        
        Note that these do not exist and so NotImplemented is returned. '''
        
        return NotImplemented
    
    def applied_geometric(self, lamination, action):
        ''' Return the action and condition matrices describing the PL map
        applied to the geometric coordinates of the given lamination after
        post-multiplying by the action matrix. '''
        
        assert isinstance(lamination, flipper.kernel.Lamination)
        assert isinstance(action, flipper.kernel.Matrix)
        
        return self.geometric * action, flipper.kernel.zero_matrix(0)
    
    def pl_action(self, index, action):
        ''' Return the action and condition matrices describing the PL map
        applied to the geometric coordinates by the cell of the specified index
        after post-multiplying by the action matrix. '''
        
        assert isinstance(index, flipper.IntegerType)
        assert isinstance(action, flipper.kernel.Matrix)
        
        return (self.geometric * action, flipper.kernel.zero_matrix(0))

