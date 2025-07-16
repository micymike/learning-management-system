import { useEffect, useState } from "react";

const BlogList = () => {
  const [blogs, setBlogs] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/blogs")
      .then((response) => response.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setBlogs(data);
        } else {
          setError("Invalid data format");
        }
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
        setError("Error fetching data");
      });
  }, []);

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="blog-list">
      <h1 className="font-bold text-3xl">Blog List</h1>
      {blogs.length > 0 ? (
        blogs.map((blog) => (
          <div
            key={blog.id}
            className="blog-item border border-gray-400 rounded-md p-4 mb-4"
          >
            <h2 className="font-bold text-2xl">{blog.title}</h2>
            <img src={blog.image} alt={blog.title} className="blog-image" />
            <p>
              <strong>Category:</strong> {blog.category}
            </p>
            <p>
              <strong>Author:</strong> {blog.author}
            </p>
            <p>
              <strong>Published Date:</strong> {blog.published_date}
            </p>
            <p>
              <strong>Reading Time:</strong> {blog.reading_time}
            </p>
            <p>{blog.content}</p>
            <p>
              <strong>Tags:</strong> {blog.tags.join(", ")}
            </p>
          </div>
        ))
      ) : (
        <p>No blogs available.</p>
      )}
    </div>
  );
};

export default BlogList;
