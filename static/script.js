document.getElementById("translate-btn").addEventListener("click", async () => {
  const inputText = document.getElementById("input-text").value;
  if (!inputText) {
    alert("Please enter some text.");
    return;
  }

  try {
    const extendedBreakdown = document.getElementById("breakdown-type").checked;

    const response = await fetch("/translate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sentence: inputText,
        extended: extendedBreakdown, // Send the checkbox state
      }),
    });

    const data = await response.json();
    document.getElementById("translation-output").value = data.translation;

    const breakdownOutput = document.getElementById("breakdown-output");
    breakdownOutput.innerHTML = data.breakdown
      .map((item) => {
        // Check if token and lemma are the same
        const displayLemma =
          item.token !== item.lemma
            ? `<br><strong>Base Form:</strong> ${item.lemma}`
            : "";

        // Handle extended definitions (which might contain newlines)
        const definition = extendedBreakdown
          ? item.definition.replace(/\n/g, "<br>")
          : item.definition;

        return `
                <div class="breakdown-item">
                    <strong>Word:</strong> ${item.token}${displayLemma}<br>
                    <strong>Type:</strong> ${item.pos}<br>
                    <strong>Definition:</strong> ${definition}<br><br>
                </div>
            `;
      })
      .join("");

    // Scroll to the top of the page after translation
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (error) {
    console.error("Error:", error);
    alert("An error occurred while translating.");
  }
});
document.addEventListener("DOMContentLoaded", function () {
  const tryMeBtn = document.getElementById("try-me-btn");
  const inputText = document.getElementById("input-text");
  const translateBtn = document.getElementById("translate-btn");

  const samplePhrases = [
    "これはペンです。",
    "昨日は雨が降りました。",
    "東京に行きたいです。",
    "猫が好きです。",
    "英語を話せますか？",
  ];

  document
    .getElementById("breakdown-type")
    .addEventListener("change", function () {
      const inputText = document.getElementById("input-text").value;
      if (inputText) {
        document.getElementById("translate-btn").click();
      }
    });

  tryMeBtn.addEventListener("click", function () {
    const randomPhrase =
      samplePhrases[Math.floor(Math.random() * samplePhrases.length)];
    inputText.value = randomPhrase;
    translateBtn.click();
  });
});
