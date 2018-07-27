#perl
#BY: Seneca Menard
#version 1.8 (modo3 update)
#This script is for doing micro bevels or extends, and then putting you back to whatever tool you were last using.
#
#-Works with VERTS, EDGES, and POLYGONS
#-It automatically deselects non-border edges for you.
#-In polygon mode, it bevels the polygons with join on to keep them together.
#-It retains any tool you're currently in.
#-If you're not using any tools, it'll put you in MOVE
#-If nothing's selected, it'll know to do nothing.
#new feature (7-17-05) This script will now work with CUSTOM action centers (ie. if you were using center=elemnet, axis= auto)
#bugfix (8-1-05) poly.extrude in custom workplanes would create duplicate verts, so i switched to bevel
#bugfix (9-30-06) the script now works properly with the new M2 transform tools.
#bugfix (8-9-07) now works properly in multiple layers <> supports ALL transform tools <> fixed M3 ACTR bug



#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================
#===																		 SETUP																		====
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================

my $modoVer = lxq("query platformservice appversion ?");
my $mainlayer = lxq("query layerservice layers ? main");
my @selectVerts;

#NEW tool preset--------------------------------------------------------
if		(lxq( "tool.set xfrm.move ?") eq "on")			{	our $tool = "xfrm.move";			}
elsif	(lxq("tool.set xfrm.rotate ?") eq "on")			{	our $tool = "xfrm.rotate";			}
elsif 	(lxq("tool.set xfrm.stretch ?") eq "on")		{	our $tool = "xfrm.stretch";			}
elsif 	(lxq("tool.set xfrm.scale ?") eq "on")			{	our $tool = "xfrm.scale";			}
elsif	(lxq("tool.set Transform ?") eq "on")			{	our $tool = "Transform";			}
elsif	(lxq("tool.set TransformMove ?") eq "on")		{	our $tool = "TransformMove";		}
elsif	(lxq("tool.set TransformScale ?") eq "on")		{	our $tool = "TransformScale";		}
elsif	(lxq("tool.set TransformUScale ?") eq "on")		{	our $tool = "TransformUScale";		}
elsif	(lxq("tool.set TransformRotate ?") eq "on")		{	our $tool = "TransformRotate";		}
else													{	our $tool = "TransformMove";		}
#------------------------------------------------------------------------------


#CONVERT THE SYMM AXIS TO MY OLDSCHOOL NUMBER AND TURN IT OFF
our $symmAxis = lxq("select.symmetryState ?");
if 		($symmAxis eq "none")	{	$symmAxis = 3;	}
elsif	($symmAxis eq "x")		{	$symmAxis = 0;	}
elsif	($symmAxis eq "y")		{	$symmAxis = 1;	}
elsif	($symmAxis eq "z")		{	$symmAxis = 2;	}
if		($symmAxis != 3)		{	lx("select.symmetryState none");	}

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#REMEMBER SELECTION SETTINGS and then set it to selectauto  ((MODO2 FIX))
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#sets the ACTR preset
our $seltype;
our $selAxis;
our $selCenter;
our $actr = 1;
if		(lxq( "tool.set actr.select ?") eq "on")			{	$seltype = "actr.select";		}
elsif	(lxq( "tool.set actr.selectauto ?") eq "on")		{	$seltype = "actr.selectauto";	}
elsif	(lxq( "tool.set actr.element ?") eq "on")			{	$seltype = "actr.element";		}
elsif	(lxq( "tool.set actr.screen ?") eq "on")			{	$seltype = "actr.screen";		}
elsif	(lxq( "tool.set actr.origin ?") eq "on")			{	$seltype = "actr.origin";		}
elsif	(lxq( "tool.set actr.local ?") eq "on")				{	$seltype = "actr.local";		}
elsif	(lxq( "tool.set actr.pivot ?") eq "on")				{	$seltype = "actr.pivot";		}
elsif	(lxq( "tool.set actr.auto ?") eq "on")				{	$seltype = "actr.auto";			}
else
{
	$actr = 0;
	lxout("custom Action Center");
	if		(lxq( "tool.set axis.select ?") eq "on")		{	 $selAxis = "select";			}
	elsif	(lxq( "tool.set axis.element ?") eq "on")		{	 $selAxis = "element";			}
	elsif	(lxq( "tool.set axis.view ?") eq "on")			{	 $selAxis = "view";				}
	elsif	(lxq( "tool.set axis.origin ?") eq "on")		{	 $selAxis = "origin";			}
	elsif	(lxq( "tool.set axis.local ?") eq "on")			{	 $selAxis = "local";			}
	elsif	(lxq( "tool.set axis.pivot ?") eq "on")			{	 $selAxis = "pivot";			}
	elsif	(lxq( "tool.set axis.auto ?") eq "on")			{	 $selAxis = "auto";				}
	else													{	 $actr = 1;  $seltype = "actr.auto"; lxout("You were using an action AXIS that I couldn't read");}

	if		(lxq( "tool.set center.select ?") eq "on")		{	 $selCenter = "select";			}
	elsif	(lxq( "tool.set center.element ?") eq "on")		{	 $selCenter = "element";		}
	elsif	(lxq( "tool.set center.view ?") eq "on")		{	 $selCenter = "view";			}
	elsif	(lxq( "tool.set center.origin ?") eq "on")		{	 $selCenter = "origin";			}
	elsif	(lxq( "tool.set center.local ?") eq "on")		{	 $selCenter = "local";			}
	elsif	(lxq( "tool.set center.pivot ?") eq "on")		{	 $selCenter = "pivot";			}
	elsif	(lxq( "tool.set center.auto ?") eq "on")		{	 $selCenter = "auto";			}
	else													{ 	 $actr = 1;  $seltype = "actr.auto"; lxout("You were using an action CENTER that I couldn't read");}
}
lx("tool.set actr.auto on");



#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================
#===																	 MAIN ROUTINES																====
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================

#VERT MODE
if( lxq( "select.typeFrom {vertex;edge;polygon;item} ?" ) ) {
	our @verts = lxq("query layerservice selection ? vert");

	#one vert = one vert setup
	if (@verts == 1){
		my @verts = lxq("query layerservice verts ? selected");
		&oneVertSetup(@verts);
	}
	#two vert = one vert setup or bevelittle
	elsif (@verts == 2){
		my @verts = lxq("query layerservice verts ? selected");
		my @pos1 = lxq("query layerservice vert.pos ? @verts[0]");
		my @pos2 = lxq("query layerservice vert.pos ? @verts[1]");

		if (($symmAxis != 3) && (@pos1[$symmAxis] == @pos2[$symmAxis]*-1)){
			&oneVertSetup(@verts);
		}else{
			&vertBevelittle;
		}
	}
	#over two vert = bevelittle
	elsif (@verts > 2) {
		&vertBevelittle;
	}
	#zero vert = die
	else{
		die("\n.\n[----------------------------------You don't have any verts selected, so I'm killing the script-------------------------------------]\n[--PLEASE TURN OFF THIS WARNING WINDOW by clicking on the (In the future) button and choose (Hide Message)--] \n[-----------------------------------This window is not supposed to come up, but I can't control that.---------------------------]\n.\n");
	}
}

#EDGE MODE
elsif( lxq( "select.typeFrom {edge;vertex;polygon;item} ?" ) ) {
	lx("select.edge remove poly equal 2");
	my @edges = lxq("query layerservice selection ? edge");
	if (@edges != 0) {
		lx("select.edge remove poly equal 2");
		lx("tool.set edge.extend on");
		lx("tool.attr edge.extend segs 1");
		lx("tool.attr edge.extend offZ [0 m]");
		lx("tool.attr edge.extend offX [0 m]");
		lx("tool.attr edge.extend offY [0 m]");
		lx("tool.doapply");
		lx("tool.set edge.extend off 0");
		if ($modoVer > 300){&restoreACTR;}
		}else{
			die("\n.\n[--------------------------------You don't have any border edges selected, so I can't run the script----------------------------]\n[--PLEASE TURN OFF THIS WARNING WINDOW by clicking on the (In the future) button and choose (Hide Message)--] \n[-----------------------------------This window is not supposed to come up, but I can't control that.---------------------------]\n.\n");
	}
}


#POLY MODE
elsif( lxq( "select.typeFrom {polygon;vertex;edge;item} ?" ) ) {
	my @polys = lxq("query layerservice selection ? poly");
	if (@polys != 0) {
		lx("tool.set poly.extrude on");
		lx("tool.reset");
		lx("tool.attr poly.extrude mode shift");
		lx("tool.attr poly.extrude shiftX 0");
		lx("tool.attr poly.extrude shiftY 0");
		lx("tool.attr poly.extrude shiftZ 0");
		lx("tool.attr poly.extrude segs 1");
		lx("tool.doapply");
		lx("tool.set poly.extrude off 0");
		if ($modoVer > 300){&restoreACTR;}
		}else{
			die("\n.\n[----------------------------------You don't have any polygons selected, so I can't run the script-------------------------------]\n[--PLEASE TURN OFF THIS WARNING WINDOW by clicking on the (In the future) button and choose (Hide Message)--] \n[-----------------------------------This window is not supposed to come up, but I can't control that.---------------------------]\n.\n");
	}
}

else {
	die("\n.\n[---------------------------------------------Must have verts, edges or polys selected!---------------------------------------------]\n[--PLEASE TURN OFF THIS WARNING WINDOW by clicking on the (In the future) button and choose (Hide Message)--] \n[-----------------------------------This window is not supposed to come up, but I can't control that.---------------------------]\n.\n");
}


#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================
#===																		 CLEANUP																	====
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================

#uses the new tool preset-------------------------------------------
lx("tool.set $tool on");
if (($modoVer < 300) && ($tool eq "TransformMove")){
	lx("tool.attr xfrm.transform H translate");
}
#------------------------------------------------------------------------------

#restore selection
if (@selectVerts > 0){
	lx("select.drop vertex");
	foreach my $vert (@selectVerts){
		lx("select.element $mainlayer vertex add $vert");
	}
}

#Set Symmetry back
if ($symmAxis != 3)
{
	#CONVERT MY OLDSCHOOL SYMM AXIS TO MODO's NEWSCHOOL NAME
	if 		($symmAxis == "3")	{	$symmAxis = "none";	}
	elsif	($symmAxis == "0")	{	$symmAxis = "x";		}
	elsif	($symmAxis == "1")	{	$symmAxis = "y";		}
	elsif	($symmAxis == "2")	{	$symmAxis = "z";		}
	lxout("turning symm back on ($symmAxis)"); lx("!!select.symmetryState $symmAxis");
}


#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================
#===																		 SUBROUTINES																====
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================

#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#ONE VERT SETUP SUB
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
sub oneVertSetup{
	foreach my $vert (@_){
		my @vertList = lxq("query layerservice vert.vertList ? $vert");
		if (@vertList < 2){
			my @polys = lxq("query layerservice vert.polyList ? $vert");
			if (@polys == 1){
				my $polyType = lxq("query layerservice poly.type ? @polys[0]");
				if (($polyType eq "subdiv") || ($polyType eq "face"))	{	&add2PtPoly($vert);		}
				elsif ($polyType eq "curve")							{	&extendCurve($vert);	}
				elsif ($polyType eq "bezier")							{	&extendBezier($vert);	}
			}
		}
		else{
			my @polys = lxq("query layerservice vert.polyList ? $vert");
			if (@polys == 1){
				my $polyType = lxq("query layerservice poly.type ? @polys[0]");
				if (($polyType eq "subdiv") || ($polyType eq "face")){
					&addPolyVert($vert);
				}else{
					die("\n.\n[------------------------------------------This vert add feature is only for multi point polys----------------------------------------]\n[--PLEASE TURN OFF THIS WARNING WINDOW by clicking on the (In the future) button and choose (Hide Message)--] \n[-----------------------------------This window is not supposed to come up, but I can't control that.---------------------------]\n.\n");
				}
			}else{
				die("\n.\n[-------------------This vert add feature is only for cases when your vert is connected to only one poly--------------------]\n[--PLEASE TURN OFF THIS WARNING WINDOW by clicking on the (In the future) button and choose (Hide Message)--] \n[-----------------------------------This window is not supposed to come up, but I can't control that.---------------------------]\n.\n");
			}
		}
	}
}

#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#ADD A 2 POINT POLY SUB
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
sub add2PtPoly{
	my @pos = lxq("query layerservice vert.pos ? @_[0]");
	my $vertCount = lxq("query layerservice vert.n ? all");
	push(@selectVerts,$vertCount);
	lx("vert.new @pos");
	lx("select.element $mainlayer vertex set @_[0]");
	lx("select.element $mainlayer vertex add $vertCount");
	lx("poly.makeFace");
}

#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#ADD A VERT TO THE POLY SUB
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
sub addPolyVert{

	#TEMP : NEED TO PUT IN SYMMETRICAL WEIGHTING.
	#if mouse not on same symm side as vert, flip it and run algo.  Then
	#save out weight position for next time and don't run the queries.

	my @vertList = lxq("query layerservice vert.vertList ? @_[0]");
	my $view = lxq("query view3dservice mouse.view ?");
	my @mousePos = lxq("query view3dservice mouse.pos ?");

	my @vertPos1 = lxq("query layerservice vert.pos ? @_[0]");
	my @vertPos2 = lxq("query layerservice vert.pos ? @vertList[0]");
	my @vertPos3 = lxq("query layerservice vert.pos ? @vertList[1]");

	#switch the mousePos if it's on the wrong symmAxis
	if (@verts == 2){
		lxout("[->] Using symm flip");
		if (((@mousePos[$symmAxis] > 1) && (@vertPos1[$symmAxis] < 1)) || ((@mousePos[$symmAxis] < 1) && (@vertPos1[$symmAxis] > 1))){
			lxout("flipping the mousePos");
			@mousePos[$symmAxis] *= -1;
		}else{
			lxout("not flipping the mousePos");
		}
	}

	my @vector1 = unitVector(arrMath(@vertPos1,@mousePos,subt));
	my @vector2 = unitVector(arrMath(@vertPos1,@vertPos2,subt));
	my @vector3 = unitVector(arrMath(@vertPos1,@vertPos3,subt));

	my $dp1 = dotProduct(\@vector1,\@vector2);
	my $dp2 = dotProduct(\@vector1,\@vector3);

	my $vert1 = $mainlayer-1 . "," . @_[0];
	if ($dp1 > $dp2)	{	our $vert2 =  $mainlayer-1 . "," . @vertList[0];	}
	else				{	our $vert2 =  $mainlayer-1 . "," . @vertList[1];	}

	#add the point with edge knife
	lx("tool.set edge.knife on");
	lx("tool.reset");
	lx("tool.attr edge.knife split 0");
	lx("tool.setAttr edge.knife count 1");
	lx("tool.setAttr edge.knife vert0 $vert1");
	lx("tool.setAttr edge.knife vert1 $vert2");
	lx("tool.setAttr edge.knife pos [50 %]");
	lx("tool.doApply");
	lx("tool.set edge.knife off");

	my $vertCount = lxq("query layerservice vert.n ? all")-1;
	lx("select.element $mainlayer vertex set $vertCount");
	my @movePos = lxq("query layerservice vert.pos ? @_[0]");
	lx("vert.set X @movePos[0]");
	lx("vert.set Y @movePos[1]");
	lx("vert.set Z @movePos[2]");
	push(@selectVerts,$vertCount);
}

#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#EXTEND A CURVE SUB
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
sub extendCurve{
	my @polys = lxq("query layerservice vert.polyList ? @_[0]");
	my @pos = lxq("query layerservice vert.pos ? @_[0]");
	my $vertCount = lxq("query layerservice vert.n ? all");
	push(@selectVerts,$vertCount);
	lx("vert.new @pos");
	lx("select.element $mainlayer vertex set @_[0]");
	lx("select.element $mainlayer vertex add $vertCount");
	lx("poly.makeFace");

	my $newestPoly = lxq("query layerservice poly.n ? all")-1;
	lx("select.drop polygon");
	lx("select.element $mainlayer polygon add @polys[0]");
	lx("select.element $mainlayer polygon add $newestPoly");
	lx("poly.merge");
}

#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#EXTEND A BEZIER CURVE SUB
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
sub extendBezier{
	my $runScript = 1;
	my $vert2;
	my $vertCount = lxq("query layerservice vert.n ? all");
	my @pos1 = lxq("query layerservice vert.pos ? @_[0]");
	my @pos2 = lxq("query layerservice vert.pos ? @_[0]-1");
	my @disp;
	my $check1 = 0;
	my $check2 = 0;

	#--------------------------------------------------------------
	#find which of the two verts is the handle vert.
	#--------------------------------------------------------------
	#vert1 check.
	my @vert1Polys = lxq("query layerservice vert.polyList ? @_[0]-1");
	if (@vert1Polys == 0)	{	$check1 = 1;	}
	else				{	$check1 = 0;	}

	#vert2 check
	if (@_[0]+1 < $vertCount){
		popup("yes");
		my @vert2Polys = lxq("query layerservice vert.polyList ? @_[0]+1");
		$bleh = @vert2Polys;
		popup("bleh = $bleh");
		if (@vert2Polys < 2)	{
			popup("yes it's equal to zero");
			$check2 = 1;	}
		else				{	$check2 = 0;	}
	}

popup("check1=$check1 <> check2=$check2");

	#--------------------------------------------------------------
	#compare the two verts
	#--------------------------------------------------------------
	if (($check1==1) && ($check2==1)){
		my @pos3 = lxq("query layerservice vert.pos ? @_[0]+1");
		my @disp1 = arrMath(@pos2,@pos1,subt);
		my @disp2 = arrMath(@pos3,@pos1,subt);
		if ((abs(@disp1[0])+abs(@disp1[1])+abs(@disp1[2]))<(abs(@disp2[0])+abs(@disp2[1])+abs(@disp2[2]))){
			$vert2 = @_[0]-1;
			lxout("[->] checked both verts and found vert1 ($vert2) to be closer");
		}else{
			$vert2 = @_[0]+1;
			@pos2 = @pos3;
			lxout("[->] checked both verts and found vert1 ($vert2) to be closer");
		}
	}elsif (($check1==1) && ($check2==0)){
		$vert2 = @_[0]-1;
		lxout("[->] vert2 doesn't exist or isn't a 0polyvert, so ignoring it (@_[0]+1) and chose vert2 ($vert2) instead");
	}elsif (($check1==0) && ($check2==1)){
		$vert2 = @_[0]+1;
		@pos2 = lxq("query layerservice vert.pos ? @_[0]+1");
		lxout("[->] vert1 doesn't exist or isn't a 0polyvert, so ignoring it (@_[0]-1) and chose vert1 ($vert2) instead");
	}else{
		lxout("[->] Neither verts are legal so I'm ignoring both and not extending the bezier curve");
		$runScript = 0;
	}

	@disp = arrMath(@pos2,@pos1,subt);
	popup("disp = @disp");


	if ($runScript == 1){
		push(@selectVerts,$vertCount,$vertCount+1);

		lx("tool.set prim.bezier on 0");
		lx("tool.setAttr prim.bezier number 1");
		lx("tool.setAttr prim.bezier closed 0");
		lx("tool.setAttr prim.bezier current 1");
		lx("tool.setAttr prim.bezier ptX [@pos1[0]]");
		lx("tool.setAttr prim.bezier ptY [@pos1[1]]");
		lx("tool.setAttr prim.bezier ptZ [@pos1[2]]");
		lx("tool.setAttr prim.bezier outX [0 m]");
		lx("tool.setAttr prim.bezier outY [0 m]");
		lx("tool.setAttr prim.bezier outZ [0 m]");
		lx("tool.setAttr prim.bezier inX (@disp[0]*-.25)");
		lx("tool.setAttr prim.bezier inY (@disp[1]*-.25)");
		lx("tool.setAttr prim.bezier inZ (@disp[2]*-.25)");
		lx("tool.setAttr prim.bezier _new 0");

		lx("tool.setAttr prim.bezier number 2");
		lx("tool.setAttr prim.bezier current 1");
		lx("tool.setAttr prim.bezier ptX (@pos1[0]+@disp[0])");
		lx("tool.setAttr prim.bezier ptY (@pos1[1]+@disp[1])");
		lx("tool.setAttr prim.bezier ptZ (@pos1[2]+@disp[2])");
		lx("tool.setAttr prim.bezier outX [0 m]");
		lx("tool.setAttr prim.bezier outY [0 m]");
		lx("tool.setAttr prim.bezier outZ [0 m]");
		lx("tool.setAttr prim.bezier inX (@disp[0]*-.25)");
		lx("tool.setAttr prim.bezier inY (@disp[1]*-.25)");
		lx("tool.setAttr prim.bezier inZ (@disp[2]*-.25)");
		lx("tool.setAttr prim.bezier _new 0");
		lx("tool.doApply");
		lx("tool.set prim.bezier off 0");

		#merge the two verts
		lx("select.element $mainlayer vertex add $vertCount");
		lx("!!vert.merge auto [0] [1 um]");

		#merge the two polys
		my $newestPoly = lxq("query layerservice poly.n ? all")-1;
		lx("select.drop polygon");
		lx("select.element $mainlayer polygon add $newestPoly");
		lx("select.element $mainlayer polygon add ($newestPoly-1)");
		lx("!!poly.merge");
	}
}

#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#VERT BEVELITTLE SUB
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
sub vertBevelittle{
	lx("select.convert edge");
	lx("select.edge remove poly equal 2");

	if (lxq("query layerservice edge.n ? selected") > 0){
		lx("tool.set edge.extend on");
		lx("tool.attr edge.extend segs 1");
		lx("tool.attr edge.extend offZ [0 m]");
		lx("tool.attr edge.extend offX [0 m]");
		lx("tool.attr edge.extend offY [0 m]");
		lx("tool.doapply");
		lx("tool.set edge.extend off 0");
		lx("select.convert vertex");
		if ($modoVer > 300){&restoreACTR;}
	}else{
		die("\n.\n[--------------------------------You don't have any border verts selected, so I can't run the script-----------------------------]\n[--PLEASE TURN OFF THIS WARNING WINDOW by clicking on the (In the future) button and choose (Hide Message)--] \n[-----------------------------------This window is not supposed to come up, but I can't control that.---------------------------]\n.\n");
	}
}




#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================
#===															GENERAL SUBROUTINES																====
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================

#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#RESTORE THE ACTR
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
sub restoreACTR{
	lxout("[->]Restoring $seltype $selCenter $selAxis ACTR");
	if ($actr == 1) {	lx( "tool.set {$seltype} on" ); }
	else { lx("tool.set center.$selCenter on"); lx("tool.set axis.$selAxis on"); }
}

#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#PERFORM MATH FROM ONE ARRAY TO ANOTHER subroutine
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#USAGE : my @disp = arrMath(@pos2,@pos1,subt);
sub arrMath{
	my @array1 = (@_[0],@_[1],@_[2]);
	my @array2 = (@_[3],@_[4],@_[5]);
	my $math = @_[6];

	my @newArray;
	if ($math eq "add")		{	@newArray = (@array1[0]+@array2[0],@array1[1]+@array2[1],@array1[2]+@array2[2]);	}
	elsif ($math eq "subt")	{	@newArray = (@array1[0]-@array2[0],@array1[1]-@array2[1],@array1[2]-@array2[2]);	}
	elsif ($math eq "mult")	{	@newArray = (@array1[0]*@array2[0],@array1[1]*@array2[1],@array1[2]*@array2[2]);	}
	elsif ($math eq "div")		{	@newArray = (@array1[0]/@array2[0],@array1[1]/@array2[1],@array1[2]/@array2[2]);	}
	return @newArray;
}

#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#UNIT VECTOR SUBROUTINE
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#USAGE : my @unitVector = unitVector(@vector);
sub unitVector{
	my $dist1 = sqrt((@_[0]*@_[0])+(@_[1]*@_[1])+(@_[2]*@_[2]));
	@_ = ((@_[0]/$dist1),(@_[1]/$dist1),(@_[2]/$dist1));
	return @_;
}

#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#DOT PRODUCT subroutine
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#USAGE : my $dp = dotProduct(\@vector1,\@vector2);
sub dotProduct{
	my @array1 = @{$_[0]};
	my @array2 = @{$_[1]};
	my $dp = (	(@array1[0]*@array2[0])+(@array1[1]*@array2[1])+(@array1[2]*@array2[2])	);
	return $dp;
}

#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#POPUP SUB
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
sub popup #(MODO2 FIX)
{
	lx("dialog.setup yesNo");
	lx("dialog.msg {@_}");
	lx("dialog.open");
	my $confirm = lxq("dialog.result ?");
	if($confirm eq "no"){die;}
}