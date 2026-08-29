"""Config flow for EPEVER BLE integration."""

import re
from typing import Any

import voluptuous as vol

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_MAC, CONF_SCAN_INTERVAL

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

MAC_REGEX = re.compile(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")

# Keywords that suggest an EPEVER BLE device
EPEVER_KEYWORDS = ("hn_", "epever", "tracer", "fapao", "solar", "bt05")


def _is_likely_epever(name: str) -> bool:
    lower = name.lower()
    return any(kw in lower for kw in EPEVER_KEYWORDS)


class EPEVERBLEConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EPEVER BLE."""

    VERSION = 1

    def __init__(self):
        self._discovered_devices: dict[str, str] = {}
        self._discovery_info: BluetoothServiceInfoBleak | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 1: scan for devices and let the user pick one."""
        if user_input is not None:
            mac = user_input[CONF_MAC]

            if mac == "__manual__":
                return await self.async_step_manual()

            mac = mac.upper()
            await self.async_set_unique_id(mac)
            self._abort_if_unique_id_configured()

            name = self._discovered_devices.get(mac, mac[-8:])
            return self.async_create_entry(
                title=f"EPEVER {name}",
                data={
                    CONF_MAC: mac,
                    CONF_SCAN_INTERVAL: user_input.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                },
            )

        self._discovered_devices = {
            info.address.upper(): info.name or info.address
            for info in async_discovered_service_info(self.hass)
            if info.name and _is_likely_epever(info.name)
        }

        if not self._discovered_devices:
            # No devices found — go straight to manual entry
            return await self.async_step_manual()

        # Build selection list: "MAC — Name" for display
        device_options: dict[str, str] = {}
        for mac, name in self._discovered_devices.items():
            label = f"{name} ({mac})" if name != mac else mac
            device_options[mac] = label
        device_options["__manual__"] = "Enter MAC address manually..."

        # Pre-select the first likely EPEVER device
        default_mac = None
        for mac, name in self._discovered_devices.items():
            if _is_likely_epever(name):
                default_mac = mac
                break
        if default_mac is None:
            default_mac = next(iter(self._discovered_devices))

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MAC, default=default_mac): vol.In(device_options),
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): vol.All(int, vol.Range(min=10)),
                }
            ),
        )

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle discovery from a local adapter or Bluetooth proxy."""
        mac = discovery_info.address.upper()
        await self.async_set_unique_id(mac)
        self._abort_if_unique_id_configured()
        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {"name": discovery_info.name or mac}
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm a device discovered by Home Assistant Bluetooth."""
        assert self._discovery_info is not None
        if user_input is not None:
            mac = self._discovery_info.address.upper()
            return self.async_create_entry(
                title=self._discovery_info.name or mac,
                data={
                    CONF_MAC: mac,
                    CONF_SCAN_INTERVAL: user_input.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                },
            )

        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): vol.All(int, vol.Range(min=10)),
                }
            ),
            description_placeholders={
                "name": self._discovery_info.name or self._discovery_info.address,
            },
        )

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Fallback step: manual MAC address entry."""
        errors = {}

        if user_input is not None:
            mac = user_input[CONF_MAC].strip().upper()

            if not MAC_REGEX.match(mac):
                errors["mac"] = "invalid_mac"
            else:
                await self.async_set_unique_id(mac)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"EPEVER {mac[-8:]}",
                    data={
                        CONF_MAC: mac,
                        CONF_SCAN_INTERVAL: user_input.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    },
                )

        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MAC): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): vol.All(int, vol.Range(min=10)),
                }
            ),
            errors=errors,
        )
