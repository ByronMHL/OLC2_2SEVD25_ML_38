import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css"; // Tailwind import

// Limpieza segura de cache al iniciar la app
// Evita mostrar resultados viejos tras reiniciar el backend
try {
  // Borra solo las claves usadas por Evaluación
  localStorage.removeItem('trainingResults')
  localStorage.removeItem('tuningResults')
} catch (e) {
  // Ignorar errores de acceso a localStorage
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);