from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


class ApplicationSecurityConfig(BaseModel):
	"""Application security configuration. All fields optional.

	Allows extra keys for forward compatibility with Wowza.
	"""

	model_config = ConfigDict(extra="allow")

	playMaximumConnections: Optional[int] = None
	publishBlockDuplicateStreamNames: Optional[bool] = None
	publishIPWhiteList: Optional[str] = None
	playAuthenticationMethod: Optional[str] = None
	clientStreamWriteAccess: Optional[str] = None
	playIPWhiteList: Optional[str] = None
	publishRequirePassword: Optional[bool] = None
	playIPBlackList: Optional[str] = None
	secureTokenVersion: Optional[int] = None
	publishPasswordFile: Optional[str] = None
	publishValidEncoders: Optional[str] = None
	secureTokenQueryParametersPrefix: Optional[str] = None
	secureTokenUseTEAForRTMP: Optional[bool] = None
	publishAuthenticationMethod: Optional[str] = None
	secureTokenHashAlgorithm: Optional[str] = None
	publishIPBlackList: Optional[str] = None
	playRequireSecureConnection: Optional[bool] = None
	secureTokenOriginSharedSecret: Optional[str] = None
	secureTokenIncludeClientIPInHash: Optional[bool] = None
	publishRTMPSecureURL: Optional[str] = None
	secureTokenSharedSecret: Optional[str] = None


class ApplicationDvrConfig(BaseModel):
    """Application DVR configuration. All fields optional.

    Allows extra keys for forward compatibility with Wowza.
    """

    model_config = ConfigDict(extra="allow")

    # Optionals
    dvrEnable: Optional[bool] = None  # Corrected type to boolean

    # Optionals
    recorders: Optional[str] = None
    store: Optional[str] = None
    windowDuration: Optional[int] = None
    storageDir: Optional[str] = None
    archiveStrategy: Optional[str] = None
    dvrOnlyStreaming: Optional[bool] = None
    startRecordingOnStartup: Optional[bool] = None
    dvrEncryptionSharedSecret: Optional[str] = None
    dvrMediaCacheEnabled: Optional[bool] = None
    httpRandomizeMediaName: Optional[bool] = None
    licenseType: Optional[str] = None
    inUse: Optional[bool] = None


class ApplicationDrmConfig(BaseModel):
	"""Application DRM configuration. All fields optional; structured per Wowza examples."""

	model_config = ConfigDict(extra="allow")

	licenseType: Optional[str] = None
	inUse: Optional[bool] = None
	ezDRMUsername: Optional[str] = None
	ezDRMPassword: Optional[str] = None
	buyDRMUserKey: Optional[str] = None
	buyDRMProtectSmoothStreaming: Optional[bool] = None
	buyDRMProtectCupertinoStreaming: Optional[bool] = None
	buyDRMProtectMpegDashStreaming: Optional[bool] = None
	verimatrixProtectCupertinoStreaming: Optional[bool] = None
	verimatrixCupertinoKeyServerIpAddress: Optional[str] = None
	verimatrixCupertinoKeyServerPort: Optional[int] = None
	verimatrixCupertinoVODPerSessionKeys: Optional[bool] = None
	verimatrixProtectSmoothStreaming: Optional[bool] = None
	verimatrixSmoothKeyServerIpAddress: Optional[str] = None
	verimatrixSmoothKeyServerPort: Optional[int] = None
	cupertinoEncryptionAPIBased: Optional[bool] = None

	class BuyDrmStreamMaps(BaseModel):
		model_config = ConfigDict(extra="allow")
		buyDRMStreamNameMapFile: Optional[str] = None
		buyDRMStreamMaps: Optional[List[Any]] = None

	class VerimatrixStreamMaps(BaseModel):
		model_config = ConfigDict(extra="allow")
		filename: Optional[str] = None
		verimatrixStreamMaps: Optional[List[Any]] = None

	buyDRMStreamMaps: Optional[BuyDrmStreamMaps] = None
	verimatrixStreamMaps: Optional[VerimatrixStreamMaps] = None


class ApplicationTranscoderConfig(BaseModel):
    """Application Transcoder configuration. `liveStreamTranscoder` is required; others optional."""

    model_config = ConfigDict(extra="allow")

    # Required
    liveStreamTranscoder: Literal["transcoder", "(none)"] = Field(
        ...,
        description="REQUIRED: Live stream transcoder setting. Must be exactly 'transcoder' to enable transcoding or '(none)' to disable transcoding.",
        examples=["transcoder", "(none)"]
    )

    # Optionals
    templatesInUse: Optional[str] = None
    profileDir: Optional[str] = None
    templateDir: Optional[str] = None
    createTemplateDir: Optional[bool] = None
    licensed: Optional[bool] = None
    available: Optional[bool] = None
    licenses: Optional[int] = None
    licensesInUse: Optional[int] = None

    class TemplateRef(BaseModel):
        id: Optional[str] = None
        href: Optional[str] = None

    class Templates(BaseModel):
        vhostName: Optional[str] = None
        templates: Optional[List['ApplicationTranscoderConfig.TemplateRef']] = None

    templates: Optional[Templates] = None



class StreamConfig(BaseModel):
	"""Application stream configuration."""

	model_config = ConfigDict(extra="allow")

	streamType: Optional[str] = None
	storageDir: Optional[str] = None
	createStorageDir: Optional[bool] = None
	httpRandomizeMediaName: Optional[bool] = None
	liveStreamPacketizer: Optional[List[str]] = None


class WebRTCConfig(BaseModel):
	"""Application WebRTC configuration."""

	model_config = ConfigDict(extra="allow")

	enablePublish: Optional[bool] = None
	enablePlay: Optional[bool] = None
	iceCandidateIpAddresses: Optional[str] = None
	udpBindAddress: Optional[str] = None
	preferredCodecsAudio: Optional[str] = None
	preferredCodecsVideo: Optional[str] = None


class ModuleItem(BaseModel):
	"""Single application module entry."""

	name: str
	description: Optional[str] = None
	class_name: str = Field(..., alias="class", validation_alias="class", serialization_alias="class")
	order: int


class ModulesConfig(BaseModel):
	"""Application modules configuration."""

	moduleList: List[ModuleItem]


# class ApplicationCreate(BaseModel):
# 	"""Create application payload.

# 	- name: required
# 	- appType: required (e.g., "Live", "VOD")
# 	- other blocks optional; extras allowed so full schema can be passed through
# 	"""

# 	model_config = ConfigDict(extra="allow")

# 	name: str = Field(..., description="REQUIRED: Application name. Must be unique on the server.")
# 	appType: str = Field(..., description="REQUIRED: Application type. Common values: 'Live', 'VOD'", examples=["Live", "VOD"])
# 	description: Optional[str] = None
# 	clientStreamReadAccess: Optional[str] = None
# 	clientStreamWriteAccess: Optional[str] = None
# 	httpCORSHeadersEnabled: Optional[bool] = None
# 	repeaterOriginURL: Optional[str] = None
# 	repeaterQueryString: Optional[str] = None
# 	streamConfig: Optional[StreamConfig] = None
# 	dvrConfig: Optional[ApplicationDvrConfig] = None
# 	drmConfig: Optional[ApplicationDrmConfig] = None
# 	transcoderConfig: Optional[ApplicationTranscoderConfig] = None
# 	webRTCConfig: Optional[WebRTCConfig] = None
# 	securityConfig: Optional[ApplicationSecurityConfig] = None
# 	modules: Optional[ModulesConfig] = None
# 	# Additional config blocks may be provided and are allowed via extras



class ApplicationCreate(BaseModel):
    """
    Schema for creating a new Wowza Streaming Engine application.

    Notes:
    - Only `name` is strictly required.
    - `appType` defaults to "Live".
    - All other fields are optional and have safe defaults.
    - `extra="allow"` ensures we can still pass through full schemas if needed.
    """

    model_config = ConfigDict(extra="allow")

    # Required
    name: str = Field(
        ...,
        description="REQUIRED: Application name. Must be unique on the server."
    )

    # Required with default
    appType: str = Field(
        default="Live",
        description="Application type. Defaults to 'Live'. Common values: 'Live', 'VOD'",
        examples=["Live", "VOD"]
    )

    # Optional with defaults
    description: Optional[str] = Field(
        default="Default application created by MCP",
        description="Human-readable description of the application."
    )
    clientStreamReadAccess: Optional[str] = Field(
        default="*",
        description="Who can read client streams (default: *)"
    )
    clientStreamWriteAccess: Optional[str] = Field(
        default="*",
        description="Who can write client streams (default: *)"
    )
    httpCORSHeadersEnabled: Optional[bool] = Field(
        default=True,
        description="Enable CORS headers for HTTP requests (default: true)."
    )

    # Feature toggles (default safe values)
    dvrEnabled: Optional[bool] = Field(
        default=False, description="Enable DVR for the application"
    )
    transcoderEnabled: Optional[bool] = Field(
        default=False, description="Enable transcoder for the application"
    )
    streamRecorderEnabled: Optional[bool] = Field(
        default=False, description="Enable stream recorder for the application"
    )
    webRTCEnabled: Optional[bool] = Field(
        default=False, description="Enable WebRTC support"
    )
    hlsEnabled: Optional[bool] = Field(
        default=True, description="Enable HLS playback (default: true)"
    )
    dashEnabled: Optional[bool] = Field(
        default=False, description="Enable MPEG-DASH playback"
    )
    securityEnabled: Optional[bool] = Field(
        default=False, description="Enable security module (default: false)"
    )


class ApplicationConfig(BaseModel):
    """
    Full Wowza application configuration returned from the API.
    This mirrors the server-side schema more closely.
    """

    model_config = ConfigDict(extra="allow")

    name: str
    appType: str
    description: Optional[str] = None
    clientStreamReadAccess: Optional[str] = None
    clientStreamWriteAccess: Optional[str] = None
    httpCORSHeadersEnabled: Optional[bool] = None

    dvrEnabled: Optional[bool] = None
    transcoderEnabled: Optional[bool] = None
    streamRecorderEnabled: Optional[bool] = None
    webRTCEnabled: Optional[bool] = None
    hlsEnabled: Optional[bool] = None
    dashEnabled: Optional[bool] = None
    securityEnabled: Optional[bool] = None



class ApplicationUpdate(BaseModel):
	"""Update application payload. All fields optional; extras allowed."""

	model_config = ConfigDict(extra="allow")

	name: Optional[str] = None
	appType: Optional[str] = None
	description: Optional[str] = None
	clientStreamReadAccess: Optional[str] = None
	clientStreamWriteAccess: Optional[str] = None
	httpCORSHeadersEnabled: Optional[bool] = None
	repeaterOriginURL: Optional[str] = None
	repeaterQueryString: Optional[str] = None
	streamConfig: Optional[StreamConfig] = None
	dvrConfig: Optional[ApplicationDvrConfig] = None
	drmConfig: Optional[ApplicationDrmConfig] = None
	transcoderConfig: Optional[ApplicationTranscoderConfig] = None
	webRTCConfig: Optional[WebRTCConfig] = None
	securityConfig: Optional[ApplicationSecurityConfig] = None
	modules: Optional[ModulesConfig] = None


class ApplicationAdvancedUpdate(BaseModel):
	"""Advanced application update (modules, custom properties). Flexible and optional."""

	model_config = ConfigDict(extra="allow")


class StreamFileCreate(BaseModel):
	"""Create a .stream file payload."""

	name: str
	uri: str
	sourceControlUserName: Optional[str] = None
	sourceControlPassword: Optional[str] = None
	sourceControlDriver: Optional[str] = None


class ServerLicensesUpdate(BaseModel):
	"""Server licenses update.

	Accepts input as `licenses` but serializes to Wowza's expected `licenseList`.
	"""

	license_list: List[str] = Field(
		..., validation_alias="licenses", serialization_alias="licenseList"
	)


class ServerListener(BaseModel):
	"""Single server listener entry."""

	order: int
	baseClass: str


class ServerListenersUpdate(BaseModel):
	"""Server listeners update wrapper.

	Serializes to Wowza's `serverListeners` list.
	"""

	server_listeners: List[ServerListener] = Field(
		..., alias="serverListeners", validation_alias="server_listeners"
	)


class MediaCacheSourceCreate(BaseModel):
	"""Media Cache Source (v3) create/update payload."""

	model_config = ConfigDict(extra="allow")

	type: str
	basePath: str
	prefix: str
	description: Optional[str] = None
	minTimeToLive: Optional[int] = None
	maxTimeToLive: Optional[int] = None
	isAmazonS3: Optional[bool] = None
	s3BucketNameInDomain: Optional[bool] = None
	awsAccessKeyId: Optional[str] = None
	awsSecretAccessKey: Optional[str] = None
	isPassThru: Optional[bool] = None
	baseClass: Optional[str] = None
	readerClass: Optional[str] = None
	httpReaderFactoryClass: Optional[str] = None
	azureAccountName: Optional[str] = None
	azureContainerName: Optional[str] = None
	azureAccountKey: Optional[str] = None
	googleServiceID: Optional[str] = None
	googleServiceKey: Optional[str] = None
	googleServicePrivateKeyFile: Optional[str] = None
	googleServicePrivateKeyPassword: Optional[str] = None
	googleEncMethod: Optional[str] = None


class MediaCacheStoreCreate(BaseModel):
	"""Media Cache Store (v3) create/update payload."""

	model_config = ConfigDict(extra="allow")

	path: str
	maxSize: str
	description: Optional[str] = None
	writeRate: Optional[str] = None
	writeRateMaxBucketSize: Optional[str] = None


class MediaCacheConfigUpdate(BaseModel):
	"""Media Cache global config (v3) update payload. Flexible and optional."""

	model_config = ConfigDict(extra="allow")


class SmilFileCreate(BaseModel):
	"""SMIL file creation payload."""

	name: str = Field(..., description="SMIL file name (without .smil extension)")
	contents: str = Field(..., description="SMIL file XML contents")
	description: Optional[str] = Field(None, description="Optional description of the SMIL file")


class BuyDRMStreamMap(BaseModel):
	"""Single BuyDRM stream mapping entry."""

	model_config = ConfigDict(extra="allow")

	streamName: str = Field(..., description="Stream name to protect")
	contentId: Optional[str] = Field(None, description="Content ID for BuyDRM")
	# Allow additional fields for BuyDRM configuration


class BuyDRMStreamMapsData(BaseModel):
	"""BuyDRM stream maps configuration data."""

	model_config = ConfigDict(extra="allow")

	streamMap: List[BuyDRMStreamMap] = Field(
		...,
		description="List of stream mappings for BuyDRM protection"
	)


class VerimatrixStreamMap(BaseModel):
	"""Single Verimatrix stream mapping entry."""

	model_config = ConfigDict(extra="allow")

	streamName: str = Field(..., description="Stream name to protect")
	assetId: Optional[str] = Field(None, description="Asset ID for Verimatrix")
	# Allow additional fields for Verimatrix configuration


class VerimatrixStreamMapsData(BaseModel):
	"""Verimatrix stream maps configuration data."""

	model_config = ConfigDict(extra="allow")

	streamMap: List[VerimatrixStreamMap] = Field(
		...,
		description="List of stream mappings for Verimatrix protection"
	)


class TranscoderEncodeCreate(BaseModel):
	"""Transcoder encode configuration payload."""

	model_config = ConfigDict(extra="allow")

	name: str = Field(..., description="Encode name (e.g., '480p', '720p')")
	videoCodec: Literal["H.264", "H.265"] = Field(
		"H.264",
		description="Video codec to use for encoding"
	)
	audioCodec: Literal["AAC", "Opus"] = Field(
		"AAC",
		description="Audio codec to use for encoding"
	)
	videoBitrate: Optional[int] = Field(None, description="Video bitrate in kbps")
	audioBitrate: Optional[int] = Field(None, description="Audio bitrate in kbps")
	videoFrameSize: Optional[str] = Field(
		None,
		description="Video frame size (e.g., '1280x720', '1920x1080')"
	)
	videoFramerate: Optional[int] = Field(None, description="Video framerate (fps)")


# ===== User Management Models =====

class UserCreate(BaseModel):
	"""Create/update user payload for Wowza Streaming Engine.

	Based on UserConfig schema from Wowza Swagger. For creating users,
	only userName and password are typically required.
	"""

	model_config = ConfigDict(extra="allow")

	# Required for create
	userName: str = Field(..., description="Username for authentication")
	password: str = Field(..., description="User password")

	# Optional with defaults
	description: Optional[str] = Field(
		default="User created via MCP",
		description="Description of the user"
	)
	groups: List[str] = Field(
		default_factory=lambda: ["admin"],
		description="List of groups the user belongs to. Common: admin, readonly"
	)
	passwordEncoding: Literal["digest", "plaintext"] = Field(
		default="digest",
		description="Password encoding type"
	)
	realm: Optional[str] = Field(
		default="Wowza",
		description="Authentication realm"
	)


class UserUpdate(BaseModel):
	"""Update user payload. All fields optional for updates."""

	model_config = ConfigDict(extra="allow")

	password: Optional[str] = Field(None, description="New password")
	description: Optional[str] = Field(None, description="User description")
	groups: Optional[List[str]] = Field(None, description="User groups")
	passwordEncoding: Optional[Literal["digest", "plaintext"]] = Field(None, description="Password encoding")
	realm: Optional[str] = Field(None, description="Authentication realm")

