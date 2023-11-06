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
}
