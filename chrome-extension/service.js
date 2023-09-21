function extractSentences() {
    const sentences = [];
    const order = [];
    const regex = /[^.?!]{1,100}[.?!]+|[^.?!]{1,100}\b|[^.?!]{1,100}/g;
    const elements = document.querySelectorAll("p, h1, h2, h3, h4, h5, h6, td");

    elements.forEach(element => {
        const text = element.textContent;
        const matches = text.match(regex);

        if (matches) {
            matches.forEach(match => {
                if (match.length > 1) {
                    sentences.push(match.trim())
                    order.push(element);
                }
            });
        }
    });

    const replacements = [];
    const chunkSize = 30;
    for (let i = 0; i < sentences.length; i += chunkSize) {
        const chunk = sentences.slice(i, i + chunkSize);
        chrome.runtime.sendMessage({ sentences: chunk }, function (response) {
            replaceSentencesOnPage(order.slice(i, i + chunkSize), sentences.slice(i, i + chunkSize), response.replacements);
        });
    }

}

function replaceSentencesOnPage(elements, originals, replacements) {
    if (!replacements.replacements) return;
    console.log(originals);
    console.log(replacements);
    for (var i = 0; i < elements.length; i++) {
        const element = elements[i];
        const originalSentence = originals[i];
        const replacedSentence = replacements.replacements[i];

        if (originalSentence === replacedSentence)
            continue;
        
        element.innerHTML = element.innerHTML.replace(originalSentence, `<span class="replaced-${i}">${replacedSentence}</span>`);
        element.addEventListener("mouseenter", makeOriginal(element, originalSentence, replacedSentence, i), { once: true });
    }
}

function makeOriginal(element, originalSentence, replacedSentence, i) {
    return () => {
        element.innerHTML = element.innerHTML.replace(`<span class="replaced-${i}">${replacedSentence}</span>`, `<span class="original-${i}" style="color: green;">${originalSentence}</span>`);
        element.classList.add("hovered");
        element.addEventListener("mouseleave", makeReplaced(element, originalSentence, replacedSentence, i), { once: true });
    }
}

function makeReplaced(element, originalSentence, replacedSentence, i) {
    return () => {
        element.innerHTML = element.innerHTML.replace(`<span class="original-${i}" style="color: green;">${originalSentence}</span>`, `<span class="replaced-${i}">${replacedSentence}</span>`);
        element.classList.remove("hovered");
        element.addEventListener("mouseenter", makeOriginal(element, originalSentence, replacedSentence, i), { once: true });
    }
}

extractSentences();
