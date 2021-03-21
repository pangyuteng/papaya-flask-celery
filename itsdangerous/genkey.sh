
if [ ! -f .env ]; then
    echo SECRET_KEY=$(openssl rand -hex 12) >> .env
else
    echo ".env found, no need to generate."
fi

if [ ! -f keystore/cert.pem ] || [ ! -f keystore/key.pem ]; then
    openssl req -x509 -newkey rsa:4096 -nodes -out keystore/cert.pem -keyout keystore/key.pem -days 365
else
    echo "keystore/cert.pem and keystore/key.pem found, no need to generate."
fi

