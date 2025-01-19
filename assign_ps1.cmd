$cert = Get-ChildItem -path cert:\CurrentUser\My -CodeSigningCert
Set-AuthenticodeSignature ".venv\Scripts\activate.ps1" $cert
