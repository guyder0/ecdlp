# кривые без особенностей
./ecgen --fp -c5 -p -r 32 > dataset/general/32bit.json
./ecgen --fp -c5 -p -r 16 > dataset/general/16bit.json

# кривые с составным порядом для атаки Pohlig-Hellman
./ecgen --fp -c5 -r --smooth=32 64 > dataset/smooth/64bit32smooth.json
./ecgen --fp -c5 -r --smooth=16 64 > dataset/smooth/64bit16smooth.json
./ecgen --fp -c5 -r --smooth=16 32 > dataset/smooth/32bit16smooth.json
./ecgen --fp -c5 -r --smooth=8  16 > dataset/smooth/16bit8smooth.json

# кривые с простым порядком, совпадающим с порядком поля для Smart Attack
./ecgen --fp -c5 -r --anomalous 64 > dataset/anomalous/64bit.json
./ecgen --fp -c5 -r --anomalous 16 > dataset/anomalous/16bit.json