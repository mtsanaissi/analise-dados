# Jules's Learning Log

This document serves as a log for Jules to learn from its mistakes and improve its performance.

## Lessons learned

*   **Forgetting to adhere to the `JULES.md` guidelines:** I will make sure to review the `JULES.md` file before every task to ensure I am following all the established conventions and guidelines.
*   **Start with the Environment**: My first step in a new task session must be to run `pythonpip install -r requirements.txt` to ensure all dependencies are present. I should then run the test suite with `python -m pytest` to confirm the environment is stable before making any code changes.
*   **The Entry Point is src/run.py**: I now know that the main entry point for running the application is python src/run.py, which then uses src/main/orchestrator.py to delegate to the different phases.