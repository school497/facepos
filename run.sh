cd ~/Library/Application\ Support
mkdir FacePOS
cd ~/Library/Application\ Support/FacePOS
mkdir faces
mkdir balances
mkdir business
curl -O https://raw.githubusercontent.com/school497/facepos/main/main.py
curl -O https://raw.githubusercontent.com/school497/facepos/main/civilian.py
curl -O https://raw.githubusercontent.com/school497/facepos/main/business.py
curl -O https://raw.githubusercontent.com/school497/facepos/main/bank.py 
chmod 777 ~/Library/Application\ Support/FacePOS
chmod 777 *
python3 ~/Library/Application\ Support/FacePOS/main.py
