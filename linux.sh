echo "Unix InstaPy Setup"
echo =============================================================================================
echo "Downloading Chrome Driver..."
arch=$(getconf LONG_BIT)
kernel=$(uname)
if [ $kernel == "Darwin" ]; then
  curl -o chromedriver.zip -O https://chromedriver.storage.googleapis.com/2.29/chromedriver_mac64.zip
else
  if [ $arch == "64" ]; then
    wget https://chromedriver.storage.googleapis.com/2.29/chromedriver_linux64.zip -O chromedriver.zip
  else
    wget https://chromedriver.storage.googleapis.com/2.29/chromedriver_linux32.zip -O chromedriver.zip
  fi
fi
echo "Chrome Driver download completed."
echo " "
echo "Unzipping Chrome Driver..."
unzip chromedriver.zip
mv ./chromedriver ./assets/chromedriver
echo "Unzipping completed."
echo " "
echo "Removing unneeded files..."
rm chromedriver.zip
echo "Removal completed."
echo " "
if [ $kernel == "Darwin" ]; then
  sudo python setup.py install
else
  sudo pip install setuptools
  sudo apt-get install python-dev
  sudo pip install ./
fi
echo "Setup is completed."
read -n1 -r -p "Press any key to continue..." key
