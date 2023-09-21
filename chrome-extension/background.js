chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.sentences) {
    const url = "http://localhost:5000/replace_sentences";

    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ sentences: request.sentences })
    })
      .then(response => response.json())
      .then(replacements => {
        sendResponse({ replacements: replacements });
      })
      .catch(error => {
        console.log("Unable to fetch replacement sentences from server.");
        sendResponse({ replacements: [] }); // Send an empty array in case of an error
      });

    return true; // Indicates that sendResponse will be called asynchronously
  }
});

chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  if (message.action === 'postWords') {
    chrome.storage.sync.get('words', function (data) {
      const wordList = data.words;
      if (wordList) {
        // Perform your POST request to http://localhost:5000
        const url = 'http://localhost:5000/set_src_list'; // Replace with your server URL
        const requestBody = { words: wordList };

        fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
        })
          .then(function (response) {
            if (response.ok) {
              console.log('Words posted successfully');
            } else {
              console.error('Failed to post words');
            }
          })
          .catch(function (error) {
            console.error('Error:', error);
          });
      }
    });
  }
});
