import time
from unittest.mock import patch

import pytest

from hermes.aeriel import serve


@pytest.fixture(params=[None, [0], [3, 4]])
def gpus(request):
    return request.param


@pytest.fixture(params=[None, "log.txt"])
def log_file(request):
    return request.param


@pytest.fixture(params=[None, "--model-control-mode explicit"])
def server_args(request):
    return request.param


def execute(cmd):
    return cmd[-1]


@patch("spython.main.Client.instance")
@patch("spython.main.Client.execute", new=execute)
def test_singularity_instance_run(
    instance_mock, execute_mock, gpus, log_file, server_args
):
    with serve(
        "/path/to/repo",
        "/path/to/image",
        gpus=gpus,
        server_arg=None if server_args is None else server_args.split(),
        log_file=log_file,
    ) as instance:
        time.sleep(1e-3)

    command = instance._response_queue.get_nowait()
    if gpus is not None:
        assert command.startswith("CUDA_VISIBLE_DEVICES=" + ",".join(gpus))
    else:
        assert command.startswith("/opt/tritonserver/bin/tritonserver")

    if server_args is not None:
        assert server_args in command

    if log_file is not None:
        assert command.endswith(f"> {log_file} 2>&1")
    elif server_args is not None:
        assert command.endswith(server_args)
    else:
        assert command.endswith("/path/to/repo")
