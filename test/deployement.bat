git clone https://github.com/Sans-Interdit/Beauvoir_DWWM_Project.git

cd Beauvoir_DWWM_Project\back

(
echo API_KEY=""
echo CRYPT_KEY=""
) > .env

cd ..\datas

python database.py
python handle_qdrant.py