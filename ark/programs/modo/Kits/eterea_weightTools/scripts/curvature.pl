#perl

###########################################
#
# Bake curvature to vertex colour.
#  v 1.0
#  by James O'Hare
#  www.farfarer.com
#  jamesohare@gmail.com
#
#
# Description:
#  Bakes out normalized per-vertex convexity to RGBA vertex map.
#  Includes options for concavity/convexity/both and for which or all RGBA channels.
#
#  It will apply to either only current vertex selection or - if no vertices are selected - to all visible vertices.
#  Be aware that the values will be normalized within the current selection if you have one.
#
#
# Usage:
#  @curvature.pl abs/inv r/g/b/a
#
#  Both arguments are optional.
#
#  Argument 1:
#   abs - Absolute. Will bake the absolute curvature map (convex and concave = 1, mid-range = 0).
#   inv - Invert. Will bake the inverse convexity map (convex = 0, concave = 1).
#   No argument given will bake standard convexity map (convex = 1, concave = 0).
#
#  Argument 2:
#   r - will bake to the red channel.
#   g - will bake to the green channel.
#   b - will bake to the blue channel.
#   a - will bake to the alpha channel.
#   No argument given will bake to all RGBA channels.
#
#  Examples:
#   @curvature.pl b			(bake the curvature to the blue channel)
#   @curvature.pl abs g		(bake the absolute curvature to the green channel)
#   @curvature.pl inv		(bake the inverse curvature to all rgba channels)
#
###########################################

# Default names for the vertex maps used by the script.
# Change these here if they conflict with maps you're already using.
$colMapName = "Color";			# Name of the RGBA colour map.
$colTempMapName = "ColorTemp";	# Name of the temporary RGBA colour map.
$curvMapName = "CurvatureTemp"; # Name of the curvature weight map.

# Find out what we're baking and whether we should use the second argument for RGBA channel.
my $useArg2 = 0;
if ( lc(@ARGV[0]) eq "abs" ) {
	lx("vertMap.bakeConvexity $curvMapName both 1.0 false false");
	$useArg2 = 1;
}
elsif ( lc(@ARGV[0]) eq "inv" ) {
	lx("vertMap.bakeConvexity $curvMapName concavity 1.0 false false");
	$useArg2 = 1;
}
else {
	lx("vertMap.bakeConvexity $curvMapName convexity 1.0 false false");
}

# Find out what RGBA channel we're baking to, if any.
# Default to -1 (all channels).
my $channel = -1;

# Depending on which argument we're using to get it from.
if ($useArg2) {
	$channel = @ARGV[1];
} else {
	$channel = @ARGV[0];
}

# See if the argument is a channel.
if (lc($channel) eq "r") {
	$channel = 0;
}
elsif (lc($channel) eq "g") {
	$channel = 1;
}
elsif (lc($channel) eq "b") {
	$channel = 2;
}
elsif (lc($channel) eq "a") {
	$channel = 3;
}
else {
	# Otherwise back to default it goes.
	$channel = -1;
}

# Find the convexity map we just baked.
my $curvMap;
my @vmaps = lxq("query layerservice vmaps ? weight");
foreach $vmap (@vmaps) {
	my $vmapName = lxq("query layerservice vmap.name ? $vmap");
	if ($vmapName eq $curvMapName) {
		$curvMap = $vmap;
		last;
	}
}

# Set up some default values. Hopefully way in excess of what the bake will give.
my $multiplier = 1.0;
my $minValue = 99999.0;
my $maxValue = -99999.0;

# Get the selected verts (if there are any selected) or all visible verts (if not).
my @vertices;
if (lxq("query layerservice vert.N ? selected") == 0) {
	@vertices = lxq( "query layerservice verts ? visible" );
} else {
	@vertices = lxq( "query layerservice verts ? selected" );
}

# Go through the verts and figure out the highest and lowest values.
# From there we can figure out how to normalize all of them to 0-1.
my $selVMap = lxq( "query layerservice vmap.index ? $curvMap" );
foreach my $vert (@vertices) {
	my $value = lxq( "query layerservice vert.vmapValue ? $vert" );

	if ($value > $maxValue) {
		$maxValue = $value;
	}
	elsif ($value < $minValue) {
		$minValue = $value;
	}
}

# Work out the vales we need to change the vmap values by to normalize it 0-1.
$multiplier = 1.0 / ($maxValue - $minValue);
$minValue *= -1.0; # Invert the minValue here as we'll be subtracting this in the next step. I feel safer doing it here.

# Multiply by multiplier and subtract the minValue.
# This normalizes the map into the 0-1 range.
lx("vertMap.math \"WGHT[1]:$curvMapName\" \"WGHT[1]:$curvMapName\" $multiplier $minValue direct 0 \"\" 0.0 0.0 direct 0");

if ($channel == -1) {
	# If we're just applying it clean out to all RGBA channels, this is easier.
	# Copy curvature to vertex rgba.
	lx("vertMap.math \"RGBA[4]:$colMapName\" \"WGHT[1]:$curvMapName\" 1.0 0.0 component 0 \"WGHT[1]:$curvMapName\" 0.0 0.0 component 0");
}
else {
	# Otherwise we're going to have to do a bit of juggling to allow vertMap.math to work nicely.

	# Create a temporary rgba map.
	# Copy curvature to all channels.
	lx("vertMap.new $colTempMapName rgba true {0.0 0.0 0.0} 0.0");
	lx("vertMap.math \"RGBA[4]:$colTempMapName\" \"WGHT[1]:$curvMapName\" 1.0 0.0 component 0 \"WGHT[1]:$curvMapName\" 0.0 0.0 direct 0");

	# Check to see if we need to create an rgba map.
	# Must be an easier way of checking whether a vertex map exists?
	my $needsColMap = 1;
	my @colVmaps = lxq("query layerservice vmaps ? rgba");
	foreach $colVmap (@colVmaps) {
		my $colVmapName = lxq("query layerservice vmap.name ? $colVmap");
		if ($colVmapName eq $colMapName) {
			$needsColMap = 0;
			last;
		}
	}
	if ($needsColMap) {
		# When creating an rgba map, I'm defaulting to alpha being 1.
		# This seems like it would cause the least amount of issues overall.
		# If you want it to be 0 for some reason, change the last number here from 1.0 to 0.0.
		lx("vertMap.new $colMapName rgba true {0.0 0.0 0.0} 1.0");
	}

	# Blank the channels of the temp rgba map we don't want.
	# Blank the channel of the rgba map we're replacing.
	if ($channel == 0) { # Red
		lx("select.vertexMap $colTempMapName rgba replace");
		lx("vertMap.setValue rgba 1 0.0"); # G
		lx("vertMap.setValue rgba 2 0.0"); # B
		lx("vertMap.setValue rgba 3 0.0"); # A
		lx("select.vertexMap $colMapName rgba replace");
		lx("vertMap.setValue rgba 0 0.0"); # R
	}
	elsif ($channel == 1) { # Green
		lx("select.vertexMap $colTempMapName rgba replace");
		lx("vertMap.setValue rgba 0 0.0"); # R
		lx("vertMap.setValue rgba 2 0.0"); # B
		lx("vertMap.setValue rgba 3 0.0"); # A
		lx("select.vertexMap $colMapName rgba replace");
		lx("vertMap.setValue rgba 1 0.0"); # G
	}
	elsif ($channel == 2) { # Blue
		lx("select.vertexMap $colTempMapName rgba replace");
		lx("vertMap.setValue rgba 0 0.0"); # R
		lx("vertMap.setValue rgba 1 0.0"); # G
		lx("vertMap.setValue rgba 3 0.0"); # A
		lx("select.vertexMap $colMapName rgba replace");
		lx("vertMap.setValue rgba 2 0.0"); # B
	}
	elsif ($channel == 3) { # Alpha
		lx("select.vertexMap $colTempMapName rgba replace");
		lx("vertMap.setValue rgba 0 0.0"); # R
		lx("vertMap.setValue rgba 1 0.0"); # G
		lx("vertMap.setValue rgba 2 0.0"); # B
		lx("select.vertexMap $colMapName rgba replace");
		lx("vertMap.setValue rgba 3 0.0"); # A
	}

	# Combine the temporary and proper rgba maps.
	lx("vertMap.math \"RGBA[4]:$colMapName\" \"RGBA[4]:$colMapName\" 1.0 0.0 direct 0 \"RGBA[4]:$colTempMapName\" 1.0 0.0 direct 0");

	# Select and delete the temporary rgba map. It's work is done.
	lx("select.vertexMap $colTempMapName rgba replace");
	lx("!!vertMap.delete rgba");
}
# Select and delete the curvature weight map. It's work is done.
lx("select.vertexMap $curvMapName wght replace");
lx("!!vertMap.delete wght");
# Select colour map.
lx("select.vertexMap $colMapName rgba replace");