import React from "react";
import PropTypes from "prop-types";

export default function Likes({ likes, lognameLikesThis, updateLikes }) {
  let text;
  if (lognameLikesThis) {
    text = "unlike";
  } else {
    text = "like";
  }

  return (
    <div>
      {likes === 1 ? <p> {likes} like </p> : <p> {likes} likes </p>}
      <button
        className="like-unlike-button"
        type="button"
        style={{ marginLeft: 11 }}
        onClick={updateLikes}
      >
        {text}
      </button>
    </div>
  );
}

Likes.propTypes = {
  likes: PropTypes.number.isRequired,
  lognameLikesThis: PropTypes.bool.isRequired,
  updateLikes: PropTypes.func.isRequired,
};
