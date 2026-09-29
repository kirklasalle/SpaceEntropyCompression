# JavaFX client

This client renders a 3D scatter plot from the Python simulation API:

- Endpoint: `POST http://127.0.0.1:5000/api/v1/simulate`
- Data source: entropy-aware model output (`M[x,y,z,S]`)
- Display mode: highest-entropy slice (`S = S_max`) as a 3D point cloud

## Run

Prerequisites:

- Java JDK installed (set `JAVA_HOME` to the JDK root)
	- Your confirmed path: `G:\Program Files\Java\jdk-25.0.2`
- Maven on PATH (you can use `../install_maven.ps1` from workspace root)

1. Start the Python backend from `emergent_matter_model`:
	- `python server.py`
2. In this `javafx_client` folder, launch the JavaFX app:
	- `mvn javafx:run`

If the backend is not reachable, the app starts with fallback sample points and indicates that in the window title.

API schema and Java mapping details:

- Python OpenAPI spec: `../openapi.yaml`
- Java contract note: `API_CONTRACT.md`

See https://openjfx.io/ for JavaFX setup details.
