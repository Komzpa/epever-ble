# Contributing

Bug reports should include the controller model, BLE device name, Home Assistant version, installation method, and debug logs with Bluetooth addresses redacted if desired.

## Development

```bash
python -m pip install -e '.[test]'
python -m pytest
```

Keep the standalone package and `custom_components/epever_ble` aligned. The Home Assistant integration must remain self-contained because HACS installs only the integration directory.

Hardware compatibility claims must name the exact controller model and distinguish direct testing from community reports.
