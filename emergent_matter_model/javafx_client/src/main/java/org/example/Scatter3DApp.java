package org.example;

import javafx.application.Application;
import javafx.scene.*;
import javafx.scene.paint.Color;
import javafx.scene.paint.PhongMaterial;
import javafx.scene.shape.Sphere;
import javafx.scene.transform.Rotate;
import javafx.stage.Stage;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

/**
 * 3-D scatter-plot viewer for Emergent Matter Model data.
 *
 * Currently uses hard-coded sample points.  A future version will fetch
 * simulation results from the Python REST API (entropy as the last
 * dimensional coordinate).
 */
public class Scatter3DApp extends Application {

    private static final String API_URL = "http://127.0.0.1:5000/api/v1/simulate";

    private static final class SimulationPoint {
        final double x;
        final double y;
        final double z;
        final double matter;

        SimulationPoint(double x, double y, double z, double matter) {
            this.x = x;
            this.y = y;
            this.z = z;
            this.matter = matter;
        }
    }

    private static double[] linspace(double start, double end, int count) {
        double[] values = new double[count];
        if (count == 1) {
            values[0] = start;
            return values;
        }
        double step = (end - start) / (count - 1);
        for (int i = 0; i < count; i++) {
            values[i] = start + i * step;
        }
        return values;
    }

    private static JSONObject buildSimulationPayload() {
        double[] x = linspace(-2.0, 2.0, 11);
        double[] y = linspace(-2.0, 2.0, 11);
        double[] z = linspace(-2.0, 2.0, 11);
        double[] s = linspace(0.0, 1.0, 5);

        JSONArray xGrid = new JSONArray();
        JSONArray yGrid = new JSONArray();
        JSONArray zGrid = new JSONArray();
        JSONArray sGrid = new JSONArray();
        for (double value : x) xGrid.put(value);
        for (double value : y) yGrid.put(value);
        for (double value : z) zGrid.put(value);
        for (double value : s) sGrid.put(value);

        JSONArray xGridAll = new JSONArray();
        xGridAll.put(xGrid);
        xGridAll.put(yGrid);
        xGridAll.put(zGrid);
        xGridAll.put(sGrid);

        JSONArray weights = new JSONArray();
        weights.put(0.3);
        weights.put(0.3);
        weights.put(0.2);
        weights.put(0.2);

        JSONObject payload = new JSONObject();
        payload.put("n", 4);
        payload.put("weights", weights);
        payload.put("X_grid", xGridAll);
        payload.put("k", 1.0);
        payload.put("alpha", 1.0);
        payload.put("C0", 1.0);
        return payload;
    }

    private static List<SimulationPoint> fetchSimulationPoints() throws IOException, InterruptedException {
        HttpClient client = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(3))
            .build();

        JSONObject payload = buildSimulationPayload();
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(API_URL))
            .timeout(Duration.ofSeconds(20))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(payload.toString()))
            .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() != 200) {
            throw new IOException("API error status " + response.statusCode() + ": " + response.body());
        }

        JSONObject json = new JSONObject(response.body());
        JSONArray m = json.getJSONArray("M");

        int nx = m.length();
        int ny = m.getJSONArray(0).length();
        int nz = m.getJSONArray(0).getJSONArray(0).length();
        int ns = m.getJSONArray(0).getJSONArray(0).getJSONArray(0).length();
        int sIndex = ns - 1;

        List<SimulationPoint> points = new ArrayList<>(nx * ny * nz);
        double minMatter = Double.POSITIVE_INFINITY;
        double maxMatter = Double.NEGATIVE_INFINITY;

        for (int ix = 0; ix < nx; ix++) {
            JSONArray yArr = m.getJSONArray(ix);
            for (int iy = 0; iy < ny; iy++) {
                JSONArray zArr = yArr.getJSONArray(iy);
                for (int iz = 0; iz < nz; iz++) {
                    double matter = zArr.getJSONArray(iz).getDouble(sIndex);
                    if (Double.isFinite(matter)) {
                        minMatter = Math.min(minMatter, matter);
                        maxMatter = Math.max(maxMatter, matter);
                    }
                    double xCoord = ((double) ix / (nx - 1) - 0.5) * 320.0;
                    double yCoord = ((double) iy / (ny - 1) - 0.5) * 320.0;
                    double zCoord = ((double) iz / (nz - 1) - 0.5) * 320.0;
                    points.add(new SimulationPoint(xCoord, yCoord, zCoord, matter));
                }
            }
        }

        if (!Double.isFinite(minMatter) || !Double.isFinite(maxMatter)) {
            minMatter = 0.0;
            maxMatter = 1.0;
        }

        double range = Math.max(maxMatter - minMatter, 1e-9);
        List<SimulationPoint> filtered = new ArrayList<>();
        for (SimulationPoint p : points) {
            if (!Double.isFinite(p.matter)) {
                continue;
            }
            double normalized = (p.matter - minMatter) / range;
            if (normalized >= 0.45) {
                filtered.add(new SimulationPoint(p.x, p.y, p.z, normalized));
            }
        }

        return filtered.isEmpty() ? points : filtered;
    }

    private static List<SimulationPoint> fallbackPoints() {
        List<SimulationPoint> points = new ArrayList<>();
        points.add(new SimulationPoint(0, 0, 0, 1.0));
        points.add(new SimulationPoint(50, 50, 50, 0.9));
        points.add(new SimulationPoint(-50, -50, -50, 0.9));
        points.add(new SimulationPoint(100, 0, 0, 0.8));
        points.add(new SimulationPoint(0, 100, 0, 0.8));
        points.add(new SimulationPoint(0, 0, 100, 0.8));
        points.add(new SimulationPoint(-100, 0, 0, 0.8));
        points.add(new SimulationPoint(0, -100, 0, 0.8));
        points.add(new SimulationPoint(0, 0, -100, 0.8));
        return points;
    }

    @Override
    public void start(Stage primaryStage) {
        Group root = new Group();

        List<SimulationPoint> points;
        boolean usingFallback = false;
        try {
            points = fetchSimulationPoints();
        } catch (Exception ex) {
            points = fallbackPoints();
            usingFallback = true;
            ex.printStackTrace();
        }

        for (SimulationPoint p : points) {
            double radius = 3.0 + 7.0 * Math.max(0.0, Math.min(1.0, p.matter));
            Sphere sphere = new Sphere(radius);
            PhongMaterial material = new PhongMaterial();
            Color color = Color.color(0.2 + 0.7 * Math.max(0.0, Math.min(1.0, p.matter)), 0.5, 1.0);
            material.setDiffuseColor(color);
            sphere.setMaterial(material);
            sphere.setTranslateX(p.x);
            sphere.setTranslateY(p.y);
            sphere.setTranslateZ(p.z);
            root.getChildren().add(sphere);
        }

        PerspectiveCamera camera = new PerspectiveCamera(true);
        camera.setTranslateZ(-500);
        camera.setNearClip(0.1);
        camera.setFarClip(10000.0);
        camera.setFieldOfView(35);

        Scene scene = new Scene(root, 800, 600, true);
        scene.setFill(Color.BLACK);
        scene.setCamera(camera);

        // Add rotation for better 3-D perspective
        Rotate rotateX = new Rotate(30, Rotate.X_AXIS);
        Rotate rotateY = new Rotate(30, Rotate.Y_AXIS);
        root.getTransforms().addAll(rotateX, rotateY);

        if (usingFallback) {
            primaryStage.setTitle("Emergent Matter — 3D Scatter (fallback data; start Python server)");
        } else {
            primaryStage.setTitle("Emergent Matter — 3D Scatter (live API)");
        }
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
