from app import create_app


def test_config():
    assert create_app() # no testing 
    assert create_app(testing=True).testing

def test_hello(client):
    response = client.get("/nadia")
    assert response.data == b"Hello nadia"
