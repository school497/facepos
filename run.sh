cd ~/Applications
mkdir FacePOS
cd ~/Applications
mkdir faces
mkdir balances
mkdir business
curl -O https://raw.githubusercontent.com/school497/facepos/main/main.py
curl -O https://raw.githubusercontent.com/school497/facepos/main/civilian.py
curl -O https://raw.githubusercontent.com/school497/facepos/main/business.py
curl -O https://raw.githubusercontent.com/school497/facepos/main/bank.py 
python3 ~/Applications/FacePOS/main.py
