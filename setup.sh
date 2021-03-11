sudo apt-get update
sudo apt-get install gdal-bin libgdal-dev libatlas-base-dev cmake make -y

sudo apt-get install sqlite3
mkdir ../tmp
cd ../tmp
wget https://download.osgeo.org/proj/proj-6.3.2.tar.gz
tar xvf proj-6.3.2.tar.gz
cd proj-6.3.2
./configure
make
sudo make install
sudo ldconfig

mkdir ../libspatialindex
cd ../libspatialindex
wget https://github.com/libspatialindex/libspatialindex/releases/download/1.9.3/spatialindex-src-1.9.3.tar.gz
tar -xvf spatialindex-src-1.9.3.tar.gz
cd spatialindex-src-1.9.3/
cmake -DCMAKE_INSTALL_PREFIX=/usr/local .
make
sudo make install
sudo ldconfig

pip3 install venv
python3 -m venv env
source env/bin/activate

pip install -r requirements.txt

touch .env