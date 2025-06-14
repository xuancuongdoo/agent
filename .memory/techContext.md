# Agent Server Technical Context

## Technologies Used

### Core Technologies

1. **Python 3.10+**: The primary programming language used for the project.

2. **FastAPI**: A modern, fast web framework for building APIs with Python based on standard Python type hints.

3. **Uvicorn**: An ASGI server that serves the FastAPI application.

4. **Pydantic**: Used for data validation and settings management using Python type annotations.

5. **OpenAI Agents**: A Python library for building and deploying intelligent agents using OpenAI models.

6. **AsyncIO**: Python's asynchronous I/O framework for handling concurrent operations.

### Development Tools

1. **uv**: A fast Python package installer and resolver, used for dependency management.

2. **Hatchling**: Used as the build backend for the Python package.

3. **Docker**: Used for containerization of the application.

4. **Git**: Used for version control.

### Future Considerations

1. **Database**: Considering integration with a database for more scalable memory storage.

2. **Monitoring Tools**: Planning to add monitoring tools for better observability.

3. **Testing Frameworks**: Will add pytest and other testing frameworks for unit and integration testing.

## Development Setup

### Local Development

1. **Prerequisites**:
   - Python 3.10 or higher
   - uv package manager (`pip install uv`)
   - Git

2. **Installation**:
   ```bash
   # Clone the repository
   git clone <repository-url>
   cd agent-server

   # Create a virtual environment
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   uv sync
   ```

3. **Running the Server**:
   ```bash
   # Run the development server
   python main.py
   ```

### Docker Development

1. **Prerequisites**:
   - Docker

2. **Building and Running**:
   ```bash
   # Build the Docker image
   docker build -t agent-server .

   # Run the Docker container
   docker run -p 8000:8000 agent-server
   ```

## Technical Constraints

1. **Python Version**: The project requires Python 3.10 or higher due to the use of modern Python features like union types and match statements.

2. **Memory Storage**: Currently limited to file-based storage, which may not be suitable for production environments with high load.

3. **OpenAI Agents Compatibility**: The system is designed to work with the OpenAI Agents Python library, which may have its own limitations and constraints.

4. **Async Operations**: All operations are designed to be asynchronous, which may require careful handling of concurrency issues.

## Dependencies

Key dependencies and their versions are defined in `pyproject.toml`:

```toml
[project]
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn>=0.24.0",
    "pydantic>=2.0.0",
    "openai-agents>=0.0.9",
]
```

Development dependencies:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.0.0",
]
```

## Configuration

1. **Server Configuration**: The server is configured to run on `0.0.0.0:8000` by default, with hot-reloading enabled in development.

2. **Tool Configuration**: Code linting and formatting tools are configured in `pyproject.toml`:
   - Black: line length of 100, targeting Python 3.10
   - isort: configured to be compatible with Black
   - mypy: configured with strict type checking

## Deployment Considerations

1. **Production Server**: For production deployment, consider using Gunicorn with Uvicorn workers.

2. **Environment Variables**: Currently, the system does not use environment variables for configuration, but this is planned for future versions.

3. **Scaling**: The system can be horizontally scaled by running multiple instances behind a load balancer.

4. **Monitoring**: Will need to add monitoring and observability tools for production use. 