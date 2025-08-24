import { createBrowserRouter, RouterProvider } from "react-router-dom";
import AppLayout from "../layout/AppLayout";
import Revision from "../pages/Revision";
import CompanyPrep from "../pages/CompanyPrep";

const router = createBrowserRouter([
  {
    element: <AppLayout />,
    children: [
      { path: "/", element: <Revision /> },
      { path: "/revision", element: <Revision /> },
      { path: "/company", element: <CompanyPrep /> },
    ],
  },
]);

export default function AppRouter() {
  return <RouterProvider router={router} />;
}
