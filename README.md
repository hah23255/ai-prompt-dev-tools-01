# Prompt Enhancer

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Contributing](#contributing)
- [License](#license)

## Overview
Prompt Enhancer is an AI-driven system designed to transform user-provided topics into detailed technical research documents. It leverages an orchestration framework (CrewAI) along with specialized agents that utilize Pydantic for data validation and LMStudio for high-quality language model processing (running on local hardware with 12GB VRAM or less). A simple web interface allows users to submit prompts and view the multi-step enhancement process in action.

## Features
- Modular architecture: Uses an orchestrator to manage multiple processing steps.
- Multi-stage enhancement: Breaks down the prompt into categories such as topic analysis, category breakdown, online research integration, and iterative refinement.
- LMStudio Integration: Leverages a local language model with robust compute capabilities (16GB VRAM) for real-time processing.
- Data validation: Employs Pydantic to ensure data integrity across modules.
- Web interface: Provides an easy-to-use front end for submitting prompts and visualizing the processing workflow.

## Tech Stack
- Python 3.11: Main programming language.
- CrewAI: Orchestrates specialized AI agents.
- Pydantic: Validates input/output data structures.
- LMStudio: Powers local model execution (requires 16GB VRAM).
- Web Framework (e.g., Flask or FastAPI): Powers the web interface.

## Installation
1. Clone the repository:
   git clone https://github.com/adamjen/Prompt_Maker.git
2. Change into the project directory:
   cd prompt-enhancer
3. Install dependencies:
   pip install -r requirements.txt

Note: Ensure your system meets the hardware requirements for LMStudio (at least 12GB VRAM).

## Running the Application

To run this project, you will need to have LMStudio installed and running. Ensure you have downloaded and are using the `unsloth/qwen3-8b` model within LMStudio.

Once LMStudio is set up with the specified model, you can start the application by running the `startup.sh` script:

```bash
./startup.sh
```

This script will activate the virtual environment and launch the application. The web interface will typically be available on `http://localhost:8000` or a similar port. Use the provided form to submit topics or prompts.

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch (e.g., git checkout -b feature/YourFeature).
3. Make your changes and commit them.
4. Push your branch and open a pull request for review.

For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License. See the LICENSE file for details.