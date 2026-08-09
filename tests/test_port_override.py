from pilot_api.config.settings import Settings


def test_settings_can_be_instantiated_without_port_override() -> None:
    settings = Settings()

    assert settings.app_name == "PilotApiPython"
