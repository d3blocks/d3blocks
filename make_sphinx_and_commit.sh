echo "$PWD"
cd docs
echo "$PWD"

echo "Cleaning previous builds first.."
make.bat clean

echo "Building new html.."
make.bat html

cd ..

read -p "Press [q]uit to Quit and [Enter] key to: git add -> commit -> push."
read VAR


if [[ $VAR = "" ]]; then 
    git pull
    git add .
    git commit -m "update sphinx pages"
    git push

    read -p "All done! Press [Enter] to close this window."
    exit
fi


if [ $VAR == "q" ]; then
  echo Quit!
fi

read -p "Press [Enter] to close this window."



