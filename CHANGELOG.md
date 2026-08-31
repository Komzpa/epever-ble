# Changelog

## Unreleased

- Add HACS metadata and automated HACS/hassfest validation.
- Add protocol and register-parsing tests.
- Expose the signed controller-side battery net current from registers `0x331B-0x331C`.
- Correct the G3 register semantics for PV output and battery output, and expose the previously omitted battery-output and MOSFET measurements.
- Document direct hardware validation with the EPEVER XTRA3210N G3.
- Derive the Home Assistant device name from the config entry instead of hardcoding a model or household-specific identity.
- Route Home Assistant connections through its Bluetooth manager, including connectable ESPHome Bluetooth proxies, while keeping raw L2CAP local to the standalone CLI.

## 1.0.0

- Initial standalone client and Home Assistant custom integration for EPEVER controllers with compatible built-in HN-series BLE modules.
