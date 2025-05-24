from app import app
import ssl

if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    app.run(host='127.0.0.1', port=5000, debug=False, ssl_context=context) 