echo "InstaPy Linux Setup"
echo =============================================================================================
echo "Downloading Chrome Driver..."
wget https://chromedriver.storage.googleapis.com/2.29/chromedriver_linux32.zip
echo "Chrome Driver download completed."
echo " "
echo "Unzipping Chrome Driver..."
unzip chromedriver_linux32.zip
mv ./chromedriver ./assets/chromedriver
echo "Unzipping completed."
echo " "
echo "Removing unneeded files..."
rm chromedriver_linux32.zip
echo "Removal completed."
echo " "
sudo pip install setuptools
sudo apt-get install python-dev
sudo pip install ./
echo "Setup is completed."
read -n1 -r -p "Press any key to continue..." key
