import React from "react";
import { createRoot } from "react-dom/client";
import InfiniteScroll from "react-infinite-scroll-component";
import Post from "./post";

// Create a root
const root = createRoot(document.getElementById("reactEntry"));

// Scroll to top when refreshing
function handleWindowBeforeUnload() {
  window.scrollTo(0, 0);
}

window.onbeforeunload = handleWindowBeforeUnload;

class App extends React.Component {
  constructor() {
    super();
    this.state = {
      items: [],
      hasMore: true,
      next: null,
    };
    this.fetchMoreData = this.fetchMoreData.bind(this);
  }

  componentDidMount() {
    fetch("/api/v1/posts/", {
      credentials: "same-origin",
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (!response.ok) throw Error(response.message);
        return response.json();
      })
      .then((data) => {
        let nextBool;
        if (data.next !== "") nextBool = true;
        else nextBool = false;
        this.setState({
          items: data.results,
          hasMore: nextBool,
          next: data.next,
        });
      })
      .catch((error) => console.log("Error with data fetching': ", error));
  }

  fetchData(url) {
    fetch(url, {
      credentials: "same-origin",
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (!response.ok) throw Error(response.message);
        return response.json();
      })
      .then((data) => {
        let nextBool;
        if (data.next !== "") nextBool = true;
        else nextBool = false;
        const { items } = this.state;
        this.setState({
          items: [...items, ...data.results],
          hasMore: nextBool,
          next: data.next,
        });
      })
      .catch((error) => console.log("Error with data fetching': ", error));
  }

  fetchMoreData() {
    // a fake async api call like which sends
    // 20 more records in .5 secs
    const { hasMore, next } = this.state;
    if (hasMore) {
      setTimeout(() => {
        this.fetchData(next);
      }, 500);
    }
  }

  render() {
    const { items, hasMore } = this.state;

    return (
      <div>
        {items !== [] ? (
          <InfiniteScroll
            dataLength={items.length}
            next={this.fetchMoreData}
            hasMore={hasMore}
            loader={<h4>Loading...</h4>}
          >
            {items.map(({ postid, url }) => (
              <div key={postid}>
                <Post url={url} />
                <br />
              </div>
            ))}
          </InfiniteScroll>
        ) : (
          <span />
        )}
      </div>
    );
  }
}

root.render(<App />);
