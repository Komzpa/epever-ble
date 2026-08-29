import epever_ble
from epever_ble import read_all_data


class FakeBLE:
    def __init__(self) -> None:
        self.calls: list[tuple[int, int, int]] = []
        self.responses = {
            (0x3100, 8): [398, 0, 0, 0, 1303, 0, 0, 0],
            (0x310C, 8): [1303, 842, 10779, 0, 2500, 2630, 0, 0],
            (0x311A, 2): [68, 0],
            (0x3200, 3): [0, 2 << 2, 0],
            (0x330C, 8): [1, 0, 2, 0, 3, 0, 4, 0],
            (0x3304, 8): [5, 0, 6, 0, 7, 0, 8, 0],
        }

    def read_input_registers(
        self, start: int, count: int, slave: int = 1
    ) -> list[int]:
        self.calls.append((start, count, slave))
        return self.responses[(start, count)]


def test_read_all_data_maps_xtra3210n_g3_register_values(monkeypatch) -> None:
    monkeypatch.setattr(epever_ble._reader_mod.time, "sleep", lambda _: None)
    ble = FakeBLE()

    data = read_all_data(ble)

    assert data == {
        "pv_voltage": 3.98,
        "pv_current": 0.0,
        "pv_power": 0.0,
        "batt_voltage": 13.03,
        "batt_charge_current": 0.0,
        "batt_charge_power": 0.0,
        "load_voltage": 13.03,
        "load_current": 8.42,
        "load_power": 107.79,
        "batt_temp": 25.0,
        "device_temp": 26.3,
        "batt_soc": 68,
        "charge_mode": "Boost",
        "gen_today": 0.01,
        "gen_month": 0.02,
        "gen_year": 0.03,
        "gen_total": 0.04,
        "use_today": 0.05,
        "use_month": 0.06,
        "use_year": 0.07,
        "use_total": 0.08,
    }
    assert ble.calls == [
        (0x3100, 8, 1),
        (0x310C, 8, 1),
        (0x311A, 2, 1),
        (0x3200, 3, 1),
        (0x330C, 8, 1),
        (0x3304, 8, 1),
    ]


def test_read_all_data_keeps_missing_batches_absent(monkeypatch) -> None:
    monkeypatch.setattr(epever_ble._reader_mod.time, "sleep", lambda _: None)

    class NoDataBLE:
        def read_input_registers(self, start: int, count: int, slave: int = 1):
            return None

    assert read_all_data(NoDataBLE()) == {}
