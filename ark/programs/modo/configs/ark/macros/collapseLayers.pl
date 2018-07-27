#perl
#COLLAPSE LAYERS
#AUTHOR: Seneca Menard
#version 1.0
#This script will copy all the current scene's geometry into layer 1 and then delete all the other layers.

my $mainlayerID = lxq("query layerservice layer.id ? 1");
my @layers = lxq("query layerservice layers ? all");
my @layerIDList;
lx("select.drop polygon");

#COPY TO LAYER 1
for (my $i=1; $i<@layers; $i++){
	my $layerID = lxq("query layerservice layer.id ? @layers[$i]");
	push(@layerIDList,$layerID);
	lx("select.subItem [$layerID] set mesh;meshInst;camera;light;txtrLocator;backdrop;groupLocator [0] [1]");
	lx("select.invert");
	if (lxq("select.count polygon ?") > 0){
		lx("select.copy");
		lx("select.subItem [$mainlayerID] set mesh;meshInst;camera;light;txtrLocator;backdrop;groupLocator [0] [1]");
		lx("select.paste");
	}
}

#DELETE ALL THE LAYERS
foreach my $layerID (@layerIDList){
	lx("select.subItem [$layerID] set mesh;meshInst;camera;light;txtrLocator;backdrop;groupLocator [0] [1]");
	lx("layer.deleteSelected");
}

my $count = $#layerIDList+1;
lxout("There were ($count) layers to be copied to layer 1 and then deleted.");