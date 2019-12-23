import os
from collections import namedtuple

import nameko
import pytest
import yaml
from nameko.cli.main import setup_yaml_parser
from nameko.testing.services import replace_dependencies


@pytest.fixture(scope="session")
def project_root():
    return os.path.dirname(os.path.dirname(__file__))


@pytest.fixture(scope="session")
def test_config(project_root):
    config_file = os.path.join(project_root, "config.yaml")
    setup_yaml_parser()
    with open(config_file) as stream:
        config = yaml.unsafe_load(stream.read())
    with nameko.config.patch(config, clear=True):
        yield


@pytest.fixture
def config(test_config, rabbit_config, web_config):
    pass


@pytest.fixture
def create_service(container_factory):
    def create(service_cls, *dependencies, **dependency_map):

        dependency_names = list(dependencies) + list(dependency_map.keys())

        ServiceMeta = namedtuple("ServiceMeta", ["container"] + dependency_names)

        container = container_factory(service_cls)

        mocked_dependencies = replace_dependencies(
            container, *dependencies, **dependency_map
        )

        if len(dependency_names) == 1:
            mocked_dependencies = (mocked_dependencies,)

        container.start()

        return ServiceMeta(container, *mocked_dependencies, **dependency_map)

    return create

