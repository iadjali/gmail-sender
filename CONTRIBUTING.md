# Contributing to gmail-sender

Thank you for your interest in contributing to gmail-sender! This document provides guidelines for contributing to the project.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/gmail-sender.git
   cd gmail-sender
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install development dependencies:
   ```bash
   pip install ruff mypy pytest
   ```

## Code Quality

This project uses several tools to maintain code quality:

- **ruff**: Linting and code formatting
- **mypy**: Type checking
- **pytest**: Testing

Run all checks locally before submitting:
```bash
ruff check .
mypy gmail_sender.py
pytest
```

## Testing

- Write tests for new features in `tests/test_gmail_sender.py`
- Ensure all tests pass before submitting
- Test both success and error cases
- Mock external API calls in tests

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests and linting
5. Commit your changes: `git commit -m "Add your feature"`
6. Push to your fork: `git push origin feature/your-feature`
7. Create a Pull Request

## Code Style

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write descriptive docstrings
- Keep functions small and focused
- Use meaningful variable names

## Security

- Never commit OAuth credentials or tokens
- Be careful with email validation to prevent injection attacks
- Follow the principle of least privilege

## Reporting Issues

When reporting bugs, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Any relevant error messages

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.
