
''' The flipper kernel.

Some of the functions and methods have assumptions on them. We denote
in a functions docstring:

 - *Assumes that* ...
        If the assumptions are met then this function is guaranteed to terminate correctly.
        If not then this function will either:
        
            - terminate correctly, OR
            - a flipper.AssumptionError will be raised.
    
 - *Assumes (and checks) that* ...
        If the assumptions are met then this function is guaranteed to terminate correctly.
        If not then this a flipper.AssumptionError will be raised. '''

from realalg import RealNumberField, RealAlgebraic  # noqa: F401

from .bundle import Bundle  # noqa: F401
from .encoding import Encoding  # noqa: F401
from .error import AssumptionError, ComputationError, FatalError, ApproximationError, AbortError  # noqa: F401
from .equippedtriangulation import EquippedTriangulation  # noqa: F401
from .flatstructure import FlatStructure, Vector2  # noqa: F401
from .lamination import Lamination  # noqa: F401
from .matrix import Matrix, id_matrix, zero_matrix, dot  # noqa: F401
from .moves import Move, Isometry, EdgeFlip, LinearTransformation  # noqa: F401
from .permutation import Permutation  # noqa: F401
from .splittingsequence import SplittingSequence, SplittingSequences  # noqa: F401
from .triangulation import Vertex, Edge, Triangle, Triangulation, Corner, norm  # noqa: F401
from .triangulation3 import Tetrahedron, Triangulation3  # noqa: F401

from . import utilities  # noqa: F401

# Functions that help with construction.
from .taut import monodromy_from_bundle  # noqa: F401
create_triangulation = Triangulation.from_tuple
triangulation_from_iso_sig = Triangulation.from_string
create_equipped_triangulation = EquippedTriangulation.from_tuple

