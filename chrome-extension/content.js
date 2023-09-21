// Get all the text nodes on the page
function getTextNodes(node) {
  const textNodes = [];
  if (node.nodeType === Node.TEXT_NODE) {
    if (node.nodeValue.trim() !== '') {
      textNodes.push(node);
    }
  } else {
    const childNodes = node.childNodes;
    for (let i = 0; i < childNodes.length; i++) {
      textNodes.push(...getTextNodes(childNodes[i]));
    }
  }
  return textNodes;
}

// Extract sentences from text nodes
function extractSentences(nodes) {
  const sentences = [];
  const regex = /[^.?!]+[.?!]*(?![.?!])/g;

  nodes.forEach(node => {
    const text = node.nodeValue.trim();
    const textSentences = text.match(regex);
    if (textSentences) {
      sentences.push(...textSentences);
    }
  });

  return sentences;
}

// Perform the sentence replacement
function replaceSentences() {
  console.log("Replacing sentences");
  // Get all sentences on the page
  const textNodes = getTextNodes(document.body);
  const sentences = extractSentences(textNodes);

  // POST request to replace_sentences endpoint
  fetch('http://localhost:5000/replace_sentences', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(sentences)
  })
    .then(response => response.json())
    .then(replacedSentences => {
      // Replace the original sentences with the returned list
      let sentenceIndex = 0;
      textNodes.forEach(node => {
        const text = node.nodeValue.trim();
        const textSentences = text.match(regex);
        if (textSentences) {
          for (let i = 0; i < textSentences.length; i++) {
            node.nodeValue = node.nodeValue.replace(textSentences[i], replacedSentences[sentenceIndex]);
            sentenceIndex++;
          }
        }
      });
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

console.log("This prints to the console of the page (injected only if the page url matched)")
// Execute the sentence replacement when the DOM is ready
document.addEventListener('DOMContentLoaded', replaceSentences);
