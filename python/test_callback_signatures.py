"""Callback authentication must reject malformed input without side effects."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api import create_app
from core import Engine, Problem


MALFORMED_SIGNATURES = [None, True, 123, [], {}, '', 'a' * 63, '0' * 64, 'é' * 64, '🔑' * 64]
BODY = {'id': 'payment-1', 'invoice': 'INV-100', 'amount': 10000}


@pytest.mark.parametrize('signature', MALFORMED_SIGNATURES, ids=['null', 'boolean', 'number', 'array', 'object', 'empty', 'short', 'wrong-digest', 'unicode', 'emoji'])
def test_invalid_signature_leaves_workflow_unchanged(signature):
    engine = Engine()
    try:
        before = engine.state()
        with pytest.raises(Problem) as error:
            engine.command('callback', {**BODY, 'signature': signature}, 'operator')
        assert error.value.status == 401
        assert engine.state() == before

        # A rejected attempt must not consume the event identifier.
        result = engine.command('callback', {**BODY, 'signature': engine.signature(BODY)}, 'operator')
        assert result['status'] == 'matched'
        assert len(engine.state()['events']) == 1
        assert len(engine.state()['audit']) == 1
    finally:
        engine.db.close()


@pytest.mark.parametrize('signature', MALFORMED_SIGNATURES, ids=['null', 'boolean', 'number', 'array', 'object', 'empty', 'short', 'wrong-digest', 'unicode', 'emoji'])
def test_api_returns_401_for_invalid_signature(signature):
    project = Path(__file__).parent / 'financial-reconciliation-and-exception-workbench-python' / 'project.json'
    app = create_app(project)
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.post(
                '/api/action',
                json={'action': 'callback', 'payload': {**BODY, 'signature': signature}},
                headers={'Authorization': 'Bearer local-operator'},
            )
            assert response.status_code == 401
            assert response.json() == {'detail': 'Invalid callback signature'}
            assert app.state.engine.state()['events'] == []
            assert app.state.engine.state()['audit'] == []
    finally:
        app.state.engine.db.close()
