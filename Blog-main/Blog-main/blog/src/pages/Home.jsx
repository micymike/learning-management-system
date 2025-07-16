// Import necessary components
import Header from "../components/Header";
import Footer from "../components/Footer";
import Banner from "../components/Banner";
import BlogCard from "../components/BlogCard";
import blogsData from "../assets/blogsData.json";

// Home component
const Home = () => {
  return (
    <>
      {/* Render Header component */}
      <Header />
      {/* Render Banner component */}
      <Banner />
      {/* Container for blog cards */}
      <div className="mt-6 bg-white py-4 px-4 border-solid relative">
        {/* Map over blogsData and render BlogCard for each blog */}
        {blogsData.map((blog) => (
          <BlogCard
            key={blog.id}
            image={blog.image}
            title={blog.title}
            content={blog.content}
            category={blog.category}
            author={blog.author}
            publishedDate={blog.published_date}
            readingTime={blog.reading_time}
          />
        ))}
      </div>
      {/* Render Footer component */}
      <Footer />
    </>
  );
};

// Export Home component
export default Home;
