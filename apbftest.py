from apbf import *

strlist = [
	"1.011",
	#"101.1000000000000",
	## "101",
	## "000101",
	## "-101",
	## "-000000101",
	## "101.0",
	## "101.",
	## ".10111",
	## "-.2034",
	## "101.11",
	## "-101.11",
	## "-000101.11	",
	## "-000101.11e-3",
	#"101.e-3",
	#"101.2e4",
	## "101.2e-4",
	## "0101.3e-5",
	## "101.e+3",
	## "101.2e-4",
	#"101.2e-4",
	#"0101.3e5",
	## "0101.e-5",
	## "-101.e-3",
	## "-101.2e4",
	## "-101.2e-4",
	## "-0101.3e-5",
	## "-0101.e-5" 
	]

for s in strlist:
	m = str(mpap(s)) #.sci() #__repr__()
	print (f"{s} ===>>> {m}\n----------------------")
