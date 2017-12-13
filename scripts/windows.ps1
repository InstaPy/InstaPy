echo "InstaPy Windows Setup"
echo =============================================================================================
echo "Installing Selenium"
pip install selenium
python -m pip install pyvirtualdisplay
py get-pip.py
echo " "
echo "Installing GUI Tool"
$webclient = New-Object System.Net.WebClient
$webclient.DownloadFile("https://github.com/Nemixalone/GUI-tool-for-InstaPy-script/releases/download/0.4/InstaPy-GUI.exe","$pwd\InstaPy-GUI.exe")
mv "$pwd\InstaPy-GUI.exe" "$pwd\..\InstaPy-GUI.exe"
echo " "
cd ..\
echo "Downloading Chrome Driver..."
$webclient = New-Object System.Net.WebClient
$webclient.DownloadFile("https://chromedriver.storage.googleapis.com/2.34/chromedriver_win32.zip","$pwd\chromedriver.zip")
echo "Chrome Driver download completed."
echo " "
echo "Unzipping Chrome Driver..."
$shell = new-object -com shell.application
$zip = $shell.NameSpace("$pwd\chromedriver.zip")
foreach($item in $zip.items())
{
$shell.Namespace("$pwd\assets\").copyhere($item)
}
mv "$pwd\assets\chromedriver.exe" "$pwd\assets\chromedriver"
echo "Unzipping completed."
echo " "
echo "Removing unneeded files..."
rm chromedriver.zip
echo "Removal completed."
echo " "
python setup.py install
echo "Setup is completed."
pause
