#perl

# Title: i_lx_mirror_vmap.pl
# Author: iLight
# Utilisation: Luxology Modo 701
# Description: Search for the user.value string through the selected vertex maps. Create new maps if it does not exist and apply the vertMap.mirror command to the corresponding symmetric vertex maps.

my $source = lxq( "user.value i_lx_mirror_vmap.source  ?" );
my $destination = lxq( "user.value i_lx_mirror_vmap.destination  ?" );
my $axis = lxq( "user.value i_lx_mirror_vmap.axis  ?" );
my $searchReplace = lxq( "user.value i_lx_mirror_vmap.enable  ?" );

my $quote = "\"";

#list of Vertex Map types available for this command.
my @listvMapType = ("pick", "edgepick", "weight", "texture", "morph", "spot", "rgb", "rgba");
my @listvMapPrefix = ("PICK[0]:", "EPCK[0]:", "WGHT[1]:", "TXUV[2]:", "MORF[3]:", "SPOT[3]:", "RGB[3]:", "RGBA[4]:");


sub indexvMapType {
	for (my $n=0; $n<8; $n++){
		if ($_[0] eq $listvMapType[$n]){
			return $n;
		}
	}
	return -1;
}
#Get the current symmetry state.
$currentSymm = lxq("select.symmetryState ?");

#Activate the symmetry if deactivated
if ($currentSymm !~ /[x-z]/){
	if ($axis !~ /[x-z]/ && $axis !~ /[X-Z]/){
		$axis = "x";
	}
	lx("select.symmetryState $axis");
}


if ($searchReplace){
	
	#if enabled, search and replace command.
	my $length = length ($source);
	
	my @vmap = lxq("query layerservice vmaps ? selected");
	my $vmapN = scalar(@vmap);
	
	for (my $i=0; $i<$vmapN; $i++){
		
		#get the vmap name and type.
		my $vmapSourceName = lxq("query layerservice vmap.name ? $vmap[$i]");
		my $vmapSourceType = lxq("query layerservice vmap.type ? $vmap[$i]");
		
		my $indexName = index ($vmapSourceName, $source);
		my $indexType = indexvMapType ($vmapSourceType);
		
		
		if (($indexName != -1) && ($indexType != -1)){
			
			#classic vmap case.
			#get the symetric name
			my $vmapDestinationName = $vmapSourceName;        
			substr ($vmapDestinationName, $indexName, $length, $destination);
			$vmapSourceName = $quote.$listvMapPrefix[$indexType].$vmapSourceName.$quote;
			lx("vertMap.mirror $vmapSourceName $vmapDestinationName");
			
			
		} else {
			
			
			#Weight Container case.
			$indexName = index ($vmapSourceName, "weightContainer");
			
			if (($indexName != -1) && ($indexType == 2)){
				#For Weight Containers, the name of the vmap is the ID of the container with the __item_ prefix.
				my $itemLength = length ($vmapSourceName);
				my $itemSource = substr ($vmapSourceName, 7, $itemLength - 7);
				
				#get the name of the Weight Container
				my $itemSourceName = lxq("query sceneservice item.name ? $itemSource");
				$indexName = index ($itemSourceName, $source);
				
				if ($indexName != -1){
					#get the symetric name
					my $itemDestinationName = $itemSourceName;
					substr ($itemDestinationName, $indexName, $length, $destination);
					
					#get the ID of the symetric Weight Container
					my $itemDestination = lxq ("query sceneservice item.id ? $itemDestinationName");
					my $vmapDestinationName = "__item_".$itemDestination;
					$vmapSourceName = $quote.$listvMapPrefix[2].$vmapSourceName.$quote;
					lx("vertMap.mirror $vmapSourceName $vmapDestinationName");
					
				}
			}
		}
	}
	
} else {
	#if disabled, basic command.
	lx("vertMap.mirror");
}
#Return to the original symmetry state.
if ($currentSymm !~ /[x-z]/){
lx("select.symmetryState $currentSymm");
}