import "../blog.css";
import { useState } from "react";

// PostCard component
const PostCard = ({
  image,
  title,
  category,
  content,
  publishedDate,
  readingTime,
  details,
  author,
}) => {
  // State for like button
  const [like, setLike] = useState(false);

  // Toggle like state
  function toggleLike() {
    setLike(!like);
  }

  return (
    <div className=" mt-6 w-64 py-4 px-4  relative flex-col flex justify-center">
      {/* Post image */}
      <img
        src={image}
        alt={title}
        width={"900px"}
        height={"300px"}
        className="rounded border-blue-600 border-6 "
      />
      <div className="rounded mt-6 bg-none py-4 relative overflow-hidden flex-auto border-solid text-sm">
        <div className="rounded mt-6 bg-none py-4 overflow-hidden flex-col border-solid text-sm align-middle">
          {/* Post title */}
          <span className="postcard--title">{title}</span>

          <div className="flex flex-wrap">
            <div className="flex flex-col">
              {/* Post category */}
              <span className="mr-2 font-bold">({category})</span>
              {/* Published date */}
              <span className="mr-2">{publishedDate}</span>
              {/* Reading time */}
              <span>{readingTime} min read</span>
              {/* Post content */}
              <span className="mr-2 postcard--content">{content}</span>
              {/* Post details */}
              <span className="postcard--details">{details}</span>
            </div>
          </div>
        </div>
        {/* Like button */}
        <div onClick={toggleLike} className="postcard--like">
          <img
            src={like ? "../img/fullheart.png" : "../img/emptyheart.png"}
            alt="like"
            className="like--button"
            title="Like"
          />

          {/* Like confirmation message */}
          {like && (
            <span className="like--text animate-bounce">
              Thanks for Liking!{" "}
            </span>
          )}
        </div>
        {/* Author name */}
        <span className="postcard--author">by {author}</span>
      </div>

      <hr className="font-bold" />
    </div>
  );
};

import PropTypes from "prop-types";

// PropTypes for PostCard component
PostCard.propTypes = {
  image: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  details: PropTypes.string.isRequired,
  content: PropTypes.string.isRequired,
  category: PropTypes.string.isRequired,
  author: PropTypes.string.isRequired,
  publishedDate: PropTypes.string.isRequired,
  readingTime: PropTypes.number.isRequired,
};

export default PostCard;
