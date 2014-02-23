
import Flipper.kernel.abstracttriangulation
import Flipper.kernel.algebraicapproximation
import Flipper.kernel.encoding
import Flipper.kernel.error
import Flipper.kernel.interval
import Flipper.kernel.isometry
import Flipper.kernel.lamination
import Flipper.kernel.layeredtriangulation
import Flipper.kernel.matrix
import Flipper.kernel.numberfield
import Flipper.kernel.permutation
import Flipper.kernel.splittingsequence
import Flipper.kernel.symboliccomputation
import Flipper.kernel.types
import Flipper.kernel.version

import Flipper.examples.abstracttriangulation
import Flipper.examples.lamination
import Flipper.examples.layeredtriangulation

import Flipper.tests.algebraicapproximation
import Flipper.tests.interval
import Flipper.tests.lamination
import Flipper.tests.layeredtriangulation
import Flipper.tests.matrix

import Flipper.application.main
import Flipper.application.mappingclass
import Flipper.application.pieces
import Flipper.application.progress
import Flipper.application.widgets

Lamination =  Flipper.kernel.lamination.Lamination
AbstractTriangulation = Flipper.kernel.abstracttriangulation.AbstractTriangulation
Isometry = Flipper.kernel.isometry.Isometry
LayeredTriangulation = Flipper.kernel.layeredtriangulation.LayeredTriangulation
Matrix = Flipper.kernel.matrix.Matrix

isometry_from_edge_map = Flipper.kernel.isometry.isometry_from_edge_map

AbortError = Flipper.kernel.error.AbortError
ApproximationError = Flipper.kernel.error.ApproximationError
AssumptionError = Flipper.kernel.error.AssumptionError
ComputationError = Flipper.kernel.error.ComputationError

Integer_Type = Flipper.kernel.types.Integer_Type
