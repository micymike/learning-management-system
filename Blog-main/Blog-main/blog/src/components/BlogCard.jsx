import "../Home.css";
import { Link } from "react-router-dom";

const BlogCard = ({
  image,
  title,
  category,
  author,
  publishedDate,
  readingTime,
}) => {
  return (
    <div className="home--blogs_container">
    <div className="home--blogs">
      <Link to={`/blogs`}>
        <img
          src={image}
          alt={title}
          width={"300px"}
          height={"300px"}
          className="rounded border-blue-600 border-6 home--blog_image"
        />
      </Link>
      <div className="rounded mt-6 bg-none py-4 relative overflow-hidden  border-solid text-sm">
        <div className="rounded mt-6 bg-none py-2 overflow-hidden  border-solid text-sm align-middle">
          <span className="font-bold break-words home--blog_title">{title}</span>

          <div className="home--blog_content">
            <div className="flex flex-col">
            <span className="mr-2">{publishedDate}</span>
              <span>{readingTime} read</span>
              <span className="mr-2 home--blog_author"> &#64;{author}</span>
              
              <span className="mr-2 font-bold home--blog_category">{category}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
    
  
  );
};

import PropTypes from "prop-types";

BlogCard.propTypes = {
  image: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  content: PropTypes.string.isRequired,
  category: PropTypes.string.isRequired,
  author: PropTypes.string.isRequired,
  publishedDate: PropTypes.string.isRequired,
  readingTime: PropTypes.number.isRequired,
};

export default BlogCard;
