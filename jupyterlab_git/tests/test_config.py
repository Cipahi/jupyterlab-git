import json
from unittest.mock import Mock, call, patch

import pytest
import tornado

from jupyterlab_git.git import Git
from jupyterlab_git.handlers import GitConfigHandler

from .testutils import FakeContentManager, NS, maybe_future


@patch("jupyterlab_git.git.execute")
async def test_git_get_config_success(mock_execute, jp_fetch):
    # Given
    mock_execute.return_value = maybe_future(
        (0, "user.name=John Snow\nuser.email=john.snow@iscoming.com", "")
    )

    # When
    body = {"path": "test_path"}
    response = await jp_fetch(NS, "config", body=json.dumps(body), method="POST")

    # Then
    mock_execute.assert_called_once_with(["git", "config", "--list"], cwd="test_path")

    assert response.code == 201
    payload = json.loads(response.body)
    assert payload == {
        "code": 0,
        "options": {
            "user.name": "John Snow",
            "user.email": "john.snow@iscoming.com",
        },
    }


@patch("jupyterlab_git.git.execute")
async def test_git_get_config_multiline(mock_execute, jp_fetch):
    # Given
    output = (
        "user.name=John Snow\n"
        "user.email=john.snow@iscoming.com\n"
        'alias.summary=!f() {     printf "Summary of this branch...\n'
        '";     printf "%s\n'
        '" $(git rev-parse --abbrev-ref HEAD);     printf "\n'
        "Most-active files, with churn count\n"
        '"; git churn | head -7;   }; f\n'
        'alias.topic-base-branch-name=!f(){     printf "master\n'
        '";   };f\n'
        'alias.topic-start=!f(){     topic_branch="$1";     git topic-create "$topic_branch";     git topic-push;   };f'
    )
    mock_execute.return_value = maybe_future((0, output, ""))

    # When
    body = {"path": "test_path"}
    response = await jp_fetch(NS, "config", body=json.dumps(body), method="POST")

    # Then
    mock_execute.assert_called_once_with(["git", "config", "--list"], cwd="test_path")

    assert response.code == 201
    payload = json.loads(response.body)
    assert payload == {
        "code": 0,
        "options": {
            "user.name": "John Snow",
            "user.email": "john.snow@iscoming.com",
        },
    }


@patch("jupyterlab_git.git.execute")
@patch(
    "jupyterlab_git.handlers.ALLOWED_OPTIONS",
    ["alias.summary", "alias.topic-base-branch-name"],
)
async def test_git_get_config_accepted_multiline(mock_execute, jp_fetch):
    # Given
    output = (
        "user.name=John Snow\n"
        "user.email=john.snow@iscoming.com\n"
        'alias.summary=!f() {     printf "Summary of this branch...\n'
        '";     printf "%s\n'
        '" $(git rev-parse --abbrev-ref HEAD);     printf "\n'
        "Most-active files, with churn count\n"
        '"; git churn | head -7;   }; f\n'
        'alias.topic-base-branch-name=!f(){     printf "master\n'
        '";   };f\n'
        'alias.topic-start=!f(){     topic_branch="$1";     git topic-create "$topic_branch";     git topic-push;   };f'
    )
    mock_execute.return_value = maybe_future((0, output, ""))

    # When
    body = {"path": "test_path"}
    response = await jp_fetch(NS, "config", body=json.dumps(body), method="POST")

    # Then
    mock_execute.assert_called_once_with(["git", "config", "--list"], cwd="test_path")

    assert response.code == 201
    payload = json.loads(response.body)
    assert payload == {
        "code": 0,
        "options": {
            "alias.summary": '!f() {     printf "Summary of this branch...\n'
            '";     printf "%s\n'
            '" $(git rev-parse --abbrev-ref HEAD);     printf "\n'
            "Most-active files, with churn count\n"
            '"; git churn | head -7;   }; f',
            "alias.topic-base-branch-name": '!f(){     printf "master\n";   };f',
        },
    }


@patch("jupyterlab_git.git.execute")
async def test_git_set_config_success(mock_execute, jp_fetch):
    # Given
    mock_execute.return_value = maybe_future((0, "", ""))

    # When
    body = {
        "path": "test_path",
        "options": {
            "user.name": "John Snow",
            "user.email": "john.snow@iscoming.com",
        },
    }
    response = await jp_fetch(NS, "config", body=json.dumps(body), method="POST")

    # Then
    assert mock_execute.call_count == 2
    mock_execute.assert_has_calls(
        [
            call(
                ["git", "config", "--add", "user.email", "john.snow@iscoming.com"],
                cwd="test_path",
            ),
            call(
                ["git", "config", "--add", "user.name", "John Snow"],
                cwd="test_path",
            ),
        ],
        any_order=True,
    )

    assert response.code == 201
    payload = json.loads(response.body)
    assert payload == {"code": 0, "message": ""}
