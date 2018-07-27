#!perl

# er9_forceSubdiv.pl v2.0
# for modo601sp5
# by er_9 (2014/2/6)



# default subdivision ( 0:sds 1:psub )
my $psub = 0;


# default target polygon ( 0:all 1:selected )
my $limited = 1;


my $script = "er9_forceSubdiv";
#lxout("script: $script");


# get argument
foreach(@ARGV) {
	if($_ eq "sds")  	{ $psub = 0; }
	elsif($_ eq "psub") 	{ $psub = 1; }
	elsif($_ eq "all") 	{ $limited = 0; }
	elsif($_ eq "selected") { $limited = 1; }
}
#lxout("psub: $psub");
#lxout("limited: $limited");




#lxout("----- fg layer check -----");

my @fg = lxq("query layerservice layers ? fg");
#lxout("fg: @fg");

if(!@fg) {
	lxout("abort: no fg layer");
	return;
}



#lxout("----- poly visible check -----");

my $poly_check = 0;
my %fg_hash;

foreach(@fg) {
	my $layer_index = $_;
	my $layer_id = lxq("query layerservice layer.id ? $layer_index");

	$fg_hash{$layer_id} = "$layer_index";

	if(lxq("query layerservice poly.N ? visible")) {
		$poly_check++;
	}
}
#lxout("poly_check: $poly_check");

if(!$poly_check) {
	lxout("abort: no visible polygon");
	return;
}



#lxout("----- selection mode -----");

my $sel_mode = &sel_mode_check;
#lxout("sel_mode: $sel_mode");

if(!$sel_mode) {
	lxout("abort: invalid selection mode");
	return;
}



#lxout("----- store mesh selection -----");

# mesh id list of selected meshes
my @store_mesh;
if($sel_mode eq "item" || $sel_mode eq "pivot" || $sel_mode eq "center") {
	@store_mesh = lxq("query sceneservice selection ? mesh");
}
#lxout("store_mesh: @store_mesh");



#lxout("----- invalid layer check -----");

my @drop_list;
foreach(@store_mesh) {
	if(!$fg_hash{$_}) {
		push(@drop_list, $_);
	}
}
#lxout("drop_list: @drop_list");



#lxout("------ store poly selection ------");

my $store_poly = 0;

$store_poly = &store_polyset;
#lxout("store_poly: $store_poly");



#lxout("------ drop invalid layer ------");

foreach(@drop_list) {
	#lxout("drop: $_");
	lx("select.subItem {$_} remove mesh");
}



#lxout("------ convert selection ------");

# for selection mode consistency
lx("select.type $sel_mode");

# convert
if($limited) {
	#lxout("<limited>");

	if($sel_mode eq "polygon") {
		#lxout("$sel_mode >>> polygon");

		if(!lxq("select.count polygon ?")) { &invert_poly; }
	}
	elsif($sel_mode eq "ptag") {
		#lxout("$sel_mode >>> polygon");

		if(lxq("select.count ptag ?")) { lx("select.convert polygon"); }
		else { &invert_poly; }
	}
	else {
		#lxout("else: $sel_mode >>> polygon");
		&invert_poly;
	}
}
else {
	#lxout("<all>");

	#lxout("else: $sel_mode >>> polygon");
	&invert_poly;
}

# drop wrong polygons
&drop_wrong_poly;







#lxout("----- target poly check -----");

my $target_poly_count = lxq("select.count polygon ?");
#lxout("target_poly_count: $target_poly_count");

if(!$target_poly_count) {
	lxout("abort: no target polygon");
	# continue to restore selection
}
else {
	#lxout("----- force subdivision -----");

	if($psub) { &force_psub; }
	else { &force_sds; }
}






#lxout("----- restore selection -----");

if(@drop_list) { &restore_mesh; }
&restore_poly(1);

# restore selection mode
if(@drop_list) { lx("select.type item"); }	# to avoid default selection mode
lx("select.type $sel_mode");









#### subroutine ####

sub force_psub {
	#lxout("force psub");

	lx("select.polygon remove type psubdiv 2");	# drop psub selection
	my $rest_count = lxq("select.count polygon ?");	# count remaining face/sds
	#lxout("rest_count: $rest_count");

	if($rest_count) {
		#lxout("<target is including face/sds>");

		#lxout("face >>> psub , sds --> face");
		lx("poly.convert face psubdiv true");		# face to psub, sds to face

		lx("select.polygon remove type psubdiv 2");	# drop psub selection
		my $face_count = lxq("select.count polygon ?");	# count remaining face
		#lxout("face_count: $face_count");


		if($face_count) {
			#lxout("face --> psub");
			lx("poly.convert face psubdiv true");	# face to psub

			lx("select.polygon remove type psubdiv 2");	# drop psub selection
			$face_count = lxq("select.count polygon ?");	# count remaining sel
			#lxout("face_count: $face_count");
		}

		if($face_count != $rest_count) {
			#lxout("skip>> solved");
			return;
		}

		# if face_count is same as rest_count
		lxout("<<continue: target is including unknown polygon type>>");
	}
	

	#lxout("<target is entirely psub>");

	&restore_target; # restore target selection

	#lxout("psub >>> face");
	lx("poly.convert face psubdiv true");	# psub to face
	my $ok = lxok;
	#lxout("ok: $ok");

	if(!$ok) {
		lxout("abort: user cancel (force psub)");
		return;
	}
	

} # end_sub



sub force_sds {
	#lxout("force sds");

	lx("select.polygon remove type subdiv 1");	# drop sds selection
	my $rest_count = lxq("select.count polygon ?");	# count remaining face/psub
	#lxout("rest_count: $rest_count");

	if($rest_count) {
		#lxout("<target is including face/psub>");

		#lxout("face >>> sds , psub --> face");
		lx("poly.convert face subpatch true");	# face to sds, psub to face
		my $ok = lxok;
		#lxout("ok: $ok");


		if(!$ok) {
			lxout("abort: user cancel (force sds)");
			return;
		}
		

		lx("select.polygon remove type subdiv 1");	# drop sds selection
		my $face_count = lxq("select.count polygon ?");	# count remaining face
		#lxout("face_count: $face_count");

		if($face_count) {
			#lxout("face --> sds");
			lx("poly.convert face subpatch true");	# face to sds

			lx("select.polygon remove type subdiv 1");	# drop sds selection
			$face_count = lxq("select.count polygon ?");	# count remaining sel
			#lxout("face_count: $face_count");
		}

		if($face_count != $rest_count) {
			#lxout("skip>> solved");
			return;
		}

		# if face_count is same as rest_count
		lxout("<<continue: target is including unknown polygon type>>");
	}


	#lxout("<target is entirely sds>");

	&restore_target; # restore target selection

	#lxout("sds >>> face");
	lx("poly.convert face subpatch true");	# sds to face


} # end_sub



sub restore_target {
	#lxout("restore target selection");

	if($limited) {
		#lxout("<limited>");

		if($sel_mode eq "polygon" && $store_poly) {
			&restore_poly(0);
		}
		elsif($sel_mode eq "ptag" && lxq("select.count ptag ?")) {
			lx("select.type ptag");
			lx("select.convert polygon");
		}
		else { &invert_poly; }
	}
	else {
		#lxout("<all>");
		&invert_poly;
	}

	&drop_wrong_poly;
}

sub store_polyset {
	#lxout("store selset: polygon");

	lx("select.type polygon");

	my $sel_count = lxq("select.count polygon ?");
	#lxout("sel_count: $sel_count");

	# if nothing selected, skip process.
	if(!$sel_count) {
		#lxout("skip: no selected poly");
		lx("select.type $sel_mode");
		return 0;
	}


	my @fg = lxq("query layerservice layers ? fg");
	#lxout("fg: @fg");

	my $visible_count = 0;
	foreach(@fg) {
		lxq("query layerservice layer.id ? $_");
		$visible_count += lxq("query layerservice poly.N ? visible");
	}
	#lxout("visible_count: $visible_count");

	my $unsel_count = $visible_count - $sel_count;
	#lxout("unsel_count: $unsel_count");


	my $store_poly = 0;
	if(!$sel_count) {
		$store_poly = 0;
	}
	elsif($sel_count == $visible_count) {
		$store_poly = -2;
	}
	elsif($sel_count > $unsel_count) {
		$store_poly = -1;
	}
	elsif($sel_count <= $unsel_count) {
		$store_poly = 1;
	}


	if($store_poly == 1) {
		# remove potential invalid selection set
		lx("select.invert");
		lx("select.editSet $script remove");
		lx("select.invert");

		# store selection
		lx("select.editSet $script add");
	}
	elsif($store_poly == -1) {
		# remove potential invalid selection set
		lx("select.editSet $script remove");
		lx("select.invert");

		# store selection
		lx("select.editSet $script add");

		lx("select.invert");
	}

	lx("select.type $sel_mode");

	return $store_poly;
}

sub drop_wrong_poly {
	#lxout("drop wrong polygons");

	lx("!select.polygon remove vertex psubdiv 1");	# point poly
	lx("!select.polygon remove vertex psubdiv 2");	# line poly

	lx("!select.polygon remove type curve 3");	# curve
	lx("!select.polygon remove type bezier 4");	# bezier
	lx("!select.polygon remove type spatch 5");	# spline patch
	lx("!select.polygon remove type text 6");	# text
}

sub invert_poly {
	#lxout("invert poly selection");

	lx("select.type polygon");
	lx("select.drop polygon");
	lx("select.invert");
}

sub restore_mesh {
	#lxout("restore mesh selection");

	foreach(@store_mesh) {
		#lxout("$_");
		lx("select.subItem {$_} add mesh");
	}
}

sub restore_poly {
	#lxout("restore poly selection");

	my $remove_selset = $_[0];
	#lxout("remove_selset: $remove_selset");

	lx("select.type polygon");
	lx("select.drop polygon");

	if($store_poly == 1 || $store_poly == -1) {
		# restore selection
		lx("select.useSet $script select");

		# remove selection set
		if($remove_selset) { lx("select.editSet $script remove"); }

		if($store_poly == -1) { lx("select.invert"); }
	}
	elsif($store_poly == -2) {
		lx("select.invert");
	}
}

sub sel_mode_check {
	my $sel_mode;

	if(lxq("select.typeFrom vertex;edge;polygon;item;pivot;center;ptag ?")) {
		$sel_mode = "vertex";
	}
	elsif(lxq("select.typeFrom edge;vertex;polygon;item;pivot;center;ptag ?")) {
		$sel_mode = "edge";
	}
	elsif(lxq("select.typeFrom polygon;edge;vertex;item;pivot;center;ptag ?")) {
		$sel_mode = "polygon";
	}
	elsif(lxq("select.typeFrom ptag;item;pivot;center;edge;polygon;vertex ?")) {
		$sel_mode = "ptag";
	}
	elsif(lxq("select.typeFrom item;pivot;center;edge;polygon;vertex;ptag ?")) {
		$sel_mode = "item";
	}
	elsif(lxq("select.typeFrom pivot;center;item;edge;polygon;vertex;ptag ?")) {
		$sel_mode = "pivot";
	}
	elsif(lxq("select.typeFrom center;pivot;item;edge;polygon;vertex;ptag ?")) {
		$sel_mode = "center";
	}

	return $sel_mode;
}



