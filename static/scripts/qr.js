function generateQRCode() {
	const urlInput = document.getElementsByClassName("short-url")[0];
	let qrCodeContainer = document.getElementById("qrcode");

	// Check if the QR code container already exists, and create it if not
	if (!qrCodeContainer) {
		qrCodeContainer = document.createElement("div");
		qrCodeContainer.id = "qrcode";
		document
			.querySelector(".short-url-container")
			.appendChild(qrCodeContainer);
	}

	// Remove any previous QR codes if they exist
	while (qrCodeContainer.firstChild) {
		qrCodeContainer.removeChild(qrCodeContainer.firstChild);
	}

	const qrcode = new QRCode(qrCodeContainer, {
		text: urlInput.value,
		width: 128,
		height: 128,
	});

	// Show the QR code container
	qrCodeContainer.style.display = "block";

	// Create a download button
	const downloadButton = document.createElement("a");
	downloadButton.innerText = "Download QR Code";
	downloadButton.href = qrCodeContainer.querySelector("img").src;
	downloadButton.download = "qrcode.png"; // Set the file name for download

	// Append the download button to the QR code container
	qrCodeContainer.appendChild(downloadButton);
}
