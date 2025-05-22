import pytest
import os

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for testing."""
    os.environ['OPENAI_API_KEY'] = 'fake-openai-key'
    os.environ['ANTHROPIC_API_KEY'] = 'fake-anthropic-key'
    yield
    # Cleanup
    os.environ.pop('OPENAI_API_KEY', None)
    os.environ.pop('ANTHROPIC_API_KEY', None) 