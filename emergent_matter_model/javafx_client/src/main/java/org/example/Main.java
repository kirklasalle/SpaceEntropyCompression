package org.example;

import javafx.application.Application;

/**
 * Application entry point for the Emergent Matter JavaFX client.
 *
 * Delegates to {@link Scatter3DApp} for 3-D scatter visualisation.
 * In a future version this will add a menu to choose between different
 * visualisation modes and fetch data from the Python REST API.
 */
public class Main {
    public static void main(String[] args) {
        Application.launch(Scatter3DApp.class, args);
    }
}
