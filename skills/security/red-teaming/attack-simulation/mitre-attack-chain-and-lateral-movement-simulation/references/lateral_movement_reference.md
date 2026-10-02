# Lateral Movement Techniques & Event ID Mapping

## Key Techniques
1. **Pass-the-Hash (T1550.002)**:
   - Uses NTLM hashes directly to authenticate without cracking the plaintext password.
   - Event IDs: 4624 (Logon Type 3, NTLM Package, Key Length 0).
2. **Kerberoasting (T1558.003)**:
   - Requests Ticket Granting Service (TGS) tickets for service accounts with SPNs to crack RC4/AES offline.
   - Event ID: 4769 (A Kerberos service ticket was requested, Ticket Options 0x40810000, Ticket Encryption 0x17 for RC4).
3. **WMI Execution (T1047)**:
   - Spawns processes remotely via `wmic process call create` or PowerShell WMI cmdlets.
   - Process: `WmiPrvSE.exe` spawning child processes.
