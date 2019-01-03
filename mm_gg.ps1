$servers = @()
cd $PSScriptRoot
foreach ($line in Get-Content .\ip.txt) {$servers = $servers + $line}
$username = "user"
$password = "password"
$pw = convertto-securestring -AsPlainText -Force -String $password
$cred = new-object -typename System.Management.Automation.PSCredential -argumentlist $username,$pw

foreach ($server in $servers) {
    $path = "C:\PS"
    $sm=$true
    $fn = $server + ".xml"
    $sb = { Param ($fn)
        $path = "C:\PS"
        If (test-path $path) {
            Set-Location -Path $path
            if (Test-Path nvidia-smi.exe) {& "./nvidia-smi.exe" -q -x -f $fn}
        }
        elseIf (!(test-path $path)) {
            New-Item -ItemType Directory -Force -Path $path
            Set-Location -Path $path
            if (!(Test-Path nvidia-smi.exe)) {$sm=$false}
        }
    }

    $session = New-PSSession $server #-Credential $cred
    Invoke-Command -ScriptBlock $sb -ThrottleLimit 50 -Session $session -ArgumentList $fn
    $sm = Invoke-Command -Session $session {$sm}
    if ($sm -eq $false) {
        Copy-Item -Path "C:\Users\user\Desktop\mm\nvidia-smi.exe" -Destination $path -Recurse -ToSession $session
        Invoke-Command -ScriptBlock $sb -ThrottleLimit 50 -Session $session -ArgumentList $fn
        }

    Copy-Item -Path "C:\PS\*.xml" -Destination "C:\Users\user\Desktop\mm\" -Recurse -Force -FromSession $session
    Remove-PSSession $session
}
