# Contributing to ASUS Router Monitoring

We welcome contributions to improve this ASUS router monitoring stack! 

## How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Test your changes**: Ensure the exporter works with your router model
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

## Development Setup

1. **Prerequisites**: Python 3.12+, Docker, ASUS router access
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Test connection**: `python3 test_connection.py`
4. **Run locally**: `python3 asus_exporter.py`

## Testing

- Test with different ASUS router models
- Verify all metrics are collected correctly
- Ensure Docker deployment works
- Check Grafana dashboard displays properly

## Router Compatibility

If you test with a new router model:
- Document which metrics work/don't work
- Include router model and firmware version
- Add any special configuration needed

## Code Style

- Follow existing Python code style
- Add docstrings for new functions
- Include error handling
- Update README if adding new features

## Reporting Issues

- Include router model and firmware version
- Provide error logs from the exporter
- Describe expected vs actual behavior
- Include configuration (without passwords!)

Thank you for contributing! 🚀
