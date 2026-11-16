$ErrorActionPreference = 'Stop'
$project = 'fieldnode-s7'
$composeArgs = @('compose', '-p', $project, '-f', 'docker-compose.mule.yml')

& docker @composeArgs up -d --build
if ($LASTEXITCODE -ne 0) { throw 'compose up falhou' }
Start-Sleep -Seconds 3
$webHealthy = $false
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    $health = (& docker inspect --format '{{.State.Health.Status}}' "${project}-web-1" 2>$null)
    if ($health -eq 'healthy') { $webHealthy = $true; break }
    Start-Sleep -Seconds 2
}
if (-not $webHealthy) { throw 'web não ficou saudável' }
& docker network disconnect "${project}_base_net" "${project}-mule-1"
if ($LASTEXITCODE -ne 0) { throw 'desconexão da base_net falhou' }
& docker network connect "${project}_field_net" "${project}-mule-1" 2>$null
if ($LASTEXITCODE -ne 0) { throw 'conexão da field_net falhou' }
& docker @composeArgs exec -T mule python -m simulators.transbordo_mule_client --edge-export-url http://edge:8081/outbox/export --mule-token s7-mule-token --mule-buffer-path /data/mule.db --api-url http://web:8000/api/telemetria/ --device-key demo-device-key --offline
if ($LASTEXITCODE -ne 0) { throw 'coleta HTTP falhou' }
& docker network disconnect "${project}_field_net" "${project}-mule-1"
if ($LASTEXITCODE -ne 0) { throw 'desconexão da field_net falhou' }
& docker network connect "${project}_base_net" "${project}-mule-1"
if ($LASTEXITCODE -ne 0) { throw 'conexão da base_net falhou' }
& docker @composeArgs exec -T mule python -m simulators.transbordo_mule_client --skip-edge-collection --mule-buffer-path /data/mule.db --api-url http://web:8000/api/telemetria/ --device-key demo-device-key --node-id mule-s7
if ($LASTEXITCODE -ne 0) { throw 'entrega HTTP falhou' }
& docker @composeArgs ps
