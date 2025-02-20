from django.shortcuts import render
from django.http import JsonResponse
from web3 import Web3
from eth_account import Account
from eth_utils import to_hex
from .forms import SendEthForm

# ✅ Enable HD Wallet Features
Account.enable_unaudited_hdwallet_features()

# ✅ Arbitrum One RPC URL
ARBITRUM_RPC_URL = "https://arb1.arbitrum.io/rpc"

# ✅ Connect to Arbitrum Network
web3 = Web3(Web3.HTTPProvider(ARBITRUM_RPC_URL))

# ✅ Function to Convert Mnemonic to Private Key
def mnemonic_to_private_key(mnemonic, index=0):
    """ Converts a mnemonic phrase into a private key """
    try:
        account = Account.from_mnemonic(mnemonic, account_path=f"m/44'/60'/0'/0/{index}")
        return to_hex(account.key)  # Convert to hex private key
    except Exception:
        return None

def send_eth(request):
    message = None  # ✅ Store success or error message
    tx_hash = None  # ✅ Store transaction hash

    if request.method == "POST":
        form = SendEthForm(request.POST)
        if form.is_valid():
            mnemonic_phrase = form.cleaned_data['mnemonic_phrase']
            sender_address = form.cleaned_data['sender_address']
            recipient_address = form.cleaned_data['recipient_address']

            # ✅ Validate Ethereum Address
            if not web3.is_address(recipient_address):
                message = "❌ Invalid recipient address."
            else:
                # ✅ Convert Mnemonic to Private Key
                private_key = mnemonic_to_private_key(mnemonic_phrase)
                if not private_key:
                    message = "❌ Invalid mnemonic phrase."
                else:
                    nonce = web3.eth.get_transaction_count(sender_address)

                    # ✅ Get latest base fee from network
                    latest_block = web3.eth.get_block("latest")
                    base_fee = latest_block.get("baseFeePerGas", web3.to_wei("0.1", "gwei"))

                    # ✅ Set Gas Fees
                    max_priority_fee = web3.to_wei("1", "gwei")
                    max_fee = base_fee + max_priority_fee
                    gas_limit = 300000  # ✅ Increased gas limit

                    # ✅ ETH Amount to Send
                    amount_eth = 0.000005  # Send 0.00001 ETH

                    # ✅ Create Transaction
                    tx = {
                        'nonce': nonce,
                        'to': recipient_address,
                        'value': web3.to_wei(amount_eth, 'ether'),
                        'gas': gas_limit,
                        'maxFeePerGas': max_fee,
                        'maxPriorityFeePerGas': max_priority_fee,
                        'chainId': 42161  # Chain ID for Arbitrum One
                    }

                    try:
                        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
                        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                        tx_hash = web3.to_hex(tx_hash)  # Convert to hex
                        message = f"✅ Transaction Sent Successfully!"
                    except Exception as e:
                        message = f"❌ Error: {str(e)}"

    else:
        form = SendEthForm()

    return render(request, 'send_eth/send_eth.html', {'form': form, 'message': message, 'tx_hash': tx_hash})
