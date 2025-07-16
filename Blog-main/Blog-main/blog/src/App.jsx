// @blog\src\App.jsx
import { Outlet } from "react-router-dom";
import "../src/style.css";

// App component
function App() {
  return (
    <>
      <div>
        {/* Render nested routes */}
        <Outlet />
      </div>
    </>
  );
}
export default App;
