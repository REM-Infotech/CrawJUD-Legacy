param (
  [Parameter(Mandatory = $true)]
  [string] $DOTENV_KEY,
  $APPLICATION_APP,
  [string] $SERVER_HOSTNAME
)
function StartApp {

  param (
    [string] $SERVER_HOSTNAME,
    [string] $DOTENV_KEY,
    [string] $APPLICATION_APP
  )



  $env:INTO_DOCKER = 'true'
  $env:DOTENV_KEY = $DOTENV_KEY
  $env:APPLICATION_APP = $APPLICATION_APP
  $env:SERVER_HOSTNAME = $SERVER_HOSTNAME

  if ($APPLICATION_APP -eq 'worker') {

    function StartWorker {
      param (
        [string] $DOTENV_KEY,
        [string] $APPLICATION_APP
      )

      poetry run celery -A app.run.app

    }

    poetry run celery -A app.run.app worker -E --loglevel=INFO -P threads -c 50

  } elseif ($APPLICATION_APP -eq 'quart') {

    function StartASGI {
      param (
        [string] $DOTENV_KEY,
        [string] $APPLICATION_APP
      )

      poetry run python -m app

    }

  } elseif ($APPLICATION_APP -eq 'beat') {
    function StartBeat {
      param (
        [string] $DOTENV_KEY,
        [string] $APPLICATION_APP
      )

      poetry run celery -A app.run.app beat --loglevel=INFO --scheduler job.FlaskSchedule.DatabaseScheduler

    }
  }

  switch ($APPLICATION_APP) {
    'worker' { StartWorker -DOTENV_KEY $DOTENV_KEY }
    'quart' { StartASGI -DOTENV_KEY $DOTENV_KEY }
    'beat' { StartBeat -DOTENV_KEY $DOTENV_KEY }
    default { Throw "Opção inválida: $APPLICATION_APP" }
  }

}

if ($APPLICATION_APP -is [string]) {
  Write-Host "Initializing $APPLICATION_APP"
  StartApp -DOTENV_KEY $DOTENV_KEY -APPLICATION_APP $APPLICATION_APP -SERVER_HOSTNAME $SERVER_HOSTNAME
} elseif ($APPLICATION_APP -is [System.Object]) {


  foreach ($app in $APPLICATION_APP) {

    if ($app -eq 'worker' -or $app -eq 'beat') {

      Write-Host "Initializing celery[$app]"

    } elseif ($app -eq 'quart') {

      Write-Host "Initializing asgi[$app]"
    }


    StartApp -DOTENV_KEY $DOTENV_KEY -APPLICATION_APP $app -SERVER_HOSTNAME $SERVER_HOSTNAME
  }
} else {
  Throw "Opção inválida: $APPLICATION_APP"

}
# SIG # Begin signature block
# MIII5QYJKoZIhvcNAQcCoIII1jCCCNICAQExCzAJBgUrDgMCGgUAMGkGCisGAQQB
# gjcCAQSgWzBZMDQGCisGAQQBgjcCAR4wJgIDAQAABBAfzDtgWUsITrck0sYpfvNR
# AgEAAgEAAgEAAgEAAgEAMCEwCQYFKw4DAhoFAAQUJc2iG0Xn1DiJ1lZa+l50i+58
# uL+gggZIMIIGRDCCBSygAwIBAgITHgAAFw+vQ2JVyMWIGwAAAAAXDzANBgkqhkiG
# 9w0BAQsFADBPMRgwFgYKCZImiZPyLGQBGRYIaW50cmFuZXQxEzARBgoJkiaJk/Is
# ZAEZFgNmbXYxHjAcBgNVBAMTFWZtdi1TUlYtQVNHQVJELURDMi1DQTAeFw0yNTAy
# MTExNDI3NDhaFw0yNjAyMTExNDI3NDhaMHAxGDAWBgoJkiaJk/IsZAEZFghpbnRy
# YW5ldDETMBEGCgmSJomT8ixkARkWA2ZtdjERMA8GA1UECxMIVVNVQVJJT1MxEzAR
# BgNVBAsTClQuSS4gLSBERVYxFzAVBgNVBAMTDk5pY2hvbGFzIFNpbHZhMIIBIjAN
# BgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2Btk8f9LgKVhfATflFIO2qNGiDnk
# hzkTrSht5E92DKeQATHz8gBoeb/tgsFCxbmhD/Tz8pwPrFnef5MxQO4qgdW17wUa
# hIVRgvsVgEWxm/FyQVw6rxty+ceVnHgD0BiQUfS7gA87tpwXhRpm7VoBg1+HtGQ7
# 8nX/eZsBVpvq1oCWRggrsSspo9Y/WF6fSszz2RgPTtb3PGR9hfCxt3sMf0/7rfar
# EaULKIINY3E6CWqyrmo7mdBWrQOBu+BcsnC2NODozcVyDgT/aWPNx5E29SxLlA9m
# cklwzNNZjMwbMm4B4RCxswWEDpgqZVceKUMGAbZWBkY3NlI88fW1L8FNDQIDAQAB
# o4IC9jCCAvIwJQYJKwYBBAGCNxQCBBgeFgBDAG8AZABlAFMAaQBnAG4AaQBuAGcw
# EwYDVR0lBAwwCgYIKwYBBQUHAwMwDgYDVR0PAQH/BAQDAgeAMB0GA1UdDgQWBBRP
# IYTcQglIKFxsAk+It2wecPU8mTAfBgNVHSMEGDAWgBQHujZf+/2B9+kUeELE3EIs
# MzGpbTCB2wYDVR0fBIHTMIHQMIHNoIHKoIHHhoHEbGRhcDovLy9DTj1mbXYtU1JW
# LUFTR0FSRC1EQzItQ0EsQ049U1JWLUFTR0FSRC1EQzIsQ049Q0RQLENOPVB1Ymxp
# YyUyMEtleSUyMFNlcnZpY2VzLENOPVNlcnZpY2VzLENOPUNvbmZpZ3VyYXRpb24s
# REM9Zm12LERDPWludHJhbmV0P2NlcnRpZmljYXRlUmV2b2NhdGlvbkxpc3Q/YmFz
# ZT9vYmplY3RDbGFzcz1jUkxEaXN0cmlidXRpb25Qb2ludDCB/QYIKwYBBQUHAQEE
# gfAwge0wgbUGCCsGAQUFBzAChoGobGRhcDovLy9DTj1mbXYtU1JWLUFTR0FSRC1E
# QzItQ0EsQ049QUlBLENOPVB1YmxpYyUyMEtleSUyMFNlcnZpY2VzLENOPVNlcnZp
# Y2VzLENOPUNvbmZpZ3VyYXRpb24sREM9Zm12LERDPWludHJhbmV0P2NBQ2VydGlm
# aWNhdGU/YmFzZT9vYmplY3RDbGFzcz1jZXJ0aWZpY2F0aW9uQXV0aG9yaXR5MDMG
# CCsGAQUFBzABhidodHRwOi8vU1JWLUFTR0FSRC1EQzIuZm12LmludHJhbmV0L29j
# c3AwNgYDVR0RBC8wLaArBgorBgEEAYI3FAIDoB0MG25pY2hvbGFzLnNpbHZhQGZt
# di5pbnRyYW5ldDBOBgkrBgEEAYI3GQIEQTA/oD0GCisGAQQBgjcZAgGgLwQtUy0x
# LTUtMjEtNjIzMTQyOTQxLTM4NTI4ODkxMjMtMTQyNDU1NDMxNy0xMTQyMA0GCSqG
# SIb3DQEBCwUAA4IBAQDDsgCQ8r2xmf/XVeOk4ENIK9UTla4tVwoauX6FgqBsKJ+S
# SDyiKJgKpotv2nevoxHdzFp+EnpeCVFfkH54cXPzvB/aIJDSeLlIUXNgfBqbBi3C
# h7owZ6t0ktB6rvFwXWvW7UPAPU2PPYcv2F5smjcHS+LlE99Z8OMCxw2+B4YLIGt0
# iGsOXzSEczxAwd+QB0j6rRFfnw8rSmVMt7XAfb/xtV5NXb1OgarEhj8S1U8SME7Q
# tjirWcvmO2jaHwn8MQnLYLBfkDorebphdQnEJkWFx4fnhLQYAj5K/eY5gY8CZ+SM
# kxzJk1rawLFRa1SkhCc5TscGusK2WG3PzxhXXYXPMYICBzCCAgMCAQEwZjBPMRgw
# FgYKCZImiZPyLGQBGRYIaW50cmFuZXQxEzARBgoJkiaJk/IsZAEZFgNmbXYxHjAc
# BgNVBAMTFWZtdi1TUlYtQVNHQVJELURDMi1DQQITHgAAFw+vQ2JVyMWIGwAAAAAX
# DzAJBgUrDgMCGgUAoHgwGAYKKwYBBAGCNwIBDDEKMAigAoAAoQKAADAZBgkqhkiG
# 9w0BCQMxDAYKKwYBBAGCNwIBBDAcBgorBgEEAYI3AgELMQ4wDAYKKwYBBAGCNwIB
# FTAjBgkqhkiG9w0BCQQxFgQUVU37VVi0wQbYp8iIW2xvcwN5234wDQYJKoZIhvcN
# AQEBBQAEggEAuK7HgGqid4BDaAcr5zj3yIMFZIhdQExHwMTR74L4sX/Afh+X+Hry
# SAHfk+bJvXY3GbTdnwBfxVki1ekGNyN6BnXVWsw90qKLIgChKO2wT7LFGaxVaI/6
# j5dBBaJq+NI6TiJ+LnwbH+pYZvoJk9qLz2y/n7ZOH2x+OQXexZKjeg49l5YxLb52
# /QE27C6TVMhfXg+fvjrOul4gBPuZf/2uQNlQuRa+FEDTLlok6h2o6clzeEsNM3cX
# WJfufGaNMaVqvB9dK5nU8ncQgSSulMK3/0JlpC4TmmKApFb+2v7+hE+PEf+YMay1
# YreiNzkTWmztr56aX+0Wh/l4Vc15NOFZnw==
# SIG # End signature block
