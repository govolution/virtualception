Get-VMHost | Foreach { Stop-VMHostService -HostService ($_ | Get-VMHostService | Where { $_.Key -eq “TSM-SSH”} ) }
