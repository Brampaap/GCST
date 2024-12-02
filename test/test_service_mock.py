from itertools import cycle
from unittest.mock import Mock
from core.chat import Task

from core.lib.exercise.default import dialog

service = Mock()

service.process.side_effect = cycle([Task(**item).right_answer for item in dialog])
