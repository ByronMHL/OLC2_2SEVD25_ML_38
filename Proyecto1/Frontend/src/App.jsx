import { createBrowserRouter, RouterProvider } from "react-router-dom";
import DashboardLayout from "./layout/DashboardLayout.jsx";
import CargaMasiva from "./pages/cargaMasiva.jsx";
import Ajuste from "./pages/Ajuste.jsx";
import Evaluacion from "./pages/Evaluacion.jsx";
import Prediccion from "./pages/Prediccion.jsx";

const router = createBrowserRouter([
  {
    element: <DashboardLayout />,
    children: [
      { path: "/", element: <CargaMasiva /> },
      { path: "/ajuste", element: <Ajuste /> },
      { path: "/evaluacion", element: <Evaluacion /> },
      { path: "/prediccion", element: <Prediccion /> },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
