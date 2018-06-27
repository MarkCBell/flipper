
''' A module for representing triangulations of surface bundles over the circle.

Provides one class: Bundle. '''

import flipper

class Bundle(object):
    ''' This represents a triangulation of a surface bundle over the circle.
    
    It is specified by a triangulation of the surface, a triangulation of the
    bundle and an immersion map. Mapping classes can build their bundles and
    this is the standard way users are expected to create these. '''
    def __init__(self, triangulation, triangulation3, immersion):
        assert isinstance(triangulation, flipper.kernel.Triangulation)
        assert isinstance(triangulation3, flipper.kernel.Triangulation3)
        assert isinstance(immersion, dict)
        assert all(triangle in immersion for triangle in triangulation)
        assert all(isinstance(immersion[triangle], (list, tuple)) for triangle in triangulation)
        assert all(len(immersion[triangle]) == 2 for triangle in triangulation)
        assert all(isinstance(immersion[triangle][0], flipper.kernel.Tetrahedron) for triangle in triangulation)
        assert all(isinstance(immersion[triangle][1], flipper.kernel.Permutation) for triangle in triangulation)
        
        self.triangulation = triangulation
        self.triangulation3 = triangulation3
        self.immersion = immersion
        # This is a dict mapping:
        #   triangle |---> (tetrahedra, perm).
        
        assert self.triangulation3.is_closed()
    
    def __repr__(self):
        return str(self)
    def __str__(self):
        return str(self.triangulation3)
    
    def snappy_string(self, name='flipper_triangulation', filled=True):
        ''' Return the SnapPy string describing this triangulation.
        
        If filled=True then the fake cusps are filled along their fibre slope. '''
        
        fillings = [slope if filled_cusp else (0, 0) for filled_cusp, slope in zip(self.cusp_types(), self.fibre_slopes())] if filled else None
        return self.triangulation3.snappy_string(name, fillings)
    
    def __snappy__(self):
        return self.snappy_string()
    
    def cusp_types(self):
        ''' Return the list of the type of each cusp. '''
        
        cusp_types = [None] * self.triangulation3.num_cusps
        
        for corner_class in self.triangulation.corner_classes:
            vertex = corner_class[0].vertex
            filled = vertex.filled
            for corner in corner_class:
                tetrahedron, permutation = self.immersion[corner.triangle]
                index = tetrahedron.cusp_indices[permutation(corner.side)]
                if cusp_types[index] is None:
                    cusp_types[index] = filled
                else:
                    assert cusp_types[index] == filled
        
        return cusp_types
        
    def fibre_slopes(self):
        ''' Return the list of fibre slopes on each cusp. '''
        
        LONGITUDES, MERIDIANS = flipper.kernel.triangulation3.LONGITUDES, flipper.kernel.triangulation3.MERIDIANS
        
        slopes = [None] * self.triangulation3.num_cusps
        
        for index in range(self.triangulation3.num_cusps):
            meridian_intersection, longitude_intersection = 0, 0
            for corner_class in self.triangulation.corner_classes:
                corner = corner_class[0]
                tetra, perm = self.immersion[corner.triangle]
                if tetra.cusp_indices[perm(corner.side)] == index:
                    for corner in corner_class:
                        tetra, perm = self.immersion[corner.triangle]
                        side, other = perm(corner.side), perm(3)
                        meridian_intersection += tetra.peripheral_curves[MERIDIANS][side][other]
                        longitude_intersection += tetra.peripheral_curves[LONGITUDES][side][other]
                    slopes[index] = (longitude_intersection, -meridian_intersection)
                    break
            else:
                raise RuntimeError('No vertex was mapped to this cusp.')
        
        return slopes
        
    def degeneracy_slopes(self):
        ''' Return the list of degeneracy slopes on each cusp.
        
        This triangulation is must be veering. '''
        
        assert self.triangulation3.is_veering()
        
        VEERING_LEFT, VEERING_RIGHT = flipper.kernel.triangulation3.VEERING_LEFT, flipper.kernel.triangulation3.VEERING_RIGHT
        TEMPS = flipper.kernel.triangulation3.TEMPS
        VERTICES_MEETING = flipper.kernel.triangulation3.VERTICES_MEETING
        EXIT_CUSP_LEFT, EXIT_CUSP_RIGHT = flipper.kernel.triangulation3.EXIT_CUSP_LEFT, flipper.kernel.triangulation3.EXIT_CUSP_RIGHT
        
        slopes = [None] * self.triangulation3.num_cusps
        
        cusp_pairing = self.triangulation3.cusp_identification_map()
        for index, cusp in enumerate(self.triangulation3.cusps):
            self.triangulation3.clear_temp_peripheral_structure()
            
            # Set the degeneracy curve into the TEMPS peripheral structure.
            # First find a good starting point:
            start_tetrahedron, start_side = cusp[0]
            edge_labels = [start_tetrahedron.get_edge_label(start_side, other) for other in VERTICES_MEETING[start_side]]
            for i in range(3):
                if edge_labels[(i+1) % 3] == VEERING_RIGHT and edge_labels[(i+2) % 3] == VEERING_LEFT:
                    start_other = VERTICES_MEETING[start_side][i]
                    break
            
            # Then walk around, never crossing through an edge where both ends veer the same way.
            current_tetrahedron, current_side, current_other = start_tetrahedron, start_side, start_other
            while True:
                current_tetrahedron.peripheral_curves[TEMPS][current_side][current_other] += 1
                if start_tetrahedron.get_edge_label(current_side, current_other) == VEERING_LEFT:
                    leave = EXIT_CUSP_LEFT[(current_side, current_other)]
                else:
                    leave = EXIT_CUSP_RIGHT[(current_side, current_other)]
                current_tetrahedron.peripheral_curves[TEMPS][current_side][leave] -= 1
                current_tetrahedron, current_side, current_other = cusp_pairing[(current_tetrahedron, current_side, leave)]
                if (current_tetrahedron, current_side, current_other) == (start_tetrahedron, start_side, start_other):
                    break
            
            slopes[index] = self.triangulation3.slope()
        
        return slopes

