#!/bin/bash
declare -a major_regions=("Hannover" "Wuppertal" "Ruhrgebiet" "Bern" "München" "Eichwalde" "Stuttgart" "Augsburg" "Bielefeld" "Konstanz")
for i in "${major_regions[@]}"
do
	python main.py $i
done