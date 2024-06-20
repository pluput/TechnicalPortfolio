const { createApp } = Vue

createApp({
  data() {
    return {
      image: 'https://music.apple.com/us/artist/ayokay/648926675?uo=4&origin=*',
      resultCount: 0,
      enteredSearch: '',
      results: [],
      resultsToShow: [],
      resetToOriginalActive: true,
      collectionNameActive: false,
      priceActive: false,
      allActive: true,
      categoriesGiven: [],
      categoriesChosen: [],
      play: new Map(),
      audio: ''
    }
  },
  methods: {
    enterPressed: function() {
      var url = "https://itunes.apple.com/search?term=" + this.enteredSearch + "&attribute=allArtistTerm";
      url = url.replace(/\s/g, '+');

      this.resultCount = 0;
      this.results = [];
      this.resultsToShow = [];
      this.resetToOriginalActive = true;
      this.collectionNameActive = false;
      this.priceActive = false;
      this.allActive = true;
      this.categoriesGiven = [];
      this.categoriesChosen = [];
      this.play = new Map();

      fetch(url)
        .then(response => {
          if (!response.ok) {
            throw new Error ('Not A Valid Link!');
          }
          return response.json();
        })
        .then(results => {
          this.resultCount = results.resultCount;
          console.log(results);
          if (this.resultCount == 0) {
            alert("No Artist Was Found With The Keyword");
          }

          this.results = this.results.concat(results.results);
          this.resultsToShow = this.resultsToShow.concat(this.results);

          for (let i = 0; i < this.resultCount; i++) {
            if (this.categoriesGiven.indexOf(this.results[i].primaryGenreName) === -1) {
              this.categoriesGiven.push(this.results[i].primaryGenreName);
            }

            this.play.set(this.results[i].trackId, 'Play');
          }
        })
        .catch((error) => {
          console.log('fetcherror: ${error}');
        })
    },

    resetToOriginal: function () {
      this.resetToOriginalActive = true;
      this.collectionNameActive = false;
      this.priceActive = false;

      //we find what genres are currently selected, make them false and pretend they were clicked on again
      //  this way we get the original order back
      if (this.allActive) {
        this.allActiveClick();
      }
      else {
        tempCategory = this.categoriesChosen[0];
        this.categoriesChosen.splice(0, 1);
        this.categoryActiveClick(tempCategory);
      }
    },

    collectionName: function () {
      this.resetToOriginalActive = false;
      this.collectionNameActive = true;
      this.priceActive = false;

      this.resultsToShow.sort(this.compareCollectionName);
    },

    price: function (event) {
      this.resetToOriginalActive = false;
      this.collectionNameActive = false;
      this.priceActive = true;

      this.resultsToShow.sort(this.comparePrice);
    },

    compareCollectionName: function(a, b) {
      if (a.collectionName < b.collectionName) {
        return -1;
      }
      else if (a.collectionName > b.collectionName) {
        return 1;
      }
      else {
        return 0;
      }
    },

    comparePrice: function(a, b) {
      if (a.collectionPrice < b.collectionPrice) {
        return -1;
      }
      else if (a.collectionPrice > b.collectionPrice) {
        return 1;
      }
      else {
        return 0;
      }
    },

    allActiveClick: function () {
      //set allActive to true, all else to false
      this.allActive = true;
      this.categoriesChosen = [];

      //show original results and count
      this.resultsToShow = [];
      this.resultsToShow = this.resultsToShow.concat(this.results);
      this.resultCount = this.resultsToShow.length;

      //here we make sure its all still sorted by collection name or price
      //  original sort won't be affected
      if (this.collectionNameActive) {
        this.resultsToShow.sort(this.compareCollectionName);
      }
      else if (this.priceActive) {
        this.resultsToShow.sort(this.comparePrice);
      }
    },

    categoryActiveClick: function (category) {
      //set 'category' button to true or 'all' to true if user is unclicking 'category'
      if (this.allActive) {
        this.allActive = false;
      }

      if (!(this.categoriesChosen.indexOf(category) === -1) && this.categoriesChosen.length === 1) {
        this.categoriesChosen.splice(this.categoriesChosen.indexOf(category), 1);
        this.allActive = true;
        this.resultsToShow = [];
        this.resultsToShow = this.resultsToShow.concat(this.results);
      }
      else if (!(this.categoriesChosen.indexOf(category) === -1)) {
        this.categoriesChosen.splice(this.categoriesChosen.indexOf(category), 1);
        tempArray = [];
        for (i of this.resultsToShow) {
          if (i.primaryGenreName != category) {
            tempArray.push(i);
          }
        }
        this.resultsToShow = [];
        this.resultsToShow = this.resultsToShow.concat(tempArray);
      }
      else {
        this.categoriesChosen.push(category);
        tempArray = [];
        for (i of this.results) {
          for (j of this.categoriesChosen) {
            if (i.primaryGenreName === j) {
              tempArray.push(i);
              continue;
            }
          }
        }

        this.resultsToShow = [];
        this.resultsToShow = this.resultsToShow.concat(tempArray);
      }

      //set resultCount to curr length
      this.resultCount = this.resultsToShow.length;

      //here we make sure its all still sorted by collection name or price
      //  original sort won't be affected
      if (this.collectionNameActive) {
        this.resultsToShow.sort(this.compareCollectionName);
      }
      else if (this.priceActive) {
        this.resultsToShow.sort(this.comparePrice);
      }
    },

    playButton: function (result) {

      if (this.play.get(result.trackId) === 'Play') {
        if (this.audio) {
          alert("STOP CURRENT SONG TO PLAY NEW ONE");
          return;
        }
        this.play.set(result.trackId, 'Stop');
        this.audio = new Audio(result.previewUrl);
        this.audio.play();
      }

      else {
        this.play.set(result.trackId, 'Play');
        this.audio.pause();
        this.audio.currentTime = 0;
        this.audio = '';
      }
    },

    sortListPopUp: function () {
      sortedNames = [];
      for (let i = 0; i < this.resultCount; i++) {
        sortedNames.push(this.results[i].collectionName);
      }

      sortedNames.sort();
      alert(sortedNames.join(", "));
    }

  }
}).mount('#app')