for i in 1 6 11 12; do
    echo "Scanning i2c-$i..."
    sudo i2cdetect -y $i
done
