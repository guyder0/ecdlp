# 32bit кривые без особенностей
./ecgen --fp -c5 -r 32 > dataset/32bit.json

# 64bit кривые с составным порядом (простые множители до 32 бит) для атаки Pohlig-Hellman
./ecgen --fp -c5 -r --smooth=32 64 > dataset/64bit32smooth.json
