# API Examples

These examples target the simulation endpoint where `X_grid` contains coordinate axes for multidimensional space $X = (x, y, z, d_0, \dots)$.

## Start server

```powershell
# from emergent_matter_model/
python server.py
# or using the virtual environment:
# .\.venv\Scripts\python.exe server.py
```

## PowerShell request (`/api/v1/simulate`)

```powershell
$body = @{
  n = 4
  weights = @(0.3, 0.3, 0.2, 0.2)
  X_grid = @(
    @(-2, -1, 0, 1, 2),
    @(-2, -1, 0, 1, 2),
    @(-2, -1, 0, 1, 2),
    @(0, 0.25, 0.5, 0.75, 1.0)
  )
  k = 1.0
  alpha = 1.0
  C0 = 1.0
} | ConvertTo-Json -Depth 10

Invoke-RestMethod \
  -Uri "http://127.0.0.1:5000/api/v1/simulate" \
  -Method Post \
  -ContentType "application/json" \
  -Body $body
```

## curl request (`/api/v1/simulate`)

```bash
curl -X POST "http://127.0.0.1:5000/api/v1/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "n": 4,
    "weights": [0.3, 0.3, 0.2, 0.2],
    "X_grid": [
      [-2, -1, 0, 1, 2],
      [-2, -1, 0, 1, 2],
      [-2, -1, 0, 1, 2],
      [0, 0.25, 0.5, 0.75, 1.0]
    ],
    "k": 1.0,
    "alpha": 1.0,
    "C0": 1.0
  }'
```

## Legacy endpoint (`/simulate`)

Use the same body and only change URL to:

- `http://127.0.0.1:5000/simulate`

## Data library

Catalog and verification reads do not require mutation privileges:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/v1/datasets"
Invoke-RestMethod `
  -Uri "http://127.0.0.1:5000/api/v1/datasets/sparc-rotation-curves?verify=true"
Invoke-RestMethod `
  -Uri "http://127.0.0.1:5000/api/v1/datasets/verify" `
  -Method Post
```

Imports, network fetches, backups, restores and destructive garbage collection
are disabled by default. Enable them only on a trusted host:

```powershell
$env:EMRF_API_ALLOW_DATA_WRITE = "1"
python server.py

$body = @{
  logical_name = "SPARC_Lelli2016c.mrt"
  retries = 3
  timeout = 180
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://127.0.0.1:5000/api/v1/datasets/sparc-rotation-curves/fetch" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

For an independent backup root, configure a mounted drive or cloud-synchronized
folder without placing credentials in the repository:

```powershell
$env:EMRF_OFFSITE_BACKUP_DIR = "E:\\EMRF-Offsite"
Invoke-RestMethod `
  -Uri "http://127.0.0.1:5000/api/v1/data/backups/offsite" `
  -Method Post `
  -ContentType "application/json" `
  -Body "{}"
```

The complete request and response contract is in `openapi.yaml`.

## Postman

Import collection:

- `postman/EmergentMatterAPI.postman_collection.json`
