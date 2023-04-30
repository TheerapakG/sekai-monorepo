# SPDX-FileCopyrightText: 2022-2023 Erik Chan <erikchan002@gmail.com>
# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from asyncio.locks import Lock
from contextlib import asynccontextmanager
import dataclasses
from functools import wraps
from typing import AsyncIterator, Coroutine, Callable, Optional, TypeVar
from typing_extensions import ParamSpec, Concatenate
from json import load, dump, JSONDecodeError
from pathlib import Path

from aiohttp.abc import AbstractCookieJar

from async_pjsekai.models.master_data import MasterData
from async_pjsekai.models.system_info import SystemInfo
from pjsekai.models.asset_bundle_info import *
from pjsekai.models.game_version import *
from pjsekai.models.information import *
from pjsekai.enums import *
from async_pjsekai.api import API
from async_pjsekai.asset import Asset
from pjsekai.exceptions import *
from pjsekai.utilities import *
from pjsekai.live import *

from .models.converters import msgpack_converter

P = ParamSpec("P")
R = TypeVar("R")


class Client:
    def _auth_required(func: Callable[Concatenate["Client", P], R]) -> Callable[Concatenate["Client", P], R]:  # type: ignore[misc]
        @wraps(func)
        def wrapper_auth_required(
            self: "Client", *args: P.args, **kwargs: P.kwargs
        ) -> R:
            if not self.is_logged_in:
                raise NotAuthenticatedException("Authentication required")
            return func(self, *args, **kwargs)

        return wrapper_auth_required

    def _auto_session_refresh(func: Callable[Concatenate["Client", P], Coroutine[None, None, R]]) -> Callable[Concatenate["Client", P], Coroutine[None, None, R]]:  # type: ignore[misc]
        @wraps(func)
        async def wrapper_auto_session_refresh(
            self: "Client", *args: P.args, **kwargs: P.kwargs
        ) -> R:
            try:
                return await func(self, *args, **kwargs)
            except SessionExpired:
                if self.auto_session_refresh:
                    await self.refresh_signed_cookie()
                    if (
                        self.is_logged_in
                        and self.user_id is not None
                        and self.credential is not None
                    ):
                        await self.login(self.user_id, self.credential)
                    return await func(self, *args, **kwargs)
                raise

        return wrapper_auto_session_refresh

    def _auto_update(func: Callable[Concatenate["Client", P], Coroutine[None, None, R]]) -> Callable[Concatenate["Client", P], Coroutine[None, None, R]]:  # type: ignore[misc]
        async def wrapper_auto_update(
            self: "Client", *args: P.args, **kwargs: P.kwargs
        ) -> R:
            if self.auto_update:
                try:
                    try:
                        return await func(self, *args, **kwargs)
                    except AppUpdateRequired as e:
                        await self.update_app(
                            e.app_version, e.app_hash, e.multi_play_version
                        )
                        await self.update_all()
                        raise
                    except MultipleUpdatesRequired as e:
                        await self.update_asset(e.asset_version, e.asset_hash)
                        await self.update_data(e.data_version, e.app_version_status)
                        raise
                    except AssetUpdateRequired as e:
                        await self.update_asset(e.asset_version, e.asset_hash)
                        raise
                    except DataUpdateRequired as e:
                        await self.update_data(e.data_version, e.app_version_status)
                        raise
                    except UpdateRequired:
                        await self.update_all()
                        raise
                except UpdateRequired:
                    return await func(self, *args, **kwargs)
            return await func(self, *args, **kwargs)

        return wrapper_auto_update

    hca_key: Optional[bytes]
    auto_session_refresh: bool
    auto_update: bool

    _system_info_file_path: Optional[Path]

    @property
    def system_info_file_path(self) -> Optional[Path]:
        return self._system_info_file_path

    _master_data_file_path: Optional[Path]

    @property
    def master_data_file_path(self) -> Optional[Path]:
        return self._master_data_file_path

    _user_data_file_path: Optional[Path]

    @property
    def user_data_file_path(self) -> Optional[Path]:
        return self._user_data_file_path

    _asset_directory: Optional[Path]

    @property
    def asset_directory(self) -> Optional[Path]:
        return self._asset_directory

    _api_manager: API

    @property
    def api_manager(self) -> API:
        return self._api_manager

    _asset: Optional[Asset]

    @property
    def asset(self) -> Optional[Asset]:
        return self._asset

    _user_id: Union[int, str, None]

    @property
    def user_id(self) -> Union[int, str, None]:
        return self._user_id

    _credential: Optional[str]

    @property
    def credential(self) -> Optional[str]:
        return self._credential

    _system_info: SystemInfo
    _system_info_lock: Lock

    @property
    @asynccontextmanager
    async def system_info(self):
        async with self._system_info_lock:
            yield self._system_info

    @system_info.setter
    def system_info(self, new_value: SystemInfo) -> None:
        self._system_info = new_value
        if self.system_info_file_path is not None:
            self.system_info_file_path.parent.mkdir(parents=True, exist_ok=True)
            with self.system_info_file_path.open("wb") as f:
                f.write(msgpack_converter.dumps(new_value, SystemInfo))

    _master_data: MasterData
    _master_data_lock: Lock

    @property
    @asynccontextmanager
    async def master_data(self):
        async with self._master_data_lock:
            yield self._master_data

    @master_data.setter
    def master_data(self, new_value: MasterData) -> None:
        self._master_data = new_value
        if self.master_data_file_path is not None:
            self.master_data_file_path.parent.mkdir(parents=True, exist_ok=True)
            with self.master_data_file_path.open("wb") as f:
                f.write(msgpack_converter.dumps(new_value, MasterData))

    _user_data: dict
    _user_data_lock: Lock

    @property
    @asynccontextmanager
    async def user_data(self):
        async with self._user_data_lock:
            yield self._user_data

    def _update_user_resources(self, response) -> dict:
        self._user_data = {
            **self._user_data,
            **response["updatedResources"],
        }
        if self.user_data_file_path is not None:
            self.user_data_file_path.parent.mkdir(parents=True, exist_ok=True)
            with self.user_data_file_path.open("w") as f:
                dump(self._user_data, f, indent=2, ensure_ascii=False)
        del response["updatedResources"]
        return response

    @property
    @asynccontextmanager
    async def now(self) -> AsyncIterator[Optional[int]]:
        async with self.user_data as user_data:
            yield user_data["now"]

    @property
    @_auth_required
    async def friends(self) -> AsyncIterator[Optional[list[dict]]]:
        async with self.user_data as user_data:
            if "userFriends" not in user_data:
                yield None
            else:
                yield [
                    friend
                    for friend in user_data["userFriends"]
                    if friend["friendStatus"] == "friend"
                ]

    @property
    @_auth_required
    async def received_friend_requests(self) -> AsyncIterator[Optional[list[dict]]]:
        async with self.user_data as user_data:
            if "userFriends" not in user_data:
                yield None
            else:
                yield [
                    friend
                    for friend in user_data["userFriends"]
                    if friend["friendStatus"] == "pending_request"
                ]

    @property
    @_auth_required
    async def sent_friend_requests(self) -> AsyncIterator[Optional[list[dict]]]:
        async with self.user_data as user_data:
            if "userFriends" not in user_data:
                yield None
            else:
                yield [
                    friend
                    for friend in user_data["userFriends"]
                    if friend["friendStatus"] == "sent_request"
                ]

    @property
    def key(self) -> Optional[bytes]:
        return self.api_manager.key

    @key.setter
    def key(self, new_value: Optional[bytes]) -> None:
        self.api_manager.key = new_value

    @property
    def iv(self) -> Optional[bytes]:
        return self.api_manager.iv

    @iv.setter
    def iv(self, new_value: Optional[bytes]) -> None:
        self.api_manager.iv = new_value

    @property
    def jwt_secret(self) -> Optional[str]:
        return self.api_manager.jwt_secret

    @jwt_secret.setter
    def jwt_secret(self, new_value: Optional[str]) -> None:
        self.api_manager.jwt_secret = new_value

    @property
    def platform(self) -> Platform:
        return self.api_manager.platform

    @platform.setter
    def platform(self, new_value) -> None:
        self.api_manager.platform = new_value

    @property
    def game_version(self) -> GameVersion:
        return self.api_manager.game_version

    @game_version.setter
    def game_version(self, new_value) -> None:
        self.api_manager.game_version = new_value

    @property
    def api_domain(self) -> str:
        return self.api_manager.api_domain

    @api_domain.setter
    def api_domain(self, new_value) -> None:
        self.api_manager.api_domain = new_value

    @property
    def asset_bundle_domain(self) -> str:
        return self.api_manager.asset_bundle_domain

    @asset_bundle_domain.setter
    def asset_bundle_domain(self, new_value) -> None:
        self.api_manager.asset_bundle_domain = new_value

    @property
    def asset_bundle_info_domain(self) -> str:
        return self.api_manager.asset_bundle_info_domain

    @asset_bundle_info_domain.setter
    def asset_bundle_info_domain(self, new_value) -> None:
        self.api_manager.asset_bundle_info_domain = new_value

    @property
    def game_version_domain(self) -> str:
        return self.api_manager.game_version_domain

    @game_version_domain.setter
    def game_version_domain(self, new_value) -> None:
        self.api_manager.game_version_domain = new_value

    @property
    def signature_domain(self) -> str:
        return self.api_manager.signature_domain

    @signature_domain.setter
    def signature_domain(self, new_value) -> None:
        self.api_manager.signature_domain = new_value

    @property
    def enable_api_encryption(self) -> bool:
        return self.api_manager.enable_api_encryption

    @enable_api_encryption.setter
    def enable_api_encryption(self, new_value) -> None:
        self.api_manager.enable_api_encryption = new_value

    @property
    def enable_asset_bundle_encryption(self) -> bool:
        return self.api_manager.enable_asset_bundle_encryption

    @enable_asset_bundle_encryption.setter
    def enable_asset_bundle_encryption(self, new_value) -> None:
        self.api_manager.enable_asset_bundle_encryption = new_value

    @property
    def enable_asset_bundle_info_encryption(self) -> bool:
        return self.api_manager.enable_asset_bundle_info_encryption

    @enable_asset_bundle_info_encryption.setter
    def enable_asset_bundle_info_encryption(self, new_value) -> None:
        self.api_manager.enable_asset_bundle_info_encryption = new_value

    @property
    def enable_game_version_encryption(self) -> bool:
        return self.api_manager.enable_game_version_encryption

    @enable_game_version_encryption.setter
    def enable_game_version_encryption(self, new_value) -> None:
        self.api_manager.enable_game_version_encryption = new_value

    @property
    def enable_signature_encryption(self) -> bool:
        return self.api_manager.enable_signature_encryption

    @enable_signature_encryption.setter
    def enable_signature_encryption(self, new_value) -> None:
        self.api_manager.enable_signature_encryption = new_value

    @property
    def is_logged_in(self) -> bool:
        return self.user_id is not None and self.credential is not None

    def __init__(
        self,
        key: Optional[bytes] = None,
        iv: Optional[bytes] = None,
        hca_key: Optional[bytes] = None,
        jwt_secret: Optional[str] = None,
        platform: Platform = Platform.ANDROID,
        system_info_file_path: Optional[str] = None,
        master_data_file_path: Optional[str] = None,
        user_data_file_path: Optional[str] = None,
        asset_directory: Optional[str] = None,
        app_version: Optional[str] = None,
        app_hash: Optional[str] = None,
        multi_play_version: Optional[str] = None,
        api_domain: Optional[str] = None,
        asset_bundle_domain: str = API.DEFAULT_ASSET_BUNDLE_DOMAIN,
        asset_bundle_info_domain: str = API.DEFAULT_ASSET_BUNDLE_INFO_DOMAIN,
        game_version_domain: str = API.DEFAULT_GAME_VERSION_DOMAIN,
        signature_domain: str = API.DEFAULT_SIGNATURE_DOMAIN,
        enable_api_encryption: bool = API.DEFAULT_ENABLE_API_ENCRYPTION,
        enable_asset_bundle_encryption: bool = API.DEFAULT_ENABLE_ASSET_BUNDLE_ENCRYPTION,
        enable_asset_bundle_info_encryption: bool = API.DEFAULT_ENABLE_ASSET_BUNDLE_INFO_ENCRYPTION,
        enable_game_version_encryption: bool = API.DEFAULT_ENABLE_GAME_VERSION_ENCRYPTION,
        enable_signature_encryption: bool = API.DEFAULT_ENABLE_SIGNATURE_ENCRYPTION,
        server_number: Optional[int] = None,
        update_all_on_init: bool = False,
        auto_session_refresh: bool = True,
        auto_update: bool = False,
    ) -> None:
        self.hca_key = hca_key
        self.auto_session_refresh = auto_session_refresh
        self.auto_update = auto_update

        self._system_info_file_path = None
        self._master_data_file_path = None
        self._user_data_file_path = None
        self._asset_directory = None
        if system_info_file_path is not None:
            self._system_info_file_path = Path(system_info_file_path)
        if master_data_file_path is not None:
            self._master_data_file_path = Path(master_data_file_path)
        if user_data_file_path is not None:
            self._user_data_file_path = Path(user_data_file_path)
        if asset_directory is not None:
            self._asset_directory = Path(asset_directory)
        self._asset = None

        self._system_info_lock = Lock()

        if self.system_info_file_path is not None:
            try:
                with self.system_info_file_path.open("rb") as f:
                    self._system_info = msgpack_converter.loads(f.read(), SystemInfo)
            except FileNotFoundError:
                self.system_info = SystemInfo.create()
        else:
            self.system_info = SystemInfo.create()
        if app_version is not None and app_hash is not None:
            self.system_info = dataclasses.replace(
                self._system_info,
                app_version=app_version,
                app_hash=app_hash,
                multi_play_version=multi_play_version,
            )

        self._master_data_lock = Lock()

        if self.master_data_file_path is not None:
            try:
                with self.master_data_file_path.open("rb") as f:
                    self._master_data = msgpack_converter.loads(f.read(), MasterData)
            except FileNotFoundError:
                self.master_data = MasterData.create()
        else:
            self.master_data = MasterData.create()

        self._user_data_lock = Lock()

        self._user_data = {}
        if self.user_data_file_path is not None:
            try:
                with self.user_data_file_path.open("r") as f:
                    self._user_data = load(f)
            except (FileNotFoundError, JSONDecodeError):
                with self.user_data_file_path.open("w") as f:
                    dump(self.user_data, f, indent=2, ensure_ascii=False)

        self._user_id = None
        self._credential = None
        if (
            self._system_info.asset_version is not None
            and self._system_info.asset_hash is not None
            and asset_directory is not None
        ):
            self._asset = Asset(
                self._system_info.asset_version,
                self._system_info.asset_hash,
                asset_directory,
            )

        self._platform = platform
        self._key = key
        self._iv = iv
        self._jwt_secret = jwt_secret
        self._api_domain = api_domain
        self._asset_bundle_domain = asset_bundle_domain
        self._asset_bundle_info_domain = asset_bundle_info_domain
        self._game_version_domain = game_version_domain
        self._signature_domain = signature_domain
        self._enable_api_encryption = enable_api_encryption
        self._enable_asset_bundle_encryption = enable_asset_bundle_encryption
        self._enable_asset_bundle_info_encryption = enable_asset_bundle_info_encryption
        self._enable_game_version_encryption = enable_game_version_encryption
        self._enable_signature_encryption = enable_signature_encryption
        self._server_number = server_number

        self._update_all_on_init = update_all_on_init

    async def start(self):
        self._api_manager = API(
            platform=self._platform,
            key=self._key,
            iv=self._iv,
            jwt_secret=self._jwt_secret,
            system_info=self._system_info,
            api_domain=self._api_domain or API.DEFAULT_API_DOMAIN,
            asset_bundle_domain=self._asset_bundle_domain,
            asset_bundle_info_domain=self._asset_bundle_info_domain,
            game_version_domain=self._game_version_domain,
            signature_domain=self._signature_domain,
            enable_api_encryption=self._enable_api_encryption,
            enable_asset_bundle_encryption=self._enable_asset_bundle_encryption,
            enable_asset_bundle_info_encryption=self._enable_asset_bundle_info_encryption,
            enable_game_version_encryption=self._enable_game_version_encryption,
            enable_signature_encryption=self._enable_signature_encryption,
            server_number=self._server_number,
        )

        await self.refresh_signed_cookie()

        if self.api_manager.key is None or self.api_manager.iv is None:
            return

        if self._system_info.app_version is None or self._system_info.app_hash is None:
            await self.update_app()

        self.game_version = GameVersion(**await self.api_manager.get_game_version())
        if self._api_domain is not None:
            self.api_domain = self._api_domain
        else:
            if self.game_version.domain is not None:
                self.api_domain = self.game_version.domain
            else:
                self.api_domain = API.DEFAULT_API_DOMAIN

        if self._update_all_on_init:
            await self.update_all()

    async def close(self):
        await self.api_manager.close()

    @_auto_update
    @_auto_session_refresh
    async def register(self) -> dict:
        async with self._user_data_lock:
            response: dict = await self.api_manager.register()
            return self._update_user_resources(response)

    @_auto_update
    @_auto_session_refresh
    async def login(self, user_id: Union[int, str], credential: str) -> dict:
        async with self.system_info as system_info, self._user_data_lock:
            response: dict = await self.api_manager.authenticate(user_id, credential)
            self._user_id = user_id
            self._credential = credential

            info: SystemInfo = msgpack_converter.structure(response, SystemInfo)

            if info.app_version_status is AppVersionStatus.MAINTENANCE:
                raise ServerInMaintenance()
            elif (
                info.app_version_status is None
                or info.app_version_status is AppVersionStatus.NOT_AVAILABLE
                or system_info.app_version != info.app_version
            ):
                raise AppUpdateRequired(
                    info.app_version, info.app_hash, info.multi_play_version
                )
            else:
                asset_update_required: bool = (
                    system_info.asset_version != info.asset_version
                    or self.asset is None
                    or self.asset.version != info.asset_version
                )
                if (
                    info.data_version is not None
                    and info.asset_version is not None
                    and info.asset_hash is not None
                    and system_info.data_version != info.data_version
                    and asset_update_required
                ):
                    raise MultipleUpdatesRequired(info.data_version, info.asset_version, info.asset_hash, info.app_version_status.value)  # type: ignore
                elif (
                    info.asset_version is not None
                    and info.asset_hash is not None
                    and asset_update_required
                ):
                    raise AssetUpdateRequired(info.asset_version, info.asset_hash)
                elif (
                    info.data_version is not None
                    and system_info.data_version != info.data_version
                ):
                    raise DataUpdateRequired(info.data_version, info.app_version_status.value)  # type: ignore

            self._user_data = await self.api_manager.get_user_data(user_id)
            self._update_user_resources(await self.api_manager.get_login_bonus(user_id))
            return response

    @_auto_update
    @_auto_session_refresh
    @_auth_required
    async def reload_user_data(self, name: Optional[str] = None) -> dict:
        async with self._user_data_lock:
            user_data = await self.api_manager.get_user_data(self.user_id, name)  # type: ignore[arg-type]
            self._user_data = user_data
            return user_data

    @_auto_update
    @_auto_session_refresh
    async def check_version(self, bypass_availability: bool = False) -> SystemInfo:
        response: dict = await self.api_manager.get_system_info()
        app_versions: list[SystemInfo] = [
            app_version_info
            for app_version_info in (
                msgpack_converter.structure(app_version, SystemInfo)
                for app_version in response["appVersions"]
            )
            if bypass_availability
            or app_version_info.app_version_status is not AppVersionStatus.NOT_AVAILABLE
        ]
        async with self.system_info as system_info:
            if len(app_versions) > 0:
                matching_app_version_info: list[SystemInfo] = [
                    app_version_info
                    for app_version_info in app_versions
                    if app_version_info.app_version == system_info.app_version
                ]
                if len(matching_app_version_info) > 0:
                    info: SystemInfo = matching_app_version_info[-1]
                    if info.system_profile != system_info.system_profile:
                        self.system_info = SystemInfo(
                            system_profile=info.system_profile,
                            app_version=system_info.app_version,
                            app_hash=system_info.app_hash,
                            multi_play_version=system_info.multi_play_version,
                            app_version_status=info.app_version_status,
                        )
                    status: str = "" if info.app_version_status is None else info.app_version_status.value  # type: ignore
                    asset_update_required: bool = (
                        system_info.asset_version != info.asset_version
                        or self.asset is None
                        or self.asset.version != info.asset_version
                    )
                    if (
                        not bypass_availability
                        and info.app_version_status is AppVersionStatus.MAINTENANCE
                    ):
                        raise ServerInMaintenance()
                    if (
                        info.data_version is not None
                        and info.asset_version is not None
                        and info.asset_hash is not None
                        and system_info.data_version != info.data_version
                        and asset_update_required
                    ):
                        raise MultipleUpdatesRequired(
                            info.data_version,
                            info.asset_version,
                            info.asset_hash,
                            status,
                        )
                    elif (
                        info.asset_version is not None
                        and info.asset_hash is not None
                        and asset_update_required
                    ):
                        raise AssetUpdateRequired(info.asset_version, info.asset_hash)
                    elif (
                        info.data_version is not None
                        and system_info.data_version != info.data_version
                    ):
                        raise DataUpdateRequired(info.data_version, status)
                    return info
                elif (
                    app_versions[-1].app_version is not None
                    and app_versions[-1].app_hash is not None
                    and app_versions[-1].multi_play_version is not None
                ):
                    raise AppUpdateRequired(
                        app_versions[-1].app_version,
                        app_versions[-1].app_hash,
                        app_versions[-1].multi_play_version,
                    )
        raise NoAvailableVersions()

    async def update_app(
        self,
        app_version: Optional[str] = None,
        app_hash: Optional[str] = None,
        multi_play_version: Optional[str] = None,
    ) -> None:
        if app_version is None or app_hash is None or multi_play_version is None:
            try:
                await self.check_version()
            except AppUpdateRequired as e:
                app_version = e.app_version
                app_hash = e.app_hash
                multi_play_version = e.multi_play_version
            except (
                ServerInMaintenance,
                MultipleUpdatesRequired,
                AssetUpdateRequired,
                DataUpdateRequired,
            ):
                return
        async with self.system_info as system_info:
            new_system_info = dataclasses.replace(
                system_info,
                app_version=app_version,
                app_hash=app_hash,
                multi_play_version=multi_play_version,
            )
            self.system_info = new_system_info
            self.api_manager.system_info = new_system_info

    @_auto_session_refresh
    async def update_data(self, data_version: str, app_version_status: str) -> None:
        async with self._master_data_lock, self.system_info as system_info:
            del self._master_data
            response = await self.api_manager.get_master_data_packed(data_version)
            self.master_data = msgpack_converter.loads(response, MasterData)
            new_system_info = dataclasses.replace(
                system_info,
                data_version=data_version,
                app_version_status=app_version_status,
            )
            self.system_info = new_system_info
            self.api_manager.system_info = new_system_info

    @_auto_session_refresh
    async def update_asset(self, asset_version: str, asset_hash: str) -> None:
        async with self.system_info as system_info:
            if self.asset_directory is None:
                self._asset = Asset(asset_version, asset_hash)
            else:
                self._asset = Asset(
                    asset_version, asset_hash, str(self.asset_directory)
                )
            await self._asset.get_asset_bundle_info(self.api_manager)
            new_system_info = dataclasses.replace(
                system_info, asset_version=asset_version, asset_hash=asset_hash
            )
            self.system_info = new_system_info
            self.api_manager.system_info = new_system_info

    async def update_all(self) -> bool:
        try:
            await self.check_version()
        except AppUpdateRequired as e:
            await self.update_app(e.app_version, e.app_hash, e.multi_play_version)
            await self.update_all()
            return True
        except MultipleUpdatesRequired as e:
            await self.update_asset(e.asset_version, e.asset_hash)
            await self.update_data(e.data_version, e.app_version_status)
            return True
        except AssetUpdateRequired as e:
            await self.update_asset(e.asset_version, e.asset_hash)
            return True
        except DataUpdateRequired as e:
            await self.update_data(e.data_version, e.app_version_status)
            return True
        return False

    async def refresh_signed_cookie(self) -> AbstractCookieJar:
        cookies: Dict[str, str] = {
            k: v
            for k, v in (
                cookie.split("=")
                for cookie in (
                    c.strip()
                    for c in (await self.api_manager.get_signed_cookie()).split(";")
                )
                if cookie != ""
            )
        }
        self.api_manager.session.cookie_jar.clear()
        self.api_manager.session.cookie_jar.update_cookies(cookies)
        return self.api_manager.session.cookie_jar

    @_auto_update
    @_auto_session_refresh
    async def ping(self) -> dict:
        return await self.api_manager.ping()

    @_auto_update
    @_auto_session_refresh
    async def get_notices(self) -> list[Information]:
        return [
            Information(**information)
            for information in (await self.api_manager.get_notices())["informations"]
        ]

    @_auto_update
    @_auth_required
    @_auto_session_refresh
    async def transfer_out(self, password: str) -> dict:
        async with self._user_data_lock:
            response: dict = await self.api_manager.generate_transfer_code(
                self.user_id,  # type: ignore[arg-type]
                password,
            )
            return self._update_user_resources(response)

    @_auto_update
    @_auto_session_refresh
    async def transfer_check(self, transfer_code: str, password: str) -> dict:
        response: dict = await self.api_manager.checkTransferCode(
            transfer_code, password
        )
        return response

    @_auto_update
    @_auto_session_refresh
    async def transfer_in(self, transfer_code: str, password: str) -> dict:
        response: dict = await self.api_manager.generate_credential(
            transfer_code, password
        )
        user_id: Union[int, str] = response["afterUserGamedata"]["userId"]
        credential: str = response["credential"]
        return await self.login(user_id, credential)

    @_auto_update
    @_auto_session_refresh
    @_auth_required
    async def advance_tutorial(self, unit: Unit = Unit.LN) -> dict:
        async with self.user_data as user_data, self._user_data_lock:
            current_tutorial_status: TutorialStatus = TutorialStatus(
                user_data["userTutorial"]["tutorialStatus"]
            )
            response: dict = await self.api_manager.set_tutorial_status(
                self.user_id,  # type: ignore[arg-type]
                current_tutorial_status.next(unit),
            )
            return self._update_user_resources(response)

    @_auto_update
    @_auto_session_refresh
    @_auth_required
    async def receive_present(self, present_id) -> dict:
        async with self._user_data_lock:
            response: dict = await self.api_manager.receive_presents(
                self.user_id,  # type: ignore[arg-type]
                [present_id],
            )
            return self._update_user_resources(response)

    @_auto_update
    @_auto_session_refresh
    @_auth_required
    async def receive_all_presents(self) -> dict:
        async with self.user_data as user_data:
            response: dict = await self.api_manager.receive_presents(
                self.user_id,  # type: ignore[arg-type]
                [present["presentId"] for present in user_data["userPresents"]],
            )
            return self._update_user_resources(response)

    @_auto_update
    @_auto_session_refresh
    @_auth_required
    async def gacha(self, gacha_id: int, gach_behavior_id: int) -> dict:
        async with self._user_data_lock:
            response: dict = await self.api_manager.gacha(
                self.user_id, gacha_id, gach_behavior_id  # type: ignore[arg-type]
            )
            return self._update_user_resources(response)

    @_auto_update
    @_auto_session_refresh
    @_auth_required
    async def start_solo_live(self, live: SoloLive):
        async with self._user_data_lock:
            response: dict = await self.api_manager.start_solo_live(
                self.user_id,  # type: ignore[arg-type]
                live.music_id,
                live.music_difficulty_id,
                live.music_vocal_id,
                live.deck_id,
                live.boost_count,
                live.is_auto,
            )
            live.start(
                response["userLiveId"], response["skills"], response["comboCutins"]
            )
            return self._update_user_resources(response)

    @_auto_update
    @_auto_session_refresh
    @_auth_required
    async def end_solo_live(self, live: SoloLive) -> dict:
        async with self._user_data_lock:
            if not live.is_active or live.live_id is None:
                raise LiveNotActive
            if live.life <= 0:
                raise LiveDead
            response: dict = await self.api_manager.end_solo_live(
                self.user_id,  # type: ignore[arg-type]
                live.live_id,
                live.score,
                live.perfect_count,
                live.great_count,
                live.good_count,
                live.bad_count,
                live.miss_count,
                live.max_combo,
                live.life,
                live.tap_count,
                live.continue_count,
            )
            live.end()
            return self._update_user_resources(response)

    @_auto_update
    @_auto_session_refresh
    @_auth_required
    async def get_event_rankings(
        self,
        event_id: int,
        target_user_id: Union[int, str, None] = None,
        target_rank: Optional[int] = None,
        higher_limit: Optional[int] = None,
        lower_limit: Optional[int] = None,
    ) -> dict:
        if target_user_id is None and target_rank is None:
            target_user_id = self.user_id
        return await self.api_manager.get_event_rankings(
            self.user_id,  # type: ignore[arg-type]
            event_id,
            target_user_id,
            target_rank,
            higher_limit,
            lower_limit,
        )

    @_auto_update
    @_auto_session_refresh
    async def get_event_teams_player_count(self, event_id: int) -> dict:
        return await self.api_manager.get_event_teams_player_count(event_id)

    @_auto_update
    @_auto_session_refresh
    async def get_event_teams_point(self, event_id: int) -> dict:
        return await self.api_manager.get_event_teams_point(event_id)

    @_auto_update
    @_auto_session_refresh
    @_auth_required
    async def get_rank_match_rankings(
        self,
        rank_match_season_id: int,
        target_user_id: Union[int, str, None] = None,
        target_rank: Optional[int] = None,
        higher_limit: Optional[int] = None,
        lower_limit: Optional[int] = None,
    ) -> dict:
        if target_user_id is None and target_rank is None:
            target_user_id = self.user_id
        return await self.api_manager.get_rank_match_rankings(
            self.user_id,  # type: ignore[arg-type]
            rank_match_season_id,
            target_user_id,
            target_rank,
            higher_limit,
            lower_limit,
        )

    @_auto_update
    @_auto_session_refresh
    @_auth_required
    async def send_friend_request(
        self, user_id: Union[int, str], message: Optional[str] = None
    ) -> None:
        async with self._user_data_lock:
            response: dict = await self.api_manager.send_friend_request(self.user_id, user_id, message)  # type: ignore[arg-type]
            self._update_user_resources(response)

    @_auto_update
    @_auto_session_refresh
    @_auth_required
    async def reject_friend_request(self, request_user_id: Union[int, str]) -> None:
        async with self._user_data_lock:
            response: dict = await self.api_manager.reject_friend_request(self.user_id, request_user_id)  # type: ignore[arg-type]
            self._update_user_resources(response)

    @_auto_update
    @_auto_session_refresh
    @_auth_required
    async def accept_friend_request(self, request_user_id: Union[int, str]) -> dict:
        async with self._user_data_lock:
            response: dict = await self.api_manager.accept_friend_request(self.user_id, request_user_id)  # type: ignore[arg-type]
            return self._update_user_resources(response)

    @_auto_update
    @_auto_session_refresh
    @_auth_required
    async def remove_friend(self, friend_user_id: Union[int, str]) -> dict:
        async with self._user_data_lock:
            response: dict = await self.api_manager.remove_friend(self.user_id, friend_user_id)  # type: ignore[arg-type]
            return self._update_user_resources(response)
