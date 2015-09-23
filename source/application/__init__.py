
''' The flipper GUI application. '''

from . import main
from . import pieces
from . import options
from . import inputbox
from . import choicebox
from . import progress
from . import widgets

# Set up shorter names for all of the different classes and some common constructors.
start = main.start
Options = options.Options
FlipperApplication = main.FlipperApplication
ColourPalette = pieces.ColourPalette
CanvasVertex = pieces.CanvasVertex
CanvasEdge = pieces.CanvasEdge
CanvasTriangle = pieces.CanvasTriangle
CurveComponent = pieces.CurveComponent
TrainTrackBlock = pieces.TrainTrackBlock
ProgressApp = progress.ProgressApp
SplitButton = widgets.SplitButton
Meter = widgets.Meter
AnimatedCanvas = widgets.AnimatedCanvas

lines_intersect = pieces.lines_intersect
interpolate = pieces.interpolate

apply_progression = progress.apply_progression
get_input = inputbox.get_input
get_choice = choicebox.get_choice

