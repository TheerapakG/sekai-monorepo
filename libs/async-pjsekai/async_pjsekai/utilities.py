# SPDX-FileCopyrightText: 2022-2023 Erik Chan <erikchan002@gmail.com>
# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from typing import AsyncIterator, Optional

from msgpack import packb, unpackb
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def msgpack(dict: Optional[dict]) -> bytes:
    return b"" if dict is None else packb(dict)  # type: ignore


def unmsgpack(data: bytes) -> dict:
    return unpackb(data, strict_map_key=False) if len(data) > 0 else {}  # type: ignore


def encrypt(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    ciphertext: bytes = cipher.encrypt(pad(plaintext, 16))
    return ciphertext


def decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    plaintext: bytes = unpad(cipher.decrypt(ciphertext), 16)
    return plaintext


async def deobfuscated(obfuscated_chunks: AsyncIterator[bytes]) -> AsyncIterator[bytes]:
    count = 0
    async for chunk in obfuscated_chunks:
        if (count - 4) >= 128:
            yield chunk
        else:
            yield bytes(
                [
                    int(byte)
                    if (count + i - 4) >= 128 or (count + i - 4) % 8 >= 5
                    else int(byte) ^ 0xFF
                    for i, byte in enumerate(chunk)
                    if (count + i) >= 4
                ]
            )
        count += len(chunk)


async def obfuscated(chunks: AsyncIterator[bytes]) -> AsyncIterator[bytes]:
    count = 0
    async for chunk in chunks:
        if count >= 128:
            yield chunk
        else:
            yield bytes(
                [0x10, 0, 0, 0]
                + [
                    int(byte)
                    if (count + i) >= 128 or (count + i) % 8 >= 5
                    else int(byte) ^ 0xFF
                    for i, byte in enumerate(chunk)
                ]
            )
        count += len(chunk)
