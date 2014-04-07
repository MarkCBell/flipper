
from . import main
from . import pieces
from . import options
from . import inputbox
from . import progress
from . import widgets

# Set up shorter names for all of the different classes and some common constructors.
start = main.start
Options = options.Options
FlipperApp = main.FlipperApp
ColourPalette = pieces.ColourPalette
Vertex = pieces.Vertex
Edge = pieces.Edge
Triangle = pieces.Triangle
CurveComponent = pieces.CurveComponent
TrainTrackBlock = pieces.TrainTrackBlock
ProgressApp = progress.ProgressApp
SplitButton = widgets.SplitButton
Meter = widgets.Meter

lines_intersect = pieces.lines_intersect

apply_progression = progress.apply_progression
get_input = inputbox.get_input

