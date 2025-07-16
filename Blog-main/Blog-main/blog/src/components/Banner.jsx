import { Link } from "react-router-dom";
import { TfiWrite } from "react-icons/tfi";
import "../Home.css";

export default function Banner() {
  return (
    <div className="bg-black p-6 banner">
      <h1 className=" justify-center text-center  font-bold text-6xl banner--heading">
        Welcome to<span className="banner--bloggy"> Bloggy</span>
      </h1>
      <h2 className=" flex justify-center font-bold text-center m-5 banner--description">
        Your go-to destination for insightful articles, engaging stories, and
        thought-provoking discussions. Bloggy is for everyone.
      </h2>
      <button className="chat-bot bg-black text-white rounded py-2 px-1">
        <a href="https://blogchatbot2-group9.streamlit.app/">
          Meta Llama Chat Bot
          <img
            src="https://img.icons8.com/?size=100&id=PvvcWRWxRKSR&format=png&color=000000"
            alt="meta"
            width={"30px"}
          />
        </a>
      </button>
      <div>
        <Link
          to="/editor"
          className="text-center flex justify-center font-small hover:text-white create--blog"
        >
          Create Blog <TfiWrite />
        </Link>
      </div>
    </div>
  );
}
