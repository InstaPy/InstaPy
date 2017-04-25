echo "InstaPy MacOS Setup"
echo =============================================================================================
echo "Downloading Chrome Driver..."
curl -O https://chromedriver.storage.googleapis.com/2.29/chromedriver_mac64.zip
echo "Chrome Driver download completed."
echo " "
echo "Unzipping Chrome Driver..."
unzip chromedriver_mac64.zip
mv ./chromedriver ./assets/chromedriver
echo "Unzipping completed."
echo " "
echo "Removing unneeded files..."
rm chromedriver_mac64.zip
echo "Removal completed."
echo " "
sudo python setup.py install
echo "Setup is completed."
read -n1 -r -p "Press any key to continue..." key
