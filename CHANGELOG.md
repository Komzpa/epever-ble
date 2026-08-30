# Changelog

## Unreleased

- Add HACS metadata and automated HACS/hassfest validation.
- Add protocol and register-parsing tests.
- Document direct hardware validation with the EPEVER XTRA3210N G3.
- Derive the Home Assistant device name from the config entry instead of hardcoding a model or household-specific identity.
- Route Home Assistant connections through its Bluetooth manager, including connectable ESPHome Bluetooth proxies, while keeping raw L2CAP local to the standalone CLI.
- Expose the timestamp of the last successful controller poll for fail-safe automations.

## 1.0.0

- Initial standalone client and Home Assistant custom integration for EPEVER controllers with compatible built-in HN-series BLE modules.
