# Contributing to 3x1_Project

Thank you for your interest in contributing to the Collatz Conjecture testing project!

## How to Contribute

### Reporting Issues
- Check if the issue already exists in the Issues tab
- Provide clear description, steps to reproduce, and expected vs actual behavior
- Include Python version, OS, and any relevant error messages

### Submitting Changes
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit with clear messages (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style
- Follow PEP 8 Python style guidelines
- Add docstrings to functions
- Keep functions focused and modular
- Comment complex algorithms

### Testing
- Test your changes with various input sizes
- Verify database integrity after changes
- Run migration scripts if you modify the database schema

### Ideas for Contributions
- Performance optimizations
- Additional statistical analysis
- CLI argument parsing
- Database compression strategies
- Visualization tools
- Alternative hashing algorithms
- Documentation improvements

## Development Setup

```bash
# Clone the repository
git clone https://github.com/dustinober1/3x1_Project.git
cd 3x1_Project

# Install Git LFS (for database files)
git lfs install

# Run the script
python3 3x1.py

# Run migration (if needed)
python3 migrate_to_sqlite.py
```

## Questions?

Feel free to open an issue for discussion or reach out via GitHub!
