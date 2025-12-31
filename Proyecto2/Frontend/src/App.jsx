import { createBrowserRouter, RouterProvider } from "react-router-dom";
import DashboardLayout from "./layout/DashboardLayout.jsx";
import CargaMasiva from "./pages/cargaMasiva.jsx";
import Entrenamiento from "./pages/Entrenamiento.jsx";
import Reportes from "./pages/Reportes.jsx";
import Evaluacion from "./pages/Evaluacion.jsx";

const router = createBrowserRouter([
  {
    element: <DashboardLayout />,
    children: [
      { path: "/", element: <CargaMasiva /> },
      { path: "/entrenamiento", element: <Entrenamiento /> },
      { path: "/evaluacion", element: <Evaluacion /> },
      { path: "/reportes", element: <Reportes /> },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
