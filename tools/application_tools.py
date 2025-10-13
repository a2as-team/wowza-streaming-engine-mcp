# application_tools.py

import json
import logging
from typing import Dict, Optional, List, Any, Literal, Union

from api_client.application_api import WowzaApplicationApiClient
from models import (
	ApplicationCreate,
	ApplicationUpdate,
	ApplicationAdvancedUpdate,
	ApplicationSecurityConfig,
	ApplicationDvrConfig,
	ApplicationDrmConfig,
	ApplicationTranscoderConfig,
	StreamFileCreate,
	SmilFileCreate,
	BuyDRMStreamMapsData,
	VerimatrixStreamMapsData,
	TranscoderEncodeCreate,
)
from models.schema_utils import create_enhanced_tool_description, get_literal_constraints
from .shared_client_utils import get_engine_config, make_client


def register_tools(mcp, CONFIG=None):
    """
    Register Wowza Streaming Engine Application-related MCP tools.
    """
    client = make_client(WowzaApplicationApiClient, CONFIG)
    config = get_engine_config(CONFIG)

    @mcp.tool(
        tags={"application","read"},
        description="Get a list of all applications for the default vhost."
    )
    async def get_wowza_applications() -> str:
        """Retrieves a list of all applications."""

        result = await client.get_applications_config(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"]
        )
        return json.dumps(result, indent=2)


    @mcp.tool(
        tags={"application", "read"},
        description="Get historical statistics for a specific application."
    )
    async def get_wowza_application_historical_stats(app_name: str) -> str:

        result = await client.get_application_historic_stats(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application","read"},
        description="Get the configuration of a specific application."
    )
    async def get_wowza_application_config(app_name: str) -> str:
        """
        Retrieves the full configuration for a specific application.

        Args: 
            app_name: The name of the application (e.g., 'live').
        """

        result = await client.get_application_config(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application","write"},
        description=create_enhanced_tool_description(
            (
                "Create a NEW application from scratch on the Wowza Streaming Engine.\n\n"
                "The app_name must match the 'name' inside app_data.\n\n"
                "WARNING: DO NOT use this to copy/clone/duplicate an existing application!\n"
                "This tool only creates basic config and will MISS critical settings like:\n"
                "- streamType (causes transcoding to fail)\n"
                "- liveStreamPacketizer configuration\n"
                "- Advanced transcoder, WebRTC, security settings\n\n"
                "To copy an application, use control_wowza_application with action='copy'."
            ),
            ApplicationCreate,
            "app_data"
        )
    )
    async def create_wowza_application(
        app_name: str,
        app_data: Optional[ApplicationCreate] = None
    ) -> str:
        """Create a new application from scratch.

        WARNING: This creates a NEW application with basic settings only.
        DO NOT use this to copy/clone an existing application - critical settings
        like streamType will be missing, causing features like transcoding to fail.

        To copy an existing application with ALL its configuration, use
        control_wowza_application with action='copy' instead.

        The `app_name` must match the `name` inside `app_data`.
        If no app_data is provided, sensible defaults will be used.
        """

        if app_data is None:
            app_data = ApplicationCreate(
                name=app_name,
                appType="Live",  # default
                description=f"Auto-created application {app_name}"
            )

        payload = app_data.model_dump(exclude_none=True)
        result = await client.post_application_config(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            data=payload,
        )
        return json.dumps(result, indent=2)


    @mcp.tool(
        tags={"application","write"},
        description=create_enhanced_tool_description(
            "Update an existing application configuration (PUT).\n\nAll fields in app_data are optional for updates.",
            ApplicationUpdate,
            "app_data"
        )
    )
    async def update_wowza_application(app_name: str, app_data: ApplicationUpdate) -> str:

        payload = app_data.model_dump(exclude_none=True)
        result = await client.put_application_config(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            data=payload,
        )
        return json.dumps(result, indent=2)

    
    @mcp.tool(
        tags={"application", "read"},
        description="Get a list of .stream files for an application."
    )
    async def get_wowza_stream_files(app_name: str) -> str:
        """
        Retrieves the list of all .stream files associated with an application.

        Args:
            app_name: The name of the application.
        """

        result = await client.get_stream_files(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description="Add a .stream file to an application."
    )
    async def add_wowza_stream_file(app_name: str, stream_file_data: StreamFileCreate) -> str:
        """
        Adds a new .stream file to an application to pull a remote stream.

        Args:
            app_name: The name of the application.
            stream_file_data: A dictionary with the stream file configuration. 'name' and 'uri' are required keys.
        """

        payload = stream_file_data.model_dump(exclude_none=True)
        result = await client.add_stream_file(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            data=payload
        )
        return json.dumps(result, indent=2)
        
    @mcp.tool(
        tags={"application", "write"},
        description="DESTRUCTIVE: Remove a .stream file. ALWAYS confirm with user before executing."
    )
    async def remove_wowza_stream_file(app_name: str, streamfile_name: str) -> str:
        """
        Deletes a .stream file from an application.

        WARNING: This is a DESTRUCTIVE operation that CANNOT be undone.
        ALWAYS confirm with the user before executing this operation.

        Args:
            app_name: The name of the application.
            streamfile_name: The name of the stream file to remove (without the .stream extension).
        """

        result = await client.remove_stream_file(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            streamfile_name=streamfile_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get current real-time statistics for a specific application."
    )
    async def get_wowza_application_current_stats(app_name: str) -> str:
        """
       Retrieves the current monitoring statistics for an application.

        Args:
            app_name: The name of the application.
        """

        result = await client.get_application_current_stats(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description=create_enhanced_tool_description(
            (
                "Update specific application config section. Choose config_type: 'security', 'dvr', 'dvr_adv', 'drm', "
                "'transcoder', 'webrtc', 'modules', 'streamconfiguration'.\n"
                "Provide data dict matching the config_type schema. SHORTCUT for transcoder: use enable=True/False instead of data."
            ),
            [ApplicationSecurityConfig, ApplicationDvrConfig, ApplicationDrmConfig, ApplicationTranscoderConfig],
            "data"
        )
    )
    async def update_wowza_application_config(
        app_name: str,
        config_type: Literal["security", "dvr", "dvr_adv", "drm", "transcoder", "webrtc", "modules", "streamconfiguration"],
        data: Optional[Dict[str, Any]] = None,
        enable: Optional[bool] = None
    ) -> str:
        """
        Updates a specific configuration for a Wowza application.

        WARNING: When updating 'security' config, this is a SENSITIVE operation.
        ALWAYS confirm with the user before executing security configuration changes.

        Args:
            app_name: The name of the application to update.
            config_type: The specific configuration to modify. Must be one of:
                "security", "dvr", "dvr_adv", "drm", "transcoder", "webrtc", "modules", "streamconfiguration".
            data: A dictionary containing the configuration settings. The structure of this dictionary
                  must match the required schema for the given 'config_type'.
            enable: A convenience flag ONLY for 'transcoder'. If set to True or False,
                    it will enable or disable the transcoder. This can be used instead of 'data'.
        """
        # Map config_type to the corresponding client method and Pydantic model class
        config_map = {
            "security": (client.put_security_config, ApplicationSecurityConfig),
            "dvr": (client.put_dvr_config, ApplicationDvrConfig),
            "dvr_adv": (client.put_dvr_config_adv, None),  # Advanced DVR config
            "drm": (client.put_drm_config, ApplicationDrmConfig),
            "transcoder": (client.put_transcoder_config, ApplicationTranscoderConfig),
            "webrtc": (client.put_webrtc_config, None),  # No pydantic model yet
            "modules": (client.put_modules_config, None),  # No pydantic model yet
            "streamconfiguration": (client.put_streamconfiguration_config, None),  # No pydantic model yet
        }

        if config_type not in config_map:
            raise ValueError(f"Invalid config_type: '{config_type}'. Must be one of {list(config_map.keys())}")

        client_method, expected_model = config_map[config_type]

        # 1. Handle the 'enable' shortcut for transcoder first. This can create or modify the 'data' dictionary.
        if config_type == "transcoder" and enable is not None:
            transcoder_enable_value = "transcoder" if enable else ""
            if data is None:
                # If no data was provided, create a new dictionary.
                data = {"liveStreamTranscoder": transcoder_enable_value}
            else:
                # If data was provided, overwrite the specific key.
                data["liveStreamTranscoder"] = transcoder_enable_value
        elif enable is not None:
            # If 'enable' is used for any other config type, it's an error.
            raise ValueError("'enable' parameter is only valid when config_type is 'transcoder'")

        # 2. Now that the shortcut is handled, check if 'data' exists. If not, it's an error.
        if data is None:
            raise ValueError(f"'data' dictionary is required for config_type '{config_type}' (unless using 'enable' with 'transcoder').")

        # 3. Validate the dictionary against the expected Pydantic model (if available).
        # This replaces the complex Union type hint and provides robust runtime validation.
        if expected_model is not None:
            try:
                parsed_data = expected_model.model_validate(data)
                payload = parsed_data.model_dump(exclude_none=True)
            except Exception as e:
                raise TypeError(f"The provided 'data' dictionary is not valid for config_type '{config_type}'. Error: {e}") from e
        else:
            # For config types without pydantic models, use data directly
            payload = data

        # 4. Make the API call.
        result = await client_method(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            data=payload,
        )

        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application","write"},
        description="DESTRUCTIVE: Delete an application. ALWAYS confirm with user before executing."
    )
    async def delete_wowza_application(app_name: str) -> str:
        """
        Deletes the specified application configuration.

        WARNING: This is a DESTRUCTIVE operation that CANNOT be undone.
        ALWAYS confirm with the user before executing this operation.

        Args:
            app_name: The name of the application to delete.
        """
        result = await client.delete_application_config(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application","write"},
        description=(
            "Perform an action on an application (copy, restart, shutdown, start).\n\n"
            "IMPORTANT: Use action='copy' to clone/duplicate an application with ALL its configuration.\n"
            "The 'copy' action creates an EXACT copy including streamType, transcoder settings, WebRTC, "
            "security, modules, and all advanced properties. This is the ONLY way to ensure a complete copy."
        )
    )
    async def control_wowza_application(
        app_name: str,
        action: Literal["copy", "restart", "shutdown", "start"],
        destination_app_name: Optional[str] = None
    ) -> str:
        """
        Performs an action on the specified application.

        IMPORTANT: When user asks to "copy", "clone", or "duplicate" an application,
        use action='copy' to create an EXACT copy with ALL configuration settings.
        This includes:
        - Stream configuration (streamType: "live", packetizers)
        - Transcoder templates and settings
        - WebRTC, security, DVR, DRM configuration
        - Modules and advanced properties

        DO NOT use create_wowza_application to copy apps - it will miss critical settings
        like streamType which causes transcoding to fail.

        Args:
            app_name: The name of the application to control.
            action: The action to perform. Must be one of: copy, restart, shutdown, start.
            destination_app_name: Required when action is 'copy'. The name for the copied application.
        """
        if action == "copy" and not destination_app_name:
            raise ValueError("destination_app_name is required when action is 'copy'")

        result = await client.put_application_action(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            action=action,
            dst_entry_name=destination_app_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application","read"},
        description="Get the advanced configuration for an application."
    )
    async def get_wowza_application_config_adv(app_name: str) -> str:
        """
        Retrieves the advanced configuration for the specified application.

        Args:
            app_name: The name of the application.
        """
        result = await client.get_application_config_adv(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application","write"},
        description=create_enhanced_tool_description(
            "Update an application's advanced settings (modules, custom properties).",
            ApplicationAdvancedUpdate,
            "app_data"
        )
    )
    async def update_wowza_application_adv(app_name: str, app_data: ApplicationAdvancedUpdate) -> str:
        """
        Updates the advanced configuration for the specified application.

        Args:
            app_name: The name of the application.
            app_data: The advanced configuration data including modules and properties.
        """
        payload = app_data.model_dump(exclude_none=True)
        result = await client.put_application_config_adv(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            data=payload,
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get the configuration of a specific .stream file."
    )
    async def get_wowza_stream_file(app_name: str, streamfile_name: str) -> str:
        """
        Retrieves the specified stream file configuration.

        Args:
            app_name: The name of the application.
            streamfile_name: The name of the stream file (without the .stream extension).
        """
        result = await client.get_stream_file(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            streamfile_name=streamfile_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description="Update a .stream file configuration in an application."
    )
    async def update_wowza_stream_file(app_name: str, streamfile_name: str, stream_file_data: StreamFileCreate) -> str:
        """
        Updates an existing .stream file configuration.

        Args:
            app_name: The name of the application.
            streamfile_name: The name of the stream file to update (without the .stream extension).
            stream_file_data: The updated stream file configuration.
        """
        payload = stream_file_data.model_dump(exclude_none=True)
        result = await client.update_stream_file(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            streamfile_name=streamfile_name,
            data=payload
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description="Connect a .stream file to start pulling the remote stream."
    )
    async def connect_wowza_stream_file(
        app_name: str,
        streamfile_name: str,
        media_caster_type: Literal["rtp", "rtp-record", "shoutcast", "shoutcast-record", "liverepeater"] = "rtp",
        connect_app_name: Optional[str] = None,
        app_instance: Optional[str] = None
    ) -> str:
        """
        Initiates the connection for a MediaCaster stream defined in a .stream file.

        Args:
            app_name: The application where the .stream file resides.
            streamfile_name: The name of the stream file to connect.
            media_caster_type: The type of media caster. Defaults to 'rtp'.
            connect_app_name: Optional application name for the connection.
            app_instance: Optional application instance name.
        """
        result = await client.connect_stream_file(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            streamfile_name=streamfile_name,
            media_caster_type=media_caster_type,
            connect_app_name=connect_app_name,
            app_instance=app_instance
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get a specific configuration section (security, dvr, dvr_adv, drm, transcoder, webrtc, modules, or streamconfiguration) for a Wowza application."
    )
    async def get_wowza_application_subconfig(
        app_name: str,
        config_type: Literal["security", "dvr", "dvr_adv", "drm", "transcoder", "webrtc", "modules", "streamconfiguration"]
    ) -> str:
        """
        Retrieves a specific configuration section for a Wowza application.

        Args:
            app_name: The name of the application.
            config_type: The specific configuration to retrieve. Must be one of:
                "security", "dvr", "dvr_adv", "drm", "transcoder", "webrtc", "modules", "streamconfiguration".
        """
        config_map = {
            "security": client.get_security_config,
            "dvr": client.get_dvr_config,
            "dvr_adv": client.get_dvr_config_adv,
            "drm": client.get_drm_config,
            "transcoder": client.get_transcoder_config,
            "webrtc": client.get_webrtc_config,
            "modules": client.get_modules_config,
            "streamconfiguration": client.get_streamconfiguration_config,
        }

        if config_type not in config_map:
            raise ValueError(f"Invalid config_type: '{config_type}'. Must be one of {list(config_map.keys())}")

        client_method = config_map[config_type]
        result = await client_method(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name
        )

        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get a list of all instances for an application."
    )
    async def get_wowza_application_instances(app_name: str) -> str:
        """
        Retrieves the list of instances for the specified application.

        Args:
            app_name: The name of the application.
        """
        result = await client.get_instances(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get information about a specific application instance."
    )
    async def get_wowza_application_instance(app_name: str, instance_name: str = "_definst_") -> str:
        """
        Retrieves the specified application instance information.

        Args:
            app_name: The name of the application.
            instance_name: The name of the instance (defaults to '_definst_', the default instance).
        """
        result = await client.get_instance(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            instance_name=instance_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description="Start an application instance."
    )
    async def start_wowza_application_instance(app_name: str, instance_name: str = "_definst_") -> str:
        """
        Starts the specified application instance.

        Args:
            app_name: The name of the application.
            instance_name: The name of the instance to start (defaults to '_definst_', the default instance).
        """
        result = await client.put_instance_action(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            instance_name=instance_name,
            action="start"
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get a list of all stream recorders for an application instance."
    )
    async def get_wowza_stream_recorders(app_name: str, instance_name: str = "_definst_") -> str:
        """
        Retrieves the list of stream recorders for the specified application instance.

        Args:
            app_name: The name of the application.
            instance_name: The name of the instance (defaults to '_definst_').
        """
        result = await client.get_recorders(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            instance_name=instance_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get information about a specific stream recorder."
    )
    async def get_wowza_stream_recorder(app_name: str, recorder_name: str, instance_name: str = "_definst_") -> str:
        """
        Retrieves the specified stream recorder information.

        Args:
            app_name: The name of the application.
            recorder_name: The name of the stream recorder.
            instance_name: The name of the instance (defaults to '_definst_').
        """
        result = await client.get_recorder(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            instance_name=instance_name,
            recorder_name=recorder_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get default recorder configuration template. Used internally by create_wowza_stream_recorder."
    )
    async def get_wowza_stream_recorder_defaults(app_name: str, recorder_name: str, instance_name: str = "_definst_") -> str:
        """
        Retrieves default recorder configuration template for the specified recorder name.
    
        Args:
            app_name: The name of the application.
            recorder_name: The desired name for the stream recorder.
            instance_name: The name of the instance (defaults to '_definst_').

        Returns:
            JSON string with complete default recorder configuration including all required fields.
            The 'option' field is automatically corrected from 'Version existing file' to 'Version'.
        """
        result = await client.get_default_stream_recorder(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            instance_name=instance_name,
            recorder_name=recorder_name
        )

        # Fix Wowza API bug: The /default endpoint returns "Version existing file"
        # but the POST endpoint only accepts "Version", "Append", or "Overwrite"
        if isinstance(result, dict) and "option" in result:
            if result["option"] == "Version existing file":
                result["option"] = "Version"

        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description=(
            "Create a stream recorder to record an incoming stream.\n\n"
            "CRITICAL: stream_name MUST match the exact incoming stream name (NO suffixes!).\n\n"
            "BEFORE creating the recorder, ASK the user to confirm these settings."
        )
    )
    async def create_wowza_stream_recorder(
        app_name: str,
        stream_name: str,
        instance_name: str = "_definst_",
        output_path: str = "/usr/local/WowzaStreamingEngine/content",
        file_format: Literal["MP4", "FLV"] = "MP4",
        record_option: Literal["Version", "Append", "Overwrite"] = "Version",
        record_data: bool = False,
        start_on_keyframe: bool = True
    ) -> str:
        """
        Args:
            app_name: The name of the application (e.g., 'live').
            stream_name: The exact name of the incoming stream to record (NO suffixes!).
            instance_name: The instance name (defaults to '_definst_').
            output_path: Directory for recordings (defaults to Wowza content directory).
            file_format: File format - 'MP4' or 'FLV' (defaults to 'MP4').
            record_option: Recording option - 'Version', 'Append', or 'Overwrite' (defaults to 'Version').
            record_data: Enable data recording (defaults to False).
            start_on_keyframe: Start recording on key frame (defaults to True).
        """
        # Step 1: Get defaults
        defaults = await client.get_default_stream_recorder(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            instance_name=instance_name,
            recorder_name=stream_name
        )

        # Step 2: Fix the Wowza API bug with option field
        if isinstance(defaults, dict) and "option" in defaults:
            if defaults["option"] == "Version existing file":
                defaults["option"] = "Version"

        # Step 3: Customize the configuration with user-provided values
        defaults["recorderName"] = stream_name
        defaults["baseFile"] = stream_name
        defaults["currentFile"] = f"{output_path}/{stream_name}.{file_format.lower()}"
        defaults["outputPath"] = output_path
        defaults["fileFormat"] = file_format.upper()
        defaults["option"] = record_option
        defaults["recordData"] = record_data
        defaults["startOnKeyFrame"] = start_on_keyframe

        # Step 4: Create the recorder
        result = await client.add_stream_recorder(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            instance_name=instance_name,
            recorder_name=stream_name,
            data=defaults
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description="Control a stream recorder (split or stop recording)."
    )
    async def control_wowza_stream_recorder(
        app_name: str,
        recorder_name: str,
        action: Literal["splitRecording", "stopRecording"],
        instance_name: str = "_definst_"
    ) -> str:
        """
        Performs an action on a stream recorder.

        Args:
            app_name: The name of the application.
            recorder_name: The name of the stream recorder.
            action: The action to perform ('splitRecording' or 'stopRecording').
            instance_name: The name of the instance (defaults to '_definst_').
        """
        result = await client.put_recorder_action(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            instance_name=instance_name,
            recorder_name=recorder_name,
            action=action
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get a list of all SMIL files for an application."
    )
    async def get_wowza_smil_files(app_name: str) -> str:
        """
        Retrieves the list of SMIL files for the specified application.

        Args:
            app_name: The name of the application.
        """
        result = await client.get_smil_files(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get the configuration of a specific SMIL file."
    )
    async def get_wowza_smil_file(app_name: str, smilfile_name: str) -> str:
        """
        Retrieves the specified SMIL file configuration.

        Args:
            app_name: The name of the application.
            smilfile_name: The name of the SMIL file (without the .smil extension).
        """
        result = await client.get_smil_file(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            smilfile_name=smilfile_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description="Add a new SMIL file to an application."
    )
    async def add_wowza_smil_file(app_name: str, smil_data: SmilFileCreate) -> str:
        """
        Adds a new SMIL file to the specified application.

        Args:
            app_name: The name of the application.
            smil_data: The SMIL file configuration (name, contents, optional description).
        """
        payload = smil_data.model_dump(exclude_none=True)
        result = await client.add_smil_file(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            data=payload
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description="DESTRUCTIVE: Remove a SMIL file. ALWAYS confirm with user before executing."
    )
    async def remove_wowza_smil_file(app_name: str, smilfile_name: str) -> str:
        """
        Deletes a SMIL file from the specified application.

        WARNING: This is a DESTRUCTIVE operation that CANNOT be undone.
        ALWAYS confirm with the user before executing this operation.

        Args:
            app_name: The name of the application.
            smilfile_name: The name of the SMIL file to remove (without the .smil extension).
        """
        result = await client.delete_smil_file(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            smilfile_name=smilfile_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get the advanced DVR configuration for an application."
    )
    async def get_wowza_dvr_config_adv(app_name: str) -> str:
        """
        Retrieves the advanced DVR configuration for the specified application.

        Args:
            app_name: The name of the application.
        """
        result = await client.get_dvr_config_adv(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description=(
            "Update the advanced DVR configuration for an application.\n\n"
            "All fields in dvr_adv_data are optional. Common fields include:\n"
            "- dvrRecorderStartOption: str - Start option for recorder\n"
            "- dvrWindowDuration: int - Window duration in seconds\n"
            "- dvrStoreName: str - DVR store name\n"
            "- dvrEncryptionSharedSecret: str - Encryption secret\n"
            "- dvrConvertionEnabled: bool - Enable conversion\n"
            "Refer to Wowza documentation for complete list of advanced DVR properties."
        )
    )
    async def update_wowza_dvr_config_adv(app_name: str, dvr_adv_data: Dict[str, Any]) -> str:
        """
        Updates the advanced DVR configuration for the specified application.

        Args:
            app_name: The name of the application.
            dvr_adv_data: The advanced DVR configuration data. All fields are optional.
        """
        result = await client.put_dvr_config_adv(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            data=dvr_adv_data
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get the advanced DRM configuration for an application."
    )
    async def get_wowza_drm_config_adv(app_name: str) -> str:
        """
        Retrieves the advanced DRM configuration for the specified application.

        Args:
            app_name: The name of the application.
        """
        result = await client.get_drm_config_adv(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description=(
            "Update the advanced DRM configuration for an application.\n\n"
            "All fields in drm_adv_data are optional. Common fields include:\n"
            "- cupertinoEncryptionAPIBased: bool - Enable API-based encryption\n"
            "- cupertinoPlaylistEncryptionKeyIndex: int - Encryption key index\n"
            "- sanjosePlaylistEncryptionKeyIndex: int - San Jose encryption key\n"
            "Refer to Wowza documentation for complete list of advanced DRM properties."
        )
    )
    async def update_wowza_drm_config_adv(app_name: str, drm_adv_data: Dict[str, Any]) -> str:
        """
        Updates the advanced DRM configuration for the specified application.

        Args:
            app_name: The name of the application.
            drm_adv_data: The advanced DRM configuration data. All fields are optional.
        """
        result = await client.put_drm_config_adv(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            data=drm_adv_data
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get the BuyDRM stream mapfile configuration."
    )
    async def get_wowza_buydrm_stream_maps(app_name: str) -> str:
        """
        Retrieves the BuyDRM stream mapfile for the specified application.

        Args:
            app_name: The name of the application.
        """
        result = await client.get_buydrm_stream_maps(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description="Update the BuyDRM stream mapfile configuration."
    )
    async def update_wowza_buydrm_stream_maps(app_name: str, buydrm_data: BuyDRMStreamMapsData) -> str:
        """
        Updates the BuyDRM stream mapfile for the specified application.

        Args:
            app_name: The name of the application.
            buydrm_data: The BuyDRM mapfile configuration with streamMap array.
        """
        payload = buydrm_data.model_dump(exclude_none=True)
        result = await client.put_buydrm_stream_maps(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            data=payload
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get the Verimatrix stream mapfile configuration."
    )
    async def get_wowza_verimatrix_stream_maps(app_name: str) -> str:
        """
        Retrieves the Verimatrix stream mapfile for the specified application.

        Args:
            app_name: The name of the application.
        """
        result = await client.get_verimatrix_stream_maps(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description="Update the Verimatrix stream mapfile configuration."
    )
    async def update_wowza_verimatrix_stream_maps(app_name: str, verimatrix_data: VerimatrixStreamMapsData) -> str:
        """
        Updates the Verimatrix stream mapfile for the specified application.

        Args:
            app_name: The name of the application.
            verimatrix_data: The Verimatrix mapfile configuration with streamMap array.
        """
        payload = verimatrix_data.model_dump(exclude_none=True)
        result = await client.put_verimatrix_stream_maps(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            data=payload
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get the advanced WebRTC configuration for an application."
    )
    async def get_wowza_webrtc_config_adv(app_name: str) -> str:
        """
        Retrieves the advanced WebRTC configuration for the specified application.

        Args:
            app_name: The name of the application.
        """
        result = await client.get_webrtc_config_adv(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description=(
            "Update the advanced WebRTC configuration for an application.\n\n"
            "All fields in webrtc_adv_data are optional. Common fields include:\n"
            "- webRTCDebugLog: bool - Enable debug logging\n"
            "- webRTCMaxRTCPWaitTime: int - Max RTCP wait time\n"
            "- webRTCUDPTransportReceiveBufferSize: int - UDP buffer size\n"
            "Refer to Wowza documentation for complete list of advanced WebRTC properties."
        )
    )
    async def update_wowza_webrtc_config_adv(app_name: str, webrtc_adv_data: Dict[str, Any]) -> str:
        """
        Updates the advanced WebRTC configuration for the specified application.

        Args:
            app_name: The name of the application.
            webrtc_adv_data: The advanced WebRTC configuration data. All fields are optional.
        """
        result = await client.put_webrtc_config_adv(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            data=webrtc_adv_data
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get the advanced Transcoder configuration for an application."
    )
    async def get_wowza_transcoder_config_adv(app_name: str) -> str:
        """
        Retrieves the advanced Transcoder configuration for the specified application.

        Args:
            app_name: The name of the application.
        """
        result = await client.get_transcoder_config_adv(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description=(
            "Update the advanced Transcoder configuration for an application.\n\n"
            "All fields in transcoder_adv_data are optional. Common fields include:\n"
            "- transcoderAppendToOutputStreamName: str - Suffix for output streams\n"
            "- transcoderSessionTimeout: int - Session timeout in milliseconds\n"
            "- transcoderDecoderMaxFrameReorderBuffer: int - Max frame reorder buffer\n"
            "Refer to Wowza documentation for complete list of advanced Transcoder properties."
        )
    )
    async def update_wowza_transcoder_config_adv(app_name: str, transcoder_adv_data: Dict[str, Any]) -> str:
        """
        Updates the advanced Transcoder configuration for the specified application.

        Args:
            app_name: The name of the application.
            transcoder_adv_data: The advanced Transcoder configuration data. All fields are optional.
        """
        result = await client.put_transcoder_config_adv(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            data=transcoder_adv_data
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get the advanced configuration for a specific stream file."
    )
    async def get_wowza_stream_file_adv(app_name: str, streamfile_name: str) -> str:
        """
        Retrieves the advanced stream file configuration.

        Args:
            app_name: The name of the application.
            streamfile_name: The name of the stream file (without the .stream extension).
        """
        result = await client.get_stream_file_adv(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            streamfile_name=streamfile_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description=(
            "Update the advanced configuration for a specific stream file.\n\n"
            "All fields in streamfile_adv_data are optional. Common fields include:\n"
            "- playOnStream: str - Play on stream setting\n"
            "- streamTimeout: int - Stream timeout in milliseconds\n"
            "- httpRandomizeMediaRequests: bool - Randomize media requests\n"
            "Refer to Wowza documentation for complete list of advanced stream file properties."
        )
    )
    async def update_wowza_stream_file_adv(app_name: str, streamfile_name: str, streamfile_adv_data: Dict[str, Any]) -> str:
        """
        Updates the advanced stream file configuration.

        Args:
            app_name: The name of the application.
            streamfile_name: The name of the stream file (without the .stream extension).
            streamfile_adv_data: The advanced stream file configuration data. All fields are optional.
        """
        result = await client.put_stream_file_adv(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            streamfile_name=streamfile_name,
            data=streamfile_adv_data
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get current statistics for a specific incoming stream."
    )
    async def get_wowza_incoming_stream_stats(
        app_name: str,
        stream_name: str,
        instance_name: str = "_definst_"
    ) -> str:
        """
        Retrieves current statistics for the specified incoming stream.

        Args:
            app_name: The name of the application.
            stream_name: The name of the incoming stream.
            instance_name: The name of the instance (defaults to '_definst_').
        """
        result = await client.get_incoming_stream_current_stats(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            instance_name=instance_name,
            stream_name=stream_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description=(
            "Get transcoder template(s) for a Wowza application.\n\n"
            "Usage:\n"
            "- To list all templates: omit template_name and include_advanced\n"
            "- To get a specific template: provide template_name\n"
            "- To get advanced config: provide template_name and include_advanced=True"
        )
    )
    async def get_wowza_transcoder_template(
        app_name: str,
        template_name: Optional[str] = None,
        include_advanced: bool = False
    ) -> str:
        """
        Retrieves transcoder template(s). Supports list all, get one, or get advanced config.

        Args:
            app_name: The application name.
            template_name: Optional template name. If None, returns list of all templates.
            include_advanced: If True and template_name provided, returns advanced configuration.
        """
        if template_name is None:
            # List all templates
            result = await client.get_transcoder_templates(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name
            )
        elif include_advanced:
            # Get advanced config for specific template
            result = await client.get_transcoder_template_adv(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name
            )
        else:
            # Get specific template
            result = await client.get_transcoder_template(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name
            )

        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description=(
            "Manage transcoder templates: create, update, update_advanced, delete, start, stop.\n"
            "Required for create/update: template_data with 'name' and 'templates' array.\n\n"
            "WARNING: For delete operations, ALWAYS confirm with user before executing."
        )
    )
    async def manage_wowza_transcoder_template(
        app_name: str,
        operation: Literal["create", "update", "update_advanced", "delete", "start", "stop"],
        template_name: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Comprehensive transcoder template management.

        WARNING: When using 'delete' operation, this is a DESTRUCTIVE operation.
        ALWAYS confirm with the user before executing delete operations.

        Args:
            app_name: The application name.
            operation: The operation to perform.
            template_name: Template name (required for all except 'create').
            template_data: Template configuration (required for 'create', 'update', 'update_advanced').
                For create/update: must include 'name' and 'templates' array.
        """
        # Validation
        if operation in ["update", "update_advanced", "delete", "start", "stop"] and not template_name:
            raise ValueError(f"template_name is required for operation '{operation}'")

        if operation in ["create", "update", "update_advanced"] and not template_data:
            raise ValueError(f"template_data is required for operation '{operation}'")

        # Route to appropriate API method
        if operation == "create":
            result = await client.create_transcoder_template(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                data=template_data
            )
        elif operation == "update":
            result = await client.update_transcoder_template(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name,
                data=template_data
            )
        elif operation == "update_advanced":
            result = await client.update_transcoder_template_adv(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name,
                data=template_data
            )
        elif operation == "delete":
            result = await client.delete_transcoder_template(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name
            )
        elif operation in ["start", "stop"]:
            result = await client.transcoder_template_action(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name,
                action=operation
            )

        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get transcoder encode(s) for a template. Supports list all, get one, or get advanced config."
    )
    async def get_wowza_transcoder_encode(
        app_name: str,
        template_name: str,
        encode_name: Optional[str] = None,
        include_advanced: bool = False
    ) -> str:
        """
        Retrieves transcoder encode(s) for a template.

        Args:
            app_name: Application name
            template_name: Template name
            encode_name: Optional encode name. If None, returns list of all encodes
            include_advanced: If True, returns advanced configuration (requires encode_name)
        """
        if encode_name is None:
            result = await client.get_transcoder_encodes(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name
            )
        elif include_advanced:
            result = await client.get_transcoder_encode_adv(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name,
                encode_name=encode_name
            )
        else:
            result = await client.get_transcoder_encode(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name,
                encode_name=encode_name
            )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description="Manage transcoder encodes: create, update, update_advanced, delete. WARNING: For delete operations, ALWAYS confirm with user before executing."
    )
    async def manage_wowza_transcoder_encode(
        app_name: str,
        template_name: str,
        operation: Literal["create", "update", "update_advanced", "delete"],
        encode_name: Optional[str] = None,
        encode_data: Optional[TranscoderEncodeCreate] = None,
        encode_data_advanced: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Manages transcoder encode configurations.

        WARNING: When using 'delete' operation, this is a DESTRUCTIVE operation.
        ALWAYS confirm with the user before executing delete operations.

        Args:
            app_name: Application name
            template_name: Template name
            operation: Operation to perform
            encode_name: Name of encode (required for update/delete)
            encode_data: Configuration data (required for create/update). Uses structured model with Literal types for codecs.
            encode_data_advanced: Advanced configuration data (for update_advanced operation only). Use Dict for advanced configs.
        """
        if operation == "create":
            if not encode_data:
                raise ValueError("encode_data is required for create operation")
            payload = encode_data.model_dump(exclude_none=True)
            result = await client.create_transcoder_encode(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name,
                data=payload
            )
        elif operation == "update":
            if not encode_name or not encode_data:
                raise ValueError("encode_name and encode_data are required for update operation")
            payload = encode_data.model_dump(exclude_none=True)
            result = await client.update_transcoder_encode(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name,
                encode_name=encode_name,
                data=payload
            )
        elif operation == "update_advanced":
            if not encode_name or not encode_data_advanced:
                raise ValueError("encode_name and encode_data_advanced are required for update_advanced operation")
            result = await client.update_transcoder_encode_adv(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name,
                encode_name=encode_name,
                data=encode_data_advanced
            )
        elif operation == "delete":
            if not encode_name:
                raise ValueError("encode_name is required for delete operation")
            result = await client.delete_transcoder_encode(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name,
                encode_name=encode_name
            )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get transcoder overlay configuration for decode or encode."
    )
    async def get_wowza_transcoder_overlay(
        app_name: str,
        template_name: str,
        overlay_type: Literal["decode", "encode"],
        encode_name: Optional[str] = None
    ) -> str:
        """
        Retrieves transcoder overlay configuration.

        Args:
            app_name: Application name
            template_name: Template name
            overlay_type: Type of overlay - 'decode' or 'encode'
            encode_name: Required for encode overlays
        """
        if overlay_type == "decode":
            result = await client.get_transcoder_overlay_decode(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name
            )
        else:
            if not encode_name:
                raise ValueError("encode_name is required for encode overlay")
            result = await client.get_transcoder_overlay_encode(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name,
                encode_name=encode_name
            )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description=(
            "Manage transcoder overlays (decode/encode): update, delete.\n"
            "Required for update: overlay_data with overlayArchive, overlayProvider.\n\n"
            "WARNING: For delete operations, ALWAYS confirm with user before executing."
        )
    )
    async def manage_wowza_transcoder_overlay(
        app_name: str,
        template_name: str,
        overlay_type: Literal["decode", "encode"],
        operation: Literal["update", "delete"],
        encode_name: Optional[str] = None,
        overlay_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Manages transcoder overlay configurations.

        WARNING: When using 'delete' operation, this is a DESTRUCTIVE operation.
        ALWAYS confirm with the user before executing delete operations.

        Args:
            app_name: Application name
            template_name: Template name
            overlay_type: Type of overlay - 'decode' or 'encode'
            operation: Operation to perform - 'update' or 'delete'
            encode_name: Required for encode overlays
            overlay_data: Configuration data (required for update).
                Must include 'overlayArchive' and 'overlayProvider' for update.
        """
        if overlay_type == "decode":
            if operation == "update":
                if not overlay_data:
                    raise ValueError("overlay_data is required for update operation")
                result = await client.update_transcoder_overlay_decode(
                    server_name=config["server_name"],
                    vhost_name=config["vhost_name"],
                    app_name=app_name,
                    template_name=template_name,
                    data=overlay_data
                )
            else:
                result = await client.delete_transcoder_overlay_decode(
                    server_name=config["server_name"],
                    vhost_name=config["vhost_name"],
                    app_name=app_name,
                    template_name=template_name
                )
        else:
            if not encode_name:
                raise ValueError("encode_name is required for encode overlay")
            if operation == "update":
                if not overlay_data:
                    raise ValueError("overlay_data is required for update operation")
                result = await client.update_transcoder_overlay_encode(
                    server_name=config["server_name"],
                    vhost_name=config["vhost_name"],
                    app_name=app_name,
                    template_name=template_name,
                    encode_name=encode_name,
                    data=overlay_data
                )
            else:
                result = await client.delete_transcoder_overlay_encode(
                    server_name=config["server_name"],
                    vhost_name=config["vhost_name"],
                    app_name=app_name,
                    template_name=template_name,
                    encode_name=encode_name
                )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get transcoder stream name group(s). Supports list all or get specific group."
    )
    async def get_wowza_transcoder_streamname_group(
        app_name: str,
        template_name: str,
        group_name: Optional[str] = None
    ) -> str:
        """
        Retrieves transcoder stream name group(s).

        Args:
            app_name: Application name
            template_name: Template name
            group_name: Optional group name. If None, returns list of all groups
        """
        if group_name is None:
            result = await client.get_transcoder_streamname_groups(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name
            )
        else:
            result = await client.get_transcoder_streamname_group(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name,
                group_name=group_name
            )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description="Manage transcoder stream name groups: create, update, delete. Required: group_data with streamName, member array. WARNING: For delete operations, ALWAYS confirm with user before executing."
    )
    async def manage_wowza_transcoder_streamname_group(
        app_name: str,
        template_name: str,
        operation: Literal["create", "update", "delete"],
        group_name: Optional[str] = None,
        group_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Manages transcoder stream name groups.

        WARNING: When using 'delete' operation, this is a DESTRUCTIVE operation.
        ALWAYS confirm with the user before executing delete operations.

        Args:
            app_name: Application name
            template_name: Template name
            operation: Operation to perform
            group_name: Name of group (required for update/delete)
            group_data: Configuration data (required for create/update).
                Must include 'streamName' and 'member' array for create/update.
        """
        if operation == "create":
            if not group_data:
                raise ValueError("group_data is required for create operation")
            result = await client.create_transcoder_streamname_group(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name,
                data=group_data
            )
        elif operation == "update":
            if not group_name or not group_data:
                raise ValueError("group_name and group_data are required for update operation")
            result = await client.update_transcoder_streamname_group(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name,
                group_name=group_name,
                data=group_data
            )
        elif operation == "delete":
            if not group_name:
                raise ValueError("group_name is required for delete operation")
            result = await client.delete_transcoder_streamname_group(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                template_name=template_name,
                group_name=group_name
            )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get publisher(s) for an application. Supports list all or get specific publisher."
    )
    async def get_wowza_publisher(
        app_name: str,
        publisher_name: Optional[str] = None
    ) -> str:
        """
        Retrieves publisher(s) for an application.

        Args:
            app_name: Application name
            publisher_name: Optional publisher name. If None, returns list of all publishers
        """
        if publisher_name is None:
            result = await client.get_publishers(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name
            )
        else:
            result = await client.get_publisher(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                publisher_name=publisher_name
            )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description=(
            "Manage publishers - create, add, update, or delete.\n\n"
            "Required fields in publisher_data (for create/add/update):\n"
            "- name: str - Publisher name\n"
            "- enabled: bool - Whether publisher is enabled\n\n"
            "Optional fields:\n"
            "- description: str - Publisher description\n"
            "- Various publisher-specific properties\n\n"
            "WARNING: For delete operations, ALWAYS confirm with user before executing."
        )
    )
    async def manage_wowza_publisher(
        app_name: str,
        operation: Literal["create", "add", "update", "delete"],
        publisher_name: Optional[str] = None,
        publisher_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Manages publisher configurations.

        WARNING: When using 'delete' operation, this is a DESTRUCTIVE operation.
        ALWAYS confirm with the user before executing delete operations.

        Args:
            app_name: Application name
            operation: Operation to perform
            publisher_name: Name of publisher (required for add/update/delete)
            publisher_data: Configuration data (required for create/add/update).
                Must include 'name' and 'enabled' for create/add/update.
        """
        if operation == "create":
            if not publisher_data:
                raise ValueError("publisher_data is required for create operation")
            result = await client.create_publisher(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                data=publisher_data
            )
        elif operation == "add":
            if not publisher_name or not publisher_data:
                raise ValueError("publisher_name and publisher_data are required for add operation")
            result = await client.add_publisher(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                publisher_name=publisher_name,
                data=publisher_data
            )
        elif operation == "update":
            if not publisher_name or not publisher_data:
                raise ValueError("publisher_name and publisher_data are required for update operation")
            result = await client.update_publisher(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                publisher_name=publisher_name,
                data=publisher_data
            )
        elif operation == "delete":
            if not publisher_name:
                raise ValueError("publisher_name is required for delete operation")
            result = await client.delete_publisher(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                publisher_name=publisher_name
            )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get push publish (stream target) entry(ies). Supports list all or get specific entry."
    )
    async def get_wowza_push_publish_entry(
        app_name: str,
        entry_name: Optional[str] = None
    ) -> str:
        """
        Retrieves push publish map entry(ies).

        Args:
            app_name: Application name
            entry_name: Optional entry name. If None, returns list of all entries
        """
        if entry_name is None:
            result = await client.get_push_publish_entries(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name
            )
        else:
            result = await client.get_push_publish_entry(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                entry_name=entry_name
            )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description=(
            "Manage push publish entries (also called stream targets).\n\n"
            "QUICK ENABLE/DISABLE: Use operation='update' with enabled parameter.\n\n"
            "CREATE requires entry_data with: entryName, profile, streamName, sourceStreamName, serverName, enabled.\n"
            "Optional: userName, password, application.\n\n"
            "WARNING: For delete operations, ALWAYS confirm with user before executing."
        )
    )
    async def manage_wowza_push_publish_entry(
        app_name: str,
        operation: Literal["create", "add", "update", "update_all", "delete", "action"],
        entry_name: Optional[str] = None,
        entry_data: Optional[Dict[str, Any]] = None,
        action: Optional[Literal["enable", "disable", "restart", "copy", "connect", "disconnect"]] = None,
        enabled: Optional[bool] = None,
        dst_entry_name: Optional[str] = None
    ) -> str:
        """
        Manages push publish map entries (also called stream targets).

        WARNING: When using 'delete' operation, this is a DESTRUCTIVE operation.
        ALWAYS confirm with the user before executing delete operations.

        Args:
            app_name: Application name
            operation: Operation to perform
            entry_name: Entry name (required for add/update/delete/action)
            entry_data: Configuration data (required for create/add/update)
            action: Action to perform (required for action operation)
            enabled: Shortcut to enable/disable with update operation
            dst_entry_name: Destination entry name (required for copy action)
        """
        # Handle the 'enabled' shortcut for update operation
        if operation == "update" and enabled is not None:
            if entry_data is None:
                entry_data = {}
            entry_data["enabled"] = enabled

        if operation == "create":
            if not entry_data:
                raise ValueError("entry_data is required for create operation")
            result = await client.create_push_publish_entry(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                data=entry_data
            )
        elif operation == "add":
            if not entry_name or not entry_data:
                raise ValueError("entry_name and entry_data are required for add operation")
            result = await client.add_push_publish_entry(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                entry_name=entry_name,
                data=entry_data
            )
        elif operation == "update":
            if not entry_name or not entry_data:
                raise ValueError("entry_name and entry_data are required for update operation")
            result = await client.update_push_publish_entry(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                entry_name=entry_name,
                data=entry_data
            )
        elif operation == "update_all":
            if not entry_data:
                raise ValueError("entry_data is required for update_all operation")
            result = await client.update_push_publish_entries(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                data=entry_data
            )
        elif operation == "delete":
            if not entry_name:
                raise ValueError("entry_name is required for delete operation")
            result = await client.delete_push_publish_entry(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                entry_name=entry_name
            )
        elif operation == "action":
            if not entry_name or not action:
                raise ValueError("entry_name and action are required for action operation")
            if action == "copy" and not dst_entry_name:
                raise ValueError("dst_entry_name is required when action is 'copy'")
            result = await client.push_publish_entry_action(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                entry_name=entry_name,
                action=action,
                dst_entry_name=dst_entry_name
            )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get incoming stream information - stream, stats, encoder config, encoder URL, or source control."
    )
    async def get_wowza_incoming_stream(
        app_name: str,
        instance_name: str,
        stream_name: str,
        info_type: Literal["stream", "stats", "encoder", "encoder_url", "source_control"] = "stream"
    ) -> str:
        """
        Retrieves incoming stream information.

        Args:
            app_name: Application name
            instance_name: Instance name
            stream_name: Stream name
            info_type: Type of information to retrieve
        """
        if info_type == "stream":
            result = await client.get_incoming_stream(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                instance_name=instance_name,
                stream_name=stream_name
            )
        elif info_type == "stats":
            result = await client.get_incoming_stream_stats(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                instance_name=instance_name,
                stream_name=stream_name
            )
        elif info_type == "encoder":
            result = await client.get_live_encoder_config(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                instance_name=instance_name,
                stream_name=stream_name
            )
        elif info_type == "encoder_url":
            result = await client.get_encoder_short_url(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                instance_name=instance_name,
                stream_name=stream_name
            )
        elif info_type == "source_control":
            result = await client.get_source_control(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                instance_name=instance_name,
                stream_name=stream_name
            )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description=(
            "Disconnect or reset an incoming stream.\n\n"
            "For regular RTMP/RTSP/WebRTC publisher streams (action_type='stream'):\n"
            "  Use action: 'disconnectStream' or 'resetStream'\n\n"
            "For .stream files or MediaCaster streams (action_type='source_control'):\n"
            "  Use action: 'connect' or 'disconnect'"
        )
    )
    async def manage_wowza_incoming_stream(
        app_name: str,
        instance_name: str,
        stream_name: str,
        action: Literal["disconnectStream", "resetStream", "connect", "disconnect"],
        action_type: Literal["stream", "source_control"] = "stream"
    ) -> str:
        """
        Manages incoming stream actions for both publisher streams and source-controlled streams.

        Args:
            app_name: Application name
            instance_name: Instance name
            stream_name: Stream name
            action: Action to perform - valid values depend on action_type
            action_type: Type of action - 'stream' (default, for publisher streams) or 'source_control' (for .stream files)
        """
        if action_type == "stream":
            result = await client.incoming_stream_action(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                instance_name=instance_name,
                stream_name=stream_name,
                action=action
            )
        elif action_type == "source_control":
            result = await client.source_control_action(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                instance_name=instance_name,
                stream_name=stream_name,
                action=action
            )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get DVR store(s) for an application instance. Supports list all or get specific store."
    )
    async def get_wowza_dvr_store(
        app_name: str,
        instance_name: str,
        store_name: Optional[str] = None
    ) -> str:
        """
        Retrieves DVR store(s) for an application instance.

        Args:
            app_name: Application name
            instance_name: Instance name
            store_name: Optional store name. If None, returns list of all stores
        """
        if store_name is None:
            result = await client.get_dvr_stores(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                instance_name=instance_name
            )
        else:
            result = await client.get_dvr_store(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                instance_name=instance_name,
                store_name=store_name
            )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description="Manage DVR store actions - can apply to all stores or specific store."
    )
    async def manage_wowza_dvr_store(
        app_name: str,
        instance_name: str,
        action: str,
        store_name: Optional[str] = None
    ) -> str:
        """
        Manages DVR store actions.

        Args:
            app_name: Application name
            instance_name: Instance name
            action: Action to perform
            store_name: Optional store name. If None, action applies to all stores
        """
        if store_name is None:
            result = await client.dvr_stores_action(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                instance_name=instance_name,
                action=action
            )
        else:
            result = await client.dvr_store_action(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                instance_name=instance_name,
                store_name=store_name,
                action=action
            )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get stream group(s) for an application instance. Supports list all or get specific group."
    )
    async def get_wowza_stream_group(
        app_name: str,
        instance_name: str,
        group_name: Optional[str] = None
    ) -> str:
        """
        Retrieves stream group(s) for an application instance.

        Args:
            app_name: Application name
            instance_name: Instance name
            group_name: Optional group name. If None, returns list of all groups
        """
        if group_name is None:
            result = await client.get_stream_groups(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                instance_name=instance_name
            )
        else:
            result = await client.get_stream_group(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                instance_name=instance_name,
                group_name=group_name
            )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description="Manage stream group actions: disconnect, remove, or reset the group."
    )
    async def manage_wowza_stream_group(
        app_name: str,
        instance_name: str,
        group_name: str,
        action: Literal["disconnectGroup", "removeGroup", "resetGroup"]
    ) -> str:
        """
        Manages stream group actions.

        Args:
            app_name: Application name
            instance_name: Instance name
            group_name: Group name
            action: Action to perform
        """
        result = await client.stream_group_action(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            instance_name=instance_name,
            group_name=group_name,
            action=action
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "read"},
        description="Get DRM mapfile configuration - BuyDRM or Verimatrix."
    )
    async def get_wowza_drm_mapfile(
        app_name: str,
        mapfile_type: Literal["buydrm", "verimatrix"]
    ) -> str:
        """
        Retrieves DRM mapfile configuration.

        Args:
            app_name: Application name
            mapfile_type: Type of DRM mapfile - 'buydrm' or 'verimatrix'
        """
        if mapfile_type == "buydrm":
            result = await client.get_buydrm_mapfile(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name
            )
        else:
            result = await client.get_verimatrix_mapfile(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name
            )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"application", "write"},
        description="Update DRM mapfile configuration - BuyDRM or Verimatrix."
    )
    async def update_wowza_drm_mapfile(
        app_name: str,
        mapfile_type: Literal["buydrm", "verimatrix"],
        mapfile_data: Dict[str, Any]
    ) -> str:
        """
        Updates DRM mapfile configuration.

        Args:
            app_name: Application name
            mapfile_type: Type of DRM mapfile - 'buydrm' or 'verimatrix'
            mapfile_data: DRM mapfile configuration data
        """
        if mapfile_type == "buydrm":
            result = await client.update_buydrm_mapfile(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                data=mapfile_data
            )
        else:
            result = await client.update_verimatrix_mapfile(
                server_name=config["server_name"],
                vhost_name=config["vhost_name"],
                app_name=app_name,
                data=mapfile_data
            )
        return json.dumps(result, indent=2)
