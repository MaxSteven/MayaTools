//Maya ASCII 2015 scene
//Name: Frame.ma
//Last modified: Fri, Apr 15, 2016 02:07:16 PM
//Codeset: 1252
requires maya "2015";
requires -nodeType "mentalrayFramebuffer" -nodeType "mentalrayOptions" -nodeType "mentalrayGlobals"
		 -nodeType "mentalrayItemsList" -dataType "byteArray" "Mayatomr" "2015.0 - 3.12.1.18 ";
requires -nodeType "ilrOptionsNode" -nodeType "ilrUIOptionsNode" -nodeType "ilrBakeLayerManager"
		 -nodeType "ilrBakeLayer" "Turtle" "2015.0.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2015";
fileInfo "version" "2015";
fileInfo "cutIdentifier" "201410051530-933320";
fileInfo "osv" "Microsoft Windows 8 Home Premium Edition, 64-bit  (Build 9200)\n";
fileInfo "license" "student";
createNode transform -s -n "persp";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -15.351568752925754 27.867299636388029 35.3775550849114 ;
	setAttr ".r" -type "double3" 325.46164726203392 1057.3999999979519 -1.7225517127924118e-015 ;
createNode camera -s -n "perspShape" -p "persp";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 43.421517481526365;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -0.85292221311940841 100.14006695741332 0.035366459129271222 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 42.253010316594107;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
createNode transform -s -n "front";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0.20723216685848478 -0.53460599647059992 100.1 ;
createNode camera -s -n "frontShape" -p "front";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 40.095927278292081;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
createNode transform -s -n "side";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 100.1 2.1711474109708839 -4.7726724841030173 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 6.3426618827707664;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "FrameRig_GRP";
createNode transform -n "FrameControl_CRV" -p "FrameRig_GRP";
	addAttr -ci true -sn "FrontShockHeight" -ln "FrontShockHeight" -at "double";
	addAttr -ci true -sn "BackShockHeight" -ln "BackShockHeight" -at "double";
	addAttr -ci true -sn "FrameAngle" -ln "FrameAngle" -at "double";
	addAttr -ci true -sn "FrameHeight" -ln "FrameHeight" -at "double";
	addAttr -ci true -sn "FrontFrameTZ" -ln "FrontFrameTZ" -at "double";
	addAttr -ci true -sn "BackFrameTZ" -ln "BackFrameTZ" -at "double";
	addAttr -ci true -sn "FrontFrameNarrowWide" -ln "FrontFrameNarrowWide" -at "double";
	addAttr -ci true -sn "BackFrameNarrowWide" -ln "BackFrameNarrowWide" -at "double";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".rp" -type "double3" 8.2380080468405446 0 0 ;
	setAttr ".sp" -type "double3" 8.2380080468405446 0 0 ;
	setAttr -k on ".FrontShockHeight";
	setAttr -k on ".BackShockHeight";
	setAttr -k on ".FrameAngle";
	setAttr -k on ".FrameHeight";
	setAttr -k on ".FrontFrameTZ";
	setAttr -k on ".BackFrameTZ";
	setAttr -k on ".FrontFrameNarrowWide";
	setAttr -k on ".BackFrameNarrowWide";
createNode nurbsCurve -n "FrameControl_CRVShape" -p "FrameControl_CRV";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		9.02161967173177 4.7982373409884682e-017 -0.78361162489122382
		8.2380080468405446 6.7857323231109134e-017 -1.1081941875543879
		7.45439642194932 4.7982373409884713e-017 -0.78361162489122427
		7.1298138592861564 1.9663354616187859e-032 -3.2112695072372299e-016
		7.45439642194932 -4.7982373409884694e-017 0.78361162489122405
		8.2380080468405446 -6.7857323231109146e-017 1.1081941875543881
		9.0216196717317683 -4.7982373409884719e-017 0.78361162489122438
		9.3462022343949318 -3.6446300679047921e-032 5.9521325992805852e-016
		9.02161967173177 4.7982373409884682e-017 -0.78361162489122382
		8.2380080468405446 6.7857323231109134e-017 -1.1081941875543879
		7.45439642194932 4.7982373409884713e-017 -0.78361162489122427
		;
createNode transform -n "FrameJoints_GRP" -p "FrameControl_CRV";
createNode transform -n "midLeft_GRP" -p "FrameJoints_GRP";
	setAttr ".rp" -type "double3" 3.0000000000000027 1.477517415474795 0 ;
	setAttr ".sp" -type "double3" 3.0000000000000027 1.477517415474795 0 ;
createNode joint -n "midLeft_JNT" -p "midLeft_GRP";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 3.0000000000000027 2.1322900112341774 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 3.0000000000000027 1.477517415474795 0 1;
	setAttr ".radi" 0.5;
createNode pointConstraint -n "midLeft_GRP_pointConstraint1" -p "midLeft_GRP";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "leftFront_JNTW0" -dv 1 -min 0 -at "double";
	addAttr -dcb 0 -ci true -k true -sn "w1" -ln "leftBack_JNTW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr ".o" -type "double3" 0 -0.6547725957593824 0 ;
	setAttr -k on ".w0";
	setAttr -k on ".w1";
createNode transform -n "midRight_GRP" -p "FrameJoints_GRP";
	setAttr ".rp" -type "double3" -3.0000000000000027 1.477517415474795 0 ;
	setAttr ".sp" -type "double3" -3.0000000000000027 1.477517415474795 0 ;
createNode joint -n "midRight_JNT" -p "midRight_GRP";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -3.0000000000000027 2.1322900112341774 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -3.0000000000000027 1.477517415474795 0 1;
	setAttr ".radi" 0.5;
createNode pointConstraint -n "midRight_GRP_pointConstraint1" -p "midRight_GRP";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "rightFront_JNTW0" -dv 1 -min 0 -at "double";
	addAttr -dcb 0 -ci true -k true -sn "w1" -ln "rightBack_JNTW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr ".o" -type "double3" 0 -0.6547725957593824 0 ;
	setAttr -k on ".w0";
	setAttr -k on ".w1";
createNode transform -n "frontCenter_GRP" -p "FrameJoints_GRP";
	setAttr ".rp" -type "double3" 0 1.4569915366249484 5.1241344655245795 ;
	setAttr ".sp" -type "double3" 0 1.4569915366249484 5.1241344655245795 ;
createNode joint -n "frontCenter_JNT" -p "frontCenter_GRP";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 0 2.111764132384331 5.1241344655245795 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 1.4569915366249484 5.1241344655245795 1;
	setAttr ".radi" 0.5;
createNode pointConstraint -n "frontCenter_GRP_pointConstraint1" -p "frontCenter_GRP";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "frontRight_JNTW0" -dv 1 -min 0 -at "double";
	addAttr -dcb 0 -ci true -k true -sn "w1" -ln "frontLeft_JNTW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr ".o" -type "double3" 0 -0.67529847460922898 -0.016129703840636722 ;
	setAttr -k on ".w0";
	setAttr -k on ".w1";
createNode transform -n "midCenter_GRP" -p "FrameJoints_GRP";
	setAttr ".rp" -type "double3" 0 1.4569915366249484 0 ;
	setAttr ".sp" -type "double3" 0 1.4569915366249484 0 ;
createNode joint -n "midCenter_JNT" -p "midCenter_GRP";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 0 2.111764132384331 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 1.4569915366249484 0 1;
	setAttr ".radi" 0.5;
createNode pointConstraint -n "midCenter_GRP_pointConstraint1" -p "midCenter_GRP";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "frontCenter_JNTW0" -dv 1 -min 0 -at "double";
	addAttr -dcb 0 -ci true -k true -sn "w1" -ln "backCenter_JNTW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr ".o" -type "double3" 0 -0.65477259575938263 -0.11385737217992586 ;
	setAttr -k on ".w0";
	setAttr -k on ".w1";
createNode transform -n "backCenter_GRP" -p "FrameJoints_GRP";
	setAttr ".rp" -type "double3" 0 1.4569915366249484 -4.8964197211647278 ;
	setAttr ".sp" -type "double3" 0 1.4569915366249484 -4.8964197211647278 ;
createNode joint -n "backCenter_JNT" -p "backCenter_GRP";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 0 2.111764132384331 -4.8964197211647278 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 1.4569915366249484 -4.8964197211647278 1;
	setAttr ".radi" 0.5;
createNode pointConstraint -n "backCenter_GRP_pointConstraint1" -p "backCenter_GRP";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "backLeft_JNTW0" -dv 1 -min 0 -at "double";
	addAttr -dcb 0 -ci true -k true -sn "w1" -ln "backRight_JNTW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr ".o" -type "double3" 8.8817841970012523e-016 -0.67529847460922898 -0.010845616421002013 ;
	setAttr -k on ".w0";
	setAttr -k on ".w1";
createNode transform -n "backRightShock_LOC" -p "FrameJoints_GRP";
	setAttr ".rp" -type "double3" -3.0000000000000027 2.7473706690282018 -4.8685500664020953 ;
	setAttr ".sp" -type "double3" -3.0000000000000027 2.7473706690282018 -4.8685500664020953 ;
createNode locator -n "backRightShock_LOCShape" -p "backRightShock_LOC";
	setAttr -k off ".v";
	setAttr ".lp" -type "double3" -3.0000000000000027 2.7473706690282018 -4.8685500664020953 ;
createNode transform -n "backRightShock_GRP" -p "backRightShock_LOC";
	setAttr ".rp" -type "double3" -3.0000000000000022 2.241192403661687 -4.8685500664020953 ;
	setAttr ".sp" -type "double3" -3.0000000000000022 2.241192403661687 -4.8685500664020953 ;
createNode joint -n "backRightShock_JNT" -p "backRightShock_GRP";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -3.0000000000000027 2.7473706690282018 -4.8685500664020953 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -3.0000000000000027 2.0925980732688192 -4.8685500664020953 1;
	setAttr ".radi" 0.5;
createNode transform -n "backLeftShock_LOC" -p "FrameJoints_GRP";
	setAttr ".rp" -type "double3" 3 2.7473706690282018 -4.8685500664020953 ;
	setAttr ".sp" -type "double3" 3 2.7473706690282018 -4.8685500664020953 ;
createNode locator -n "backLeftShock_LOCShape" -p "backLeftShock_LOC";
	setAttr -k off ".v";
	setAttr ".lp" -type "double3" 3 2.7473706690282018 -4.8685500664020953 ;
createNode transform -n "backLeftShock_GRP" -p "backLeftShock_LOC";
	setAttr ".rp" -type "double3" 3.0000000000000004 2.241192403661687 -4.8685500664020953 ;
	setAttr ".sp" -type "double3" 3.0000000000000004 2.241192403661687 -4.8685500664020953 ;
createNode joint -n "backLeftShock_JNT" -p "backLeftShock_GRP";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 3 2.7473706690282018 -4.8685500664020953 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 3 2.0925980732688192 -4.8685500664020953 1;
	setAttr ".radi" 0.5;
createNode transform -n "frontLeftShock_LOC" -p "FrameJoints_GRP";
	setAttr ".rp" -type "double3" 3 2.7473706690282018 5.1271181676607132 ;
	setAttr ".sp" -type "double3" 3 2.7473706690282018 5.1271181676607132 ;
createNode locator -n "frontLeftShock_LOCShape" -p "frontLeftShock_LOC";
	setAttr -k off ".v";
	setAttr ".lp" -type "double3" 3 2.7473706690282018 5.1271181676607132 ;
createNode transform -n "frontLeftShock_GRP" -p "frontLeftShock_LOC";
	setAttr ".rp" -type "double3" 3.0000000000000004 2.241192403661687 5.1271181676607132 ;
	setAttr ".sp" -type "double3" 3.0000000000000004 2.241192403661687 5.1271181676607132 ;
createNode joint -n "frontLeftShock_JNT" -p "frontLeftShock_GRP";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 3 2.7473706690282018 5.1271181676607132 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 3 2.0925980732688192 5.1271181676607132 1;
	setAttr ".radi" 0.5;
createNode transform -n "frontRightShock_LOC" -p "FrameJoints_GRP";
	setAttr ".rp" -type "double3" -3 2.7473706690282018 5.1271181676607132 ;
	setAttr ".sp" -type "double3" -3 2.7473706690282018 5.1271181676607132 ;
createNode locator -n "frontRightShock_LOCShape" -p "frontRightShock_LOC";
	setAttr -k off ".v";
	setAttr ".lp" -type "double3" -3 2.7473706690282018 5.1271181676607132 ;
createNode transform -n "frontRightShock_GRP" -p "frontRightShock_LOC";
	setAttr ".rp" -type "double3" -2.9999999999999996 2.241192403661687 5.1271181676607132 ;
	setAttr ".sp" -type "double3" -2.9999999999999996 2.241192403661687 5.1271181676607132 ;
createNode joint -n "frontRightShock_JNT" -p "frontRightShock_GRP";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -3 2.7473706690282018 5.1271181676607132 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -3 2.0925980732688192 5.1271181676607132 1;
	setAttr ".radi" 0.5;
createNode transform -n "FrameHeight_GRP" -p "FrameJoints_GRP";
createNode transform -n "backRight_GRP" -p "FrameHeight_GRP";
	setAttr ".rp" -type "double3" -2.0000000000000018 1.477517415474795 -4.8855741047437258 ;
	setAttr ".sp" -type "double3" -2.0000000000000018 1.477517415474795 -4.8855741047437258 ;
createNode joint -n "backRight_JNT" -p "backRight_GRP";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".uoc" 1;
	setAttr ".t" -type "double3" -2.0000000000000018 2.1322900112341774 -4.8855741047437258 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -2.0000000000000018 1.477517415474795 -4.8855741047437258 1;
	setAttr ".radi" 0.5;
createNode pointConstraint -n "backRight_GRP_pointConstraint1" -p "backRight_GRP";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "backRightShock_JNTW0" -dv 1 -min 
		0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".o" -type "double3" 1.0000000000000009 -1.2698532535534068 -0.017024038341630465 ;
	setAttr -k on ".w0";
createNode transform -n "backLeft_GRP" -p "FrameHeight_GRP";
	setAttr ".rp" -type "double3" 2 1.477517415474795 -4.8855741047437258 ;
	setAttr ".sp" -type "double3" 2 1.477517415474795 -4.8855741047437258 ;
createNode joint -n "backLeft_JNT" -p "backLeft_GRP";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 2 2.1322900112341774 -4.8855741047437258 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 2 1.477517415474795 -4.8855741047437258 1;
	setAttr ".radi" 0.5;
createNode pointConstraint -n "backLeft_GRP_pointConstraint1" -p "backLeft_GRP";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "backLeftShock_JNTW0" -dv 1 -min 0 
		-at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".o" -type "double3" -1 -1.2698532535534068 -0.017024038341630465 ;
	setAttr -k on ".w0";
createNode transform -n "rightBack_GRP" -p "FrameHeight_GRP";
	setAttr ".rp" -type "double3" -3.0000000000000027 1.477517415474795 -4.0000000000000009 ;
	setAttr ".sp" -type "double3" -3.0000000000000027 1.477517415474795 -4.0000000000000009 ;
createNode joint -n "rightBack_JNT" -p "rightBack_GRP";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -3.0000000000000027 2.1322900112341774 -4.0000000000000009 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -3.0000000000000027 1.477517415474795 -4.0000000000000009 1;
	setAttr ".radi" 0.5;
createNode pointConstraint -n "rightBack_GRP_pointConstraint1" -p "rightBack_GRP";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "backRightShock_JNTW0" -dv 1 -min 
		0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".o" -type "double3" 0 -1.2698532535534068 0.86855006640209442 ;
	setAttr -k on ".w0";
createNode transform -n "leftBack_GRP" -p "FrameHeight_GRP";
	setAttr ".rp" -type "double3" 3.0000000000000027 1.477517415474795 -4.0000000000000009 ;
	setAttr ".sp" -type "double3" 3.0000000000000027 1.477517415474795 -4.0000000000000009 ;
createNode joint -n "leftBack_JNT" -p "leftBack_GRP";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 3.0000000000000027 2.1322900112341774 -4.0000000000000009 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 3.0000000000000027 1.477517415474795 -4.0000000000000009 1;
	setAttr ".radi" 0.5;
createNode pointConstraint -n "leftBack_GRP_pointConstraint1" -p "leftBack_GRP";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "backLeftShock_JNTW0" -dv 1 -min 0 
		-at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".o" -type "double3" 2.6645352591003757e-015 -1.2698532535534068 0.86855006640209442 ;
	setAttr -k on ".w0";
createNode transform -n "rightFront_GRP" -p "FrameHeight_GRP";
	setAttr ".rp" -type "double3" -3.0000000000000027 1.477517415474795 4.0000000000000009 ;
	setAttr ".sp" -type "double3" -3.0000000000000027 1.477517415474795 4.0000000000000009 ;
createNode joint -n "rightFront_JNT" -p "rightFront_GRP";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -3.0000000000000027 2.1322900112341774 4.0000000000000009 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -3.0000000000000027 1.477517415474795 4.0000000000000009 1;
	setAttr ".radi" 0.5;
createNode pointConstraint -n "rightFront_GRP_pointConstraint1" -p "rightFront_GRP";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "frontRightShock_JNTW0" -dv 1 -min 
		0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".o" -type "double3" -2.6645352591003757e-015 -1.2698532535534068 -1.1271181676607123 ;
	setAttr -k on ".w0";
createNode transform -n "leftFront_GRP" -p "FrameHeight_GRP";
	setAttr ".rp" -type "double3" 3.0000000000000027 1.477517415474795 4.0000000000000009 ;
	setAttr ".sp" -type "double3" 3.0000000000000027 1.477517415474795 4.0000000000000009 ;
createNode joint -n "leftFront_JNT" -p "leftFront_GRP";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 3.0000000000000027 2.1322900112341774 4.0000000000000009 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 3.0000000000000027 1.477517415474795 4.0000000000000009 1;
	setAttr ".radi" 0.5;
createNode pointConstraint -n "leftFront_GRP_pointConstraint1" -p "leftFront_GRP";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "frontLeftShock_JNTW0" -dv 1 -min 
		0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".o" -type "double3" 2.6645352591003757e-015 -1.2698532535534068 -1.1271181676607123 ;
	setAttr -k on ".w0";
createNode transform -n "frontLeft_GRP" -p "FrameHeight_GRP";
	setAttr ".rp" -type "double3" 2.0000000000000018 1.477517415474795 5.1402641693652162 ;
	setAttr ".sp" -type "double3" 2.0000000000000018 1.477517415474795 5.1402641693652162 ;
createNode joint -n "frontLeft_JNT" -p "frontLeft_GRP";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 2.0000000000000018 2.1322900112341774 5.1402641693652162 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 2.0000000000000018 1.477517415474795 5.1402641693652162 1;
	setAttr ".radi" 0.5;
createNode pointConstraint -n "frontLeft_GRP_pointConstraint1" -p "frontLeft_GRP";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "frontLeftShock_JNTW0" -dv 1 -min 
		0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".o" -type "double3" -0.99999999999999822 -1.2698532535534068 0.013146001704503085 ;
	setAttr -k on ".w0";
createNode transform -n "frontRight_GRP" -p "FrameHeight_GRP";
	setAttr ".rp" -type "double3" -2.0000000000000018 1.477517415474795 5.1402641693652162 ;
	setAttr ".sp" -type "double3" -2.0000000000000018 1.477517415474795 5.1402641693652162 ;
createNode joint -n "frontRight_JNT" -p "frontRight_GRP";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -2.0000000000000018 2.1322900112341774 5.1402641693652162 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -2.0000000000000018 1.477517415474795 5.1402641693652162 1;
	setAttr ".radi" 0.5;
createNode pointConstraint -n "frontRight_GRP_pointConstraint1" -p "frontRight_GRP";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "frontRightShock_JNTW0" -dv 1 -min 
		0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".o" -type "double3" 0.99999999999999822 -1.2698532535534068 0.013146001704503085 ;
	setAttr -k on ".w0";
createNode transform -n "FrameGeos_GRP" -p "FrameRig_GRP";
createNode transform -n "Frame_1_GEO" -p "FrameGeos_GRP";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode mesh -n "Frame_1_GEOShape" -p "Frame_1_GEO";
	setAttr -k off ".v";
	setAttr -s 6 ".iog[0].og";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".pv" -type "double2" 0.42230960726737976 0.5 ;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".dr" 1;
	setAttr ".vcs" 2;
createNode mesh -n "Frame_1_GEOShapeOrig" -p "Frame_1_GEO";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 232 ".uvst[0].uvsp[0:231]" -type "float2" 0.375 0.5 0.625 0.5
		 0.375 0.75 0.625 0.75 0.875 0 0.875 0.25 0.125 0 0.125 0.25 0.15538076 0.25 0.375
		 0.46961924 0.625 0.46961924 0.84461921 0.25 0.625 0.78038073 0.84461921 0 0.15538076
		 0 0.37499997 0.78038073 0.14526087 0 0.37499997 0.77026087 0.625 0.77026087 0.85473907
		 0 0.625 0.47973913 0.85473907 0.25 0.14526087 0.25 0.375 0.47973913 0.2498122 0.25
		 0.375 0.37518778 0.625 0.37518778 0.75018775 0.25 0.625 0.87481219 0.75018775 0 0.2498122
		 0 0.375 0.87481219 0.375 0.46961924 0.625 0.46961924 0.625 0.47973913 0.375 0.47973913
		 0.375 0.5 0.625 0.5 0.625 0.75 0.375 0.75 0.37499997 0.77026087 0.625 0.77026087
		 0.625 0.78038073 0.37499997 0.78038073 0.84461921 0.25 0.84461921 0 0.85473907 0
		 0.85473907 0.25 0.14526087 0.25 0.14526087 0 0.15538076 0 0.15538076 0.25 0.375 0.37518778
		 0.625 0.37518778 0.75018775 0.25 0.75018775 0 0.625 0.87481219 0.375 0.87481219 0.2498122
		 0 0.2498122 0.25 0.875 0 0.875 0.25 0.125 0 0.125 0.25 0.84461921 0.25 0.84461921
		 0 0.85473907 0 0.85473907 0.25 0.84461921 0.25 0.85473907 0.25 0.85473907 0 0.84461921
		 0 0.84461915 0.25 0.85473907 0.25 0.85473907 0 0.84461915 0 0.84461921 0.25 0.84461921
		 0 0.85473907 0 0.85473907 0.25 0.84148771 0.25 0.625 0.46648771 0.375 0.46648771
		 0.15851229 0.25 0.37499997 0.78351223 0.15851228 0 0.84148765 0 0.625 0.78351223
		 0.625 0.7823208 0.84267914 0 0.625 0.46767914 0.84267914 0.25 0.15732084 0.25 0.375
		 0.46767914 0.15732083 0 0.37499997 0.7823208 0.375 0.46961924 0.375 0.47973913 0.625
		 0.47973913 0.625 0.46961924 0.375 0.5 0.375 0.75 0.625 0.75 0.625 0.5 0.37499997
		 0.77026087 0.37499997 0.78038073 0.625 0.78038073 0.625 0.77026087 0.14526087 0.25
		 0.15538076 0.25 0.15538076 0 0.14526087 0 0.375 0.37518778 0.375 0.46767914 0.625
		 0.46767914 0.625 0.37518778 0.75018775 0.25 0.84267914 0.25 0.84267914 0 0.75018775
		 0 0.37499997 0.7823208 0.375 0.87481219 0.625 0.87481219 0.625 0.7823208 0.15732084
		 0.25 0.2498122 0.25 0.2498122 0 0.15732083 0 0.85473907 0.25 0.875 0.25 0.875 0 0.85473907
		 0 0.125 0 0.125 0.25 0.375 0.46961924 0.625 0.46961924 0.625 0.47973913 0.375 0.47973913
		 0.375 0.5 0.625 0.5 0.625 0.75 0.375 0.75 0.37499997 0.77026087 0.625 0.77026087
		 0.625 0.78038073 0.37499997 0.78038073 0.14526087 0.25 0.14526087 0 0.15538076 0
		 0.15538076 0.25 0.625 0.46648771 0.375 0.46648771 0.84148765 0 0.84461921 0 0.84461921
		 0.25 0.84148771 0.25 0.625 0.78351223 0.37499997 0.78351223 0.15851228 0 0.15851229
		 0.25 0.85473907 0.25 0.85473907 0 0.875 0 0.875 0.25 0.125 0 0.125 0.25 0.84461921
		 0.25 0.84461921 0.25 0.84461921 0 0.84461921 0 0.85473907 0 0.85473907 0 0.85473907
		 0.25 0.85473907 0.25 0.84461915 0.25 0.84461921 0.25 0.85473907 0.25 0.85473907 0.25
		 0.85473907 0 0.85473907 0 0.84461921 0 0.84461915 0 0.84461921 0.25 0.84461921 0
		 0.375 0.37518778 0.625 0.37518778 0.2498122 0 0.2498122 0.25 0.625 0.87481219 0.375
		 0.87481219 0.75018775 0.25 0.75018775 0 0 2.1695436e-016 1 0 1 0.77635318 0 0.77635318
		 0 2.0958989e-016 0.87078869 0 0.87078869 1 0 1 0 2.1695436e-016 1 0 1 0.77635318
		 0 0.77635318 0 2.0958989e-016 0.87078869 0 0.87078869 1 0 1 0 1.8849168e-016 0.78313142
		 0 0.78313142 1 0 1 0 1.8849168e-016 0.78313142 0 0.78313142 1 0 1 0 2.1692081e-016
		 1 0 1 0.86311823 0 0.86311823 0 2.1692081e-016 1 0 1 0.86311823 0 0.86311823 0 2.0958989e-016
		 0.87078869 0 0.87078869 1 0 1 0 1.8849168e-016 0.78313142 0 0.78313142 1 0 1;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr -s 12 ".pt";
	setAttr ".pt[26]" -type "float3" 0 0 -0.0057867318 ;
	setAttr ".pt[27]" -type "float3" 0 0 -0.0057867318 ;
	setAttr ".pt[32]" -type "float3" 0 0 -2.3283064e-010 ;
	setAttr ".pt[36]" -type "float3" 0 0 -2.3283064e-010 ;
	setAttr ".pt[78]" -type "float3" 0 0 -0.0057867318 ;
	setAttr ".pt[79]" -type "float3" 0 0 -0.0057867467 ;
	setAttr ".pt[84]" -type "float3" 0 0 -2.3283064e-010 ;
	setAttr ".pt[88]" -type "float3" 0 0 -2.3283064e-010 ;
	setAttr ".pt[104]" -type "float3" 0 0 -0.10574102 ;
	setAttr ".pt[105]" -type "float3" 0 0 -0.10574102 ;
	setAttr ".pt[106]" -type "float3" 0 0 -0.10574102 ;
	setAttr ".pt[107]" -type "float3" 0 0 -0.10574102 ;
	setAttr -s 108 ".vt[0:107]"  -3.18411636 2.29640722 -6.15344715 -2.81588364 2.29640722 -6.15344715
		 -3.18411636 1.92817414 -6.15344715 -2.81588364 1.92817414 -6.15344715 -3.18411636 2.29640722 -4.64358902
		 -2.81588364 2.29640722 -4.64358902 -2.81588364 1.92817414 -4.64358902 -3.18411636 1.92817414 -4.64358902
		 -3.18411636 1.92817414 -5.14652634 -2.81588364 1.92817414 -5.14652634 -2.81588364 2.29640722 -5.14652634
		 -3.18411636 2.29640722 -5.14652634 -3.19185591 1.64159489 4.9942173e-008 -2.82184172 1.64159489 4.9942173e-008
		 -2.82184172 1.29564452 4.9942173e-008 -3.19185591 1.29564452 4.9942173e-008 -3.18411636 2.29640722 4.85913277
		 -2.81588364 2.29640722 4.85913277 -2.81588364 2.29640722 5.36207008 -3.18411636 2.29640722 5.36207008
		 -3.18411636 2.29640722 6.3689909 -2.81588364 2.29640722 6.3689909 -2.81588364 1.92817414 6.3689909
		 -3.18411636 1.92817414 6.3689909 -3.18411636 1.92817414 5.36207008 -2.81588364 1.92817414 5.36207008
		 -2.81588364 1.92817414 4.85913277 -3.18411636 1.92817414 4.85913277 -0.19864205 1.64159477 -4.63824701
		 -0.19864205 1.29564428 -4.63824701 -0.19864205 1.29564428 -5.14997816 -0.19864205 1.64159477 -5.14997816
		 -0.2208764 1.64159477 4.84972906 -0.2208764 1.64159477 5.36153936 -0.2208764 1.29564428 5.36153936
		 -0.2208764 1.29564428 4.84972906 -2 1.64159489 4.84972906 -2 1.64159489 5.36153936
		 -2 1.2956444 5.36153936 -2 1.2956444 4.84972906 -2 1.64159489 -4.63824701 -2 1.29564464 -4.63824701
		 -2 1.29564464 -5.14997816 -2 1.64159489 -5.14997816 -2.82184172 1.64159489 3.99999952
		 -3.19185591 1.64159489 3.99999952 -3.19185591 1.29564452 4.000000476837 -2.82184172 1.29564452 4.000000476837
		 -2.82184172 1.29564452 -4.000000476837 -2.82184172 1.64159489 -3.99999952 -3.19185591 1.64159489 -3.99999952
		 -3.19185591 1.29564452 -4.000000476837 3.18411636 2.29640722 -6.15344715 2.81588364 2.29640722 -6.15344715
		 3.18411636 1.92817414 -6.15344715 2.81588364 1.92817414 -6.15344715 3.18411636 2.29640722 -4.64358902
		 2.81588364 2.29640722 -4.64358902 2.81588364 1.92817414 -4.64358902 3.18411636 1.92817414 -4.64358902
		 3.18411636 1.92817414 -5.14652634 2.81588364 1.92817414 -5.14652634 2.81588364 2.29640722 -5.14652634
		 3.18411636 2.29640722 -5.14652634 3.19185591 1.64159489 4.9942173e-008 2.82184172 1.64159489 4.9942173e-008
		 2.82184172 1.29564452 4.9942173e-008 3.19185591 1.29564452 4.9942173e-008 3.18411636 2.29640722 4.85913277
		 2.81588364 2.29640722 4.85913277 2.81588364 2.29640722 5.36207008 3.18411636 2.29640722 5.36207008
		 3.18411636 2.29640722 6.3689909 2.81588364 2.29640722 6.3689909 2.81588364 1.92817414 6.3689909
		 3.18411636 1.92817414 6.3689909 3.18411636 1.92817414 5.36207008 2.81588364 1.92817414 5.36207008
		 2.81588364 1.92817414 4.85913277 3.18411636 1.92817414 4.85913277 0.19864205 1.64159477 -4.63824701
		 0.19864205 1.29564428 -4.63824701 0.19864205 1.29564428 -5.14997816 0.19864205 1.64159477 -5.14997816
		 0.2208764 1.64159477 4.84972906 0.2208764 1.64159477 5.36153936 0.2208764 1.29564428 5.36153936
		 0.2208764 1.29564428 4.84972906 2 1.64159489 4.84972906 2 1.64159489 5.36153936 2 1.2956444 5.36153936
		 2 1.2956444 4.84972906 2 1.64159489 -4.63824701 2 1.29564464 -4.63824701 2 1.29564464 -5.14997816
		 2 1.64159489 -5.14997816 2.82184172 1.64159489 3.99999952 3.19185591 1.64159489 3.99999952
		 3.19185591 1.29564452 4.000000476837 2.82184172 1.29564452 4.000000476837 2.82184172 1.29564452 -4.000000476837
		 2.82184172 1.64159489 -3.99999952 3.19185591 1.64159489 -3.99999952 3.19185591 1.29564452 -4.000000476837
		 -0.20975922 1.64159477 0.10574102 -0.20975922 1.29564428 0.10574102 0.20975922 1.29564428 0.10574102
		 0.20975922 1.64159477 0.10574102;
	setAttr -s 220 ".ed";
	setAttr ".ed[0:165]"  0 1 0 2 3 0 0 2 0 1 3 0 2 8 0 3 9 0 4 11 0 5 10 1 6 48 0
		 7 51 0 4 5 1 5 6 0 6 7 1 7 4 1 8 7 0 9 6 1 10 1 0 11 0 0 8 9 1 9 10 0 10 11 1 11 8 1
		 12 50 0 13 49 0 12 13 0 13 14 0 14 15 0 15 12 0 16 17 1 17 18 1 18 19 1 16 19 0 20 21 0
		 21 22 0 23 22 0 20 23 0 24 25 1 25 26 1 26 27 1 24 27 0 17 26 0 25 18 0 19 24 1 27 16 1
		 13 44 0 12 45 0 26 47 0 27 46 0 22 25 0 23 24 0 18 21 0 19 20 0 5 40 0 6 41 0 28 29 0
		 9 42 0 30 29 0 10 43 0 30 31 0 28 31 0 17 36 0 18 37 0 32 33 0 25 38 0 34 33 0 26 39 0
		 34 35 0 32 35 0 36 32 0 37 33 0 38 34 0 39 35 0 36 37 1 37 38 1 38 39 1 39 36 1 40 28 0
		 41 29 0 42 30 0 43 31 0 40 41 1 41 42 1 42 43 1 43 40 1 44 17 0 45 16 0 46 15 0 47 14 0
		 44 45 1 45 46 1 46 47 1 47 44 1 48 14 0 49 5 0 50 4 0 51 15 0 48 49 1 49 50 1 50 51 1
		 51 48 1 52 53 0 54 55 0 52 54 0 53 55 0 54 60 0 55 61 0 56 63 0 57 62 1 58 100 0
		 59 103 0 56 57 1 57 58 0 58 59 1 59 56 1 60 59 0 61 58 1 62 53 0 63 52 0 60 61 1
		 61 62 0 62 63 1 63 60 1 64 102 0 65 101 0 64 65 0 65 66 0 66 67 0 67 64 0 68 69 1
		 69 70 1 70 71 1 68 71 0 72 73 0 73 74 0 75 74 0 72 75 0 76 77 1 77 78 1 78 79 1 76 79 0
		 69 78 0 77 70 0 71 76 1 79 68 1 65 96 0 64 97 0 78 99 0 79 98 0 74 77 0 75 76 0 70 73 0
		 71 72 0 57 92 0 58 93 0 80 81 0 61 94 0 82 81 0 62 95 0 82 83 0 80 83 0 69 88 0 70 89 0
		 84 85 0 77 90 0 86 85 0 78 91 0;
	setAttr ".ed[166:219]" 86 87 0 84 87 0 88 84 0 89 85 0 90 86 0 91 87 0 88 89 1
		 89 90 1 90 91 1 91 88 1 92 80 0 93 81 0 94 82 0 95 83 0 92 93 1 93 94 1 94 95 1 95 92 1
		 96 69 0 97 68 0 98 67 0 99 66 0 96 97 1 97 98 1 98 99 1 99 96 1 100 66 0 101 57 0
		 102 56 0 103 67 0 100 101 1 101 102 1 102 103 1 103 100 1 28 80 1 83 31 0 29 81 1
		 30 82 0 34 86 0 85 33 0 32 84 1 87 35 1 28 104 0 29 105 0 104 105 0 81 106 0 105 106 0
		 80 107 0 107 106 0 104 107 0 32 104 0 35 105 0 84 107 0 87 106 0;
	setAttr -s 110 -ch 440 ".fc[0:109]" -type "polyFaces" 
		f 4 10 7 20 -7
		mu 0 4 9 10 20 23
		f 4 0 3 -2 -3
		mu 0 4 0 1 3 2
		f 4 18 15 12 -15
		mu 0 4 17 18 12 15
		f 4 21 14 13 6
		mu 0 4 22 16 14 8
		f 4 24 23 97 -23
		mu 0 4 25 26 90 93
		f 4 25 -93 96 -24
		mu 0 4 27 29 89 91
		f 4 99 92 26 -96
		mu 0 4 95 88 28 31
		f 4 98 95 27 22
		mu 0 4 92 94 30 24
		f 4 1 5 -19 -5
		mu 0 4 2 3 18 17
		f 4 -20 -6 -4 -17
		mu 0 4 21 19 4 5
		f 4 -21 16 -1 -18
		mu 0 4 23 20 1 0
		f 4 4 -22 17 2
		mu 0 4 6 16 22 7
		f 4 31 -31 -30 -29
		mu 0 4 32 35 34 33
		f 4 35 34 -34 -33
		mu 0 4 36 39 38 37
		f 4 39 -39 -38 -37
		mu 0 4 40 43 42 41
		f 4 -32 -44 -40 -43
		mu 0 4 48 51 50 49
		f 4 88 85 28 -85
		mu 0 4 81 82 32 33
		f 4 91 84 40 46
		mu 0 4 86 80 44 45
		f 4 47 90 -47 38
		mu 0 4 43 84 87 42
		f 4 -86 89 -48 43
		mu 0 4 51 83 85 50
		f 4 49 36 -49 -35
		mu 0 4 39 40 41 38
		f 4 50 33 48 41
		mu 0 4 47 61 60 46
		f 4 51 32 -51 30
		mu 0 4 35 36 37 34
		f 4 -36 -52 42 -50
		mu 0 4 62 63 48 49
		f 4 80 77 -55 -77
		mu 0 4 76 77 65 64
		f 4 81 78 56 -78
		mu 0 4 77 78 66 65
		f 4 82 79 -59 -79
		mu 0 4 78 79 67 66
		f 4 83 76 59 -80
		mu 0 4 79 76 64 67
		f 4 72 69 -63 -69
		mu 0 4 72 73 69 68
		f 4 73 70 64 -70
		mu 0 4 73 74 70 69
		f 4 74 71 -67 -71
		mu 0 4 74 75 71 70
		f 4 75 68 67 -72
		mu 0 4 75 72 68 71
		f 4 29 61 -73 -61
		mu 0 4 44 47 73 72
		f 4 -42 63 -74 -62
		mu 0 4 47 46 74 73
		f 4 37 65 -75 -64
		mu 0 4 46 45 75 74
		f 4 -41 60 -76 -66
		mu 0 4 45 44 72 75
		f 4 11 53 -81 -53
		mu 0 4 11 13 77 76
		f 4 -16 55 -82 -54
		mu 0 4 13 19 78 77
		f 4 19 57 -83 -56
		mu 0 4 19 21 79 78
		f 4 -8 52 -84 -58
		mu 0 4 21 11 76 79
		f 4 45 -89 -45 -25
		mu 0 4 52 82 81 53
		f 4 -90 -46 -28 -87
		mu 0 4 85 83 59 58
		f 4 -91 86 -27 -88
		mu 0 4 87 84 57 56
		f 4 44 -92 87 -26
		mu 0 4 54 80 86 55
		f 4 -97 -9 -12 -94
		mu 0 4 91 89 13 11
		f 4 -98 93 -11 -95
		mu 0 4 93 90 10 9
		f 4 -14 9 -99 94
		mu 0 4 8 14 94 92
		f 4 -13 8 -100 -10
		mu 0 4 15 12 88 95
		f 4 106 -121 -108 -111
		mu 0 4 96 97 98 99
		f 4 102 101 -104 -101
		mu 0 4 100 101 102 103
		f 4 114 -113 -116 -119
		mu 0 4 104 105 106 107
		f 4 -107 -114 -115 -122
		mu 0 4 108 109 110 111
		f 4 122 -198 -124 -125
		mu 0 4 112 113 114 115
		f 4 123 -197 192 -126
		mu 0 4 116 117 118 119
		f 4 195 -127 -193 -200
		mu 0 4 120 121 122 123
		f 4 -123 -128 -196 -199
		mu 0 4 124 125 126 127
		f 4 104 118 -106 -102
		mu 0 4 101 104 107 102
		f 4 116 103 105 119
		mu 0 4 128 129 130 131
		f 4 117 100 -117 120
		mu 0 4 97 100 103 98
		f 4 -103 -118 121 -105
		mu 0 4 132 133 108 111
		f 4 128 129 130 -132
		mu 0 4 134 135 136 137
		f 4 132 133 -135 -136
		mu 0 4 138 139 140 141
		f 4 136 137 138 -140
		mu 0 4 142 143 144 145
		f 4 142 139 143 131
		mu 0 4 146 147 148 149
		f 4 184 -129 -186 -189
		mu 0 4 150 135 134 151
		f 4 -147 -141 -185 -192
		mu 0 4 152 153 154 155
		f 4 -139 146 -191 -148
		mu 0 4 145 144 156 157
		f 4 -144 147 -190 185
		mu 0 4 149 148 158 159
		f 4 134 148 -137 -150
		mu 0 4 141 140 143 142
		f 4 -142 -149 -134 -151
		mu 0 4 160 161 162 163
		f 4 -131 150 -133 -152
		mu 0 4 137 136 139 138
		f 4 149 -143 151 135
		mu 0 4 164 147 146 165
		f 4 176 154 -178 -181
		mu 0 4 166 167 168 169
		f 4 177 -157 -179 -182
		mu 0 4 169 168 170 171
		f 4 178 158 -180 -183
		mu 0 4 171 170 172 173
		f 4 179 -160 -177 -184
		mu 0 4 173 172 167 166
		f 4 168 162 -170 -173
		mu 0 4 174 175 176 177
		f 4 169 -165 -171 -174
		mu 0 4 177 176 178 179
		f 4 170 166 -172 -175
		mu 0 4 179 178 180 181
		f 4 171 -168 -169 -176
		mu 0 4 181 180 175 174
		f 4 160 172 -162 -130
		mu 0 4 154 174 177 160
		f 4 161 173 -164 141
		mu 0 4 160 177 179 161
		f 4 163 174 -166 -138
		mu 0 4 161 179 181 153
		f 4 165 175 -161 140
		mu 0 4 153 181 174 154
		f 4 152 180 -154 -112
		mu 0 4 182 166 169 183
		f 4 153 181 -156 115
		mu 0 4 183 169 171 131
		f 4 155 182 -158 -120
		mu 0 4 131 171 173 128
		f 4 157 183 -153 107
		mu 0 4 128 173 166 182
		f 4 124 144 188 -146
		mu 0 4 184 185 150 151
		f 4 186 127 145 189
		mu 0 4 158 186 187 159
		f 4 187 126 -187 190
		mu 0 4 156 188 189 157
		f 4 125 -188 191 -145
		mu 0 4 190 191 152 155
		f 4 193 111 108 196
		mu 0 4 117 182 183 118
		f 4 194 110 -194 197
		mu 0 4 113 96 99 114
		f 4 -195 198 -110 113
		mu 0 4 109 124 127 110
		f 4 109 199 -109 112
		mu 0 4 105 120 123 106
		f 4 -60 200 159 201
		mu 0 4 192 193 194 195
		f 4 -57 203 156 -203
		mu 0 4 200 201 202 203
		f 4 58 -202 -159 -204
		mu 0 4 204 205 206 207
		f 4 -65 204 164 205
		mu 0 4 208 209 210 211
		f 4 66 -208 -167 -205
		mu 0 4 216 217 218 219
		f 4 62 -206 -163 -207
		mu 0 4 220 221 222 223
		f 4 54 209 -211 -209
		mu 0 4 196 197 225 224
		f 4 202 211 -213 -210
		mu 0 4 197 198 226 225
		f 4 -155 213 214 -212
		mu 0 4 198 199 227 226
		f 4 -201 208 215 -214
		mu 0 4 199 196 224 227
		f 4 -68 216 210 -218
		mu 0 4 212 213 229 228
		f 4 206 218 -216 -217
		mu 0 4 213 214 230 229
		f 4 167 219 -215 -219
		mu 0 4 214 215 231 230
		f 4 207 217 212 -220
		mu 0 4 215 212 228 231;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
	setAttr ".vcs" 2;
createNode mentalrayItemsList -s -n "mentalrayItemsList";
createNode mentalrayGlobals -s -n "mentalrayGlobals";
createNode mentalrayOptions -s -n "miDefaultOptions";
	addAttr -ci true -m -sn "stringOptions" -ln "stringOptions" -at "compound" -nc 
		3;
	addAttr -ci true -sn "name" -ln "name" -dt "string" -p "stringOptions";
	addAttr -ci true -sn "value" -ln "value" -dt "string" -p "stringOptions";
	addAttr -ci true -sn "type" -ln "type" -dt "string" -p "stringOptions";
	setAttr -s 81 ".stringOptions";
	setAttr ".stringOptions[0].name" -type "string" "rast motion factor";
	setAttr ".stringOptions[0].value" -type "string" "1.0";
	setAttr ".stringOptions[0].type" -type "string" "scalar";
	setAttr ".stringOptions[1].name" -type "string" "rast transparency depth";
	setAttr ".stringOptions[1].value" -type "string" "8";
	setAttr ".stringOptions[1].type" -type "string" "integer";
	setAttr ".stringOptions[2].name" -type "string" "rast useopacity";
	setAttr ".stringOptions[2].value" -type "string" "true";
	setAttr ".stringOptions[2].type" -type "string" "boolean";
	setAttr ".stringOptions[3].name" -type "string" "importon";
	setAttr ".stringOptions[3].value" -type "string" "false";
	setAttr ".stringOptions[3].type" -type "string" "boolean";
	setAttr ".stringOptions[4].name" -type "string" "importon density";
	setAttr ".stringOptions[4].value" -type "string" "1.0";
	setAttr ".stringOptions[4].type" -type "string" "scalar";
	setAttr ".stringOptions[5].name" -type "string" "importon merge";
	setAttr ".stringOptions[5].value" -type "string" "0.0";
	setAttr ".stringOptions[5].type" -type "string" "scalar";
	setAttr ".stringOptions[6].name" -type "string" "importon trace depth";
	setAttr ".stringOptions[6].value" -type "string" "0";
	setAttr ".stringOptions[6].type" -type "string" "integer";
	setAttr ".stringOptions[7].name" -type "string" "importon traverse";
	setAttr ".stringOptions[7].value" -type "string" "true";
	setAttr ".stringOptions[7].type" -type "string" "boolean";
	setAttr ".stringOptions[8].name" -type "string" "shadowmap pixel samples";
	setAttr ".stringOptions[8].value" -type "string" "3";
	setAttr ".stringOptions[8].type" -type "string" "integer";
	setAttr ".stringOptions[9].name" -type "string" "ambient occlusion";
	setAttr ".stringOptions[9].value" -type "string" "false";
	setAttr ".stringOptions[9].type" -type "string" "boolean";
	setAttr ".stringOptions[10].name" -type "string" "ambient occlusion rays";
	setAttr ".stringOptions[10].value" -type "string" "64";
	setAttr ".stringOptions[10].type" -type "string" "integer";
	setAttr ".stringOptions[11].name" -type "string" "ambient occlusion cache";
	setAttr ".stringOptions[11].value" -type "string" "false";
	setAttr ".stringOptions[11].type" -type "string" "boolean";
	setAttr ".stringOptions[12].name" -type "string" "ambient occlusion cache density";
	setAttr ".stringOptions[12].value" -type "string" "1.0";
	setAttr ".stringOptions[12].type" -type "string" "scalar";
	setAttr ".stringOptions[13].name" -type "string" "ambient occlusion cache points";
	setAttr ".stringOptions[13].value" -type "string" "64";
	setAttr ".stringOptions[13].type" -type "string" "integer";
	setAttr ".stringOptions[14].name" -type "string" "irradiance particles";
	setAttr ".stringOptions[14].value" -type "string" "false";
	setAttr ".stringOptions[14].type" -type "string" "boolean";
	setAttr ".stringOptions[15].name" -type "string" "irradiance particles rays";
	setAttr ".stringOptions[15].value" -type "string" "256";
	setAttr ".stringOptions[15].type" -type "string" "integer";
	setAttr ".stringOptions[16].name" -type "string" "irradiance particles interpolate";
	setAttr ".stringOptions[16].value" -type "string" "1";
	setAttr ".stringOptions[16].type" -type "string" "integer";
	setAttr ".stringOptions[17].name" -type "string" "irradiance particles interppoints";
	setAttr ".stringOptions[17].value" -type "string" "64";
	setAttr ".stringOptions[17].type" -type "string" "integer";
	setAttr ".stringOptions[18].name" -type "string" "irradiance particles indirect passes";
	setAttr ".stringOptions[18].value" -type "string" "0";
	setAttr ".stringOptions[18].type" -type "string" "integer";
	setAttr ".stringOptions[19].name" -type "string" "irradiance particles scale";
	setAttr ".stringOptions[19].value" -type "string" "1.0";
	setAttr ".stringOptions[19].type" -type "string" "scalar";
	setAttr ".stringOptions[20].name" -type "string" "irradiance particles env";
	setAttr ".stringOptions[20].value" -type "string" "true";
	setAttr ".stringOptions[20].type" -type "string" "boolean";
	setAttr ".stringOptions[21].name" -type "string" "irradiance particles env rays";
	setAttr ".stringOptions[21].value" -type "string" "256";
	setAttr ".stringOptions[21].type" -type "string" "integer";
	setAttr ".stringOptions[22].name" -type "string" "irradiance particles env scale";
	setAttr ".stringOptions[22].value" -type "string" "1";
	setAttr ".stringOptions[22].type" -type "string" "integer";
	setAttr ".stringOptions[23].name" -type "string" "irradiance particles rebuild";
	setAttr ".stringOptions[23].value" -type "string" "true";
	setAttr ".stringOptions[23].type" -type "string" "boolean";
	setAttr ".stringOptions[24].name" -type "string" "irradiance particles file";
	setAttr ".stringOptions[24].value" -type "string" "";
	setAttr ".stringOptions[24].type" -type "string" "string";
	setAttr ".stringOptions[25].name" -type "string" "geom displace motion factor";
	setAttr ".stringOptions[25].value" -type "string" "1.0";
	setAttr ".stringOptions[25].type" -type "string" "scalar";
	setAttr ".stringOptions[26].name" -type "string" "contrast all buffers";
	setAttr ".stringOptions[26].value" -type "string" "true";
	setAttr ".stringOptions[26].type" -type "string" "boolean";
	setAttr ".stringOptions[27].name" -type "string" "finalgather normal tolerance";
	setAttr ".stringOptions[27].value" -type "string" "25.842";
	setAttr ".stringOptions[27].type" -type "string" "scalar";
	setAttr ".stringOptions[28].name" -type "string" "trace camera clip";
	setAttr ".stringOptions[28].value" -type "string" "false";
	setAttr ".stringOptions[28].type" -type "string" "boolean";
	setAttr ".stringOptions[29].name" -type "string" "unified sampling";
	setAttr ".stringOptions[29].value" -type "string" "true";
	setAttr ".stringOptions[29].type" -type "string" "boolean";
	setAttr ".stringOptions[30].name" -type "string" "samples quality";
	setAttr ".stringOptions[30].value" -type "string" "0.25 0.25 0.25 0.25";
	setAttr ".stringOptions[30].type" -type "string" "color";
	setAttr ".stringOptions[31].name" -type "string" "samples min";
	setAttr ".stringOptions[31].value" -type "string" "1.0";
	setAttr ".stringOptions[31].type" -type "string" "scalar";
	setAttr ".stringOptions[32].name" -type "string" "samples max";
	setAttr ".stringOptions[32].value" -type "string" "100.0";
	setAttr ".stringOptions[32].type" -type "string" "scalar";
	setAttr ".stringOptions[33].name" -type "string" "samples error cutoff";
	setAttr ".stringOptions[33].value" -type "string" "0.0 0.0 0.0 0.0";
	setAttr ".stringOptions[33].type" -type "string" "color";
	setAttr ".stringOptions[34].name" -type "string" "samples per object";
	setAttr ".stringOptions[34].value" -type "string" "false";
	setAttr ".stringOptions[34].type" -type "string" "boolean";
	setAttr ".stringOptions[35].name" -type "string" "progressive";
	setAttr ".stringOptions[35].value" -type "string" "false";
	setAttr ".stringOptions[35].type" -type "string" "boolean";
	setAttr ".stringOptions[36].name" -type "string" "progressive max time";
	setAttr ".stringOptions[36].value" -type "string" "0";
	setAttr ".stringOptions[36].type" -type "string" "integer";
	setAttr ".stringOptions[37].name" -type "string" "progressive subsampling size";
	setAttr ".stringOptions[37].value" -type "string" "4";
	setAttr ".stringOptions[37].type" -type "string" "integer";
	setAttr ".stringOptions[38].name" -type "string" "iray";
	setAttr ".stringOptions[38].value" -type "string" "false";
	setAttr ".stringOptions[38].type" -type "string" "boolean";
	setAttr ".stringOptions[39].name" -type "string" "light relative scale";
	setAttr ".stringOptions[39].value" -type "string" "0.31831";
	setAttr ".stringOptions[39].type" -type "string" "scalar";
	setAttr ".stringOptions[40].name" -type "string" "trace camera motion vectors";
	setAttr ".stringOptions[40].value" -type "string" "false";
	setAttr ".stringOptions[40].type" -type "string" "boolean";
	setAttr ".stringOptions[41].name" -type "string" "ray differentials";
	setAttr ".stringOptions[41].value" -type "string" "true";
	setAttr ".stringOptions[41].type" -type "string" "boolean";
	setAttr ".stringOptions[42].name" -type "string" "environment lighting mode";
	setAttr ".stringOptions[42].value" -type "string" "off";
	setAttr ".stringOptions[42].type" -type "string" "string";
	setAttr ".stringOptions[43].name" -type "string" "environment lighting quality";
	setAttr ".stringOptions[43].value" -type "string" "0.2";
	setAttr ".stringOptions[43].type" -type "string" "scalar";
	setAttr ".stringOptions[44].name" -type "string" "environment lighting shadow";
	setAttr ".stringOptions[44].value" -type "string" "transparent";
	setAttr ".stringOptions[44].type" -type "string" "string";
	setAttr ".stringOptions[45].name" -type "string" "environment lighting resolution";
	setAttr ".stringOptions[45].value" -type "string" "512";
	setAttr ".stringOptions[45].type" -type "string" "integer";
	setAttr ".stringOptions[46].name" -type "string" "environment lighting shader samples";
	setAttr ".stringOptions[46].value" -type "string" "2";
	setAttr ".stringOptions[46].type" -type "string" "integer";
	setAttr ".stringOptions[47].name" -type "string" "environment lighting scale";
	setAttr ".stringOptions[47].value" -type "string" "1 1 1";
	setAttr ".stringOptions[47].type" -type "string" "color";
	setAttr ".stringOptions[48].name" -type "string" "environment lighting caustic photons";
	setAttr ".stringOptions[48].value" -type "string" "0";
	setAttr ".stringOptions[48].type" -type "string" "integer";
	setAttr ".stringOptions[49].name" -type "string" "environment lighting globillum photons";
	setAttr ".stringOptions[49].value" -type "string" "0";
	setAttr ".stringOptions[49].type" -type "string" "integer";
	setAttr ".stringOptions[50].name" -type "string" "light importance sampling";
	setAttr ".stringOptions[50].value" -type "string" "all";
	setAttr ".stringOptions[50].type" -type "string" "string";
	setAttr ".stringOptions[51].name" -type "string" "light importance sampling quality";
	setAttr ".stringOptions[51].value" -type "string" "1.0";
	setAttr ".stringOptions[51].type" -type "string" "scalar";
	setAttr ".stringOptions[52].name" -type "string" "light importance sampling samples";
	setAttr ".stringOptions[52].value" -type "string" "4";
	setAttr ".stringOptions[52].type" -type "string" "integer";
	setAttr ".stringOptions[53].name" -type "string" "light importance sampling resolution";
	setAttr ".stringOptions[53].value" -type "string" "1.0";
	setAttr ".stringOptions[53].type" -type "string" "scalar";
	setAttr ".stringOptions[54].name" -type "string" "light importance sampling precomputed";
	setAttr ".stringOptions[54].value" -type "string" "false";
	setAttr ".stringOptions[54].type" -type "string" "boolean";
	setAttr ".stringOptions[55].name" -type "string" "mila quality";
	setAttr ".stringOptions[55].value" -type "string" "1.0";
	setAttr ".stringOptions[55].type" -type "string" "scalar";
	setAttr ".stringOptions[56].name" -type "string" "mila glossy quality";
	setAttr ".stringOptions[56].value" -type "string" "1.0";
	setAttr ".stringOptions[56].type" -type "string" "scalar";
	setAttr ".stringOptions[57].name" -type "string" "mila scatter quality";
	setAttr ".stringOptions[57].value" -type "string" "1.0";
	setAttr ".stringOptions[57].type" -type "string" "scalar";
	setAttr ".stringOptions[58].name" -type "string" "mila scatter scale";
	setAttr ".stringOptions[58].value" -type "string" "1.0";
	setAttr ".stringOptions[58].type" -type "string" "scalar";
	setAttr ".stringOptions[59].name" -type "string" "mila diffuse quality";
	setAttr ".stringOptions[59].value" -type "string" "1.0";
	setAttr ".stringOptions[59].type" -type "string" "scalar";
	setAttr ".stringOptions[60].name" -type "string" "mila diffuse detail";
	setAttr ".stringOptions[60].value" -type "string" "false";
	setAttr ".stringOptions[60].type" -type "string" "boolean";
	setAttr ".stringOptions[61].name" -type "string" "mila diffuse detail distance";
	setAttr ".stringOptions[61].value" -type "string" "10.0";
	setAttr ".stringOptions[61].type" -type "string" "scalar";
	setAttr ".stringOptions[62].name" -type "string" "mila use max distance inside";
	setAttr ".stringOptions[62].value" -type "string" "true";
	setAttr ".stringOptions[62].type" -type "string" "boolean";
	setAttr ".stringOptions[63].name" -type "string" "mila clamp output";
	setAttr ".stringOptions[63].value" -type "string" "false";
	setAttr ".stringOptions[63].type" -type "string" "boolean";
	setAttr ".stringOptions[64].name" -type "string" "mila clamp level";
	setAttr ".stringOptions[64].value" -type "string" "1.0";
	setAttr ".stringOptions[64].type" -type "string" "scalar";
	setAttr ".stringOptions[65].name" -type "string" "gi gpu";
	setAttr ".stringOptions[65].value" -type "string" "off";
	setAttr ".stringOptions[65].type" -type "string" "string";
	setAttr ".stringOptions[66].name" -type "string" "gi gpu rays";
	setAttr ".stringOptions[66].value" -type "string" "34";
	setAttr ".stringOptions[66].type" -type "string" "integer";
	setAttr ".stringOptions[67].name" -type "string" "gi gpu passes";
	setAttr ".stringOptions[67].value" -type "string" "4";
	setAttr ".stringOptions[67].type" -type "string" "integer";
	setAttr ".stringOptions[68].name" -type "string" "gi gpu presample density";
	setAttr ".stringOptions[68].value" -type "string" "1.0";
	setAttr ".stringOptions[68].type" -type "string" "scalar";
	setAttr ".stringOptions[69].name" -type "string" "gi gpu presample depth";
	setAttr ".stringOptions[69].value" -type "string" "2";
	setAttr ".stringOptions[69].type" -type "string" "integer";
	setAttr ".stringOptions[70].name" -type "string" "gi gpu filter";
	setAttr ".stringOptions[70].value" -type "string" "1.0";
	setAttr ".stringOptions[70].type" -type "string" "integer";
	setAttr ".stringOptions[71].name" -type "string" "gi gpu depth";
	setAttr ".stringOptions[71].value" -type "string" "3";
	setAttr ".stringOptions[71].type" -type "string" "integer";
	setAttr ".stringOptions[72].name" -type "string" "gi gpu devices";
	setAttr ".stringOptions[72].value" -type "string" "0";
	setAttr ".stringOptions[72].type" -type "string" "integer";
	setAttr ".stringOptions[73].name" -type "string" "shutter shape function";
	setAttr ".stringOptions[73].value" -type "string" "none";
	setAttr ".stringOptions[73].type" -type "string" "string";
	setAttr ".stringOptions[74].name" -type "string" "shutter full open";
	setAttr ".stringOptions[74].value" -type "string" "0.2";
	setAttr ".stringOptions[74].type" -type "string" "scalar";
	setAttr ".stringOptions[75].name" -type "string" "shutter full close";
	setAttr ".stringOptions[75].value" -type "string" "0.8";
	setAttr ".stringOptions[75].type" -type "string" "scalar";
	setAttr ".stringOptions[76].name" -type "string" "gi";
	setAttr ".stringOptions[76].value" -type "string" "off";
	setAttr ".stringOptions[76].type" -type "string" "boolean";
	setAttr ".stringOptions[77].name" -type "string" "gi rays";
	setAttr ".stringOptions[77].value" -type "string" "100";
	setAttr ".stringOptions[77].type" -type "string" "integer";
	setAttr ".stringOptions[78].name" -type "string" "gi depth";
	setAttr ".stringOptions[78].value" -type "string" "0";
	setAttr ".stringOptions[78].type" -type "string" "integer";
	setAttr ".stringOptions[79].name" -type "string" "gi freeze";
	setAttr ".stringOptions[79].value" -type "string" "off";
	setAttr ".stringOptions[79].type" -type "string" "boolean";
	setAttr ".stringOptions[80].name" -type "string" "gi filter";
	setAttr ".stringOptions[80].value" -type "string" "1.0";
	setAttr ".stringOptions[80].type" -type "string" "scalar";
createNode mentalrayFramebuffer -s -n "miDefaultFramebuffer";
createNode lightLinker -s -n "lightLinker1";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode displayLayerManager -n "layerManager";
createNode displayLayer -n "defaultLayer";
createNode renderLayerManager -n "renderLayerManager";
createNode renderLayer -n "defaultRenderLayer";
	setAttr ".g" yes;
createNode script -n "uiConfigurationScriptNode";
	setAttr ".b" -type "string" (
		"// Maya Mel UI Configuration File.\n//\n//  This script is machine generated.  Edit at your own risk.\n//\n//\n\nglobal string $gMainPane;\nif (`paneLayout -exists $gMainPane`) {\n\n\tglobal int $gUseScenePanelConfig;\n\tint    $useSceneConfig = $gUseScenePanelConfig;\n\tint    $menusOkayInPanels = `optionVar -q allowMenusInPanels`;\tint    $nVisPanes = `paneLayout -q -nvp $gMainPane`;\n\tint    $nPanes = 0;\n\tstring $editorName;\n\tstring $panelName;\n\tstring $itemFilterName;\n\tstring $panelConfig;\n\n\t//\n\t//  get current state of the UI\n\t//\n\tsceneUIReplacement -update $gMainPane;\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Top View\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `modelPanel -unParent -l (localizedPanelLabel(\"Top View\")) -mbv $menusOkayInPanels `;\n\t\t\t$editorName = $panelName;\n            modelEditor -e \n                -camera \"top\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"smoothShaded\" \n"
		+ "                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 0\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 16384\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -maxConstantTransparency 1\n                -rendererName \"vp2Renderer\" \n                -objectFilterShowInHUD 1\n"
		+ "                -isFiltered 0\n                -colorResolution 256 256 \n                -bumpResolution 512 512 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 1\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n"
		+ "                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -clipGhosts 1\n                -greasePencils 1\n                -shadows 0\n                $editorName;\n            modelEditor -e -viewSelected 0 $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Top View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"top\" \n            -useInteractiveMode 0\n"
		+ "            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n"
		+ "            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n"
		+ "            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Side View\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `modelPanel -unParent -l (localizedPanelLabel(\"Side View\")) -mbv $menusOkayInPanels `;\n\t\t\t$editorName = $panelName;\n            modelEditor -e \n                -camera \"side\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n"
		+ "                -displayAppearance \"smoothShaded\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 0\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 16384\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -maxConstantTransparency 1\n"
		+ "                -rendererName \"vp2Renderer\" \n                -objectFilterShowInHUD 1\n                -isFiltered 0\n                -colorResolution 256 256 \n                -bumpResolution 512 512 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 1\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n"
		+ "                -hulls 1\n                -grid 1\n                -imagePlane 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -clipGhosts 1\n                -greasePencils 1\n                -shadows 0\n                $editorName;\n            modelEditor -e -viewSelected 0 $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Side View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n"
		+ "        modelEditor -e \n            -camera \"side\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -maxConstantTransparency 1\n"
		+ "            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n"
		+ "            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Front View\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `modelPanel -unParent -l (localizedPanelLabel(\"Front View\")) -mbv $menusOkayInPanels `;\n\t\t\t$editorName = $panelName;\n            modelEditor -e \n                -camera \"front\" \n"
		+ "                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"smoothShaded\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 0\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 16384\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n"
		+ "                -maxConstantTransparency 1\n                -rendererName \"vp2Renderer\" \n                -objectFilterShowInHUD 1\n                -isFiltered 0\n                -colorResolution 256 256 \n                -bumpResolution 512 512 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 1\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n"
		+ "                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -clipGhosts 1\n                -greasePencils 1\n                -shadows 0\n                $editorName;\n            modelEditor -e -viewSelected 0 $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Front View\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"front\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n"
		+ "            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n"
		+ "            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Persp View\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `modelPanel -unParent -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels `;\n\t\t\t$editorName = $panelName;\n"
		+ "            modelEditor -e \n                -camera \"persp\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"smoothShaded\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 0\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 16384\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n"
		+ "                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -maxConstantTransparency 1\n                -rendererName \"vp2Renderer\" \n                -objectFilterShowInHUD 1\n                -isFiltered 0\n                -colorResolution 256 256 \n                -bumpResolution 512 512 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 1\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n"
		+ "                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -clipGhosts 1\n                -greasePencils 1\n                -shadows 0\n                $editorName;\n            modelEditor -e -viewSelected 0 $editorName;\n\t\t}\n"
		+ "\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"persp\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n"
		+ "            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n"
		+ "            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"Outliner\")) `;\n\tif (\"\" == $panelName) {\n"
		+ "\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `outlinerPanel -unParent -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels `;\n\t\t\t$editorName = $panelName;\n            outlinerEditor -e \n                -docTag \"isolOutln_fromSeln\" \n                -showShapes 0\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 0\n                -showConnected 0\n                -showAnimCurvesOnly 0\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 0\n                -showDagOnly 1\n                -showAssets 1\n                -showContainedOnly 1\n                -showPublishedAsConnected 0\n                -showContainerContents 1\n                -ignoreDagHierarchy 0\n                -expandConnections 0\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 1\n                -showLeafs 1\n                -showNumericAttrsOnly 0\n"
		+ "                -highlightActive 1\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"defaultSetFilter\" \n                -showSetMembers 1\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 0\n                -ignoreHiddenAttribute 0\n"
		+ "                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -docTag \"isolOutln_fromSeln\" \n            -showShapes 0\n            -showReferenceNodes 0\n            -showReferenceMembers 0\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n"
		+ "            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"graphEditor\" (localizedPanelLabel(\"Graph Editor\")) `;\n"
		+ "\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"graphEditor\" -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n"
		+ "                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n"
		+ "                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 1\n                -displayInfinities 0\n                -autoFit 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -showResults \"off\" \n                -showBufferCurves \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -stackedCurves 0\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -displayNormalized 0\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -classicMode 1\n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n"
		+ "                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayKeys 1\n                -displayTangents 0\n"
		+ "                -displayActiveKeys 0\n                -displayActiveKeyTangents 1\n                -displayInfinities 0\n                -autoFit 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -showResults \"off\" \n                -showBufferCurves \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -stackedCurves 0\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -displayNormalized 0\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -classicMode 1\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dopeSheetPanel\" (localizedPanelLabel(\"Dope Sheet\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n"
		+ "\t\t\t$panelName = `scriptedPanel -unParent  -type \"dopeSheetPanel\" -l (localizedPanelLabel(\"Dope Sheet\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 0\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 0\n                -showCompounds 1\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n"
		+ "                -highlightActive 0\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 1\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                $editorName;\n"
		+ "\t\t\t$editorName = ($panelName+\"DopeSheetEd\");\n            dopeSheetEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -autoFit 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -outliner \"dopeSheetPanel1OutlineEd\" \n                -showSummary 1\n                -showScene 0\n                -hierarchyBelow 0\n                -showTicks 1\n                -selectionWindow 0 0 0 0 \n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dope Sheet\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n"
		+ "                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 0\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 0\n                -showCompounds 1\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 1\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n"
		+ "                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"DopeSheetEd\");\n            dopeSheetEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -autoFit 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -outliner \"dopeSheetPanel1OutlineEd\" \n"
		+ "                -showSummary 1\n                -showScene 0\n                -hierarchyBelow 0\n                -showTicks 1\n                -selectionWindow 0 0 0 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"clipEditorPanel\" (localizedPanelLabel(\"Trax Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"clipEditorPanel\" -l (localizedPanelLabel(\"Trax Editor\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = clipEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -autoFit 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -manageSequencer 0 \n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n"
		+ "\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Trax Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = clipEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -autoFit 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -manageSequencer 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"sequenceEditorPanel\" (localizedPanelLabel(\"Camera Sequencer\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"sequenceEditorPanel\" -l (localizedPanelLabel(\"Camera Sequencer\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = sequenceEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n"
		+ "                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -autoFit 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -manageSequencer 1 \n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Camera Sequencer\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = sequenceEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -autoFit 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -manageSequencer 1 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperGraphPanel\" (localizedPanelLabel(\"Hypergraph Hierarchy\")) `;\n"
		+ "\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"hyperGraphPanel\" -l (localizedPanelLabel(\"Hypergraph Hierarchy\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"HyperGraphEd\");\n            hyperGraph -e \n                -graphLayoutStyle \"hierarchicalLayout\" \n                -orientation \"horiz\" \n                -mergeConnections 0\n                -zoom 1\n                -animateTransition 0\n                -showRelationships 1\n                -showShapes 0\n                -showDeformers 0\n                -showExpressions 0\n                -showConstraints 0\n                -showConnectionFromSelected 0\n                -showConnectionToSelected 0\n                -showConstraintLabels 0\n                -showUnderworld 0\n                -showInvisible 0\n                -transitionFrames 1\n                -opaqueContainers 0\n                -freeform 0\n                -imagePosition 0 0 \n                -imageScale 1\n                -imageEnabled 0\n                -graphType \"DAG\" \n"
		+ "                -heatMapDisplay 0\n                -updateSelection 1\n                -updateNodeAdded 1\n                -useDrawOverrideColor 0\n                -limitGraphTraversal -1\n                -range 0 0 \n                -iconSize \"smallIcons\" \n                -showCachedConnections 0\n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypergraph Hierarchy\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"HyperGraphEd\");\n            hyperGraph -e \n                -graphLayoutStyle \"hierarchicalLayout\" \n                -orientation \"horiz\" \n                -mergeConnections 0\n                -zoom 1\n                -animateTransition 0\n                -showRelationships 1\n                -showShapes 0\n                -showDeformers 0\n                -showExpressions 0\n                -showConstraints 0\n                -showConnectionFromSelected 0\n                -showConnectionToSelected 0\n                -showConstraintLabels 0\n"
		+ "                -showUnderworld 0\n                -showInvisible 0\n                -transitionFrames 1\n                -opaqueContainers 0\n                -freeform 0\n                -imagePosition 0 0 \n                -imageScale 1\n                -imageEnabled 0\n                -graphType \"DAG\" \n                -heatMapDisplay 0\n                -updateSelection 1\n                -updateNodeAdded 1\n                -useDrawOverrideColor 0\n                -limitGraphTraversal -1\n                -range 0 0 \n                -iconSize \"smallIcons\" \n                -showCachedConnections 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperShadePanel\" (localizedPanelLabel(\"Hypershade\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"hyperShadePanel\" -l (localizedPanelLabel(\"Hypershade\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n"
		+ "\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypershade\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"visorPanel\" (localizedPanelLabel(\"Visor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"visorPanel\" -l (localizedPanelLabel(\"Visor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Visor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"nodeEditorPanel\" (localizedPanelLabel(\"Node Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"nodeEditorPanel\" -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n"
		+ "                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -defaultPinnedState 0\n                -ignoreAssets 1\n                -additiveGraphingMode 0\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -keyReleaseCommand \"nodeEdKeyReleaseCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                $editorName;;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -defaultPinnedState 0\n                -ignoreAssets 1\n                -additiveGraphingMode 0\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -keyReleaseCommand \"nodeEdKeyReleaseCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                $editorName;;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n"
		+ "\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"createNodePanel\" (localizedPanelLabel(\"Create Node\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"createNodePanel\" -l (localizedPanelLabel(\"Create Node\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Create Node\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"polyTexturePlacementPanel\" (localizedPanelLabel(\"UV Texture Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"polyTexturePlacementPanel\" -l (localizedPanelLabel(\"UV Texture Editor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"UV Texture Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n"
		+ "\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"renderWindowPanel\" (localizedPanelLabel(\"Render View\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"renderWindowPanel\" -l (localizedPanelLabel(\"Render View\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Render View\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"blendShapePanel\" (localizedPanelLabel(\"Blend Shape\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\tblendShapePanel -unParent -l (localizedPanelLabel(\"Blend Shape\")) -mbv $menusOkayInPanels ;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tblendShapePanel -edit -l (localizedPanelLabel(\"Blend Shape\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n"
		+ "\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynRelEdPanel\" (localizedPanelLabel(\"Dynamic Relationships\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"dynRelEdPanel\" -l (localizedPanelLabel(\"Dynamic Relationships\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dynamic Relationships\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"relationshipPanel\" (localizedPanelLabel(\"Relationship Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"relationshipPanel\" -l (localizedPanelLabel(\"Relationship Editor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Relationship Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"referenceEditorPanel\" (localizedPanelLabel(\"Reference Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"referenceEditorPanel\" -l (localizedPanelLabel(\"Reference Editor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Reference Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"componentEditorPanel\" (localizedPanelLabel(\"Component Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"componentEditorPanel\" -l (localizedPanelLabel(\"Component Editor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Component Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynPaintScriptedPanelType\" (localizedPanelLabel(\"Paint Effects\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"dynPaintScriptedPanelType\" -l (localizedPanelLabel(\"Paint Effects\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Paint Effects\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"scriptEditorPanel\" (localizedPanelLabel(\"Script Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"scriptEditorPanel\" -l (localizedPanelLabel(\"Script Editor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Script Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\tif ($useSceneConfig) {\n\t\tscriptedPanel -e -to $panelName;\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"Stereo\" (localizedPanelLabel(\"Stereo\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"Stereo\" -l (localizedPanelLabel(\"Stereo\")) -mbv $menusOkayInPanels `;\nstring $editorName = ($panelName+\"Editor\");\n            stereoCameraView -e \n                -camera \"persp\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"wireframe\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 1\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n"
		+ "                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 16384\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -maxConstantTransparency 1\n                -objectFilterShowInHUD 1\n                -isFiltered 0\n                -colorResolution 4 4 \n                -bumpResolution 4 4 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 0\n                -occlusionCulling 0\n                -shadingModel 0\n"
		+ "                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n"
		+ "                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -clipGhosts 1\n                -greasePencils 1\n                -shadows 0\n                -displayMode \"centerEye\" \n                -viewColor 0 0 0 1 \n                -useCustomBackground 1\n                $editorName;\n            stereoCameraView -e -viewSelected 0 $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Stereo\")) -mbv $menusOkayInPanels  $panelName;\nstring $editorName = ($panelName+\"Editor\");\n            stereoCameraView -e \n                -camera \"persp\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"wireframe\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -selectionHiliteDisplay 1\n"
		+ "                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 1\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 16384\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -maxConstantTransparency 1\n                -objectFilterShowInHUD 1\n                -isFiltered 0\n                -colorResolution 4 4 \n                -bumpResolution 4 4 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n"
		+ "                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 0\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n"
		+ "                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -clipGhosts 1\n                -greasePencils 1\n                -shadows 0\n                -displayMode \"centerEye\" \n                -viewColor 0 0 0 1 \n                -useCustomBackground 1\n                $editorName;\n            stereoCameraView -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\tif ($useSceneConfig) {\n        string $configName = `getPanel -cwl (localizedPanelLabel(\"Current Layout\"))`;\n        if (\"\" != $configName) {\n\t\t\tpanelConfiguration -edit -label (localizedPanelLabel(\"Current Layout\")) \n\t\t\t\t-defaultImage \"vacantCell.xP:/\"\n"
		+ "\t\t\t\t-image \"\"\n\t\t\t\t-sc false\n\t\t\t\t-configString \"global string $gMainPane; paneLayout -e -cn \\\"vertical2\\\" -ps 1 20 100 -ps 2 80 100 $gMainPane;\"\n\t\t\t\t-removeAllPanels\n\t\t\t\t-ap false\n\t\t\t\t\t(localizedPanelLabel(\"Outliner\")) \n\t\t\t\t\t\"outlinerPanel\"\n\t\t\t\t\t\"$panelName = `outlinerPanel -unParent -l (localizedPanelLabel(\\\"Outliner\\\")) -mbv $menusOkayInPanels `;\\n$editorName = $panelName;\\noutlinerEditor -e \\n    -docTag \\\"isolOutln_fromSeln\\\" \\n    -showShapes 0\\n    -showReferenceNodes 0\\n    -showReferenceMembers 0\\n    -showAttributes 0\\n    -showConnected 0\\n    -showAnimCurvesOnly 0\\n    -showMuteInfo 0\\n    -organizeByLayer 1\\n    -showAnimLayerWeight 1\\n    -autoExpandLayers 1\\n    -autoExpand 0\\n    -showDagOnly 1\\n    -showAssets 1\\n    -showContainedOnly 1\\n    -showPublishedAsConnected 0\\n    -showContainerContents 1\\n    -ignoreDagHierarchy 0\\n    -expandConnections 0\\n    -showUpstreamCurves 1\\n    -showUnitlessCurves 1\\n    -showCompounds 1\\n    -showLeafs 1\\n    -showNumericAttrsOnly 0\\n    -highlightActive 1\\n    -autoSelectNewObjects 0\\n    -doNotSelectNewObjects 0\\n    -dropIsParent 1\\n    -transmitFilters 0\\n    -setFilter \\\"defaultSetFilter\\\" \\n    -showSetMembers 1\\n    -allowMultiSelection 1\\n    -alwaysToggleSelect 0\\n    -directSelect 0\\n    -displayMode \\\"DAG\\\" \\n    -expandObjects 0\\n    -setsIgnoreFilters 1\\n    -containersIgnoreFilters 0\\n    -editAttrName 0\\n    -showAttrValues 0\\n    -highlightSecondary 0\\n    -showUVAttrsOnly 0\\n    -showTextureNodesOnly 0\\n    -attrAlphaOrder \\\"default\\\" \\n    -animLayerFilterOptions \\\"allAffecting\\\" \\n    -sortOrder \\\"none\\\" \\n    -longNames 0\\n    -niceNames 1\\n    -showNamespace 1\\n    -showPinIcons 0\\n    -mapMotionTrails 0\\n    -ignoreHiddenAttribute 0\\n    $editorName\"\n"
		+ "\t\t\t\t\t\"outlinerPanel -edit -l (localizedPanelLabel(\\\"Outliner\\\")) -mbv $menusOkayInPanels  $panelName;\\n$editorName = $panelName;\\noutlinerEditor -e \\n    -docTag \\\"isolOutln_fromSeln\\\" \\n    -showShapes 0\\n    -showReferenceNodes 0\\n    -showReferenceMembers 0\\n    -showAttributes 0\\n    -showConnected 0\\n    -showAnimCurvesOnly 0\\n    -showMuteInfo 0\\n    -organizeByLayer 1\\n    -showAnimLayerWeight 1\\n    -autoExpandLayers 1\\n    -autoExpand 0\\n    -showDagOnly 1\\n    -showAssets 1\\n    -showContainedOnly 1\\n    -showPublishedAsConnected 0\\n    -showContainerContents 1\\n    -ignoreDagHierarchy 0\\n    -expandConnections 0\\n    -showUpstreamCurves 1\\n    -showUnitlessCurves 1\\n    -showCompounds 1\\n    -showLeafs 1\\n    -showNumericAttrsOnly 0\\n    -highlightActive 1\\n    -autoSelectNewObjects 0\\n    -doNotSelectNewObjects 0\\n    -dropIsParent 1\\n    -transmitFilters 0\\n    -setFilter \\\"defaultSetFilter\\\" \\n    -showSetMembers 1\\n    -allowMultiSelection 1\\n    -alwaysToggleSelect 0\\n    -directSelect 0\\n    -displayMode \\\"DAG\\\" \\n    -expandObjects 0\\n    -setsIgnoreFilters 1\\n    -containersIgnoreFilters 0\\n    -editAttrName 0\\n    -showAttrValues 0\\n    -highlightSecondary 0\\n    -showUVAttrsOnly 0\\n    -showTextureNodesOnly 0\\n    -attrAlphaOrder \\\"default\\\" \\n    -animLayerFilterOptions \\\"allAffecting\\\" \\n    -sortOrder \\\"none\\\" \\n    -longNames 0\\n    -niceNames 1\\n    -showNamespace 1\\n    -showPinIcons 0\\n    -mapMotionTrails 0\\n    -ignoreHiddenAttribute 0\\n    $editorName\"\n"
		+ "\t\t\t\t-ap false\n\t\t\t\t\t(localizedPanelLabel(\"Persp View\")) \n\t\t\t\t\t\"modelPanel\"\n"
		+ "\t\t\t\t\t\"$panelName = `modelPanel -unParent -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels `;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 16384\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName\"\n"
		+ "\t\t\t\t\t\"modelPanel -edit -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels  $panelName;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 16384\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName\"\n"
		+ "\t\t\t\t$configName;\n\n            setNamedPanelLayout (localizedPanelLabel(\"Current Layout\"));\n        }\n\n        panelHistory -e -clear mainPanelHistory;\n        setFocus `paneLayout -q -p1 $gMainPane`;\n        sceneUIReplacement -deleteRemaining;\n        sceneUIReplacement -clear;\n\t}\n\n\ngrid -spacing 5 -size 12 -divisions 5 -displayAxes yes -displayGridLines yes -displayDivisionLines yes -displayPerspectiveLabels no -displayOrthographicLabels no -displayAxesBold yes -perspectiveLabelPosition axis -orthographicLabelPosition edge;\nviewManip -drawCompass 0 -compassAngle 0 -frontParameters \"\" -homeParameters \"\" -selectionLockParameters \"\";\n}\n");
	setAttr ".st" 3;
createNode script -n "sceneConfigurationScriptNode";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 120 -ast 1 -aet 200 ";
	setAttr ".st" 6;
createNode skinCluster -n "skinCluster4";
	setAttr ".skm" 1;
	setAttr -s 108 ".wl";
	setAttr ".wl[0].w[13]"  1;
	setAttr ".wl[1].w[13]"  1;
	setAttr ".wl[2].w[13]"  1;
	setAttr ".wl[3].w[13]"  1;
	setAttr ".wl[4].w[13]"  1;
	setAttr ".wl[5].w[13]"  1;
	setAttr ".wl[6].w[13]"  1;
	setAttr ".wl[7].w[13]"  1;
	setAttr ".wl[8].w[13]"  1;
	setAttr ".wl[9].w[13]"  1;
	setAttr ".wl[10].w[13]"  1;
	setAttr ".wl[11].w[13]"  1;
	setAttr ".wl[12].w[11]"  1;
	setAttr ".wl[13].w[11]"  1;
	setAttr ".wl[14].w[11]"  1;
	setAttr ".wl[15].w[11]"  1;
	setAttr ".wl[16].w[16]"  1;
	setAttr ".wl[17].w[16]"  1;
	setAttr ".wl[18].w[16]"  1;
	setAttr ".wl[19].w[16]"  1;
	setAttr ".wl[20].w[16]"  1;
	setAttr ".wl[21].w[16]"  1;
	setAttr ".wl[22].w[16]"  1;
	setAttr ".wl[23].w[16]"  1;
	setAttr ".wl[24].w[16]"  1;
	setAttr ".wl[25].w[16]"  1;
	setAttr ".wl[26].w[16]"  1;
	setAttr ".wl[27].w[16]"  1;
	setAttr ".wl[28].w[8]"  1;
	setAttr ".wl[29].w[8]"  1;
	setAttr ".wl[30].w[8]"  1;
	setAttr ".wl[31].w[8]"  1;
	setAttr ".wl[32].w[10]"  1;
	setAttr ".wl[33].w[10]"  1;
	setAttr ".wl[34].w[10]"  1;
	setAttr ".wl[35].w[10]"  1;
	setAttr ".wl[36].w[7]"  1;
	setAttr ".wl[37].w[7]"  1;
	setAttr ".wl[38].w[7]"  1;
	setAttr ".wl[39].w[7]"  1;
	setAttr ".wl[40].w[0]"  1;
	setAttr ".wl[41].w[0]"  1;
	setAttr ".wl[42].w[0]"  1;
	setAttr ".wl[43].w[0]"  1;
	setAttr ".wl[44].w[4]"  1;
	setAttr ".wl[45].w[4]"  1;
	setAttr ".wl[46].w[4]"  1;
	setAttr ".wl[47].w[4]"  1;
	setAttr ".wl[48].w[2]"  1;
	setAttr ".wl[49].w[2]"  1;
	setAttr ".wl[50].w[2]"  1;
	setAttr ".wl[51].w[2]"  1;
	setAttr ".wl[52].w[14]"  1;
	setAttr ".wl[53].w[14]"  1;
	setAttr ".wl[54].w[14]"  1;
	setAttr ".wl[55].w[14]"  1;
	setAttr ".wl[56].w[14]"  1;
	setAttr ".wl[57].w[14]"  1;
	setAttr ".wl[58].w[14]"  1;
	setAttr ".wl[59].w[14]"  1;
	setAttr ".wl[60].w[14]"  1;
	setAttr ".wl[61].w[14]"  1;
	setAttr ".wl[62].w[14]"  1;
	setAttr ".wl[63].w[14]"  1;
	setAttr ".wl[64].w[12]"  1;
	setAttr ".wl[65].w[12]"  1;
	setAttr ".wl[66].w[12]"  1;
	setAttr ".wl[67].w[12]"  1;
	setAttr ".wl[68].w[15]"  1;
	setAttr ".wl[69].w[15]"  1;
	setAttr ".wl[70].w[15]"  1;
	setAttr ".wl[71].w[15]"  1;
	setAttr ".wl[72].w[15]"  1;
	setAttr ".wl[73].w[15]"  1;
	setAttr ".wl[74].w[15]"  1;
	setAttr ".wl[75].w[15]"  1;
	setAttr ".wl[76].w[15]"  1;
	setAttr ".wl[77].w[15]"  1;
	setAttr ".wl[78].w[15]"  1;
	setAttr ".wl[79].w[15]"  1;
	setAttr ".wl[80].w[8]"  1;
	setAttr ".wl[81].w[8]"  1;
	setAttr ".wl[82].w[8]"  1;
	setAttr ".wl[83].w[8]"  1;
	setAttr ".wl[84].w[10]"  1;
	setAttr ".wl[85].w[10]"  1;
	setAttr ".wl[86].w[10]"  1;
	setAttr ".wl[87].w[10]"  1;
	setAttr ".wl[88].w[6]"  1;
	setAttr ".wl[89].w[6]"  1;
	setAttr ".wl[90].w[6]"  1;
	setAttr ".wl[91].w[6]"  1;
	setAttr ".wl[92].w[1]"  1;
	setAttr ".wl[93].w[1]"  1;
	setAttr ".wl[94].w[1]"  1;
	setAttr ".wl[95].w[1]"  1;
	setAttr ".wl[96].w[5]"  1;
	setAttr ".wl[97].w[5]"  1;
	setAttr ".wl[98].w[5]"  1;
	setAttr ".wl[99].w[5]"  1;
	setAttr ".wl[100].w[3]"  1;
	setAttr ".wl[101].w[3]"  1;
	setAttr ".wl[102].w[3]"  1;
	setAttr ".wl[103].w[3]"  1;
	setAttr ".wl[104].w[9]"  1;
	setAttr ".wl[105].w[9]"  1;
	setAttr ".wl[106].w[9]"  1;
	setAttr ".wl[107].w[9]"  1;
	setAttr -s 17 ".pm";
	setAttr ".pm[0]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 2.0000000000000018 -1.477517415474795 4.8855741047437258 1;
	setAttr ".pm[1]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -2 -1.477517415474795 4.8855741047437258 1;
	setAttr ".pm[2]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 3.0000000000000027 -1.477517415474795 4.0000000000000009 1;
	setAttr ".pm[3]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -3.0000000000000027 -1.477517415474795 4.0000000000000009 1;
	setAttr ".pm[4]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 3.0000000000000027 -1.477517415474795 -4.0000000000000009 1;
	setAttr ".pm[5]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -3.0000000000000027 -1.477517415474795 -4.0000000000000009 1;
	setAttr ".pm[6]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -2.0000000000000018 -1.477517415474795 -5.1402641693652162 1;
	setAttr ".pm[7]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 2.0000000000000018 -1.477517415474795 -5.1402641693652162 1;
	setAttr ".pm[8]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 -1.4569915366249484 4.8964197211647278 1;
	setAttr ".pm[9]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 -1.4569915366249484 0 1;
	setAttr ".pm[10]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 -1.4569915366249484 -5.1241344655245795 1;
	setAttr ".pm[11]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 3.0000000000000027 -1.477517415474795 0 1;
	setAttr ".pm[12]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -3.0000000000000027 -1.477517415474795 0 1;
	setAttr ".pm[13]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 3.0000000000000027 -2.0925980732688192 4.8685500664020953 1;
	setAttr ".pm[14]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -3 -2.0925980732688192 4.8685500664020953 1;
	setAttr ".pm[15]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -3 -2.0925980732688192 -5.1271181676607132 1;
	setAttr ".pm[16]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 3 -2.0925980732688192 -5.1271181676607132 1;
	setAttr ".gm" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr -s 17 ".ma";
	setAttr -s 17 ".dpf[0:16]"  4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4;
	setAttr -s 17 ".lw";
	setAttr -s 17 ".lw";
	setAttr ".mi" 1;
	setAttr ".ucm" yes;
	setAttr -s 17 ".ifcl";
	setAttr -s 17 ".ifcl";
createNode groupId -n "groupId12";
	setAttr ".ihi" 0;
createNode groupParts -n "groupParts10";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "f[0:109]";
createNode tweak -n "tweak5";
createNode objectSet -n "skinCluster4Set";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "skinCluster4GroupId";
	setAttr ".ihi" 0;
createNode groupParts -n "skinCluster4GroupParts";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[*]";
createNode objectSet -n "tweakSet5";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "groupId14";
	setAttr ".ihi" 0;
createNode groupParts -n "groupParts12";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[*]";
createNode dagPose -n "bindPose5";
	setAttr -s 17 ".wm";
	setAttr -s 17 ".xm";
	setAttr ".xm[0]" -type "matrix" "xform" 1 1 1 0 0 0 0 -2.0000000000000018 1.477517415474795
		 -4.8855741047437258 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[1]" -type "matrix" "xform" 1 1 1 0 0 0 0 2 1.477517415474795 -4.8855741047437258 0
		 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[2]" -type "matrix" "xform" 1 1 1 0 0 0 0 -3.0000000000000027 1.477517415474795
		 -4.0000000000000009 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[3]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.0000000000000027 1.477517415474795
		 -4.0000000000000009 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[4]" -type "matrix" "xform" 1 1 1 0 0 0 0 -3.0000000000000027 1.477517415474795
		 4.0000000000000009 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[5]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.0000000000000027 1.477517415474795
		 4.0000000000000009 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[6]" -type "matrix" "xform" 1 1 1 0 0 0 0 2.0000000000000018 1.477517415474795
		 5.1402641693652162 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[7]" -type "matrix" "xform" 1 1 1 0 0 0 0 -2.0000000000000018 1.477517415474795
		 5.1402641693652162 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[8]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 1.4569915366249484 -4.8964197211647278 0
		 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[9]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 1.4569915366249484 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[10]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 1.4569915366249484
		 5.1241344655245795 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[11]" -type "matrix" "xform" 1 1 1 0 0 0 0 -3.0000000000000027 1.477517415474795
		 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[12]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.0000000000000027 1.477517415474795
		 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[13]" -type "matrix" "xform" 1 1 1 0 0 0 0 -3.0000000000000027 2.0925980732688192
		 -4.8685500664020953 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[14]" -type "matrix" "xform" 1 1 1 0 0 0 0 3 2.0925980732688192
		 -4.8685500664020953 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[15]" -type "matrix" "xform" 1 1 1 0 0 0 0 3 2.0925980732688192
		 5.1271181676607132 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[16]" -type "matrix" "xform" 1 1 1 0 0 0 0 -3 2.0925980732688192
		 5.1271181676607132 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr -s 17 ".m";
	setAttr -s 17 ".p";
	setAttr ".bp" yes;
createNode unitConversion -n "unitConversion1";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "multiplyDivide4";
	setAttr ".i2" -type "float3" -1 -1 1 ;
createNode ilrOptionsNode -s -n "TurtleRenderOptions";
lockNode -l 1 ;
createNode ilrUIOptionsNode -s -n "TurtleUIOptions";
lockNode -l 1 ;
createNode ilrBakeLayerManager -s -n "TurtleBakeLayerManager";
lockNode -l 1 ;
createNode ilrBakeLayer -s -n "TurtleDefaultBakeLayer";
lockNode -l 1 ;
select -ne :time1;
	setAttr -av -k on ".cch";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr ".o" 1;
	setAttr ".unw" 1;
select -ne :renderPartition;
	setAttr -cb on ".bnm";
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
	setAttr -cb on ".bnm";
select -ne :defaultShaderList1;
	setAttr -cb on ".bnm";
	setAttr -s 2 ".s";
select -ne :postProcessList1;
	setAttr -cb on ".bnm";
	setAttr -s 2 ".p";
select -ne :defaultRenderUtilityList1;
select -ne :defaultRenderingList1;
select -ne :initialShadingGroup;
	setAttr -k on ".cch";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".mwc";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr -k on ".cch";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr ".ro" yes;
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
connectAttr "midLeft_GRP_pointConstraint1.ctx" "midLeft_GRP.tx";
connectAttr "midLeft_GRP_pointConstraint1.cty" "midLeft_GRP.ty";
connectAttr "midLeft_GRP_pointConstraint1.ctz" "midLeft_GRP.tz";
connectAttr "midLeft_GRP.pim" "midLeft_GRP_pointConstraint1.cpim";
connectAttr "midLeft_GRP.rp" "midLeft_GRP_pointConstraint1.crp";
connectAttr "midLeft_GRP.rpt" "midLeft_GRP_pointConstraint1.crt";
connectAttr "leftFront_JNT.t" "midLeft_GRP_pointConstraint1.tg[0].tt";
connectAttr "leftFront_JNT.rp" "midLeft_GRP_pointConstraint1.tg[0].trp";
connectAttr "leftFront_JNT.rpt" "midLeft_GRP_pointConstraint1.tg[0].trt";
connectAttr "leftFront_JNT.pm" "midLeft_GRP_pointConstraint1.tg[0].tpm";
connectAttr "midLeft_GRP_pointConstraint1.w0" "midLeft_GRP_pointConstraint1.tg[0].tw"
		;
connectAttr "leftBack_JNT.t" "midLeft_GRP_pointConstraint1.tg[1].tt";
connectAttr "leftBack_JNT.rp" "midLeft_GRP_pointConstraint1.tg[1].trp";
connectAttr "leftBack_JNT.rpt" "midLeft_GRP_pointConstraint1.tg[1].trt";
connectAttr "leftBack_JNT.pm" "midLeft_GRP_pointConstraint1.tg[1].tpm";
connectAttr "midLeft_GRP_pointConstraint1.w1" "midLeft_GRP_pointConstraint1.tg[1].tw"
		;
connectAttr "midRight_GRP_pointConstraint1.ctx" "midRight_GRP.tx";
connectAttr "midRight_GRP_pointConstraint1.cty" "midRight_GRP.ty";
connectAttr "midRight_GRP_pointConstraint1.ctz" "midRight_GRP.tz";
connectAttr "midRight_GRP.pim" "midRight_GRP_pointConstraint1.cpim";
connectAttr "midRight_GRP.rp" "midRight_GRP_pointConstraint1.crp";
connectAttr "midRight_GRP.rpt" "midRight_GRP_pointConstraint1.crt";
connectAttr "rightFront_JNT.t" "midRight_GRP_pointConstraint1.tg[0].tt";
connectAttr "rightFront_JNT.rp" "midRight_GRP_pointConstraint1.tg[0].trp";
connectAttr "rightFront_JNT.rpt" "midRight_GRP_pointConstraint1.tg[0].trt";
connectAttr "rightFront_JNT.pm" "midRight_GRP_pointConstraint1.tg[0].tpm";
connectAttr "midRight_GRP_pointConstraint1.w0" "midRight_GRP_pointConstraint1.tg[0].tw"
		;
connectAttr "rightBack_JNT.t" "midRight_GRP_pointConstraint1.tg[1].tt";
connectAttr "rightBack_JNT.rp" "midRight_GRP_pointConstraint1.tg[1].trp";
connectAttr "rightBack_JNT.rpt" "midRight_GRP_pointConstraint1.tg[1].trt";
connectAttr "rightBack_JNT.pm" "midRight_GRP_pointConstraint1.tg[1].tpm";
connectAttr "midRight_GRP_pointConstraint1.w1" "midRight_GRP_pointConstraint1.tg[1].tw"
		;
connectAttr "frontCenter_GRP_pointConstraint1.ctx" "frontCenter_GRP.tx";
connectAttr "frontCenter_GRP_pointConstraint1.cty" "frontCenter_GRP.ty";
connectAttr "frontCenter_GRP_pointConstraint1.ctz" "frontCenter_GRP.tz";
connectAttr "frontCenter_GRP.pim" "frontCenter_GRP_pointConstraint1.cpim";
connectAttr "frontCenter_GRP.rp" "frontCenter_GRP_pointConstraint1.crp";
connectAttr "frontCenter_GRP.rpt" "frontCenter_GRP_pointConstraint1.crt";
connectAttr "frontRight_JNT.t" "frontCenter_GRP_pointConstraint1.tg[0].tt";
connectAttr "frontRight_JNT.rp" "frontCenter_GRP_pointConstraint1.tg[0].trp";
connectAttr "frontRight_JNT.rpt" "frontCenter_GRP_pointConstraint1.tg[0].trt";
connectAttr "frontRight_JNT.pm" "frontCenter_GRP_pointConstraint1.tg[0].tpm";
connectAttr "frontCenter_GRP_pointConstraint1.w0" "frontCenter_GRP_pointConstraint1.tg[0].tw"
		;
connectAttr "frontLeft_JNT.t" "frontCenter_GRP_pointConstraint1.tg[1].tt";
connectAttr "frontLeft_JNT.rp" "frontCenter_GRP_pointConstraint1.tg[1].trp";
connectAttr "frontLeft_JNT.rpt" "frontCenter_GRP_pointConstraint1.tg[1].trt";
connectAttr "frontLeft_JNT.pm" "frontCenter_GRP_pointConstraint1.tg[1].tpm";
connectAttr "frontCenter_GRP_pointConstraint1.w1" "frontCenter_GRP_pointConstraint1.tg[1].tw"
		;
connectAttr "midCenter_GRP_pointConstraint1.ctx" "midCenter_GRP.tx";
connectAttr "midCenter_GRP_pointConstraint1.cty" "midCenter_GRP.ty";
connectAttr "midCenter_GRP_pointConstraint1.ctz" "midCenter_GRP.tz";
connectAttr "midCenter_GRP.pim" "midCenter_GRP_pointConstraint1.cpim";
connectAttr "midCenter_GRP.rp" "midCenter_GRP_pointConstraint1.crp";
connectAttr "midCenter_GRP.rpt" "midCenter_GRP_pointConstraint1.crt";
connectAttr "frontCenter_JNT.t" "midCenter_GRP_pointConstraint1.tg[0].tt";
connectAttr "frontCenter_JNT.rp" "midCenter_GRP_pointConstraint1.tg[0].trp";
connectAttr "frontCenter_JNT.rpt" "midCenter_GRP_pointConstraint1.tg[0].trt";
connectAttr "frontCenter_JNT.pm" "midCenter_GRP_pointConstraint1.tg[0].tpm";
connectAttr "midCenter_GRP_pointConstraint1.w0" "midCenter_GRP_pointConstraint1.tg[0].tw"
		;
connectAttr "backCenter_JNT.t" "midCenter_GRP_pointConstraint1.tg[1].tt";
connectAttr "backCenter_JNT.rp" "midCenter_GRP_pointConstraint1.tg[1].trp";
connectAttr "backCenter_JNT.rpt" "midCenter_GRP_pointConstraint1.tg[1].trt";
connectAttr "backCenter_JNT.pm" "midCenter_GRP_pointConstraint1.tg[1].tpm";
connectAttr "midCenter_GRP_pointConstraint1.w1" "midCenter_GRP_pointConstraint1.tg[1].tw"
		;
connectAttr "backCenter_GRP_pointConstraint1.ctx" "backCenter_GRP.tx";
connectAttr "backCenter_GRP_pointConstraint1.cty" "backCenter_GRP.ty";
connectAttr "backCenter_GRP_pointConstraint1.ctz" "backCenter_GRP.tz";
connectAttr "backCenter_GRP.pim" "backCenter_GRP_pointConstraint1.cpim";
connectAttr "backCenter_GRP.rp" "backCenter_GRP_pointConstraint1.crp";
connectAttr "backCenter_GRP.rpt" "backCenter_GRP_pointConstraint1.crt";
connectAttr "backLeft_JNT.t" "backCenter_GRP_pointConstraint1.tg[0].tt";
connectAttr "backLeft_JNT.rp" "backCenter_GRP_pointConstraint1.tg[0].trp";
connectAttr "backLeft_JNT.rpt" "backCenter_GRP_pointConstraint1.tg[0].trt";
connectAttr "backLeft_JNT.pm" "backCenter_GRP_pointConstraint1.tg[0].tpm";
connectAttr "backCenter_GRP_pointConstraint1.w0" "backCenter_GRP_pointConstraint1.tg[0].tw"
		;
connectAttr "backRight_JNT.t" "backCenter_GRP_pointConstraint1.tg[1].tt";
connectAttr "backRight_JNT.rp" "backCenter_GRP_pointConstraint1.tg[1].trp";
connectAttr "backRight_JNT.rpt" "backCenter_GRP_pointConstraint1.tg[1].trt";
connectAttr "backRight_JNT.pm" "backCenter_GRP_pointConstraint1.tg[1].tpm";
connectAttr "backCenter_GRP_pointConstraint1.w1" "backCenter_GRP_pointConstraint1.tg[1].tw"
		;
connectAttr "FrameControl_CRV.BackFrameTZ" "backRightShock_LOC.tz";
connectAttr "FrameControl_CRV.BackShockHeight" "backRightShock_LOC.ty";
connectAttr "multiplyDivide4.ox" "backRightShock_LOC.tx";
connectAttr "FrameControl_CRV.BackFrameTZ" "backLeftShock_LOC.tz";
connectAttr "FrameControl_CRV.BackShockHeight" "backLeftShock_LOC.ty";
connectAttr "FrameControl_CRV.BackFrameNarrowWide" "backLeftShock_LOC.tx";
connectAttr "FrameControl_CRV.FrontFrameTZ" "frontLeftShock_LOC.tz";
connectAttr "FrameControl_CRV.FrontShockHeight" "frontLeftShock_LOC.ty";
connectAttr "FrameControl_CRV.FrontFrameNarrowWide" "frontLeftShock_LOC.tx";
connectAttr "FrameControl_CRV.FrontFrameTZ" "frontRightShock_LOC.tz";
connectAttr "FrameControl_CRV.FrontShockHeight" "frontRightShock_LOC.ty";
connectAttr "multiplyDivide4.oy" "frontRightShock_LOC.tx";
connectAttr "unitConversion1.o" "FrameHeight_GRP.rx";
connectAttr "FrameControl_CRV.FrameHeight" "FrameHeight_GRP.ty";
connectAttr "backRight_GRP_pointConstraint1.ctx" "backRight_GRP.tx";
connectAttr "backRight_GRP_pointConstraint1.ctz" "backRight_GRP.tz";
connectAttr "backRight_GRP.pim" "backRight_GRP_pointConstraint1.cpim";
connectAttr "backRight_GRP.rp" "backRight_GRP_pointConstraint1.crp";
connectAttr "backRight_GRP.rpt" "backRight_GRP_pointConstraint1.crt";
connectAttr "backRightShock_JNT.t" "backRight_GRP_pointConstraint1.tg[0].tt";
connectAttr "backRightShock_JNT.rp" "backRight_GRP_pointConstraint1.tg[0].trp";
connectAttr "backRightShock_JNT.rpt" "backRight_GRP_pointConstraint1.tg[0].trt";
connectAttr "backRightShock_JNT.pm" "backRight_GRP_pointConstraint1.tg[0].tpm";
connectAttr "backRight_GRP_pointConstraint1.w0" "backRight_GRP_pointConstraint1.tg[0].tw"
		;
connectAttr "backLeft_GRP_pointConstraint1.ctx" "backLeft_GRP.tx";
connectAttr "backLeft_GRP_pointConstraint1.ctz" "backLeft_GRP.tz";
connectAttr "backLeft_GRP.pim" "backLeft_GRP_pointConstraint1.cpim";
connectAttr "backLeft_GRP.rp" "backLeft_GRP_pointConstraint1.crp";
connectAttr "backLeft_GRP.rpt" "backLeft_GRP_pointConstraint1.crt";
connectAttr "backLeftShock_JNT.t" "backLeft_GRP_pointConstraint1.tg[0].tt";
connectAttr "backLeftShock_JNT.rp" "backLeft_GRP_pointConstraint1.tg[0].trp";
connectAttr "backLeftShock_JNT.rpt" "backLeft_GRP_pointConstraint1.tg[0].trt";
connectAttr "backLeftShock_JNT.pm" "backLeft_GRP_pointConstraint1.tg[0].tpm";
connectAttr "backLeft_GRP_pointConstraint1.w0" "backLeft_GRP_pointConstraint1.tg[0].tw"
		;
connectAttr "rightBack_GRP_pointConstraint1.ctx" "rightBack_GRP.tx";
connectAttr "rightBack_GRP_pointConstraint1.ctz" "rightBack_GRP.tz";
connectAttr "rightBack_GRP.pim" "rightBack_GRP_pointConstraint1.cpim";
connectAttr "rightBack_GRP.rp" "rightBack_GRP_pointConstraint1.crp";
connectAttr "rightBack_GRP.rpt" "rightBack_GRP_pointConstraint1.crt";
connectAttr "backRightShock_JNT.t" "rightBack_GRP_pointConstraint1.tg[0].tt";
connectAttr "backRightShock_JNT.rp" "rightBack_GRP_pointConstraint1.tg[0].trp";
connectAttr "backRightShock_JNT.rpt" "rightBack_GRP_pointConstraint1.tg[0].trt";
connectAttr "backRightShock_JNT.pm" "rightBack_GRP_pointConstraint1.tg[0].tpm";
connectAttr "rightBack_GRP_pointConstraint1.w0" "rightBack_GRP_pointConstraint1.tg[0].tw"
		;
connectAttr "leftBack_GRP_pointConstraint1.ctx" "leftBack_GRP.tx";
connectAttr "leftBack_GRP_pointConstraint1.ctz" "leftBack_GRP.tz";
connectAttr "leftBack_GRP.pim" "leftBack_GRP_pointConstraint1.cpim";
connectAttr "leftBack_GRP.rp" "leftBack_GRP_pointConstraint1.crp";
connectAttr "leftBack_GRP.rpt" "leftBack_GRP_pointConstraint1.crt";
connectAttr "backLeftShock_JNT.t" "leftBack_GRP_pointConstraint1.tg[0].tt";
connectAttr "backLeftShock_JNT.rp" "leftBack_GRP_pointConstraint1.tg[0].trp";
connectAttr "backLeftShock_JNT.rpt" "leftBack_GRP_pointConstraint1.tg[0].trt";
connectAttr "backLeftShock_JNT.pm" "leftBack_GRP_pointConstraint1.tg[0].tpm";
connectAttr "leftBack_GRP_pointConstraint1.w0" "leftBack_GRP_pointConstraint1.tg[0].tw"
		;
connectAttr "rightFront_GRP_pointConstraint1.ctx" "rightFront_GRP.tx";
connectAttr "rightFront_GRP_pointConstraint1.ctz" "rightFront_GRP.tz";
connectAttr "rightFront_GRP.pim" "rightFront_GRP_pointConstraint1.cpim";
connectAttr "rightFront_GRP.rp" "rightFront_GRP_pointConstraint1.crp";
connectAttr "rightFront_GRP.rpt" "rightFront_GRP_pointConstraint1.crt";
connectAttr "frontRightShock_JNT.t" "rightFront_GRP_pointConstraint1.tg[0].tt";
connectAttr "frontRightShock_JNT.rp" "rightFront_GRP_pointConstraint1.tg[0].trp"
		;
connectAttr "frontRightShock_JNT.rpt" "rightFront_GRP_pointConstraint1.tg[0].trt"
		;
connectAttr "frontRightShock_JNT.pm" "rightFront_GRP_pointConstraint1.tg[0].tpm"
		;
connectAttr "rightFront_GRP_pointConstraint1.w0" "rightFront_GRP_pointConstraint1.tg[0].tw"
		;
connectAttr "leftFront_GRP_pointConstraint1.ctx" "leftFront_GRP.tx";
connectAttr "leftFront_GRP_pointConstraint1.ctz" "leftFront_GRP.tz";
connectAttr "leftFront_GRP.pim" "leftFront_GRP_pointConstraint1.cpim";
connectAttr "leftFront_GRP.rp" "leftFront_GRP_pointConstraint1.crp";
connectAttr "leftFront_GRP.rpt" "leftFront_GRP_pointConstraint1.crt";
connectAttr "frontLeftShock_JNT.t" "leftFront_GRP_pointConstraint1.tg[0].tt";
connectAttr "frontLeftShock_JNT.rp" "leftFront_GRP_pointConstraint1.tg[0].trp";
connectAttr "frontLeftShock_JNT.rpt" "leftFront_GRP_pointConstraint1.tg[0].trt";
connectAttr "frontLeftShock_JNT.pm" "leftFront_GRP_pointConstraint1.tg[0].tpm";
connectAttr "leftFront_GRP_pointConstraint1.w0" "leftFront_GRP_pointConstraint1.tg[0].tw"
		;
connectAttr "frontLeft_GRP_pointConstraint1.ctx" "frontLeft_GRP.tx";
connectAttr "frontLeft_GRP_pointConstraint1.ctz" "frontLeft_GRP.tz";
connectAttr "frontLeft_GRP.pim" "frontLeft_GRP_pointConstraint1.cpim";
connectAttr "frontLeft_GRP.rp" "frontLeft_GRP_pointConstraint1.crp";
connectAttr "frontLeft_GRP.rpt" "frontLeft_GRP_pointConstraint1.crt";
connectAttr "frontLeftShock_JNT.t" "frontLeft_GRP_pointConstraint1.tg[0].tt";
connectAttr "frontLeftShock_JNT.rp" "frontLeft_GRP_pointConstraint1.tg[0].trp";
connectAttr "frontLeftShock_JNT.rpt" "frontLeft_GRP_pointConstraint1.tg[0].trt";
connectAttr "frontLeftShock_JNT.pm" "frontLeft_GRP_pointConstraint1.tg[0].tpm";
connectAttr "frontLeft_GRP_pointConstraint1.w0" "frontLeft_GRP_pointConstraint1.tg[0].tw"
		;
connectAttr "frontRight_GRP_pointConstraint1.ctx" "frontRight_GRP.tx";
connectAttr "frontRight_GRP_pointConstraint1.ctz" "frontRight_GRP.tz";
connectAttr "frontRight_GRP.pim" "frontRight_GRP_pointConstraint1.cpim";
connectAttr "frontRight_GRP.rp" "frontRight_GRP_pointConstraint1.crp";
connectAttr "frontRight_GRP.rpt" "frontRight_GRP_pointConstraint1.crt";
connectAttr "frontRightShock_JNT.t" "frontRight_GRP_pointConstraint1.tg[0].tt";
connectAttr "frontRightShock_JNT.rp" "frontRight_GRP_pointConstraint1.tg[0].trp"
		;
connectAttr "frontRightShock_JNT.rpt" "frontRight_GRP_pointConstraint1.tg[0].trt"
		;
connectAttr "frontRightShock_JNT.pm" "frontRight_GRP_pointConstraint1.tg[0].tpm"
		;
connectAttr "frontRight_GRP_pointConstraint1.w0" "frontRight_GRP_pointConstraint1.tg[0].tw"
		;
connectAttr "skinCluster4.og[0]" "Frame_1_GEOShape.i";
connectAttr "groupId12.id" "Frame_1_GEOShape.iog.og[0].gid";
connectAttr ":initialShadingGroup.mwc" "Frame_1_GEOShape.iog.og[0].gco";
connectAttr "skinCluster4GroupId.id" "Frame_1_GEOShape.iog.og[1].gid";
connectAttr "skinCluster4Set.mwc" "Frame_1_GEOShape.iog.og[1].gco";
connectAttr "groupId14.id" "Frame_1_GEOShape.iog.og[2].gid";
connectAttr "tweakSet5.mwc" "Frame_1_GEOShape.iog.og[2].gco";
connectAttr "tweak5.vl[0].vt[0]" "Frame_1_GEOShape.twl";
connectAttr ":mentalrayGlobals.msg" ":mentalrayItemsList.glb";
connectAttr ":miDefaultOptions.msg" ":mentalrayItemsList.opt" -na;
connectAttr ":miDefaultFramebuffer.msg" ":mentalrayItemsList.fb" -na;
connectAttr ":miDefaultOptions.msg" ":mentalrayGlobals.opt";
connectAttr ":miDefaultFramebuffer.msg" ":mentalrayGlobals.fb";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "skinCluster4GroupParts.og" "skinCluster4.ip[0].ig";
connectAttr "skinCluster4GroupId.id" "skinCluster4.ip[0].gi";
connectAttr "bindPose5.msg" "skinCluster4.bp";
connectAttr "backRight_JNT.wm" "skinCluster4.ma[0]";
connectAttr "backLeft_JNT.wm" "skinCluster4.ma[1]";
connectAttr "rightBack_JNT.wm" "skinCluster4.ma[2]";
connectAttr "leftBack_JNT.wm" "skinCluster4.ma[3]";
connectAttr "rightFront_JNT.wm" "skinCluster4.ma[4]";
connectAttr "leftFront_JNT.wm" "skinCluster4.ma[5]";
connectAttr "frontLeft_JNT.wm" "skinCluster4.ma[6]";
connectAttr "frontRight_JNT.wm" "skinCluster4.ma[7]";
connectAttr "backCenter_JNT.wm" "skinCluster4.ma[8]";
connectAttr "midCenter_JNT.wm" "skinCluster4.ma[9]";
connectAttr "frontCenter_JNT.wm" "skinCluster4.ma[10]";
connectAttr "midRight_JNT.wm" "skinCluster4.ma[11]";
connectAttr "midLeft_JNT.wm" "skinCluster4.ma[12]";
connectAttr "backRightShock_JNT.wm" "skinCluster4.ma[13]";
connectAttr "backLeftShock_JNT.wm" "skinCluster4.ma[14]";
connectAttr "frontLeftShock_JNT.wm" "skinCluster4.ma[15]";
connectAttr "frontRightShock_JNT.wm" "skinCluster4.ma[16]";
connectAttr "backRight_JNT.liw" "skinCluster4.lw[0]";
connectAttr "backLeft_JNT.liw" "skinCluster4.lw[1]";
connectAttr "rightBack_JNT.liw" "skinCluster4.lw[2]";
connectAttr "leftBack_JNT.liw" "skinCluster4.lw[3]";
connectAttr "rightFront_JNT.liw" "skinCluster4.lw[4]";
connectAttr "leftFront_JNT.liw" "skinCluster4.lw[5]";
connectAttr "frontLeft_JNT.liw" "skinCluster4.lw[6]";
connectAttr "frontRight_JNT.liw" "skinCluster4.lw[7]";
connectAttr "backCenter_JNT.liw" "skinCluster4.lw[8]";
connectAttr "midCenter_JNT.liw" "skinCluster4.lw[9]";
connectAttr "frontCenter_JNT.liw" "skinCluster4.lw[10]";
connectAttr "midRight_JNT.liw" "skinCluster4.lw[11]";
connectAttr "midLeft_JNT.liw" "skinCluster4.lw[12]";
connectAttr "backRightShock_JNT.liw" "skinCluster4.lw[13]";
connectAttr "backLeftShock_JNT.liw" "skinCluster4.lw[14]";
connectAttr "frontLeftShock_JNT.liw" "skinCluster4.lw[15]";
connectAttr "frontRightShock_JNT.liw" "skinCluster4.lw[16]";
connectAttr "backRight_JNT.obcc" "skinCluster4.ifcl[0]";
connectAttr "backLeft_JNT.obcc" "skinCluster4.ifcl[1]";
connectAttr "rightBack_JNT.obcc" "skinCluster4.ifcl[2]";
connectAttr "leftBack_JNT.obcc" "skinCluster4.ifcl[3]";
connectAttr "rightFront_JNT.obcc" "skinCluster4.ifcl[4]";
connectAttr "leftFront_JNT.obcc" "skinCluster4.ifcl[5]";
connectAttr "frontLeft_JNT.obcc" "skinCluster4.ifcl[6]";
connectAttr "frontRight_JNT.obcc" "skinCluster4.ifcl[7]";
connectAttr "backCenter_JNT.obcc" "skinCluster4.ifcl[8]";
connectAttr "midCenter_JNT.obcc" "skinCluster4.ifcl[9]";
connectAttr "frontCenter_JNT.obcc" "skinCluster4.ifcl[10]";
connectAttr "midRight_JNT.obcc" "skinCluster4.ifcl[11]";
connectAttr "midLeft_JNT.obcc" "skinCluster4.ifcl[12]";
connectAttr "backRightShock_JNT.obcc" "skinCluster4.ifcl[13]";
connectAttr "backLeftShock_JNT.obcc" "skinCluster4.ifcl[14]";
connectAttr "frontLeftShock_JNT.obcc" "skinCluster4.ifcl[15]";
connectAttr "frontRightShock_JNT.obcc" "skinCluster4.ifcl[16]";
connectAttr "midRight_JNT.msg" "skinCluster4.ptt";
connectAttr "Frame_1_GEOShapeOrig.w" "groupParts10.ig";
connectAttr "groupId12.id" "groupParts10.gi";
connectAttr "groupParts12.og" "tweak5.ip[0].ig";
connectAttr "groupId14.id" "tweak5.ip[0].gi";
connectAttr "skinCluster4GroupId.msg" "skinCluster4Set.gn" -na;
connectAttr "Frame_1_GEOShape.iog.og[1]" "skinCluster4Set.dsm" -na;
connectAttr "skinCluster4.msg" "skinCluster4Set.ub[0]";
connectAttr "tweak5.og[0]" "skinCluster4GroupParts.ig";
connectAttr "skinCluster4GroupId.id" "skinCluster4GroupParts.gi";
connectAttr "groupId14.msg" "tweakSet5.gn" -na;
connectAttr "Frame_1_GEOShape.iog.og[2]" "tweakSet5.dsm" -na;
connectAttr "tweak5.msg" "tweakSet5.ub[0]";
connectAttr "groupParts10.og" "groupParts12.ig";
connectAttr "groupId14.id" "groupParts12.gi";
connectAttr "backRight_JNT.msg" "bindPose5.m[0]";
connectAttr "backLeft_JNT.msg" "bindPose5.m[1]";
connectAttr "rightBack_JNT.msg" "bindPose5.m[2]";
connectAttr "leftBack_JNT.msg" "bindPose5.m[3]";
connectAttr "rightFront_JNT.msg" "bindPose5.m[4]";
connectAttr "leftFront_JNT.msg" "bindPose5.m[5]";
connectAttr "frontLeft_JNT.msg" "bindPose5.m[6]";
connectAttr "frontRight_JNT.msg" "bindPose5.m[7]";
connectAttr "backCenter_JNT.msg" "bindPose5.m[8]";
connectAttr "midCenter_JNT.msg" "bindPose5.m[9]";
connectAttr "frontCenter_JNT.msg" "bindPose5.m[10]";
connectAttr "midRight_JNT.msg" "bindPose5.m[11]";
connectAttr "midLeft_JNT.msg" "bindPose5.m[12]";
connectAttr "backRightShock_JNT.msg" "bindPose5.m[13]";
connectAttr "backLeftShock_JNT.msg" "bindPose5.m[14]";
connectAttr "frontLeftShock_JNT.msg" "bindPose5.m[15]";
connectAttr "frontRightShock_JNT.msg" "bindPose5.m[16]";
connectAttr "bindPose5.w" "bindPose5.p[0]";
connectAttr "bindPose5.w" "bindPose5.p[1]";
connectAttr "bindPose5.w" "bindPose5.p[2]";
connectAttr "bindPose5.w" "bindPose5.p[3]";
connectAttr "bindPose5.w" "bindPose5.p[4]";
connectAttr "bindPose5.w" "bindPose5.p[5]";
connectAttr "bindPose5.w" "bindPose5.p[6]";
connectAttr "bindPose5.w" "bindPose5.p[7]";
connectAttr "bindPose5.w" "bindPose5.p[8]";
connectAttr "bindPose5.w" "bindPose5.p[9]";
connectAttr "bindPose5.w" "bindPose5.p[10]";
connectAttr "bindPose5.w" "bindPose5.p[11]";
connectAttr "bindPose5.w" "bindPose5.p[12]";
connectAttr "bindPose5.w" "bindPose5.p[13]";
connectAttr "bindPose5.w" "bindPose5.p[14]";
connectAttr "bindPose5.w" "bindPose5.p[15]";
connectAttr "bindPose5.w" "bindPose5.p[16]";
connectAttr "backRight_JNT.bps" "bindPose5.wm[0]";
connectAttr "backLeft_JNT.bps" "bindPose5.wm[1]";
connectAttr "rightBack_JNT.bps" "bindPose5.wm[2]";
connectAttr "leftBack_JNT.bps" "bindPose5.wm[3]";
connectAttr "rightFront_JNT.bps" "bindPose5.wm[4]";
connectAttr "leftFront_JNT.bps" "bindPose5.wm[5]";
connectAttr "frontLeft_JNT.bps" "bindPose5.wm[6]";
connectAttr "frontRight_JNT.bps" "bindPose5.wm[7]";
connectAttr "backCenter_JNT.bps" "bindPose5.wm[8]";
connectAttr "midCenter_JNT.bps" "bindPose5.wm[9]";
connectAttr "frontCenter_JNT.bps" "bindPose5.wm[10]";
connectAttr "midRight_JNT.bps" "bindPose5.wm[11]";
connectAttr "midLeft_JNT.bps" "bindPose5.wm[12]";
connectAttr "backRightShock_JNT.bps" "bindPose5.wm[13]";
connectAttr "backLeftShock_JNT.bps" "bindPose5.wm[14]";
connectAttr "frontLeftShock_JNT.bps" "bindPose5.wm[15]";
connectAttr "frontRightShock_JNT.bps" "bindPose5.wm[16]";
connectAttr "FrameControl_CRV.FrameAngle" "unitConversion1.i";
connectAttr "FrameControl_CRV.BackFrameNarrowWide" "multiplyDivide4.i1x";
connectAttr "FrameControl_CRV.FrontFrameNarrowWide" "multiplyDivide4.i1y";
connectAttr ":TurtleDefaultBakeLayer.idx" ":TurtleBakeLayerManager.bli[0]";
connectAttr ":TurtleRenderOptions.msg" ":TurtleDefaultBakeLayer.rset";
connectAttr "multiplyDivide4.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "Frame_1_GEOShape.iog.og[0]" ":initialShadingGroup.dsm" -na;
connectAttr "groupId12.msg" ":initialShadingGroup.gn" -na;
// End of Frame.ma
