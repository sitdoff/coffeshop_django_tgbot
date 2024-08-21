from unittest.mock import AsyncMock, patch

import pytest
from handlers.command_handlers import process_help_command
from lexicon.lexicon_ru import LEXICON_RU


@pytest.mark.asyncio
async def test_process_help_command(message, user):
    message.text = "/help"
    await process_help_command(message)

    message.answer.assert_called_once_with(LEXICON_RU["commands"]["help"])
