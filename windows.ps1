echo "InstaPy Windows Setup"
echo =============================================================================================
echo "Downloading Chrome Driver..."
$webclient = New-Object System.Net.WebClient
$webclient.DownloadFile("https://chromedriver.storage.googleapis.com/2.29/chromedriver_win32.zip","$pwd\chromedriver.zip")
$shell = new-object -com shell.application
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
echo "Setup is completed."
python setup.py install
pause
