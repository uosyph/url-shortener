const urlBoxes = document.querySelectorAll(".url-box");

urlBoxes.forEach((urlBox) => {
	// Uniquify each box
	const classNames = urlBox.getAttribute("class").split(" ");
	const urlBoxIndex = classNames.indexOf("url-box");
	if (urlBoxIndex !== -1) {
		classNames.splice(urlBoxIndex, 1);
	}
	const urlClassName = classNames[0];

	// Get references to the input elements and the button
	const expDateInput = document.querySelector(
		`.${urlClassName} input[name="exp_date"]`
	);
	const isPermanentInput = document.querySelector(
		`.${urlClassName} input[name="is_permanent"]`
	);
	const saveChangesBtn = document.querySelector(
		`.${urlClassName} #save-changes-btn`
	);

	// Get the original values of the input elements
	const originalExpDateValue = expDateInput.value;
	const originalIsPermanentValue = isPermanentInput.checked;

	// Function to disable and enable the button based on the values of the input fields.
	function updateSaveButtonState() {
		if (
			expDateInput.value !== originalExpDateValue ||
			isPermanentInput.checked !== originalIsPermanentValue
		) {
			saveChangesBtn.disabled = false;
		} else {
			saveChangesBtn.disabled = true;
		}
	}

	// Function to check and uncheck the input field based on the values of the expDateInput field.
	function updateIsPermanentInputState() {
		if (expDateInput.value !== "") {
			isPermanentInput.checked = false;
		} else {
			saveChangesBtn.disabled = true;
			if (originalIsPermanentValue === true) {
				isPermanentInput.checked = true;
			} else {
				isPermanentInput.checked = false;
			}
		}
	}

	function updateSaveButtonAccordingly() {
		if (
			originalIsPermanentValue === true &&
			isPermanentInput.checked !== originalIsPermanentValue &&
			expDateInput.value === ""
		) {
			saveChangesBtn.disabled = true;
		}
	}

	// Add event listeners to the input fields.
	expDateInput.addEventListener("change", function (event) {
		updateSaveButtonState(event);
		updateIsPermanentInputState(event);
	});
	isPermanentInput.addEventListener("change", function (event) {
		updateSaveButtonState(event);
		updateSaveButtonAccordingly(event);
	});
});

function scrollToTargetAdjusted() {
	const urlClass = document.querySelector(`.url-${urlName.innerText}`);
	const offset = window.scrollY - 35;
	const scrollPosition = urlClass.getBoundingClientRect().top + offset;

	window.scrollTo({
		top: scrollPosition,
		behavior: "smooth",
	});
}

const urlName = document.querySelector(".go-url");
urlName.addEventListener("click", scrollToTargetAdjusted);
