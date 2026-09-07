"""
VerdictChainClient — commits verdicts to VerdictRegistry on Arbitrum One.
Disabled gracefully when VERDICT_CONTRACT_ADDRESS is not set.
"""

import hashlib
import json
import os
from typing import Optional

from web3 import Web3
from web3.middleware import geth_poa_middleware

_ABI = [
    {
        "inputs": [
            {"internalType": "string",  "name": "caseId",          "type": "string"},
            {"internalType": "bytes32", "name": "verdictHash",      "type": "bytes32"},
            {"internalType": "uint8",   "name": "verdict",          "type": "uint8"},
            {"internalType": "uint8",   "name": "confidenceScore",  "type": "uint8"},
            {"internalType": "uint8",   "name": "jurisdiction",     "type": "uint8"},
        ],
        "name": "commitVerdict",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "string", "name": "caseId", "type": "string"}],
        "name": "caseExists",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "verdictCount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

VERDICT_ENUM = {"PROCEED": 0, "DISMISS": 1, "ESCALATE": 2, "REVIEW": 3}
JURISDICTION_ENUM = {"LOCAL": 0, "STATE": 1, "FEDERAL": 2}


class VerdictChainClient:
    def __init__(self, rpc_url: str, private_key: str, contract_address: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.account = self.w3.eth.account.from_key(private_key)
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=_ABI,
        )

    def _canonical_hash(self, verdict_obj: dict) -> bytes:
        payload = {k: v for k, v in verdict_obj.items() if k != "on_chain_tx"}
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).digest()

    def commit_verdict(self, verdict_obj: dict) -> Optional[str]:
        case_id: str = verdict_obj.get("case_id", "")
        if not case_id:
            return None

        if self.contract.functions.caseExists(case_id).call():
            return None

        verdict_str = verdict_obj.get("verdict", "REVIEW").upper()
        jurisdiction_str = verdict_obj.get("jurisdiction", "LOCAL").upper()
        verdict_int = VERDICT_ENUM.get(verdict_str, 3)
        jurisdiction_int = JURISDICTION_ENUM.get(jurisdiction_str, 0)
        confidence = max(0, min(100, int(verdict_obj.get("confidence_score", 50))))

        verdict_hash_bytes32 = self._canonical_hash(verdict_obj)[:32]

        nonce = self.w3.eth.get_transaction_count(self.account.address)
        tx = self.contract.functions.commitVerdict(
            case_id,
            verdict_hash_bytes32,
            verdict_int,
            confidence,
            jurisdiction_int,
        ).build_transaction({
            "from":     self.account.address,
            "nonce":    nonce,
            "gas":      200_000,
            "gasPrice": self.w3.eth.gas_price,
        })

        signed = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        if receipt.status != 1:
            raise RuntimeError(f"Chain tx reverted: {tx_hash.hex()}")

        return tx_hash.hex()

    def verdict_count(self) -> int:
        return self.contract.functions.verdictCount().call()

    @property
    def wallet_address(self) -> str:
        return self.account.address


_client: Optional[VerdictChainClient] = None


def get_chain_client() -> Optional[VerdictChainClient]:
    global _client
    if _client is not None:
        return _client

    rpc_url          = os.getenv("ARBITRUM_RPC_URL")
    private_key      = os.getenv("ARBITRUM_PRIVATE_KEY")
    contract_address = os.getenv("VERDICT_CONTRACT_ADDRESS")

    if not all([rpc_url, private_key, contract_address]):
        return None

    _client = VerdictChainClient(rpc_url, private_key, contract_address)
    return _client
