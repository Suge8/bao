# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._chat_service_testkit import cleanup_chat_services, pytest, qt_app
from tests._chat_service_cases_01 import *
from tests._chat_service_cases_02 import *
from tests._chat_service_cases_03 import *
from tests._chat_service_cases_04 import *
from tests._chat_service_cases_05 import *
from tests._chat_service_cases_06 import *
from tests._chat_service_cases_07 import *
from tests._chat_service_cases_08 import *
from tests._chat_service_cases_09 import *
from tests._chat_service_cases_10 import *
from tests._chat_service_cases_11 import *
from tests._chat_service_cases_12 import *
from tests._chat_service_cases_13 import *

pytestmark = [pytest.mark.integration, pytest.mark.gui]
