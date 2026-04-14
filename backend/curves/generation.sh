# кривые без особенностей
./ecgen --fp -c1 -p -r 40 > dataset/general/40bit.json # ~20сек
./ecgen --fp -c3 -p -r 32 > dataset/general/32bit.json # ~секунда
./ecgen --fp -c5 -p -r 16 > dataset/general/16bit.json # мгновенно

# кривые с составным порядом для атаки Pohlig-Hellman
./ecgen --fp -c5 -r --smooth=32 128 > dataset/smooth/128bit32smooth.json
./ecgen --fp -c5 -r --smooth=32 64 > dataset/smooth/64bit32smooth.json
./ecgen --fp -c5 -r --smooth=16 64 > dataset/smooth/64bit16smooth.json

# кривые с простым порядком, совпадающим с порядком поля для Smart Attack
./ecgen --fp -c5 -r --anomalous 512 > dataset/anomalous/512bit.json
./ecgen --fp -c5 -r --anomalous 256 > dataset/anomalous/256bit.json
./ecgen --fp -c5 -r --anomalous 128 > dataset/anomalous/128bit.json