# Aomi Transact: Supported Protocols & Chain Reference

## Supported EVM Networks
| Network | Chain ID | Native Currency | AA Standard | Sponsorship Support |
|---|---|---|---|---|
| Ethereum Mainnet | `1` | ETH | EIP-7702 | BYOK Provider (Alchemy) |
| Base | `8453` | ETH | ERC-4337 | Zero-config proxy / Pimlico |
| Arbitrum One | `42161` | ETH | ERC-4337 | Zero-config proxy / Pimlico |
| Optimism (OP Mainnet) | `10` | ETH | ERC-4337 | Zero-config proxy / Pimlico |
| Polygon PoS | `137` | POL / MATIC | ERC-4337 | Biconomy / Pimlico |
| Linea | `59144` | ETH | ERC-4337 | Zero-config proxy |

## Primary DeFi Protocol Routing
1. **Uniswap V3**:
   - Primary router: SwapRouter02 (`0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45`).
   - Requires token approve before `exactInputSingle` / `exactInput`.
2. **Lido Staking**:
   - Contract: `0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84` (`stETH`).
   - Function: `submit(address(0))` with native ETH value.
3. **Aave V3**:
   - Pool: `0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2`.
   - Functions: `supply(asset, amount, onBehalfOf, referralCode)`, `borrow(...)`.
4. **Circle CCTP (Cross-Chain Transfer Protocol)**:
   - TokenMessenger: `0xbd3fa81b58ba92a82136038b25adec996630e183`.
   - Burn & Mint across Ethereum and Base.
