# SPDX-FileCopyrightText: 2022-2023 Erik Chan <erikchan002@gmail.com>
# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from typing import AsyncIterator, Optional

from async_pjsekai.utilities import deobfuscated, obfuscated


class AssetBundle:
    _chunks: AsyncIterator[bytes]
    _obfuscated_chunks: AsyncIterator[bytes]

    @property
    def chunks(self) -> AsyncIterator[bytes]:
        return self._chunks

    @property
    def obfuscated_chunks(self) -> AsyncIterator[bytes]:
        return self._obfuscated_chunks

    def __init__(
        self,
        chunks: Optional[AsyncIterator[bytes]] = None,
        obfuscated_chunks: Optional[AsyncIterator[bytes]] = None,
    ):
        if chunks is not None:
            self._chunks = chunks
            self._obfuscated_chunks = obfuscated(chunks)
        elif obfuscated_chunks is not None:
            self._chunks = deobfuscated(obfuscated_chunks)
            self._obfuscated_chunks = obfuscated_chunks
        else:
            raise ValueError

    def extract(self) -> None:
        raise NotImplementedError
