package org.example;

import org.json.JSONArray;
import org.json.JSONObject;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class Scatter3DAppTest {

    @AfterEach
    void clearApiUrl() {
        System.clearProperty("emrf.api.url");
    }

    @Test
    void payloadMatchesSimulationV1Contract() {
        JSONObject payload = Scatter3DApp.buildSimulationPayload();

        assertEquals(4, payload.getInt("n"));
        assertEquals(4, payload.getJSONArray("weights").length());
        assertEquals(4, payload.getJSONArray("X_grid").length());
        assertEquals(5, payload.getJSONArray("X_grid").getJSONArray(3).length());
    }

    @Test
    void apiUrlCanBeConfiguredWithoutChangingSource() {
        System.setProperty("emrf.api.url", "http://localhost:9000/api/v1/simulate");

        assertEquals(
            "http://localhost:9000/api/v1/simulate",
            Scatter3DApp.apiUrl()
        );
    }

    @Test
    void responseMappingUsesHighestEntropySliceAndFiniteValues() {
        JSONArray x = new JSONArray()
            .put(new JSONArray()
                .put(new JSONArray().put(new JSONArray().put(0.0).put(1.0)))
                .put(new JSONArray().put(new JSONArray().put(0.0).put(2.0))))
            .put(new JSONArray()
                .put(new JSONArray().put(new JSONArray().put(0.0).put(3.0)))
                .put(new JSONArray().put(new JSONArray().put(0.0).put(4.0))));

        List<Scatter3DApp.SimulationPoint> points =
            Scatter3DApp.parseSimulationPoints(new JSONObject().put("M", x));

        assertFalse(points.isEmpty());
        for (Scatter3DApp.SimulationPoint point : points) {
            assertTrue(Double.isFinite(point.matter));
        }
    }

    @Test
    void responseMappingReturnsFinitePointsWhenValuesAreUniform() {
        JSONArray x = new JSONArray()
            .put(new JSONArray()
                .put(new JSONArray().put(new JSONArray().put(0.0).put(2.0)))
                .put(new JSONArray().put(new JSONArray().put(0.0).put(2.0))));

        List<Scatter3DApp.SimulationPoint> points =
            Scatter3DApp.parseSimulationPoints(new JSONObject().put("M", x));

        assertFalse(points.isEmpty());
        assertEquals(2, points.size());
        assertTrue(points.stream().allMatch(point -> Double.isFinite(point.matter)));
    }
}
