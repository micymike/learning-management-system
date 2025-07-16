import * as React from "react"; // Import React library
import * as ReactDOM from "react-dom/client"; // Import ReactDOM library for rendering
import { createBrowserRouter, RouterProvider } from "react-router-dom"; // Import routing components from react-router-dom
import "../src/style.css"; // Import CSS styles

// Import components
import App from "./App";
import Home from "./pages/Home";
import Blogs from "./pages/Blogs";
import Contact from "./pages/Contact";
import Editor from "./pages/Editor";
import SignIn from "./pages/SignIn";

// Define routes
const router = createBrowserRouter([
  {
    path: "/", // Root path
    element: <App />, // Render App component
    children: [
      {
        index: true, // Default route
        element: <Home />, // Render Home component
      },
      {
        path: "/blogs", // Route for blogs
        element: <Blogs />, // Render Blogs component
      },
      {
        path: "/editor", // Route for editor
        element: <Editor />, // Render Editor component
      },
      {
        path: "/signin", // Route for sign in
        element: <SignIn />, // Render SignIn component
      },
      {
        path: "/contact", // Route for contact
        element: <Contact />, // Render Contact component
      },
    ],
  },
]);

// Render the app
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <RouterProvider router={router} /> {/* Provide the router to the app */}
  </React.StrictMode>
);
