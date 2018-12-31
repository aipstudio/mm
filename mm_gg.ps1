$servers = @("192.168.1.2","192.168.1.3","192.168.1.7")

foreach ($server in $servers) {
    $path = "C:\PS"
    $fn = $server + ".xml"
    $sb = { Param ($fn)
        $path = "C:\PS"
        If (test-path $path) {
            Set-Location -Path $path
            if (Test-Path nvidia-smi.exe) {& "./nvidia-smi.exe" -q -x -f $fn}
        }

        If (!(test-path $path)) {
            New-Item -ItemType Directory -Force -Path $path
        }
    }

    $session = New-PSSession $server #-Credential $cred
    Invoke-Command -ScriptBlock $sb -ThrottleLimit 50 -Session $session -ArgumentList $fn
    #Copy-Item -Path "C:\Users\user\Desktop\mm-ewbf\nvidia-smi.exe" -Destination $path -Recurse -ToSession $session
    Copy-Item -Path "C:\PS\*.xml" -Destination "C:\Users\user\Desktop\mm-ewbf\" -Recurse -Force -FromSession $session
    Remove-PSSession $session
}