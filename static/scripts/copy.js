function copyText() {
	var text = document.getElementById("copy-text");

	// Select the text field
	text.select();
	// For mobile devices
	text.setSelectionRange(0, 99999);

	// Copy the text inside the text field
	navigator.clipboard.writeText(text.value);
}

const copyTextSpans = document.querySelectorAll(".copy-urls");
copyTextSpans.forEach((span) => {
	span.addEventListener("click", () => {
		const copyText = span.innerText;

		span.style.opacity = "55%";

		// Copy the text to the clipboard
		navigator.clipboard.writeText(copyText);

		// Reset the opacity of the span after 1 second
		setTimeout(() => {
			span.style.opacity = "";
		}, 1000);
	});
});
