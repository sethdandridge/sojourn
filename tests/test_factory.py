from app import create_app


def test_config():
    assert create_app() # no testing 
    test_config = {
        "SECRET_KEY": "testkey",
        "SECURITY_PASSWORD_SALT": "passwordsalt",
        "TESTING": True,
    }
    assert create_app(test_config=test_config).testing


def test_hello(client):
    response = client.get("/nadia")
    assert response.data == b"Hello nadia"
