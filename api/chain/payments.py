"""
AgentPaymentClient — disburses per-step USDC nanopayments on Arc Testnet.
Treasury wallet pays each agent wallet on step completion.
Disabled gracefully when ARC_RPC_URL or TREASURY_PRIVATE_KEY is not set.
"""
import os
import threading
from dotenv import load_dotenv
load_dotenv('/root/modusops/api/.env')
from typing import Optional
from web3 import Web3

# USDC on Arc Testnet: 18 decimals, native gas token
ARC_USDC_ADDRESS = "0x3600000000000000000000000000000000000000"

# ERC-20 transfer ABI (minimal)
_ERC20_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "to",     "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# Per-step payment amounts in USDC (18 decimals)
STEP_PAYMENTS = {
    "law_enforcement": 250000,
    "da":              250000,
    "defense":         250000,
    "judge":           250000,
}

# Agent wallet addresses
AGENT_WALLETS = {
    "judge":           "0x0235eD951A2F6a526169e5A9E30aD9e948f00D4b",
    "law_enforcement": "0xcC7e1D8C141C3da1c5311306cAdEBD1c4bacF7bE",
    "da":              "0xA20E38c83867aBd9618490F05506c1Cf7410399c",
    "defense":         "0x0BE65019b48cDF6fDf16EEf30f5dDDeB9c56FDBB",
}

TREASURY_ADDRESS = "0x14a4a0f1f3508d70e22B2048C10470F7EC78321D"


class AgentPaymentClient:
    def __init__(
        self,
        rpc_url: str,
        treasury_private_key: str,
        usdc_address: str = ARC_USDC_ADDRESS,
    ):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = self.w3.eth.account.from_key(treasury_private_key)
        self.usdc = self.w3.eth.contract(
            address=Web3.to_checksum_address(usdc_address),
            abi=_ERC20_ABI,
        )
        self.enabled = self.w3.is_connected()
        self._nonce_lock = threading.Lock()

    def treasury_balance(self) -> float:
        """Returns treasury USDC balance in human-readable units."""
        raw = self.usdc.functions.balanceOf(
            Web3.to_checksum_address(TREASURY_ADDRESS)
        ).call()
        return raw / 10**6

    def pay_agent(self, agent_role: str, case_id: str) -> dict:
        """
        Transfer USDC from Treasury to the agent wallet for the given role.
        Returns tx hash and amount paid, or a disabled/error dict.
        """
        if not self.enabled:
            return {"status": "disabled", "reason": "Arc RPC not connected"}

        if agent_role not in AGENT_WALLETS:
            return {"status": "error", "reason": f"Unknown agent role: {agent_role}"}

        amount = STEP_PAYMENTS.get(agent_role, 0)
        if amount == 0:
            return {"status": "error", "reason": "Zero payment amount"}

        to_address = Web3.to_checksum_address(AGENT_WALLETS[agent_role])

        try:
            with self._nonce_lock:
                nonce = self.w3.eth.get_transaction_count(self.account.address, "pending")
                base_fee = self.w3.eth.get_block("latest")["baseFeePerGas"]
                priority_fee = Web3.to_wei(1, "gwei")
                tx = self.usdc.functions.transfer(to_address, amount).build_transaction({
                    "from":     self.account.address,
                    "nonce":    nonce,
                    "gas":      100_000,
                    "maxFeePerGas":         base_fee * 2 + priority_fee,
                    "maxPriorityFeePerGas": priority_fee,
                    "chainId":  5042002,  # Arc Testnet
                })
                signed = self.w3.eth.account.sign_transaction(tx, self.account.key)
                tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)

            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

            return {
                "status":     "confirmed" if receipt.status == 1 else "failed",
                "agent":      agent_role,
                "to":         to_address,
                "amount_usdc": amount / 10**6,
                "tx_hash":    tx_hash.hex(),
                "case_id":    case_id,
                "block":      receipt.blockNumber,
            }
        except Exception as e:
            return {"status": "error", "reason": str(e)}


def get_payment_client() -> Optional[AgentPaymentClient]:
    """Factory — returns None if env vars not set (graceful degradation)."""
    rpc_url     = os.getenv("ARC_RPC_URL")
    private_key = os.getenv("TREASURY_PRIVATE_KEY")
    if not rpc_url or not private_key:
        return None
    return AgentPaymentClient(rpc_url=rpc_url, treasury_private_key=private_key)
