"""
Based on реверс-инженере генерируемых ссылок на клиенте в группах и каналах.

Ссылки работают только для групп и каналов, для диалогов ссылка будет выдавать 404
"""

import base64

from maxo.utils.link import create_max_http_link


def id_to_message_url(sequence_id: int, chat_id: int) -> str:
    """Преобразует числовой ID сообщения в ссылку на сообщение."""
    # Преобразуем число в 8 байт в формате big-endian
    bytes_data = sequence_id.to_bytes(8, byteorder="big")

    # Кодируем в base64
    base64_std = base64.b64encode(bytes_data).decode("ascii")

    # Делаем URL-safe: удаляем padding и заменяем символы
    base64_url = base64_std.rstrip("=").replace("+", "-").replace("/", "_")

    return create_max_http_link("c", str(chat_id), base64_url)


def url_to_message_id(url: str) -> int:
    """Обратное преобразование: из URL-safe base64 в числовой ID."""
    # Извлекаем последнюю часть URL (после последнего /)
    base64_url = url.strip("/").split("/")[-1]

    # Восстанавливаем стандартный base64
    base64_std = base64_url.replace("-", "+").replace("_", "/")

    # Восстанавливаем padding
    padding = 8 - (len(base64_std) % 8)
    if padding < 8:  # noqa: PLR2004
        base64_std += "=" * padding

    # Декодируем
    bytes_data = base64.b64decode(base64_std)
    return int.from_bytes(bytes_data, byteorder="big")
