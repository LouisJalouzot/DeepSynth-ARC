cd training
for i in *.json
do
    echo -n "$i "
    python3 ../color_proportion.py $i 0
done