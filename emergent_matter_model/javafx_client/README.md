# JavaFX client

This client renders a 3D scatter plot from the Python simulation API:

- Endpoint: `POST http://127.0.0.1:5000/api/v1/simulate`
- Data source: entropy-aware model output (`M[x,y,z,S]`)
- Display mode: highest-entropy slice (`S = S_max`) as a 3D point cloud

## Run

Prerequisites:

- Java JDK 17+ (e.g. JDK 17, 21, or 25) with `JAVA_HOME` configured
- Internet access for the first dependency restore; the checked-in Maven
  Wrapper supplies Maven 3.9.9

1. Start the Python backend from `emergent_matter_model`:
	- `python server.py`
2. In this `javafx_client` folder, launch the JavaFX app:
	- Windows: `mvnw.cmd javafx:run`
	- Linux/macOS: `./mvnw javafx:run`

If the backend is not reachable, the app starts with fallback sample points and indicates that in the window title.
Set `EMRF_API_URL` or the Java system property `emrf.api.url` to target a
different REST v1 simulation endpoint.

Run the client contract tests with `mvnw.cmd test` on Windows or
`./mvnw test` on Linux/macOS.

API schema and Java mapping details:

- Python OpenAPI spec: `../openapi.yaml`
- Java contract note: `API_CONTRACT.md`

See https://openjfx.io/ for JavaFX setup details.
