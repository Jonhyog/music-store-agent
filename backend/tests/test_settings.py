from music_store.settings import Settings


def test_langsmith_is_off_by_default():
    assert Settings(_env_file=None).langsmith_env() == {}


def test_langsmith_needs_both_the_flag_and_a_key():
    assert Settings(_env_file=None, langsmith_tracing=True).langsmith_env() == {}
    assert Settings(_env_file=None, langsmith_api_key="k").langsmith_env() == {}


def test_langsmith_enabled_exports_tracing_environment():
    settings = Settings(_env_file=None, langsmith_tracing=True, langsmith_api_key="k")
    assert settings.langsmith_env() == {
        "LANGSMITH_TRACING": "true",
        "LANGSMITH_API_KEY": "k",
        "LANGSMITH_PROJECT": "music-store-assistant",
    }
