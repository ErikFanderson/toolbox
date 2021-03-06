from typing import List, Callable

from toolbox.database import Database
from toolbox.tool import Tool
from toolbox.logger import LogLevel


class ToolC(Tool):
    def __init__(self, db: Database, log: Callable[[], None]):
        super().__init__(db, log)

    def steps(self) -> List[Callable[[], None]]:
        def simple_fn():
            print("simple_fn!!!")

        fn = lambda: print("lambda!!!")
        steps = [fn, simple_fn, self.test_fn]
        return steps

    def test_fn(self):
        print("test_fn!!!")
        self.log("Log test", LogLevel.WARNING)
