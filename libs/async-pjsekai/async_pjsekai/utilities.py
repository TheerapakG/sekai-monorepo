# SPDX-FileCopyrightText: 2022-2023 Erik Chan <erikchan002@gmail.com>
# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from typing import AsyncIterator


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
