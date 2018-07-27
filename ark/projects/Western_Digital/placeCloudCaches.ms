clouds = for obj in $cloud* collect obj
for cloud in clouds do
(
	newCloud = PHXSimulator()
	newCloud.rendinput = "Q:/Western_Digital/Project_Assets/clouds/Cache/cloud_001/cloud_001"
	newCloud.inpoffset = 1
	newCloud.play_speed = 0
	newCloud.transform = cloud.transform
	newCloud.scale = cloud.scale * 100
)

for cloudBox in objects where classof cloudBox == PHXSimulator do
(
	cloudBox.subred = 0
	cloudBox.rendstep = 500
	cloudBox.sampler = 1
	cloudBox.jitter = true
	cloudBox.rendmode = 0
	cloudBox.prv_temperature = off
	cloudBox.prv_smoke = off
	cloudBox.prv_fuel = off
	cloudBox.prv_uvw = off
	cloudBox.prv_foam = off
	cloudBox.prv_splashes = off
	cloudBox.prv_prt = off
	cloudBox.smoketransp = .15
)



for cloudBox in objects where classof cloudBox == PHXSimulator do
(
	cloudBox.rendmode = 4
)


for cloudBox in objects where classof cloudBox == PHXSimulator do
(
	cloudBox.subred = 10
)


for cloudBox in objects where classof cloudBox == PHXSimulator do
(
	cloudBox.rendinput = substituteString cloudBox.rendinput "lvl2" "lvl3"
)



for cloudBox in objects where classof cloudBox == PHXSimulator do
(
	cloudBox.simple_color = [0,0,0]
)



for cloudBox in objects where classof cloudBox == PHXSimulator do
(
	cloudBox.prv_smoke = off
	cloudBox.show_only_sel = on
)


for cloudBox in objects where classof cloudBox == PHXSimulator do
(
	if (substring cloudBox.name 1 5 == "cloud") then
	(
		cloudNumber = substring cloudBox.name 7 1
		if (cloudNumber == "1")
			cloudBox.smoketransp = .075
)



for cloudBox in objects where classof cloudBox == PHXSimulator do
(
	if (substring cloudBox.name 1 5 == "cloud") then
	(
		cloudNumber = substring cloudBox.name 7 1
		print cloudNumber
		if (cloudNumber == "1") then
		(
			--cloudBox.smoketransp = .075
			print cloudNumber
		)
	)
)

-- names = #("


cloudRoot = "Q:/final_girls/Project_Assets/cloud_dev/Cache/"
clouds = getCurrentSelection()
for cloud in clouds do
(
	cloudBox = PHXSimulator()
	cloudBox.transform = cloud.transform
	if (substring cloud.name 1 5 == "cloud") then
	(
		cloudNumber = substring cloud.name 7 1
		cloudBox.rendinput = cloudRoot + "Cloud" + cloudNumber + "_lvl3.####.vdb"
		-- cloudBox.scale *= 25
		if (cloudNumber == "1") then
			cloudBox.smoketransp = .075
		else
			cloudBox.smoketransp = .15
	)
	else if (substring cloud.name 1 5 == "fluff") then
	(
		cloudNumber = substring cloud.name 12 1
		cloudBox.rendinput = cloudRoot + "fluffCloud" + cloudNumber + "_lvl1.####.vdb"
		cloudBox.smoketransp = .05
	)

	cloudBox.inpoffset = 1
	cloudBox.play_speed = 0
	cloudBox.subred = 10
	cloudBox.rendstep = 500
	cloudBox.sampler = 1
	cloudBox.jitter = true
	cloudBox.rendmode = 0
	cloudBox.prv_temperature = off
	cloudBox.prv_smoke = off
	cloudBox.prv_fuel = off
	cloudBox.prv_uvw = off
	cloudBox.prv_foam = off
	cloudBox.prv_splashes = off
	cloudBox.prv_prt = off
	cloudBox.prv_dwnsmp = 2
	cloudBox.name = "phx_" + cloud.name
	cloudBox.parent = cloud
)



clouds = getCurrentSelection()
dataClouds = #()
for cloud in clouds where (substring cloud.name 1 5 == "cloud") do
(
	cloudNumber = (substring cloud.name 7 1) as integer
	if (cloudNumber > 1) then
	(
		print cloudNumber
		append dataClouds cloud
	)
)
select dataClouds


0-108
90-253
240-409

cloud_3 patch:
238-303

Russia patch:
97-180

Batman patch:
280-330


set cut_paste_input [stack 0]
version 9.0 v1b126
Read {
 inputs 0
 file Q:/Western_Digital/Workspaces/assembly/Renders/v010/assembly_russia_cam_baked.%04d.exr
 format "1920 1080 0 0 1920 1080 1 HD_1080"
 first 97
 last 180
 origfirst 97
 origlast 180
 origset true
 on_error "nearest frame"
 name Read2
 selected true
 xpos -569
 ypos -110
}
Read {
 inputs 0
 file Q:/Western_Digital/Workspaces/assembly/Renders/v096/assembly_clouds_3_cam_baked.%04d.exr
 format "480 270 0 0 480 270 1 "
 first 238
 last 303
 origfirst 238
 origlast 303
 origset true
 on_error "nearest frame"
 name Read1
 selected true
 xpos -549
 ypos -325
}
