---
name: 🐛 Bug Report
about: Report a bug to help us improve the Python Load Testing Suite
title: '[BUG] '
labels: bug
assignees: ''
---

## 🐛 Bug Description

A clear and concise description of what the bug is.

## 🔄 Steps to Reproduce

1. Run command: `python start.py ...`
2. With configuration: `...`
3. See error: `...`

## 🎯 Expected Behavior

A clear description of what you expected to happen.

## 📱 Actual Behavior

A clear description of what actually happened.

## 💻 Environment

- **OS**: (e.g., macOS 12.0, Ubuntu 20.04, Windows 11)
- **Python Version**: (e.g., 3.9.0)
- **Project Version**: (e.g., 1.0.0)
- **Virtual Environment**: (Yes/No)

## 📋 Configuration

```json
// Relevant parts of your config.json (remove sensitive data)
{
  "target": {
    "host": "...",
    "endpoint": "..."
  }
}
```

## 📝 Command Used

```bash
python start.py single 5 30 --api-key "..." --verbose
```

## 📊 Log Output

```
// Paste relevant error messages or log output here
```

## 🔍 Additional Context

Add any other context about the problem here. Screenshots, additional logs, etc.

## ✅ Checklist

- [ ] I have searched existing issues to ensure this is not a duplicate
- [ ] I have included all relevant information above
- [ ] I have removed any sensitive information (API keys, URLs, etc.)
- [ ] I can reproduce this issue consistently
