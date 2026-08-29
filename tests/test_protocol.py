from epever_ble import build_modbus_read, modbus_crc16, verify_modbus_crc


def test_build_modbus_read_matches_known_frame() -> None:
    frame = build_modbus_read(slave=1, func=4, start_reg=0x3100, count=1)

    assert frame.hex() == "0104310000013f36"
    assert verify_modbus_crc(frame)


def test_verify_modbus_crc_rejects_short_or_modified_frame() -> None:
    assert not verify_modbus_crc(b"\x01\x04\x00")

    frame = bytearray(build_modbus_read(1, 4, 0x3100, 1))
    frame[3] ^= 0x01
    assert not verify_modbus_crc(bytes(frame))


def test_modbus_crc16_known_vector() -> None:
    assert modbus_crc16(bytes.fromhex("010431000001")) == 0x363F
