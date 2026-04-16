#!/bin/bash

mkdir -p production/general production/smooth production/anomalous

echo "=== Запуск генерации кривых ==="

echo "Кривые без особенностей..."
./ecgen --fp -c3 -p -r 48 > production/general/48bit.json
./ecgen --fp -c3 -p -r 40 > production/general/40bit.json
./ecgen --fp -c3 -p -r 32 > production/general/32bit.json

echo "Кривые с составным порядом для атаки Pohlig-Hellman..."
./ecgen --fp -c3 -r --smooth=40 128 > production/smooth/128bit40smooth.json
./ecgen --fp -c3 -r --smooth=32 128 > production/smooth/128bit32smooth.json

echo "Кривые с простым порядком, совпадающим с порядком поля для Smart Attack..."
./ecgen --fp -c3 -r --anomalous 512 > production/anomalous/512bit.json
./ecgen --fp -c3 -r --anomalous 256 > production/anomalous/256bit.json
./ecgen --fp -c3 -r --anomalous 128 > production/anomalous/128bit.json

echo "=== Завершено! ==="