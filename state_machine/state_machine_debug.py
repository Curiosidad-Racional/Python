from os.path import realpath, dirname, join


with open(join(dirname(realpath(__file__)), "state_machine.py"), "r") as f:
    __content = f.read()
    for text, replacement in {
            "# <PRINT enter start self>":
            """print(graph_format(self._observers),
                  "  Machine:", type(self).__name__,
                  "  State:", type(self._state).__name__,
                  "  Event: Start",
                  "  Entering from:", type(self).__name__)""",
            "# <PRINT exit start stop self>":
            """print(graph_format(self._observers),
                      "  Machine:", type(self).__name__,
                      "  State:", type(self._state).__name__,
                      "  Event:", type(e.event).__name__,
                      "  Exiting to:", type(None).__name__)""",
            "# <PRINT exit start exception self>":
            """print(graph_format(self._observers),
                      "  Machine:", type(self).__name__,
                      "  State:", type(self._state).__name__,
                      "  Event:", type(e).__name__,
                      "  Exiting to:", type(None).__name__)""",
            "# <PRINT exit stop state>":
            """print(graph_format(self._observers),
                          "  Machine:", type(self).__name__,
                          "  State:", type(self._state).__name__,
                          "  Event:", type(e.event).__name__,
                          "  Exiting to:", type(self).__name__)""",
            "# <PRINT exit exception state>":
            """print(graph_format(self._observers),
                          "  Machine:", type(self).__name__,
                          "  State:", type(self._state).__name__,
                          "  Event:", type(e).__name__,
                          "  Exiting to:", type(self).__name__)""",
            "# <PRINT exit state>":
            """print(graph_format(self._observers),
                          "  Machine:", type(self).__name__,
                          "  State:", type(self._state).__name__,
                          "  Event:", type(event).__name__,
                          "  Exiting to:", type(state).__name__)""",
            "# <PRINT enter state>":
            """print(graph_format(self._observers),
                      "  Machine:", type(self).__name__,
                      "  State:", type(self._state).__name__,
                      "  Event:", type(event).__name__,
                      "  Entering from:", type(from_state).__name__)""",
            "# <PRINT exit stop self>":
            """print(graph_format(self._observers),
                          "  Machine Exiting:", type(self).__name__,
                          "  State:", type(self._state).__name__,
                          "  Event:", type(e.event).__name__,
                          "  Exiting to:", type(self).__name__)""",
            "# <PRINT exit exception self>":
            """print(graph_format(self._observers),
                          "  Machine Exiting:", type(self).__name__,
                          "  State:", type(self._state).__name__,
                          "  Event:", type(e).__name__,
                          "  Exiting to:", type(None).__name__)""",
            "# <PRINT machine start>":
            """print(graph_format(self._observers),
              "  Machine Starting:", type(self).__name__,
              "  State:", type(None).__name__,
              "  Event:", type(event).__name__,
              "  Entering from:", type(from_state).__name__)""",
    }.items():
        __content = __content.replace(text, replacement)
    exec(__content)
    del __content