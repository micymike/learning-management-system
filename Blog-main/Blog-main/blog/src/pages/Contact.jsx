import Header from "../components/Header";
// Import the Header component from the "../components/Header" file

import Footer from "../components/Footer";
// Import the Footer component from the "../components/Footer" file

import "../Home.css";
// Import the CSS styles from the "../Home.css" file

const Contact = () => {
  return (
    <>
      {/* Render the Header component */}
      <Header />

      {/* Render a div with background color black, white text, full width, padding of 6, and the "banner" class */}
      <div className="bg-black text-white w-full p-6 banner">
        {/* Render an h1 element with flex, center alignment, white text, bold font, font size of 6xl, and margin of 5 */}
        <h1 className="  flex justify-center text-center text-white font-bold text-6xl m-5">
          Contact Page
        </h1>
      </div>

      {/* Render a div with a container class, automatic horizontal margin, and vertical padding of 8 */}
      <div className="container mx-auto py-8">
        {/* Render an h1 element with font size of 3xl, bold font, and bottom margin of 4 */}
        <h1 className="text-3xl font-bold mb-4">Contact Us</h1>

        {/* Render a form element */}
        <form>
          {/* Render a div with bottom margin of 4 */}
          <div className="mb-4">
            {/* Render a label element with "block" display, bold font, and bottom margin of 2 */}
            <label htmlFor="name" className="block font-bold mb-2">
              Name
            </label>
            {/* Render an input element of type "text", with id "name", full width, border with gray color, padding of 2, and rounded corners */}
            <input
              type="text"
              id="name"
              className="w-full border border-gray-400 p-2 rounded"
              placeholder="Enter your name"
            />
          </div>

          {/* Render a div with bottom margin of 4 */}
          <div className="mb-4">
            {/* Render a label element with "block" display, bold font, and bottom margin of 2 */}
            <label htmlFor="email" className="block font-bold mb-2">
              Email
            </label>
            {/* Render an input element of type "email", with id "email", full width, border with gray color, padding of 2, and rounded corners */}
            <input
              type="email"
              id="email"
              className="w-full border border-gray-400 p-2 rounded"
              placeholder="Enter your email"
            />
          </div>

          {/* Render a div with bottom margin of 4 */}
          <div className="mb-4">
            {/* Render a label element with "block" display, bold font, and bottom margin of 2 */}
            <label htmlFor="message" className="block font-bold mb-2">
              Message
            </label>
            {/* Render a textarea element with id "message", full width, border with gray color, padding of 2, rounded corners, and 4 rows */}
            <textarea
              id="message"
              className="w-full border border-gray-400 p-2 rounded"
              rows="4"
              placeholder="Enter your message"
            ></textarea>
          </div>

          {/* Render a button element of type "submit", with background color blue-500, hover background color blue-700, white text, bold font, vertical padding of 2, horizontal padding of 4, and rounded corners */}
          <button
            type="submit"
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Submit
          </button>
        </form>
      </div>

      {/* Render the Footer component */}
      <Footer />
    </>
  );
};

// Export the Contact component as the default export
export default Contact;
