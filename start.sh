python3 -m venv vpn_env
source vpn_env/bin/activate
pip install pydivert pyOpenSSL pycryptodome scapy
python3 vpn_server.py
deactivate
exit