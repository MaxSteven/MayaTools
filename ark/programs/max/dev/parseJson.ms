fn explode str token = 
(
	items = #()
	tokenLength = token.count
	i = findString str token
	while (i != undefined) do
	(
		append items (substring str 1 (i-1))
		str = substring str (i + tokenLength) -1
		i = findString str token
	)
	append items str
	--// if we didn't split the string return the whole string
	if (items.count < 1) then
		return #(str)
	return items
)

sqlResponse = openFile "C:/ie/sqlResponse.json" mode:"r"
data = readLine sqlResponse
--// remove the beginning and end array brackets
data = substring data 2 (data.count - 2)
data = substituteString data "\"" "'"
rows = filterString data "}"

for n = 1 to rows.count do
(
	if (n == 1) then
		start = 3
	else
		start = 5
	rows[n] = explode (substring rows[n] start (rows[n].count - start)) "', '"
)

rowStruct = "struct row ("
for attr in rows[1] do
(
	attrParts = explode attr "': '"
	attrName = substring attrParts[1] 1 (attrParts[1].count)
	rowStruct += attrName + ","
)
rowStruct = (substring rowStruct 1 (rowStruct.count - 1)) + ")"
execute rowStruct

--// global variable where the sql result (an array of structs containing the row's keys and corresponding values) is stored
global sqlResult = #()
	
--// gets the attribute's key and value from the string, adds them to the rowData which is ultimately executed and turned in to a struct
for row in rows do
(
	rowData = stringStream ""
	for attr in row do
	(
		attrParts = explode attr "': '"
		attrKey = substring attrParts[1] 1 (attrParts[1].count)
		attrValue = substring attrParts[2] 1 (attrParts[2].count)
		format "%:'%' " attrKey attrValue to:rowData
	)
	rowData = rowData as string
	command = "append sqlResult (row " + (substituteString rowData "'" "\"") + ")"
	execute command
)

format "Sql Result:\n %\n" sqlResult
