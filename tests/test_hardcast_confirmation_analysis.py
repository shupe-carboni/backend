from os import getenv
from fastapi.testclient import TestClient
from base64 import b64encode
from app.main import app
from dotenv import load_dotenv

load_dotenv()

test_client = TestClient(app)
PATH = "/hardcast/confirmations"
test_file = "./tests/test_hardcast_conf.PDF"
FLOW_NAME = getenv("FLOW_NAME")


def test_confirmation_endpoint_works():
    with open(test_file, "rb") as fh:
        file_data: str = b64encode(fh.read()).decode()

    pl = {"file": file_data, "content_type": "application/pdf"}
    headers = {"x-ms-workflow-name": FLOW_NAME}
    resp = test_client.post(PATH, json=pl, headers=headers)
    assert resp.status_code == 200, resp.text
    with open("email_test.html", "w") as email:
        email.write(resp.text)
    resp = test_client.post(PATH, json=pl)
    assert resp.status_code == 401, resp.text
    headers = {"x-ms-workflow-name": "xyz123"}
    resp = test_client.post(PATH, json=pl, headers=headers)
    assert resp.status_code == 401, resp.text
