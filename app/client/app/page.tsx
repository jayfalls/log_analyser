"use-client";
import Sidebar from "./components/sidebar"

function HomePage() {
  return (
    <div>
      <Sidebar />
      <div className="content">
        {/* Your main content goes here */}
      </div>
    </div>
  );
};

export default HomePage;