import React from "react";
import PropTypes from "prop-types";

export default function Comments({
  comments,
  textEntry,
  commentSubmit,
  handleTextBox,
  deleteComment,
}) {
  const uniqueId = Math.floor(Math.random() * 10000);

  return (
    <div>
      <div className="comment-text">
        {Object.entries(comments).map(([key, value]) => (
          <div key={key}>
            <p>
              {" "}
              <a href={`/users/${value.owner}/`}>
                <b> {value.owner} </b>{" "}
              </a>
            </p>
            <p> {value.text} </p>
            {value.lognameOwnsThis ? (
              <button
                className="delete-comment-button"
                type="button"
                style={{ marginLeft: 11 }}
                onClick={() => deleteComment(value.url, value.commentid)}
              >
                Delete comment
              </button>
            ) : (
              <span />
            )}
          </div>
        ))}
      </div>
      <br />
      <form className="comment-form" onSubmit={commentSubmit}>
        <label htmlFor={`comm-${uniqueId}`}>
          <input
            id={`comm-${uniqueId}`}
            type="text"
            value={textEntry}
            onChange={handleTextBox}
          />
        </label>
      </form>
    </div>
  );
}

const commentShape = PropTypes.shape({
  commentid: PropTypes.number.isRequired,
  owner: PropTypes.string.isRequired,
  text: PropTypes.string.isRequired,
  lognameOwnsThis: PropTypes.bool.isRequired,
  url: PropTypes.string.isRequired,
});

Comments.propTypes = {
  comments: PropTypes.arrayOf(commentShape).isRequired,
  textEntry: PropTypes.string.isRequired,
  commentSubmit: PropTypes.func.isRequired,
  handleTextBox: PropTypes.func.isRequired,
  deleteComment: PropTypes.func.isRequired,
};
