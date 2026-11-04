"""Non-finite deadlines must not bypass submission validation."""
import json
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api import create_app
from core import Engine, Problem


INVALID_DEADLINES = [float('nan'), float('inf'), float('-inf')]
SUBMISSION = {'id': 'submission-1', 'student': 'Student1', 'answers': ['transaction', 'idempotency', 'audit']}


@pytest.mark.parametrize('deadline', INVALID_DEADLINES, ids=['nan', 'positive-infinity', 'negative-infinity'])
def test_nonfinite_deadline_does_not_create_grade_or_consume_id(deadline):
    engine = Engine()
    try:
        before = engine.state()
        with pytest.raises(Problem) as error:
            engine.command('submit', {**SUBMISSION, 'deadline': deadline})
        assert error.value.status == 422
        assert engine.state() == before
        result = engine.command('submit', {**SUBMISSION, 'deadline': time.time() + 60})
        assert result['score'] == 3
        assert len(engine.state()['grades']) == 1
        assert len(engine.state()['audit']) == 1
    finally:
        engine.db.close()


@pytest.mark.parametrize('deadline', INVALID_DEADLINES, ids=['nan', 'positive-infinity', 'negative-infinity'])
def test_http_rejects_nonfinite_deadlines(deadline):
    project = Path(__file__).parent / 'education-assessment-and-progress-api-python' / 'project.json'
    app = create_app(project)
    try:
        with TestClient(app) as client:
            # Exercise the server parser directly: Python's JSON decoder accepts
            # these extensions even though standard JSON cannot represent them.
            response = client.post(
                '/api/action',
                content=json.dumps({'action': 'submit', 'payload': {**SUBMISSION, 'deadline': deadline}}),
                headers={'Authorization': 'Bearer local-learner', 'Content-Type': 'application/json'},
            )
            assert response.status_code == 422
            assert response.json() == {'detail': 'Submission deadline has passed or is invalid'}
            assert app.state.engine.state()['grades'] == []
            assert app.state.engine.state()['audit'] == []
    finally:
        app.state.engine.db.close()


@pytest.mark.parametrize('numeric_type', [int, float], ids=['integer', 'float'])
def test_finite_future_deadlines_remain_valid(numeric_type):
    engine = Engine()
    try:
        result = engine.command('submit', {**SUBMISSION, 'deadline': numeric_type(time.time() + 60)})
        assert result['score'] == 3
    finally:
        engine.db.close()
