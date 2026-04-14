# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-04-14

### Added
- Initial release of gmail-sender
- Command-line interface for sending emails via Gmail API
- Programmatic API for library usage
- Support for HTML emails, attachments, CC/BCC
- OAuth 2.0 authentication with secure token storage
- Comprehensive examples and documentation
- Email address validation
- Logging support
- Type hints and mypy support
- Unit tests with pytest
- CI/CD pipeline with linting and type checking
- MIT license

### Features
- Send plain text and HTML emails
- Attach multiple files
- CC and BCC support
- Reusable service instances for batch sending
- Custom secrets directory via environment variable
- Error handling with custom exceptions

### Security
- OAuth 2.0 with minimal Gmail send scope
- Secure credential storage outside repository
- Input validation for email addresses

### Documentation
- Complete README with setup and usage instructions
- API reference in docstrings
- Multiple usage examples
- Troubleshooting guide
- Contributing guidelines
