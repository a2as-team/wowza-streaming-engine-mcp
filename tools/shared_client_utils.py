from typing import Dict, Type, TypeVar, Any, Optional
import logging

T = TypeVar("T")

def send_client_log(level: str, message: str):
    """Shared logger callback for all API clients."""
    logging.log(getattr(logging, level.upper(), logging.INFO), f"(wowza-api-client) {message}")

def get_engine_config(config: Optional[Dict[str, Any]]) -> Dict:
    """
    Retrieves Wowza Streaming Engine connection details from the configuration.
    """
    config = config or {}
    return {
        "base_url": config.get("WOWZA_ENGINE_BASE_URL"),
        "server_name": config.get("WOWZA_ENGINE_SERVER_NAME"),
        "vhost_name": config.get("WOWZA_ENGINE_VHOST_NAME"),
        "instance_name": config.get("WOWZA_ENGINE_INSTANCE_NAME"),
        "username": config.get("WOWZA_ENGINE_USERNAME"),
        "password": config.get("WOWZA_ENGINE_PASSWORD"),
    }

def make_client(client_class: Type[T], config: Optional[Dict[str, Any]]) -> T:
    """
    Generic factory to create an API client instance.
    """
    engine_config = get_engine_config(config)
    return client_class(
        base_url=engine_config["base_url"],
        username=engine_config["username"],
        password=engine_config["password"],
        logger=send_client_log,
    )
