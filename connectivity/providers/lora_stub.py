class LoRaStubProvider:
    name = "lora"

    def available(self) -> bool:
        return False

    def max_payload_bytes(self) -> int:
        return 0

    def cost_per_msg(self) -> None:
        return None

    def send(self, batch):
        raise RuntimeError("LoRa é stub; nenhum transporte físico foi implementado")
