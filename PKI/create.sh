openssl req -x509 -config root-ca-cert.cnf -newkey rsa:2048 -out ca.pem -keyout private/ca.key -days 1826
cd certs/
ln -s ../ca.pem `openssl x509 -hash -in ../ca.pem -noout`.0
cd ..
openssl req -config req-subca-cert.cnf -newkey rsa -out tempwebcacert.pem -keyout private/webca.key
openssl ca -config ca-subca-cert.cnf -in tempwebcacert.pem -notext -out certs/webca.pem
cd certs/
ln -s webca.pem `openssl x509 -hash -in webca.pem -noout`.0
cd ..
openssl req -config req-server-cert.cnf -out tempservercert.pem -keyout private/serveur1.key -newkey rsa:2048
openssl ca -in tempservercert.pem -cert certs/webca.pem -keyfile private/webca.key -notext -out certs/serveur1.pem -notext -config ca-server-cert.cnf
cd certs/
ln -s serveur1.pem `openssl x509 -hash -in serveur1.pem -noout`.0
cd ..
openssl verify -CApath certs certs/serveur1.pem
