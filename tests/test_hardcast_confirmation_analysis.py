from fastapi.testclient import TestClient
from base64 import b64encode
from app.main import app

test_client = TestClient(app)
PATH = "/hardcast/confirmations"
test_file = "./tests/test_hardcast_conf.PDF"


def test_confirmation_endpoint_works():
    with open(test_file, "rb") as fh:
        file_data: str = b64encode(fh.read()).decode()
    pl = {"file": file_data, "content_type": "application/pdf"}
    resp = test_client.post(PATH, json=pl)
    assert resp.status_code == 200, resp.text
    with open("email_test.html", "w") as email:
        email.write(resp.text)
