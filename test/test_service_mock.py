from itertools import cycle
from unittest.mock import Mock

from core.lib.exercise.default import dialog

service = Mock()

service.process.side_effect = cycle([item["right_answer"] for item in dialog])
