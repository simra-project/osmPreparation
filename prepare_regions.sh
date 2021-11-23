#!/bin/bash
#declare -a major_regions=("Augsburg" "Dresden" "Düsseldorf" "Bern" "Pforzheim" "Wuppertal" "Stuttgart" "Hannover" "Leipzig" "Konstanz" "Nuernberg" "Mannheim" "Friedrichshafen" "Lindau" "Karlsruhe" "Freiburg" "Tübingen" "Mainz" "Rastatt" "Kaiserslautern" "Darmstadt" "Saarbrücken" "Weimar" "Brühl" "Ulm" "Sigmaringen" "Aschaffenburg" "Saarlouis" "Landau" "Frankfurt" "Bruchsal" "Breisgau-Hochschwarzwald" "Alzey" "Koblenz" "Odenwald" "Ortenau" "Vulkaneifel" "Wetterau" "Trier" "Tuttlingen" "München" "Ruhrgebiet" "Eichwalde" "Bielefeld" "Berlin")
#declare -a regions=("Dresden" "Düsseldorf" "Pforzheim" "Leipzig" "Mannheim" "Friedrichshafen" "Lindau" "Karlsruhe" "Freiburg" "Tübingen" "Mainz" "Rastatt" "Kaiserslautern" "Darmstadt" "Saarbrücken" "Weimar" "Brühl" "Ulm" "Sigmaringen" "Aschaffenburg" "Saarlouis" "Landau" "Frankfurt" "Bruchsal" "Breisgau-Hochschwarzwald" "Alzey" "Koblenz" "Odenwald" "Ortenau" "Vulkaneifel" "Wetterau" "Trier" "Tuttlingen" "Ruhrgebiet")
# declare -a regions=("Ruhrgebiet11" "Ruhrgebiet12" "Ruhrgebiet13" "Ruhrgebiet14" "Ruhrgebiet21" "Ruhrgebiet22" "Ruhrgebiet23" "Ruhrgebiet24" "Ruhrgebiet31" "Ruhrgebiet32" "Ruhrgebiet33" "Ruhrgebiet34" "Ruhrgebiet41" "Ruhrgebiet42" "Ruhrgebiet43" "Ruhrgebiet44")
declare -a regions=("Ruhrgebiet")
for i in "${regions[@]}"
do
	echo $i
	python main.py $i
done