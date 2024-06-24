python3 -m venv vpn_env
source vpn_env/bin/activate
pip install pydivert pyOpenSSL pycryptodome
python3 vpn_server.py
deactivate
exit