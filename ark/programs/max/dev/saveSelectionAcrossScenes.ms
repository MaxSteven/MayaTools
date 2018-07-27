selectString = stringStream ""
format "names = #(" to:selectString
for s in getCurrentSelection() do
	format ("\"" + s.name + "\",") to:selectString
selectOutput = selectString as string
format (substring selectOutput 1 (selectOutput.count - 1) + ")\nselect names\n")
--select (for s in names where isvalidnode (getnodebyname s) collect getnodebyname s)