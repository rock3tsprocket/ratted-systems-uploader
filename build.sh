gcc -O2 $(curl-config --cflags) $(curl-config --libs) -o uploader ./uploader.c || echo "A build error occured!" && exit 1
chmod +x uploader;
echo "Build done!"