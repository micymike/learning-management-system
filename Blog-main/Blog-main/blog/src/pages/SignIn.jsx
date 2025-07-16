import { useRef, useState, useEffect } from "react";
import { FaUser, FaLock } from "react-icons/fa6";

// SignIn component
export default function SignIn() {
  // Refs for input fields
  const userRef = useRef();
  const errRef = useRef();

  // State variables
  const [user, setUser] = useState("");
  const [pwd, setPwd] = useState("");
  const [errMsg, setErrMsg] = useState("");
  const [success, setSuccess] = useState(false);
  const [showComponents, setShowComponents] = useState(true);

  // Focus on username input field on component mount
  useEffect(() => {
    userRef.current.focus();
  }, []);

  // Clear error message when user or password changes
  useEffect(() => {
    setErrMsg("");
  }, [user, pwd]);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log(user, pwd);
    setUser("");
    setPwd("");
    setSuccess(true);
  };

  // Handle return to blog
  const handleReturnToBlog = () => {
    setShowComponents(false);
  };

  return (
    <>
      {/* Render components if showComponents is true */}
      {showComponents && (
        <>
          {/* Render success message if success is true */}
          {success ? (
            <div className="fixed inset-0 flex items-center justify-center bg-blue-600 bg-opacity-75 z-50">
              <section className="bg-black border-blue-600 text-white p-8 rounded-md">
                <h1 className="text-2xl font-bold mb-4 flex items-center">
                  <FaUser className="mr-2" />
                  Welcome!
                </h1>
                <p className="mb-4">
                  <a
                    href="/blogs"
                    className="text-blue-600 hover:underline"
                    onClick={handleReturnToBlog}
                  >
                    Return to Blog
                  </a>
                </p>
              </section>
            </div>
          ) : (
            // Render sign-in form if success is false
            <div className="fixed inset-0 flex items-center justify-center bg-blue-600 bg-opacity-75 z-50 ">
              <section className="bg-black border-blue-600 text-white p-8 rounded-md ">
                <p
                  ref={errRef}
                  className={`${errMsg ? "text-red-500 mb-4" : "offscreen"}`}
                  aria-live="assertive"
                >
                  {errMsg}
                </p>
                <h1 className="text-2xl font-bold mb-4 flex items-center">
                  <FaUser className="mr-2" />
                  Sign In
                </h1>
                <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                  <div>
                    <label
                      htmlFor="username"
                      className=" mb-2 flex items-center"
                    >
                      <FaUser className="mr-2" />
                      UserName
                    </label>
                    <input
                      type="text"
                      ref={userRef}
                      autoComplete="off"
                      onChange={(e) => setUser(e.target.value)}
                      id="username"
                      value={user}
                      required
                      className="bg-gray-800 text-white px-4 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-600"
                    />
                  </div>
                  <div>
                    <label
                      htmlFor="password"
                      className=" mb-2 flex items-center"
                    >
                      <FaLock className="mr-2" />
                      Password
                    </label>
                    <input
                      type="password"
                      onChange={(e) => setPwd(e.target.value)}
                      id="password"
                      value={pwd}
                      required
                      className="bg-gray-800 text-white px-4 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-600"
                    />
                  </div>
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-white hover:text-blue-600 transition-all duration-200 ease-in">
                    Sign In
                  </button>
                </form>
              </section>
            </div>
          )}
        </>
      )}
    </>
  );
}
