# CLI reference

Generated from the supported `argparse` command tree. Do not edit manually.

Run `emrf COMMAND --help` for complete option semantics.

## `emrf`

Emergent Matter Research Framework (EMRF) command-line interface

```text
usage: emrf [-h] [--version]
            {list,run,simulate,data,recovery,performance,runs,jobs,kb,doctor,verify,predict,serve,test}
            ...
```

| Argument | Required | Description |
|---|---:|---|
| `--version` | No | show program's version number and exit |

### `emrf list`

Supported EMRF command.

```text
usage: emrf list [-h]
                 [--category {data,analysis,stress-test,figures,visualization,service,audit,release}]
                 [--json]
```

| Argument | Required | Description |
|---|---:|---|
| `--category` | No |  |
| `--json` | No |  |

### `emrf run`

Supported EMRF command.

```text
usage: emrf run [-h] [--timeout TIMEOUT] name ...
```

| Argument | Required | Description |
|---|---:|---|
| `name` | Yes |  |
| `--timeout` | No | seconds before aborting |
| `args` | No |  |

### `emrf simulate`

Supported EMRF command.

```text
usage: emrf simulate [-h] --n N --weights WEIGHTS [WEIGHTS ...] --grid GRID
                     [--k K] [--alpha ALPHA] [--C0 C0] [--output OUTPUT]
```

| Argument | Required | Description |
|---|---:|---|
| `--n` | Yes |  |
| `--weights` | Yes |  |
| `--grid` | Yes | comma-separated axis values, one flag per dimension; use the --grid=-1,0,1 form when values start with '-' |
| `--k` | No |  |
| `--alpha` | No |  |
| `--C0` | No |  |
| `--output` | No | save result as .npy instead of printing JSON |

### `emrf data`

Supported EMRF command.

```text
usage: emrf data [-h]
                 {list,catalog,info,import,fetch,verify,backup,backup-offsite,backup-verify,restore,drill,gc}
                 ...
```

#### `emrf data list`

Supported EMRF command.

```text
usage: emrf data list [-h] [--verify] [--json]
```

| Argument | Required | Description |
|---|---:|---|
| `--verify` | No | re-hash files (read-only) |
| `--json` | No |  |

#### `emrf data catalog`

Supported EMRF command.

```text
usage: emrf data catalog [-h] [--verify] [--json]
```

| Argument | Required | Description |
|---|---:|---|
| `--verify` | No | re-hash managed objects |
| `--json` | No |  |

#### `emrf data info`

Supported EMRF command.

```text
usage: emrf data info [-h] [--verify] dataset_id
```

| Argument | Required | Description |
|---|---:|---|
| `dataset_id` | Yes |  |
| `--verify` | No |  |

#### `emrf data import`

Supported EMRF command.

```text
usage: emrf data import [-h] [--source SOURCE] dataset_id [logical_name]
```

| Argument | Required | Description |
|---|---:|---|
| `dataset_id` | Yes |  |
| `logical_name` | No |  |
| `--source` | No | source file; requires one selected holding |

#### `emrf data fetch`

Supported EMRF command.

```text
usage: emrf data fetch [-h] [--retries RETRIES] [--timeout TIMEOUT]
                       dataset_id [logical_name]
```

| Argument | Required | Description |
|---|---:|---|
| `dataset_id` | Yes |  |
| `logical_name` | No |  |
| `--retries` | No |  |
| `--timeout` | No |  |

#### `emrf data verify`

Supported EMRF command.

```text
usage: emrf data verify [-h]
```

#### `emrf data backup`

Supported EMRF command.

```text
usage: emrf data backup [-h] destination
```

| Argument | Required | Description |
|---|---:|---|
| `destination` | Yes |  |

#### `emrf data backup-offsite`

Supported EMRF command.

```text
usage: emrf data backup-offsite [-h] [--destination-root DESTINATION_ROOT]
```

| Argument | Required | Description |
|---|---:|---|
| `--destination-root` | No | overrides EMRF_OFFSITE_BACKUP_DIR without storing credentials |

#### `emrf data backup-verify`

Supported EMRF command.

```text
usage: emrf data backup-verify [-h] source
```

| Argument | Required | Description |
|---|---:|---|
| `source` | Yes |  |

#### `emrf data restore`

Supported EMRF command.

```text
usage: emrf data restore [-h] source
```

| Argument | Required | Description |
|---|---:|---|
| `source` | Yes |  |

#### `emrf data drill`

Supported EMRF command.

```text
usage: emrf data drill [-h] [--receipt RECEIPT] [--workspace WORKSPACE]
```

| Argument | Required | Description |
|---|---:|---|
| `--receipt` | No | durable JSON receipt; defaults under the data root |
| `--workspace` | No | parent directory for temporary drill data |

#### `emrf data gc`

Supported EMRF command.

```text
usage: emrf data gc [-h] [--execute]
```

| Argument | Required | Description |
|---|---:|---|
| `--execute` | No | remove reported unreferenced objects |

### `emrf recovery`

Supported EMRF command.

```text
usage: emrf recovery [-h] {backup,backup-verify,restore,drill} ...
```

#### `emrf recovery backup`

Supported EMRF command.

```text
usage: emrf recovery backup [-h] destination
```

| Argument | Required | Description |
|---|---:|---|
| `destination` | Yes |  |

#### `emrf recovery backup-verify`

Supported EMRF command.

```text
usage: emrf recovery backup-verify [-h] source
```

| Argument | Required | Description |
|---|---:|---|
| `source` | Yes |  |

#### `emrf recovery restore`

Supported EMRF command.

```text
usage: emrf recovery restore [-h] source destination
```

| Argument | Required | Description |
|---|---:|---|
| `source` | Yes |  |
| `destination` | Yes |  |

#### `emrf recovery drill`

Supported EMRF command.

```text
usage: emrf recovery drill [-h] [--receipt RECEIPT] [--workspace WORKSPACE]
```

| Argument | Required | Description |
|---|---:|---|
| `--receipt` | No |  |
| `--workspace` | No |  |

### `emrf performance`

Supported EMRF command.

```text
usage: emrf performance [-h] {run,check} ...
```

#### `emrf performance run`

Supported EMRF command.

```text
usage: emrf performance run [-h] [--profile {test,standard}]
                            [--repeats REPEATS]
                            [--workload {covariance,catalog,run_artifacts,knowledge}]
```

| Argument | Required | Description |
|---|---:|---|
| `--profile` | No |  |
| `--repeats` | No |  |
| `--workload` | No | limit execution; repeat the option to select multiple workloads |

#### `emrf performance check`

Supported EMRF command.

```text
usage: emrf performance check [-h] [--profile {test,standard}]
                              [--repeats REPEATS]
                              [--workload {covariance,catalog,run_artifacts,knowledge}]
```

| Argument | Required | Description |
|---|---:|---|
| `--profile` | No |  |
| `--repeats` | No |  |
| `--workload` | No | limit execution; repeat the option to select multiple workloads |

### `emrf runs`

Supported EMRF command.

```text
usage: emrf runs [-h] {list,info,artifacts,artifact,resume} ...
```

#### `emrf runs list`

Supported EMRF command.

```text
usage: emrf runs list [-h] [--limit LIMIT] [--json]
```

| Argument | Required | Description |
|---|---:|---|
| `--limit` | No |  |
| `--json` | No |  |

#### `emrf runs info`

Supported EMRF command.

```text
usage: emrf runs info [-h] run_id
```

| Argument | Required | Description |
|---|---:|---|
| `run_id` | Yes |  |

#### `emrf runs artifacts`

Supported EMRF command.

```text
usage: emrf runs artifacts [-h] run_id
```

| Argument | Required | Description |
|---|---:|---|
| `run_id` | Yes |  |

#### `emrf runs artifact`

Supported EMRF command.

```text
usage: emrf runs artifact [-h] --output OUTPUT run_id path
```

| Argument | Required | Description |
|---|---:|---|
| `run_id` | Yes |  |
| `path` | Yes |  |
| `--output` | Yes |  |

#### `emrf runs resume`

Supported EMRF command.

```text
usage: emrf runs resume [-h] [--timeout TIMEOUT] run_id
```

| Argument | Required | Description |
|---|---:|---|
| `run_id` | Yes |  |
| `--timeout` | No |  |

### `emrf jobs`

Supported EMRF command.

```text
usage: emrf jobs [-h] {submit,list,info,cancel,run-next} ...
```

#### `emrf jobs submit`

Supported EMRF command.

```text
usage: emrf jobs submit [-h] [--timeout TIMEOUT] [--max-attempts MAX_ATTEMPTS]
                        [--evidence-class {observational,published,synthetic,illustrative,software}]
                        name ...
```

| Argument | Required | Description |
|---|---:|---|
| `name` | Yes |  |
| `--timeout` | No |  |
| `--max-attempts` | No |  |
| `--evidence-class` | No |  |
| `args` | No |  |

#### `emrf jobs list`

Supported EMRF command.

```text
usage: emrf jobs list [-h] [--limit LIMIT] [--json]
```

| Argument | Required | Description |
|---|---:|---|
| `--limit` | No |  |
| `--json` | No |  |

#### `emrf jobs info`

Supported EMRF command.

```text
usage: emrf jobs info [-h] job_id
```

| Argument | Required | Description |
|---|---:|---|
| `job_id` | Yes |  |

#### `emrf jobs cancel`

Supported EMRF command.

```text
usage: emrf jobs cancel [-h] job_id
```

| Argument | Required | Description |
|---|---:|---|
| `job_id` | Yes |  |

#### `emrf jobs run-next`

Supported EMRF command.

```text
usage: emrf jobs run-next [-h] [--worker-id WORKER_ID]
                          [--lease-seconds LEASE_SECONDS]
```

| Argument | Required | Description |
|---|---:|---|
| `--worker-id` | No |  |
| `--lease-seconds` | No |  |

### `emrf kb`

Supported EMRF command.

```text
usage: emrf kb [-h] {validate,query,add-source,export,link-run} ...
```

#### `emrf kb validate`

Supported EMRF command.

```text
usage: emrf kb validate [-h] [--json]
```

| Argument | Required | Description |
|---|---:|---|
| `--json` | No |  |

#### `emrf kb query`

Supported EMRF command.

```text
usage: emrf kb query [-h]
                     [--kind {concept,equation,dataset,source,software,model,run,result,claim,decision}]
                     [--status {proposed,tested,supported,refuted,retracted}]
                     [--limit LIMIT] [--json]
                     [text]
```

| Argument | Required | Description |
|---|---:|---|
| `text` | No |  |
| `--kind` | No |  |
| `--status` | No |  |
| `--limit` | No |  |
| `--json` | No |  |

#### `emrf kb add-source`

Supported EMRF command.

```text
usage: emrf kb add-source [-h] --title TITLE --author AUTHOR --year YEAR
                          (--doi DOI | --arxiv ARXIV | --ads-bibcode ADS_BIBCODE)
                          --snapshot-sha256 SNAPSHOT_SHA256 --bibtex-file
                          BIBTEX_FILE
                          source_id
```

| Argument | Required | Description |
|---|---:|---|
| `source_id` | Yes | stable id in source:<name> form |
| `--title` | Yes |  |
| `--author` | Yes |  |
| `--year` | Yes |  |
| `--doi` | No |  |
| `--arxiv` | No |  |
| `--ads-bibcode` | No |  |
| `--snapshot-sha256` | Yes |  |
| `--bibtex-file` | Yes |  |

#### `emrf kb export`

Supported EMRF command.

```text
usage: emrf kb export [-h] --output OUTPUT
```

| Argument | Required | Description |
|---|---:|---|
| `--output` | Yes |  |

#### `emrf kb link-run`

Supported EMRF command.

```text
usage: emrf kb link-run [-h] [--claim CLAIM] [--source SOURCE]
                        [--dataset DATASET]
                        run_id
```

| Argument | Required | Description |
|---|---:|---|
| `run_id` | Yes |  |
| `--claim` | No |  |
| `--source` | No |  |
| `--dataset` | No |  |

### `emrf doctor`

Supported EMRF command.

```text
usage: emrf doctor [-h] [--json] [--report [FILE]]
```

| Argument | Required | Description |
|---|---:|---|
| `--json` | No |  |
| `--report` | No | write a privacy-safe support report (default: EMRF support directory) |

### `emrf verify`

Supported EMRF command.

```text
usage: emrf verify [-h] {physics,inference,engines} ...
```

#### `emrf verify physics`

Supported EMRF command.

```text
usage: emrf verify physics [-h] [--json]
```

| Argument | Required | Description |
|---|---:|---|
| `--json` | No |  |

#### `emrf verify inference`

Supported EMRF command.

```text
usage: emrf verify inference [-h] [--json]
```

| Argument | Required | Description |
|---|---:|---|
| `--json` | No |  |

#### `emrf verify engines`

Supported EMRF command.

```text
usage: emrf verify engines [-h] [--json]
```

| Argument | Required | Description |
|---|---:|---|
| `--json` | No |  |

### `emrf predict`

Supported EMRF command.

```text
usage: emrf predict [-h] (--commit FILE | --verify FILE) [--label LABEL]
                    [--commitment-id COMMITMENT_ID]
```

| Argument | Required | Description |
|---|---:|---|
| `--commit` | No | commit the SHA-256 of prediction bytes |
| `--verify` | No | verify revealed prediction bytes |
| `--label` | No | human-readable prediction label |
| `--commitment-id` | No | commitment id used with --verify |

### `emrf serve`

Supported EMRF command.

```text
usage: emrf serve [-h] [--host HOST] [--port PORT]
```

| Argument | Required | Description |
|---|---:|---|
| `--host` | No |  |
| `--port` | No |  |

### `emrf test`

Supported EMRF command.

```text
usage: emrf test [-h] ...
```

| Argument | Required | Description |
|---|---:|---|
| `args` | No |  |
