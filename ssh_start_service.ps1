Get-VMHost | Foreach { Start-VMHostService -HostService ($_ | Get-VMHostService | Where { $_.Key -eq “TSM-SSH”} ) }
