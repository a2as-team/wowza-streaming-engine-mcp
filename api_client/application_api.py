# application_api.py

import aiohttp
import logging
from typing import Dict, Optional, List, Any
from urllib.parse import urlparse, urlunparse

class WowzaApplicationApiClient:
    """
    Asynchronous API client for interacting with the Wowza Streaming Engine's
    Application-level REST API endpoints.
    """
    def __init__(self, base_url: str, username: Optional[str] = None, password: Optional[str] = None, logger=None):
        """
        Initializes the API client.

        Args:
            base_url (str): The base URL of the Wowza Streaming Engine server,
                            e.g., http://localhost:8087
            username (Optional[str]): The username for digest authentication.
            password (Optional[str]): The password for digest authentication.
            logger (function, optional): A logging function. Defaults to a standard logger.
        """
        self.logger = logger if logger else lambda level, msg: logging.log(getattr(logging, level.upper(), logging.INFO), msg)
        
        # If the URL points to localhost on port 8087 (default HTTP port for Wowza API),
        # force the scheme to be 'http' to prevent SSL errors from a common misconfiguration.
        try:
            parsed_url = urlparse(base_url)
            if parsed_url.hostname in ('localhost', '127.0.0.1') and parsed_url.port == 8087 and parsed_url.scheme == 'https':
                self.logger("warning", f"Overriding scheme for {base_url} to 'http'. Wowza's default API port 8087 uses HTTP, not HTTPS.")
                new_components = parsed_url._replace(scheme='http')
                self.base_url = urlunparse(new_components)
            else:
                self.base_url = base_url
        except Exception:
            # Fallback in case of a malformed URL
            self.base_url = base_url
        
        self.username = username
        self.password = password
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8"
        }
        self.logger("info", f"WowzaApplicationApiClient initialized for base URL: {self.base_url}")

    async def _make_request(self, method: str, url: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """Helper method to perform API requests."""
        try:
            async with aiohttp.ClientSession() as session:
                auth = None
                if self.username and self.password:
                    auth = aiohttp.BasicAuth(self.username, self.password)

                # Filter out None values from params
                if params:
                    params = {k: v for k, v in params.items() if v is not None}

                async with session.request(method, url, headers=self.headers, params=params, json=data, auth=auth) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        self.logger("error", f"API Error {response.status} for {method} {url}")
                        self.logger("error", f"Request data sent: {data}")
                        self.logger("error", f"Response: {error_text}")
                        response.raise_for_status()

                    if response.status == 204 or 'application/json' not in response.headers.get('Content-Type', ''):
                        return {"status": response.status, "message": "Success with no content returned."}

                    return await response.json()
        except aiohttp.ClientError as e:
            self.logger("error", f"API request to {url} failed: {e}")
            raise


    async def get_applications_config(self, server_name: str, vhost_name: str) -> Dict:
        """Retrieves the list of Applications for the specifed vhost."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications"
        return await self._make_request("GET", url)

    async def post_applications_config(self, server_name: str, vhost_name: str, data: Dict) -> Dict:
        """Adds an Application to the list of Applications for the specifed vhost."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications"
        return await self._make_request("POST", url, data=data)

    async def get_application_config(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the specified Application configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}"
        return await self._make_request("GET", url)

    async def post_application_config(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Adds the specified Application configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}"
        return await self._make_request("POST", url, data=data)

    async def put_application_config(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Updates the specified Application configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}"
        return await self._make_request("PUT", url, data=data)

    async def delete_application_config(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Deletes the specified Application configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}"
        return await self._make_request("DELETE", url)
        
    async def get_application_config_adv(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the specified advanced Application configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/adv"
        return await self._make_request("GET", url)

    async def put_application_config_adv(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Updates the specified advanced Application configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/adv"
        return await self._make_request("PUT", url, data=data)


    async def put_application_action(self, server_name: str, vhost_name: str, app_name: str, action: str, dst_entry_name: Optional[str] = None) -> Dict:
        """Performs an action on an application (e.g., copy, restart, shutdown, start)."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/actions/{action}"
        params = {"dstEntryName": dst_entry_name}
        return await self._make_request("PUT", url, params=params)

    
    async def get_stream_files(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the list of Stream Files for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/streamfiles"
        return await self._make_request("GET", url)

    async def add_stream_file(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Adds a Stream File to the list of Stream Files for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/streamfiles"
        return await self._make_request("POST", url, data=data)
        
    async def get_stream_file(self, server_name: str, vhost_name: str, app_name: str, streamfile_name: str) -> Dict:
        """Retrieves the specified Stream File configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/streamfiles/{streamfile_name}"
        return await self._make_request("GET", url)

    async def update_stream_file(self, server_name: str, vhost_name: str, app_name: str, streamfile_name: str, data: Dict) -> Dict:
        """Updates the specified Stream File configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/streamfiles/{streamfile_name}"
        return await self._make_request("PUT", url, data=data)

    async def remove_stream_file(self, server_name: str, vhost_name: str, app_name: str, streamfile_name: str) -> Dict:
        """Deletes the specified Stream File configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/streamfiles/{streamfile_name}"
        return await self._make_request("DELETE", url)
        
    async def connect_stream_file(self, server_name: str, vhost_name: str, app_name: str, streamfile_name: str, media_caster_type: str, connect_app_name: Optional[str] = None, app_instance: Optional[str] = None) -> Dict:
        """Connects a stream file to start media casting."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/streamfiles/{streamfile_name}/actions/connect"
        params = {
            "connectAppName": connect_app_name,
            "appInstance": app_instance,
            "mediaCasterType": media_caster_type
        }
        return await self._make_request("PUT", url, params=params)


    async def get_recorders(self, server_name: str, vhost_name: str, app_name: str, instance_name: str) -> Dict:
        """Retrieves the list of Stream Recorders for the specified Application Instance."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/streamrecorders"
        return await self._make_request("GET", url)

    async def create_recorder(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, data: Dict) -> Dict:
        """Creates a new Stream Recorder and starts recording."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/streamrecorders"
        return await self._make_request("POST", url, data=data)
        
    async def get_recorder(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, recorder_name: str) -> Dict:
        """Retrieves the specifed Stream Recorder."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/streamrecorders/{recorder_name}"
        return await self._make_request("GET", url)
        
    async def put_recorder_action(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, recorder_name: str, action: str) -> Dict:
        """Performs an action on a stream recorder (splitRecording, stopRecording)."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/streamrecorders/{recorder_name}/actions/{action}"
        return await self._make_request("PUT", url)


    async def get_smil_files(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the list of SMIL Files for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/smilfiles"
        return await self._make_request("GET", url)

    async def add_smil_file(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Adds a SMIL File to the list of SMIL Files for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/smilfiles"
        return await self._make_request("POST", url, data=data)

    async def get_smil_file(self, server_name: str, vhost_name: str, app_name: str, smilfile_name: str) -> Dict:
        """Retrieves the specified SMIL File configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/smilfiles/{smilfile_name}"
        return await self._make_request("GET", url)

    async def delete_smil_file(self, server_name: str, vhost_name: str, app_name: str, smilfile_name: str) -> Dict:
        """Deletes the specified SMIL File configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/smilfiles/{smilfile_name}"
        return await self._make_request("DELETE", url)
    

    async def get_security_config(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the Security configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/security"
        return await self._make_request("GET", url)

    async def put_security_config(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Updates the Security configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/security"
        return await self._make_request("PUT", url, data=data)

    async def get_dvr_config(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the DVR configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/dvr"
        return await self._make_request("GET", url)

    async def put_dvr_config(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Updates the DVR configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/dvr"
        return await self._make_request("PUT", url, data=data)

    async def get_drm_config(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the DRM configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/drm"
        return await self._make_request("GET", url)

    async def put_drm_config(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Updates the DRM configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/drm"
        return await self._make_request("PUT", url, data=data)
        
    async def get_transcoder_config(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the Transcoder configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder"
        return await self._make_request("GET", url)

    async def put_transcoder_config(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Updates the Transcoder configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder"
        return await self._make_request("PUT", url, data=data)

    
    async def get_application_current_stats(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the current Application statistics."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/monitoring/current"
        return await self._make_request("GET", url)

    async def get_application_historic_stats(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the historic Application statistics."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/monitoring/historic"
        return await self._make_request("GET", url)
        
    async def get_incoming_stream_current_stats(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, stream_name: str) -> Dict:
        """Retrieves the Current Incoming Stream statistics for the specifed Incoming Stream."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/incomingstreams/{stream_name}/monitoring/current"
        return await self._make_request("GET", url)


    async def get_instances(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the list of Instances for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances"
        return await self._make_request("GET", url)

    async def get_instance(self, server_name: str, vhost_name: str, app_name: str, instance_name: str) -> Dict:
        """Retrieves the specified Application Instance information."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}"
        return await self._make_request("GET", url)

    async def put_instance_action(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, action: str) -> Dict:
        """Performs an action on an application instance (currently only 'start' is supported)."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/actions/{action}"
        return await self._make_request("PUT", url)


    async def get_dvr_config_adv(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the advanced DVR configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/dvr/adv"
        return await self._make_request("GET", url)

    async def put_dvr_config_adv(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Updates the advanced DVR configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/dvr/adv"
        return await self._make_request("PUT", url, data=data)

    async def get_drm_config_adv(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the advanced DRM configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/drm/adv"
        return await self._make_request("GET", url)

    async def put_drm_config_adv(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Updates the advanced DRM configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/drm/adv"
        return await self._make_request("PUT", url, data=data)

    async def get_buydrm_stream_maps(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the BuyDRM stream mapfile for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/drm/buydrmmapfile"
        return await self._make_request("GET", url)

    async def put_buydrm_stream_maps(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Updates the BuyDRM stream mapfile for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/drm/buydrmmapfile"
        return await self._make_request("PUT", url, data=data)

    async def get_verimatrix_stream_maps(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the Verimatrix stream mapfile for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/drm/verimatrixmapfile"
        return await self._make_request("GET", url)

    async def put_verimatrix_stream_maps(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Updates the Verimatrix stream mapfile for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/drm/verimatrixmapfile"
        return await self._make_request("PUT", url, data=data)


    async def get_webrtc_config(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the WebRTC configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/webrtc"
        return await self._make_request("GET", url)

    async def put_webrtc_config(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Updates the WebRTC configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/webrtc"
        return await self._make_request("PUT", url, data=data)

    async def get_webrtc_config_adv(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the advanced WebRTC configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/webrtc/adv"
        return await self._make_request("GET", url)

    async def put_webrtc_config_adv(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Updates the advanced WebRTC configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/webrtc/adv"
        return await self._make_request("PUT", url, data=data)


    async def get_modules_config(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the list of Modules for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/modules"
        return await self._make_request("GET", url)

    async def put_modules_config(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Updates the list of Modules for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/modules"
        return await self._make_request("PUT", url, data=data)


    async def get_streamconfiguration_config(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the Stream configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/streamconfiguration"
        return await self._make_request("GET", url)

    async def put_streamconfiguration_config(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Updates the Stream configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/streamconfiguration"
        return await self._make_request("PUT", url, data=data)


    async def get_transcoder_config_adv(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the Advanced Transcoder configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/adv"
        return await self._make_request("GET", url)

    async def put_transcoder_config_adv(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Updates the Advanced Transcoder configuration for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/adv"
        return await self._make_request("PUT", url, data=data)


    async def get_stream_file_adv(self, server_name: str, vhost_name: str, app_name: str, streamfile_name: str) -> Dict:
        """Retrieves the Advanced Stream File configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/streamfiles/{streamfile_name}/adv"
        return await self._make_request("GET", url)

    async def put_stream_file_adv(self, server_name: str, vhost_name: str, app_name: str, streamfile_name: str, data: Dict) -> Dict:
        """Updates the Advanced Stream File configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/streamfiles/{streamfile_name}/adv"
        return await self._make_request("PUT", url, data=data)


    async def get_transcoder_templates(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the list of Transcoder Template Configurations for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates"
        return await self._make_request("GET", url)

    async def get_transcoder_template(self, server_name: str, vhost_name: str, app_name: str, template_name: str) -> Dict:
        """Retrieves the specified Transcoder Template configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}"
        return await self._make_request("GET", url)

    async def get_transcoder_template_adv(self, server_name: str, vhost_name: str, app_name: str, template_name: str) -> Dict:
        """Retrieves the Advanced Transcoder Template configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/adv"
        return await self._make_request("GET", url)

    async def create_transcoder_template(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Adds a Transcoder Templates Configuration to the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates"
        return await self._make_request("POST", url, data=data)

    async def update_transcoder_template(self, server_name: str, vhost_name: str, app_name: str, template_name: str, data: Dict) -> Dict:
        """Updates the specified Transcoder Template configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}"
        return await self._make_request("PUT", url, data=data)

    async def update_transcoder_template_adv(self, server_name: str, vhost_name: str, app_name: str, template_name: str, data: Dict) -> Dict:
        """Updates the Advanced Transcoder Template configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/adv"
        return await self._make_request("PUT", url, data=data)

    async def delete_transcoder_template(self, server_name: str, vhost_name: str, app_name: str, template_name: str) -> Dict:
        """Deletes the specified Transcoder Template configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}"
        return await self._make_request("DELETE", url)

    async def transcoder_template_action(self, server_name: str, vhost_name: str, app_name: str, template_name: str, action: str) -> Dict:
        """Performs an action on a transcoder template."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/actions/{action}"
        return await self._make_request("PUT", url)


    async def get_transcoder_encodes(self, server_name: str, vhost_name: str, app_name: str, template_name: str) -> Dict:
        """Retrieves the list of Transcoder Encode Configurations."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/encodes"
        return await self._make_request("GET", url)

    async def get_transcoder_encode(self, server_name: str, vhost_name: str, app_name: str, template_name: str, encode_name: str) -> Dict:
        """Retrieves the specified Transcoder Encode configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/encodes/{encode_name}"
        return await self._make_request("GET", url)

    async def get_transcoder_encode_adv(self, server_name: str, vhost_name: str, app_name: str, template_name: str, encode_name: str) -> Dict:
        """Retrieves the Advanced Transcoder Encode configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/encodes/{encode_name}/adv"
        return await self._make_request("GET", url)

    async def create_transcoder_encode(self, server_name: str, vhost_name: str, app_name: str, template_name: str, data: Dict) -> Dict:
        """Adds a Transcoder Encode Configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/encodes"
        return await self._make_request("POST", url, data=data)

    async def update_transcoder_encode(self, server_name: str, vhost_name: str, app_name: str, template_name: str, encode_name: str, data: Dict) -> Dict:
        """Updates the specified Transcoder Encode configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/encodes/{encode_name}"
        return await self._make_request("PUT", url, data=data)

    async def update_transcoder_encode_adv(self, server_name: str, vhost_name: str, app_name: str, template_name: str, encode_name: str, data: Dict) -> Dict:
        """Updates the Advanced Transcoder Encode configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/encodes/{encode_name}/adv"
        return await self._make_request("PUT", url, data=data)

    async def delete_transcoder_encode(self, server_name: str, vhost_name: str, app_name: str, template_name: str, encode_name: str) -> Dict:
        """Deletes the specified Transcoder Encode configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/encodes/{encode_name}"
        return await self._make_request("DELETE", url)


    async def get_transcoder_overlay_decode(self, server_name: str, vhost_name: str, app_name: str, template_name: str, overlay_name: str) -> Dict:
        """Retrieves the specified Transcoder Overlay Decode configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/decode/overlays/{overlay_name}"
        return await self._make_request("GET", url)

    async def update_transcoder_overlay_decode(self, server_name: str, vhost_name: str, app_name: str, template_name: str, overlay_name: str, data: Dict) -> Dict:
        """Updates the specified Transcoder Overlay Decode configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/decode/overlays/{overlay_name}"
        return await self._make_request("PUT", url, data=data)

    async def delete_transcoder_overlay_decode(self, server_name: str, vhost_name: str, app_name: str, template_name: str, overlay_name: str) -> Dict:
        """Deletes the specified Transcoder Overlay Decode configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/decode/overlays/{overlay_name}"
        return await self._make_request("DELETE", url)

    async def get_transcoder_overlay_encode(self, server_name: str, vhost_name: str, app_name: str, template_name: str, encode_name: str, overlay_name: str) -> Dict:
        """Retrieves the specified Transcoder Overlay Encode configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/encodes/{encode_name}/overlays/{overlay_name}"
        return await self._make_request("GET", url)

    async def update_transcoder_overlay_encode(self, server_name: str, vhost_name: str, app_name: str, template_name: str, encode_name: str, overlay_name: str, data: Dict) -> Dict:
        """Updates the specified Transcoder Overlay Encode configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/encodes/{encode_name}/overlays/{overlay_name}"
        return await self._make_request("PUT", url, data=data)

    async def delete_transcoder_overlay_encode(self, server_name: str, vhost_name: str, app_name: str, template_name: str, encode_name: str, overlay_name: str) -> Dict:
        """Deletes the specified Transcoder Overlay Encode configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/encodes/{encode_name}/overlays/{overlay_name}"
        return await self._make_request("DELETE", url)


    async def get_transcoder_streamname_groups(self, server_name: str, vhost_name: str, app_name: str, template_name: str) -> Dict:
        """Retrieves the list of Transcoder Stream Name Groups for the specified Template."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/streamnamegroups"
        return await self._make_request("GET", url)

    async def get_transcoder_streamname_group(self, server_name: str, vhost_name: str, app_name: str, template_name: str, group_name: str) -> Dict:
        """Retrieves the specified Transcoder StreamNameGroup configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/streamnamegroups/{group_name}"
        return await self._make_request("GET", url)

    async def create_transcoder_streamname_group(self, server_name: str, vhost_name: str, app_name: str, template_name: str, data: Dict) -> Dict:
        """Adds a Transcoder Stream Name Groups Configuration to the specified Template."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/streamnamegroups"
        return await self._make_request("POST", url, data=data)

    async def update_transcoder_streamname_group(self, server_name: str, vhost_name: str, app_name: str, template_name: str, group_name: str, data: Dict) -> Dict:
        """Updates the specified Transcoder StreamNameGroup configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/streamnamegroups/{group_name}"
        return await self._make_request("PUT", url, data=data)

    async def delete_transcoder_streamname_group(self, server_name: str, vhost_name: str, app_name: str, template_name: str, group_name: str) -> Dict:
        """Deletes the specified Transcoder StreamNameGroup configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/transcoder/templates/{template_name}/streamnamegroups/{group_name}"
        return await self._make_request("DELETE", url)

    # Publishers API methods
    async def get_publishers(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the list of Publishers for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/publishers"
        return await self._make_request("GET", url)

    async def get_publisher(self, server_name: str, vhost_name: str, app_name: str, publisher_name: str) -> Dict:
        """Retrieves the specified Publisher configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/publishers/{publisher_name}"
        return await self._make_request("GET", url)

    async def create_publisher(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Add a Publisher to list of Publishers for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/publishers"
        return await self._make_request("POST", url, data=data)

    async def add_publisher(self, server_name: str, vhost_name: str, app_name: str, publisher_name: str, data: Dict) -> Dict:
        """Adds the specified Publisher configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/publishers/{publisher_name}"
        return await self._make_request("POST", url, data=data)

    async def update_publisher(self, server_name: str, vhost_name: str, app_name: str, publisher_name: str, data: Dict) -> Dict:
        """Updates the specified Publisher configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/publishers/{publisher_name}"
        return await self._make_request("PUT", url, data=data)

    async def delete_publisher(self, server_name: str, vhost_name: str, app_name: str, publisher_name: str) -> Dict:
        """Deletes the specified Publisher configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/publishers/{publisher_name}"
        return await self._make_request("DELETE", url)

    # Push Publish API methods
    async def get_push_publish_entries(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the list of PushPublish map entries for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/pushpublish/mapentries"
        return await self._make_request("GET", url)

    async def get_push_publish_entry(self, server_name: str, vhost_name: str, app_name: str, entry_name: str) -> Dict:
        """Retrieves the specified PushPublish map entry's configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/pushpublish/mapentries/{entry_name}"
        return await self._make_request("GET", url)

    async def create_push_publish_entry(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Adds a PushPublish map entry to list of PushPublish map entries."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/pushpublish/mapentries"
        return await self._make_request("POST", url, data=data)

    async def add_push_publish_entry(self, server_name: str, vhost_name: str, app_name: str, entry_name: str, data: Dict) -> Dict:
        """Adds the specified PushPublish map entry."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/pushpublish/mapentries/{entry_name}"
        return await self._make_request("POST", url, data=data)

    async def update_push_publish_entry(self, server_name: str, vhost_name: str, app_name: str, entry_name: str, data: Dict) -> Dict:
        """Updates the specified PushPublish map entry's configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/pushpublish/mapentries/{entry_name}"
        return await self._make_request("PUT", url, data=data)

    async def update_push_publish_entries(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Updates the list of PushPublish map entries."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/pushpublish/mapentries"
        return await self._make_request("PUT", url, data=data)

    async def delete_push_publish_entry(self, server_name: str, vhost_name: str, app_name: str, entry_name: str) -> Dict:
        """Deletes the specified PushPublish map entry."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/pushpublish/mapentries/{entry_name}"
        return await self._make_request("DELETE", url)

    async def push_publish_entry_action(self, server_name: str, vhost_name: str, app_name: str, entry_name: str, action: str, dst_entry_name: Optional[str] = None) -> Dict:
        """Performs an action on the specified PushPublish map entry."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/pushpublish/mapentries/{entry_name}/actions/{action}"
        params = {"dstEntryName": dst_entry_name} if dst_entry_name else None
        return await self._make_request("PUT", url, params=params)

    async def get_push_publish_providers(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves a list of PushPublish Cloud Storage Providers."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/pushpublish/providers"
        return await self._make_request("GET", url)

    # SMIL Files API methods
    async def get_smil_files(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the list of SMIL Files for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/smilfiles"
        return await self._make_request("GET", url)

    async def get_smil_file(self, server_name: str, vhost_name: str, app_name: str, smil_file_name: str) -> Dict:
        """Retrieves the specified SMIL File configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/smilfiles/{smil_file_name}"
        return await self._make_request("GET", url)

    async def create_smil_file(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Adds a SMIL File to the list of SMIL Files."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/smilfiles"
        return await self._make_request("POST", url, data=data)

    async def add_smil_file(self, server_name: str, vhost_name: str, app_name: str, smil_file_name: str, data: Dict) -> Dict:
        """Adds the specified SMIL File configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/smilfiles/{smil_file_name}"
        return await self._make_request("POST", url, data=data)

    async def update_smil_file(self, server_name: str, vhost_name: str, app_name: str, smil_file_name: str, data: Dict) -> Dict:
        """Updates the specified SMIL File configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/smilfiles/{smil_file_name}"
        return await self._make_request("PUT", url, data=data)

    async def delete_smil_file(self, server_name: str, vhost_name: str, app_name: str, smil_file_name: str) -> Dict:
        """Deletes the specified SMIL File configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/smilfiles/{smil_file_name}"
        return await self._make_request("DELETE", url)

    async def smil_file_action(self, server_name: str, vhost_name: str, app_name: str, smil_file_name: str, action: str) -> Dict:
        """Performs an action on the specified SMIL File."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/smilfiles/{smil_file_name}/actions/{action}"
        return await self._make_request("PUT", url)

    # SDP Files API methods
    async def get_sdp_files(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the list of SDP Files for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/sdpfiles"
        return await self._make_request("GET", url)

    async def delete_sdp_file(self, server_name: str, vhost_name: str, app_name: str, sdp_file_name: str) -> Dict:
        """Deletes the specified SDP file."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/sdpfiles/{sdp_file_name}"
        return await self._make_request("DELETE", url)

    async def sdp_file_action(self, server_name: str, vhost_name: str, app_name: str, sdp_file_name: str, action: str) -> Dict:
        """Performs an action on the specified SDP file."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/sdpfiles/{sdp_file_name}/actions/{action}"
        return await self._make_request("PUT", url)

    # Stream Recorders API methods
    async def get_stream_recorders(self, server_name: str, vhost_name: str, app_name: str, instance_name: str) -> Dict:
        """Retrieves the list of Stream Recorders for the specified Application Instance."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/streamrecorders"
        return await self._make_request("GET", url)

    async def get_stream_recorder(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, recorder_name: str) -> Dict:
        """Retrieves the specified Stream Recorder."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/streamrecorders/{recorder_name}"
        return await self._make_request("GET", url)

    async def get_default_stream_recorder(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, recorder_name: str) -> Dict:
        """Retrieves a Stream Recorder of the requested name, populated with the default values."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/streamrecorders/{recorder_name}/default"
        return await self._make_request("GET", url)

    async def create_stream_recorder(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, data: Dict) -> Dict:
        """Creates a new Stream Recorder in the specified Application Instance and starts recording."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/streamrecorders"
        return await self._make_request("POST", url, data=data)

    async def add_stream_recorder(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, recorder_name: str, data: Dict) -> Dict:
        """Creates a new Stream Recorder and starts recording."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/streamrecorders/{recorder_name}"
        return await self._make_request("POST", url, data=data)

    async def stream_recorder_action(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, recorder_name: str, action: str) -> Dict:
        """Performs an action on the specified Stream Recorder."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/streamrecorders/{recorder_name}/actions/{action}"
        return await self._make_request("PUT", url)

    # Incoming Streams API methods
    async def get_incoming_stream(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, stream_name: str) -> Dict:
        """Retrieves the Incoming Stream information for the specified Incoming Stream."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/incomingstreams/{stream_name}"
        return await self._make_request("GET", url)

    async def get_incoming_stream_stats(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, stream_name: str) -> Dict:
        """Retrieves the Current Incoming Stream statistics for the specified Incoming Stream."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/incomingstreams/{stream_name}/monitoring/current"
        return await self._make_request("GET", url)

    async def get_live_encoder_config(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, stream_name: str) -> Dict:
        """Retrieves the LiveEncoder configuration for the specified IncomingStream."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/incomingstreams/{stream_name}/encoder/live"
        return await self._make_request("GET", url)

    async def get_encoder_short_url(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, stream_name: str) -> Dict:
        """Retrieves the Short URL for the LiveEncoder configuration for the specified IncomingStream."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/incomingstreams/{stream_name}/encoder/shorturl"
        return await self._make_request("GET", url)

    async def get_source_control(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, stream_name: str) -> Dict:
        """Gets information about the Source Control and its supported features."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/incomingstreams/{stream_name}/sourcecontrol"
        return await self._make_request("GET", url)

    async def incoming_stream_action(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, stream_name: str, action: str) -> Dict:
        """Performs an action on the specified Incoming Stream."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/incomingstreams/{stream_name}/actions/{action}"
        return await self._make_request("PUT", url)

    async def source_control_action(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, stream_name: str, action: str) -> Dict:
        """Performs a source control action on the specified Incoming Stream."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/incomingstreams/{stream_name}/sourcecontrol/actions/{action}"
        return await self._make_request("PUT", url)

    # DVR Stores API methods
    async def get_dvr_stores(self, server_name: str, vhost_name: str, app_name: str, instance_name: str) -> Dict:
        """Retrieves the list of DVR stores associated with this application instance."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/dvrstores"
        return await self._make_request("GET", url)

    async def get_dvr_store(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, store_name: str) -> Dict:
        """Retrieves the information about a store/converter associated with the application instance."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/dvrstores/{store_name}"
        return await self._make_request("GET", url)

    async def dvr_stores_action(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, action: str) -> Dict:
        """Performs an action on all DVR stores."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/dvrstores/actions/{action}"
        return await self._make_request("PUT", url)

    async def dvr_store_action(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, store_name: str, action: str) -> Dict:
        """Performs an action on the specified DVR store."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/dvrstores/{store_name}/actions/{action}"
        return await self._make_request("PUT", url)

    # Stream Groups API methods
    async def get_stream_groups(self, server_name: str, vhost_name: str, app_name: str, instance_name: str) -> Dict:
        """Retrieves the list of Stream Groups for the specified Application Instance."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/streamgroups"
        return await self._make_request("GET", url)

    async def get_stream_group(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, group_name: str) -> Dict:
        """Retrieves the specified StreamGroup configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/streamgroups/{group_name}"
        return await self._make_request("GET", url)

    async def stream_group_action(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, group_name: str, action: str) -> Dict:
        """Performs an action on the specified Stream Group."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/streamgroups/{group_name}/actions/{action}"
        return await self._make_request("PUT", url)

    # DRM Mapfiles API methods
    async def get_buydrm_mapfile(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the BuyDRM stream mapfile for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/drm/buydrmmapfile"
        return await self._make_request("GET", url)

    async def update_buydrm_mapfile(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Updates the BuyDRM stream mapfile for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/drm/buydrmmapfile"
        return await self._make_request("PUT", url, data=data)

    async def get_verimatrix_mapfile(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Retrieves the Verimatrix stream mapfile for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/drm/verimatrixmapfile"
        return await self._make_request("GET", url)

    async def update_verimatrix_mapfile(self, server_name: str, vhost_name: str, app_name: str, data: Dict) -> Dict:
        """Updates the Verimatrix stream mapfile for the specified Application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/drm/verimatrixmapfile"
        return await self._make_request("PUT", url, data=data)