import Header from "../components/Header";
import Footer from "../components/Footer";
import PostCard from "../components/PostCard";
import blogsData from "../assets/blogsData.json";
import "../Home.css";

const Blogs = () => {
  // Render the Blogs component
  return (
    <>
      {/* Render the Header component */}
      <Header />
      {/* Render a div with a banner class */}
      <div className="w-full p-6 banner">
        {/* Render an h1 element with styling for the Blog Page title */}
        <h1 className="  flex justify-center text-center text-white font-bold text-6xl m-5 ">
          Blog Page
        </h1>
      </div>
      {/* Render a div with styling for the blog posts */}
      <div className="mt-6 bg-white py-4 px-4 border-solid relative">
        {/* Map over the blogsData array and render a PostCard component for each blog */}
        {blogsData.map((blog) => (
          <PostCard
            key={blog.id}
            image={blog.image}
            title={blog.title}
            content={blog.content}
            category={blog.category}
            author={blog.author}
            publishedDate={blog.published_date}
            readingTime={blog.reading_time}
            details={blog.details}
          />
        ))}
      </div>

      {/* Render the Footer component */}
      <Footer />
    </>
  );
};

export default Blogs;
