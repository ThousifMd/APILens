from apilens.logger import _APILogger

def test_logger_creation(tmp_path):
    db_path = tmp_path / "test.db"
    logger = _APILogger(str(db_path))
    assert logger is not None
    logger.log_call(provider="openai", model="gpt-4o", prompt_tokens=1, completion_tokens=1, cost=0.01, status="success", error_message=None, user_id="u", tenant_id="t")
