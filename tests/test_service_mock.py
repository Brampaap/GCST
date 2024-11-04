from unittest.mock import Mock
from core.lib.exercise.default import dialog
from itertools import cycle

service = Mock()

service.process.side_effect = cycle([a for (q,a) in dialog])