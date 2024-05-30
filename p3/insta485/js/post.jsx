import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import moment from "moment";
import Likes from "./likes";
import Comments from "./comments";

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */

  const [postId, setPostId] = useState(0);
  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [created, setCreated] = useState("");
  const [ownerImgUrl, setOwnerImgUrl] = useState("");
  const [numLikes, setNumLikes] = useState(0);
  const [likeUrl, setLikeUrl] = useState("");
  const [lognameLikesThis, setLognameLikesThis] = useState(false);
  const [comments, setComments] = useState([]);
  const [textEntry, setTextEntry] = useState("");

  const updateLikes = () => {
    if (lognameLikesThis) {
      fetch(likeUrl, {
        credentials: "same-origin",
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then((response) => {
          if (!response.ok) throw Error(response.message);
          return "";
        })
        .then(() => {
          setNumLikes(numLikes - 1);
          setLognameLikesThis(false);
        })
        .catch((error) => console.log("Error deleting like: ", error));
    } else {
      const createLikeUrl = `/api/v1/likes/?postid=${postId}`;
      fetch(createLikeUrl, {
        credentials: "same-origin",
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then((response) => {
          if (!response.ok) throw Error(response.message);
          return response.json();
        })
        .then((data) => {
          setNumLikes(numLikes + 1);
          setLognameLikesThis(true);
          setLikeUrl(data.url);
        })
        .catch((error) => console.log("Error creating like: ", error));
    }
  };

  const doubleClick = () => {
    if (!lognameLikesThis) {
      updateLikes();
    }
  };

  const deleteComment = (commentUrl, commentId) => {
    fetch(commentUrl, {
      credentials: "same-origin",
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (!response.ok) throw Error(response.message);
        return "";
      })
      .then(() => {
        const newComments = [];
        for (let i = 0; i < comments.length; i += 1) {
          if (comments[i].commentid !== commentId) {
            newComments.push(comments[i]);
          }
        }
        setComments(newComments);
      })
      .catch((error) => console.log("Error deleting like: ", error));
  };

  const commentSubmit = (event) => {
    // prevents website from refreshing (default action of form submission)
    event.preventDefault();
    const createCommentUrl = `/api/v1/comments/?postid=${postId}`;
    fetch(createCommentUrl, {
      credentials: "same-origin",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: textEntry }),
    })
      .then((response) => {
        if (!response.ok) throw Error(response.message);
        return response.json();
      })
      .then((data) => {
        const newComment = data;
        comments.push(newComment);
        setComments(comments);
        setTextEntry("");
      })
      .catch((error) => console.log("Error creating comment: ", error));
  };

  const handleTextBox = (event) => {
    setTextEntry(event.target.value);
  };

  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setPostId(data.postid);
          setImgUrl(data.imgUrl);
          setCreated(moment.utc(data.created).fromNow());
          setOwner(data.owner);
          setOwnerImgUrl(data.ownerImgUrl);
          setNumLikes(Number(data.likes.numLikes));
          setLikeUrl(data.likes.url);
          setLognameLikesThis(data.likes.lognameLikesThis);
          setComments(data.comments);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

  // Render post image and post owner
  return (
    <div>
      {postId !== 0 ? (
        <div className="post">
          <div className="post-header">
            <div className="post-left">
              <div className="user-img">
                <a href={`/users/${owner}/`}>
                  <img
                    src={ownerImgUrl}
                    alt="profile_pic"
                    width="30"
                    height="30"
                  />
                </a>
              </div>
              <div className="user">
                <a href={`/users/${owner}/`}>
                  <h1 style={{ fontSize: 15 }}> {owner} </h1>
                </a>
              </div>
            </div>
            <div className="post-right">
              <a href={`/posts/${postId}/`}>
                <h1 style={{ fontSize: 15, color: "grey" }}> {created} </h1>
              </a>
            </div>
          </div>
          <img src={imgUrl} alt="post_image" onDoubleClick={doubleClick} />
          <br />
          <div className="likes-and-comments">
            <Likes
              likes={numLikes}
              lognameLikesThis={lognameLikesThis}
              updateLikes={updateLikes}
            />
            <br />
            <Comments
              comments={comments}
              textEntry={textEntry}
              commentSubmit={commentSubmit}
              handleTextBox={handleTextBox}
              deleteComment={deleteComment}
            />
          </div>
          <br />
        </div>
      ) : (
        <span />
      )}
    </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};
