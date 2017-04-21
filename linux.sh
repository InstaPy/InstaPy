echo "InstaPy Linux Setup"
echo =============================================================================================
echo "Downloading Chrome Driver..."
arch=$(getconf LONG_BIT)
if [ $arch == "64" ]; then
  wget https://chromedriver.storage.googleapis.com/2.29/chromedriver_linux64.zip -O chromedriver_linux.zip
else
  wget https://chromedriver.storage.googleapis.com/2.29/chromedriver_linux32.zip -O chromedriver_linux.zip
fi
echo "Chrome Driver download completed."
echo " "
echo "Unzipping Chrome Driver..."
unzip chromedriver_linux.zip
mv ./chromedriver ./assets/chromedriver
echo "Unzipping completed."
echo " "
echo "Removing unneeded files..."
rm chromedriver_linux.zip
echo "Removal completed."
echo " "
sudo pip install setuptools
sudo apt-get install python-dev
sudo pip install ./
echo "Setup is completed."
read -n1 -r -p "Press any key to continue..." key
