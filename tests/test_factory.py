from app import create_app


def test_config(): 
    test_config = {
        "SECRET_KEY": "testkey",
        "SECURITY_PASSWORD_SALT": "passwordsalt",
    }
    assert create_app({"TESTING": True}, test_config=test_config).testing


def test_hello(client):
    response = client.get("/nadia")
    assert response.data == b"Hello nadia"
